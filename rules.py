"""Extracción de rumores SIN IA: palabras clave + lista de clubes + lista de jugadores.
Gratis e instantáneo. Lo dudoso se marca para revisión manual."""
import csv
import os
import re

import config
from pipeline import norm, slugify

NAME_STOPWORDS = {
    "el", "la", "los", "las", "un", "una", "y", "oficial", "asi", "que", "por", "the", "why",
    "how", "what", "who", "premier", "league", "liga", "laliga", "champions", "mercado",
    "fichajes", "fichaje", "bombazo", "ultima", "hora", "exclusiva", "en", "de", "del", "con",
    "transfer", "news", "live", "real", "football", "futbol", "gossip", "sport",
    # verbos o palabras sueltas que abren titulares y no son nombres
    "confirmado", "confirmada", "colocan", "situan", "apuntan", "desvelan", "revelan", "ojo",
    "atencion", "sorpresa", "giro", "escandalo", "papers", "primera", "plan", "dan", "deja",
    "alerta", "polemica", "locura", "golpe", "adios", "vuelve", "llega", "nuevo", "nueva",
}

# Citas largas entre comillas dobles: suelen ser declaraciones, no el rumor en sí
QUOTE_RE = re.compile(r'["“«][^"”»]{15,}["”»]')

NAME_RE = re.compile(
    r"[A-ZÁÉÍÓÚÑÜÖØ][\wáéíóúñüöøçãõ'\-]+"
    r"(?:\s+(?:de\s+|van\s+|da\s+|dos\s+)?[A-ZÁÉÍÓÚÑÜÖØ][\wáéíóúñüöøçãõ'\-]+){0,2}"
)
FEE_RE = [
    re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:millones|kilos)"),
    re.compile(r"(\d+(?:[.,]\d+)?)\s*m(?:illones)?\s*(?:€|de euros|euros)"),
    re.compile(r"€\s?(\d+(?:[.,]\d+)?)\s?m\b"),
]


def _find_all(text_n, aliases):
    """Busca alias (ya normalizados) en el texto normalizado. Los más largos primero
    y sin solaparse, para que "inter de milan" no cuente también como "milan"."""
    taken, found = [], []
    for alias, value in sorted(aliases, key=lambda a: -len(a[0])):
        for m in re.finditer(r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])", text_n):
            s, e = m.span()
            if any(s < te and ts < e for ts, te in taken):
                continue
            taken.append((s, e))
            found.append((s, e, value))
    return sorted(found)


CLUB_INDEX = [(" ".join(norm(a).split()), club)
              for club, aliases in config.CLUBS.items() for a in aliases]


def load_players(path=None):
    """Lee jugadores.csv -> lista de (alias normalizado, (nombre, club))."""
    path = path or config.PLAYERS_FILE
    index = []
    if not os.path.exists(path):
        return index
    with open(path, encoding="utf-8") as f:
        for row in csv.reader(f, delimiter=";"):
            if not row or row[0].startswith("#"):
                continue
            name = row[0].strip()
            aliases = [a for a in (row[1].split("|") if len(row) > 1 else []) if a.strip()]
            club = row[2].strip() if len(row) > 2 and row[2].strip() else None
            for a in [name] + aliases:
                index.append((" ".join(norm(a).split()), (name, club)))
    return index


def add_player(name, path=None):
    path = path or config.PLAYERS_FILE
    if any(p[1][0] == name for p in load_players(path)):
        return
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"\n{name};;")


def detect_status(text_n):
    """Devuelve (estado, ¿hay alguna palabra clave fuerte?)."""
    padded = f" {' '.join(text_n.split())} "
    status, strong = None, False
    for st, words in config.STATUS_KEYWORDS:
        for w in words:
            if f" {w} " in padded:
                status = status or st
                strong = strong or w not in config.WEAK_KEYWORDS
    return status, strong


def load_ignored(path=None):
    """Nombres que nunca son jugadores (entrenadores, directivos, países...)."""
    path = path or config.IGNORED_FILE
    if not os.path.exists(path):
        return set()
    with open(path, encoding="utf-8") as f:
        return {" ".join(norm(l).split()) for l in f if l.strip() and not l.startswith("#")}


def add_ignored(name, path=None):
    path = path or config.IGNORED_FILE
    if " ".join(norm(name).split()) not in load_ignored(path):
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n{name}")


def is_known_player(name, path=None):
    return any(p[1][0] == name for p in load_players(path))


def detect_fee(title):
    low = title.lower()
    for rx in FEE_RE:
        m = rx.search(low)
        if m:
            try:
                return float(m.group(1).replace(",", "."))
            except ValueError:
                pass
    return None


def guess_name(title, title_n, blocked_spans):
    """Primer grupo de palabras en mayúscula que no sea un club ni una palabra común."""
    for m in NAME_RE.finditer(title):
        s, e = m.span()
        if any(s < be and bs < e for bs, be, _ in blocked_spans):
            continue
        words = m.group(0).split()
        while words and norm(words[0]).strip() in NAME_STOPWORDS:
            words = words[1:]
        if words and len(" ".join(words)) > 2:
            return " ".join(words)
    return None


def assign_clubs(title_n, clubs, player_club):
    """Decide club de origen y de destino a partir de los clubes encontrados."""
    names = []
    for s, e, club in clubs:
        if club not in [c for c, _ in names]:
            names.append((club, s))
    if not names:
        return None, None
    if player_club and player_club in [c for c, _ in names]:
        others = [c for c, _ in names if c != player_club]
        return player_club, (others[0] if others else None)
    padded = " ".join(title_n.split())
    for club, s in names:
        before = " ".join(title_n[max(0, s - 14):s].split())
        if any(before.endswith(m) for m in config.FROM_MARKERS):
            others = [c for c, _ in names if c != club]
            return club, (others[0] if others else None)
    return (names[1][0] if len(names) > 1 else None), names[0][0]


def extract_one(title, summary, players, ignored=frozenset()):
    """Devuelve una lista de rumores (dicts) detectados en un titular."""
    title = QUOTE_RE.sub(" ", title)
    title_n = norm(title)
    status, strong = detect_status(title_n)
    if not status:          # la palabra clave tiene que estar en el titular
        return []
    padded = f" {' '.join(title_n.split())} "
    if any(f" {w} " in padded for w in config.PAST_WORDS):
        return []           # historia o entrevista sobre el pasado, no un rumor de ahora
    if (any(f" {w} " in padded for w in config.MATCH_WORDS)
            and not any(f" {w} " in padded for w in config.TRANSFER_WORDS)):
        return []           # previa de partido, lesión o sanción ("descartado ante el Barça")
    clubs = _find_all(title_n, CLUB_INDEX)
    found_players = {}
    for s, e, (name, club) in _find_all(title_n, players):
        found_players.setdefault(name, club)

    fee = detect_fee(title)
    rumors = []
    if found_players:
        if not clubs:       # sin ningún club en el titular casi siempre es ruido
            return []
        several = len(found_players) > 1
        for name, pclub in found_players.items():
            from_club, to_club = assign_clubs(title_n, clubs, pclub)
            if not from_club and pclub and pclub != to_club:
                from_club = pclub   # si el titular no lo dice, usamos su club actual
            rumors.append({"player": name, "from_club": from_club, "to_club": to_club,
                           "status": status, "fee_eur_m": fee,
                           "uncertain": several})
    elif clubs and strong and not any(f" {w} " in padded for w in config.STAFF_WORDS):
        # nombre desconocido: exigimos más pruebas, y que no sea un directivo o técnico
        name = guess_name(title, title_n, clubs)
        name_n = f" {' '.join(norm(name).split())} " if name else ""
        if name and not any(f" {i} " in name_n for i in ignored):
            from_club, to_club = assign_clubs(title_n, clubs, None)
            rumors.append({"player": name, "from_club": from_club, "to_club": to_club,
                           "status": status, "fee_eur_m": fee, "uncertain": True})
    return rumors


def revalidate(db, players, ignored):
    """Vuelve a pasar las reglas actuales por los rumores ya guardados y borra los que
    ya no se detectarían (así los falsos positivos antiguos desaparecen solos)."""
    rows = db.execute("""SELECT r.id, r.player, i.title, i.summary FROM rumors r
                         JOIN items i ON i.id = r.item_id""").fetchall()
    cache, bad = {}, []
    for r in rows:
        key = (r["title"], r["summary"])
        if key not in cache:
            cache[key] = {ru["player"] for ru in extract_one(r["title"], r["summary"], players, ignored)}
        if r["player"] not in cache[key]:
            bad.append((r["id"],))
    db.executemany("DELETE FROM rumors WHERE id = ?", bad)
    return len(bad)


def extract_pending(db):
    players = load_players()
    ignored = load_ignored()
    removed = revalidate(db, players, ignored)
    if removed:
        print(f"  Rumores antiguos que ya no pasan las reglas (borrados): {removed}")
    saved = 0
    rows = db.execute("SELECT id, title, summary FROM items WHERE processed = 0").fetchall()
    for r in rows:
        for ru in extract_one(r["title"], r["summary"], players, ignored):
            db.execute(
                """INSERT INTO rumors (item_id, player, player_slug, from_club, to_club,
                   status, fee_eur_m, needs_review) VALUES (?,?,?,?,?,?,?,?)""",
                (r["id"], ru["player"], slugify(ru["player"]), ru["from_club"], ru["to_club"],
                 ru["status"], ru["fee_eur_m"], int(ru["uncertain"] or ru["status"] == "oficial")),
            )
            saved += 1
        db.execute("UPDATE items SET processed = 1 WHERE id = ?", (r["id"],))
    db.commit()
    return saved
