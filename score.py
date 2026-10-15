"""Termómetro de probabilidad y exportación a JSON para el generador de la web."""
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import config
import web
from pipeline import norm

ORDER = ["interes", "negociacion", "acuerdo", "oficial"]
WEIGHTS = {f["source"]: f["weight"] for f in config.FEEDS}


def thermometer(sources, statuses):
    """0-100. Heurística sencilla: cuántas fuentes distintas y cómo de fiables,
    más un plus por el estado más avanzado publicado. Ajústala con datos reales."""
    if "oficial" in statuses:
        return 100
    if statuses == {"descartado"}:
        return 0
    base = sum(WEIGHTS.get(s, 2) for s in sources) * 6
    best = max((s for s in statuses if s in ORDER), key=ORDER.index, default="interes")
    return min(95, base + config.STATUS_BONUS[best])


def published_groups(db, start=None, end=None):
    """Rumores que se publican, agrupados por (jugador, destino).
    Un grupo sale si tiene alguna mención aprobada, o si lo cuentan al menos
    AUTO_PUBLISH_MIN_SOURCES medios distintos (así no hace falta revisarlo a mano)."""
    start = start or (datetime.now(timezone.utc) - timedelta(days=config.WINDOW_DAYS)).isoformat()
    end = end or "9999"
    rows = db.execute(
        """SELECT r.*, i.source, i.url, i.title, i.published FROM rumors r
           JOIN items i ON i.id = r.item_id
           WHERE i.published >= ? AND i.published < ?
           ORDER BY i.published DESC""",
        (start, end),
    ).fetchall()
    groups = defaultdict(list)
    for r in rows:
        groups[(r["player_slug"], r["to_club"] or "?")].append(r)
    out = {}
    for key, mentions in groups.items():
        approved = any(m["needs_review"] == 0 for m in mentions)
        corroborated = len({m["source"] for m in mentions}) >= config.AUTO_PUBLISH_MIN_SOURCES
        if approved or corroborated:
            out[key] = mentions
    return out


def build(db, start=None, end=None):
    """Rumores publicados entre start y end (ISO). Por defecto, los de los últimos WINDOW_DAYS."""
    groups = published_groups(db, start, end)

    players = defaultdict(lambda: {"name": None, "rumors": []})
    clubs = defaultdict(lambda: {"in": [], "out": []})
    for (slug, to_club), mentions in groups.items():
        sources = {m["source"] for m in mentions}
        statuses = {m["status"] for m in mentions}
        entry = {
            "player": mentions[0]["player"],
            "player_slug": slug,
            "from_club": next((m["from_club"] for m in mentions if m["from_club"]), None),
            "to_club": None if to_club == "?" else to_club,
            "score": thermometer(sources, statuses),
            "sources": len(sources),
            "last_update": mentions[0]["published"],
            # Solo titular + enlace a la fuente original: nunca el texto del artículo
            "mentions": [{"source": m["source"], "title": m["title"], "url": m["url"],
                          "date": m["published"], "status": m["status"],
                          "fee": m["fee_eur_m"]} for m in mentions],
        }
        entry["leagues"] = sorted({config.CLUB_LEAGUE.get(c, "Otras ligas")
                                   for c in (entry["from_club"], entry["to_club"]) if c})
        players[slug]["name"] = entry["player"]
        players[slug]["rumors"].append(entry)
        if entry["to_club"]:
            clubs[entry["to_club"]]["in"].append(entry)
        if entry["from_club"]:
            clubs[entry["from_club"]]["out"].append(entry)

    for p in players.values():
        p["rumors"].sort(key=lambda e: -e["score"])
    hot = sorted((e for p in players.values() for e in p["rumors"]), key=lambda e: -e["score"])
    return {"players": dict(players), "clubs": dict(clubs), "hot": hot[:50]}


def leagues_for(title_n, clubs):
    """Ligas de una noticia: por la competición que nombra y por la liga de sus clubes."""
    found = [lg for lg, words in config.COMPETITION_KEYWORDS.items() if _has_any(title_n, words)]
    for c in clubs:
        lg = config.CLUB_LEAGUE.get(c, "Otras ligas")
        if lg not in found:
            found.append(lg)
    return found


def _has_any(text_n, words):
    padded = f" {' '.join(text_n.split())} "
    return any(f" {w} " in padded for w in words)


def build_news(db, start=None, end=None, limit=None):
    """Titulares de fútbol: solo titular, medio, fecha y enlace (nunca el texto).
    Por defecto, los de los últimos NEWS_DAYS días."""
    import rules
    if start is None:
        start = (datetime.now(timezone.utc) - timedelta(days=config.NEWS_DAYS)).isoformat()
        limit = limit or config.NEWS_MAX
    end = end or "9999"
    rumor_items = {m["item_id"] for ms in published_groups(db, start, end).values() for m in ms}
    news = []
    for r in db.execute("""SELECT id, source, title, url, published FROM items
                           WHERE published >= ? AND published < ? ORDER BY published DESC""",
                        (start, end)):
        title_n = norm(r["title"])
        if _has_any(title_n, config.NOT_FOOTBALL):
            continue
        clubs = []
        for _, _, club in rules._find_all(title_n, rules.CLUB_INDEX):
            if club not in clubs:
                clubs.append(club)
        news.append({"title": r["title"], "url": r["url"], "source": r["source"],
                     "date": r["published"], "clubs": clubs, "leagues": leagues_for(title_n, clubs),
                     "live": _has_any(title_n, config.LIVE_WORDS),
                     "rumor": r["id"] in rumor_items})
        if limit and len(news) >= limit:
            break
    return news


def _month_bounds(ym):
    y, m = int(ym[:4]), int(ym[5:])
    ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
    return f"{y:04d}-{m:02d}-01", f"{ny:04d}-{nm:02d}-01"


def month_index(db):
    """[(AAAA-MM, nº noticias de fútbol, nº rumores)] del más reciente al más antiguo."""
    months = [r[0] for r in db.execute(
        "SELECT DISTINCT substr(published, 1, 7) FROM items ORDER BY 1 DESC")]
    out = []
    for ym in months:
        start, end = _month_bounds(ym)
        n_news = len(build_news(db, start, end))
        n_rum = sum(len(p["rumors"]) for p in build(db, start, end)["players"].values())
        out.append((ym, n_news, n_rum))
    return out


def export_archive(db, months, all_months=False):
    """Genera web/archivo/AAAA-MM.html. Siempre el mes actual; los demás si faltan o si all_months."""
    current = datetime.now(timezone.utc).strftime("%Y-%m")
    yms = [m[0] for m in months]
    for i, ym in enumerate(yms):
        path = os.path.join("web", "archivo", f"{ym}.html")
        if not all_months and ym != current and os.path.exists(path):
            continue
        start, end = _month_bounds(ym)
        web.generate_month(ym, build(db, start, end), build_news(db, start, end),
                           prev_ym=yms[i + 1] if i + 1 < len(yms) else None,
                           next_ym=yms[i - 1] if i > 0 else None, months=months)


def export(db, out_dir="data", all_months=False):
    os.makedirs(out_dir, exist_ok=True)
    data = build(db)
    for name, content in data.items():
        with open(os.path.join(out_dir, f"{name}.json"), "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
    pending = db.execute("SELECT COUNT(*) FROM rumors WHERE needs_review = 1").fetchone()[0]
    months = month_index(db)
    export_archive(db, months, all_months)
    page = web.generate(data, build_news(db), months)
    return len(data["players"]), pending, page
