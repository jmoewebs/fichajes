"""Base de datos, lectura de feeds RSS/Atom y normalización de nombres.
Solo usa la biblioteca estándar de Python."""
import html
import re
import sqlite3
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY,
    source TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    summary TEXT,
    published TEXT NOT NULL,
    processed INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS rumors (
    id INTEGER PRIMARY KEY,
    item_id INTEGER NOT NULL REFERENCES items(id),
    player TEXT NOT NULL,
    player_slug TEXT NOT NULL,
    from_club TEXT,
    to_club TEXT,
    status TEXT NOT NULL,
    fee_eur_m REAL,
    needs_review INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_rumors_player ON rumors(player_slug);
"""

ATOM = "{http://www.w3.org/2005/Atom}"

# Nos identificamos como lector de noticias; algunos medios rechazan peticiones sin este formato
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; RumoresYFichajes/1.0; +https://rumoresyfichajes.pages.dev)",
    "Accept": "application/rss+xml, application/xml;q=0.9, text/xml;q=0.8, */*;q=0.5",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.6",
}


def connect(path=None):
    db = sqlite3.connect(path or config.DB_PATH)
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    cols = {r[1] for r in db.execute("PRAGMA table_info(items)")}
    if "rumor_only" not in cols:   # columna nueva: titulares que solo sirven para detectar rumores
        db.execute("ALTER TABLE items ADD COLUMN rumor_only INTEGER NOT NULL DEFAULT 0")
        db.commit()
    return db


# ---------- Normalización ----------

def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def norm(text):
    """Minúsculas, sin tildes y con la puntuación cambiada por espacios.
    Conserva la longitud del texto, así las posiciones coinciden con el original."""
    out = []
    for ch in text:
        base = unicodedata.normalize("NFKD", ch)[:1] or ch
        if base == "ø" or base == "Ø":
            base = "o"
        out.append(base.lower() if base.isalnum() else " ")
    return "".join(out)


CLUB_ALIASES = {" ".join(norm(a).split()): club
                for club, aliases in config.CLUBS.items() for a in aliases + [club]}


def canonical_club(name):
    if not name:
        return None
    return CLUB_ALIASES.get(" ".join(norm(name).split()), name.strip())


# ---------- Lectura de feeds ----------

def _text(el, tag):
    found = el.find(tag)
    return (found.text or "").strip() if found is not None else ""


def _clean(raw):
    raw = re.sub(r"<[^>]+>", " ", html.unescape(raw or ""))
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw[: config.SUMMARY_MAX_CHARS]


def _parse_date(raw):
    if raw:
        try:
            dt = parsedate_to_datetime(raw)          # RSS: "Wed, 14 Oct 2026 10:00:00 GMT"
        except (TypeError, ValueError):
            try:
                dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))  # Atom
            except ValueError:
                dt = None
        if dt:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc).isoformat()
    return datetime.now(timezone.utc).isoformat()


def parse_feed(xml_bytes):
    """Devuelve [{title, url, summary, published}] de un feed RSS 2.0 o Atom."""
    root = ET.fromstring(xml_bytes)
    out = []
    for it in root.iter("item"):
        out.append({
            "title": _clean(_text(it, "title")),
            "url": _text(it, "link"),
            "summary": _clean(_text(it, "description")),
            "published": _parse_date(_text(it, "pubDate")),
        })
    for e in root.iter(ATOM + "entry"):
        link = e.find(ATOM + "link")
        out.append({
            "title": _clean(_text(e, ATOM + "title")),
            "url": link.get("href", "") if link is not None else "",
            "summary": _clean(_text(e, ATOM + "summary")),
            "published": _parse_date(_text(e, ATOM + "updated") or _text(e, ATOM + "published")),
        })
    return [i for i in out if i["title"] and i["url"]]


def fetch_all(db, feeds=None):
    """Descarga todos los feeds y guarda los titulares nuevos. Devuelve cuántos son nuevos."""
    new = 0
    for feed in feeds or config.FEEDS:
        items, errors = None, []
        for url in [feed["url"]] + feed.get("fallbacks", []):
            try:
                req = urllib.request.Request(url, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=20) as r:
                    items = parse_feed(r.read())
                if items:
                    break
                errors.append(f"{url}: sin titulares")
            except Exception as exc:  # un feed caído no debe parar el resto
                errors.append(f"{url}: {exc}")
        if not items:
            print(f"[aviso] {feed['source']}: " + " | ".join(errors))
            continue
        if feed.get("google_news"):
            for it in items:   # "Titular - SPORT" -> "Titular"
                it["title"] = re.sub(r"\s+[-–]\s+[^-–]{1,40}$", "", it["title"]).strip()
                it["summary"] = ""   # la entradilla de Google Noticias solo repite el titular
        too_old = (datetime.now(timezone.utc) - timedelta(days=config.MAX_AGE_DAYS)).isoformat()
        items = [it for it in items if it["published"] >= too_old]   # noticias viejas en el feed
        added = 0
        for it in items:
            cur = db.execute(
                "INSERT OR IGNORE INTO items (source, url, title, summary, published, rumor_only) VALUES (?,?,?,?,?,?)",
                (feed["source"], it["url"], it["title"], it["summary"], it["published"], int(bool(feed.get("only_rumors")))),
            )
            new += cur.rowcount
            added += cur.rowcount
        print(f"  {feed['source']}: {len(items)} titulares en el feed, {added} nuevos")
    # Lo anterior al inicio del historial no se guarda (y se borra si ya estaba)
    old_ids = "SELECT id FROM items WHERE published < ?"
    db.execute(f"DELETE FROM rumors WHERE item_id IN ({old_ids})", (config.HISTORY_START,))
    db.execute("DELETE FROM items WHERE published < ?", (config.HISTORY_START,))
    db.commit()
    return new
