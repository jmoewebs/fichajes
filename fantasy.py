"""Parte médico general para Fantasy: bajas, dudas y recuperados según los titulares recientes.

Los jugadores que se buscan salen de jugadores.csv y de los goleadores de cada liga
(clasificaciones.json). Para cada uno manda el titular más reciente que hable de su estado.
Usa las mismas palabras que la herramienta de la web (config.FANTASY_WORDS)."""
from datetime import datetime, timedelta, timezone

import config
from pipeline import norm


def _n(text):
    return " ".join(norm(text or "").split())


def _has(padded, words):
    return next((w for w in words if f" {w} " in padded), None)


def candidates(players_index=(), standings=None):
    """{nombre: {"keys": set(formas normalizadas), "team": equipo o None}}"""
    out = {}
    for alias, (name, club) in players_index:
        c = out.setdefault(name, {"keys": set(), "team": club})
        c["keys"].update({alias, _n(name)})
    for league in (standings or {}).values():
        for s in league.get("scorers", []):
            if not s.get("player"):
                continue
            c = out.setdefault(s["player"], {"keys": set(), "team": s.get("team")})
            c["keys"].add(_n(s["player"]))
            c["team"] = c["team"] or s.get("team")
    # El apellido solo vale si es largo, poco común y no lo comparte nadie más de la lista
    last = {}
    for name in out:
        parts = _n(name).split()
        if len(parts) > 1:
            last.setdefault(parts[-1], []).append(name)
    for surname, names in last.items():
        if len(names) == 1 and len(surname) >= 4 and surname not in config.COMMON_SURNAMES:
            out[names[0]]["keys"].add(surname)
    for c in out.values():
        c["keys"] = {k for k in c["keys"] if len(k) >= 3}
    return out


def status_of(title_n):
    """Estado que indica un titular ya normalizado, o None."""
    padded = f" {title_n} "
    w = config.FANTASY_WORDS
    if _has(padded, w["back"]):
        return "back", "Recuperado"
    if _has(padded, w["susp"]):
        return "out", "Baja por sanción"
    if _has(padded, w["out"]):
        return "out", "Baja"
    if _has(padded, w["doubt"]):
        return "doubt", "Duda"
    return None


def report(news, cands, days=None):
    """Lista de {player, team, st, label, title, url, source, date}, primero bajas, luego dudas y recuperados."""
    days = days or config.FANTASY_DAYS
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    items = sorted((n for n in news if n["date"] >= cutoff), key=lambda n: n["date"], reverse=True)
    titles = [(n, f" {_n(n['title'])} ") for n in items]
    out = []
    for name, c in cands.items():
        keys = [f" {k} " for k in c["keys"]]
        for n, padded in titles:
            if any(k in padded for k in keys):
                st = status_of(padded.strip())
                if st:
                    out.append({"player": name, "team": c["team"], "st": st[0], "label": st[1],
                                "title": n["title"], "url": n["url"], "source": n["source"], "date": n["date"]})
                    break
    order = {"out": 0, "doubt": 1, "back": 2}
    out.sort(key=lambda r: r["date"], reverse=True)
    out.sort(key=lambda r: order[r["st"]])
    return out
