"""Clasificación, goleadores y asistentes de las grandes ligas (fuente: football-data.org).

Necesita una clave gratuita de football-data.org en la variable de entorno FOOTBALL_DATA_TOKEN
(en GitHub, como secreto). Sin clave no hace nada y la web sigue funcionando.
Los datos se guardan en clasificaciones.json, así si la API falla se muestra lo último bueno."""
import json
import os
import time
import urllib.request
from datetime import datetime, timedelta, timezone

import config

API = "https://api.football-data.org/v4"
DATA_VERSION = 2                   # súbelo si cambia lo que se guarda, para forzar una descarga
PAUSE = 6.5                        # plan gratuito: 10 consultas por minuto


def _get(path, token):
    req = urllib.request.Request(API + path, headers={"X-Auth-Token": token, "User-Agent": "RumoresYFichajes/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def load(path=None):
    path = path or config.STANDINGS_FILE
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _parse_table(data):
    total = next((s for s in data.get("standings", []) if s.get("type") == "TOTAL"), None)
    rows = []
    for t in (total or {}).get("table", []):
        team = t.get("team") or {}
        rows.append({
            "id": team.get("id"),
            "pos": t.get("position"), "team": team.get("shortName") or team.get("name"),
            "played": t.get("playedGames"), "won": t.get("won"), "draw": t.get("draw"),
            "lost": t.get("lost"), "gf": t.get("goalsFor"), "ga": t.get("goalsAgainst"),
            "gd": t.get("goalDifference"), "points": t.get("points"), "form": t.get("form") or "",
        })
    return rows


def _forms(matches_data, last=5):
    """{id del equipo: "W,D,L,W,W"} con sus últimos partidos, del más antiguo al más reciente.
    La clasificación del plan gratuito no trae la racha, así que se calcula con los partidos jugados."""
    results = {}
    games = [m for m in matches_data.get("matches", []) if m.get("status") == "FINISHED"]
    for m in sorted(games, key=lambda m: m.get("utcDate") or ""):
        ft = (m.get("score") or {}).get("fullTime") or {}
        h, a = ft.get("home"), ft.get("away")
        hid, aid = (m.get("homeTeam") or {}).get("id"), (m.get("awayTeam") or {}).get("id")
        if h is None or a is None or hid is None or aid is None:
            continue
        results.setdefault(hid, []).append("W" if h > a else "L" if h < a else "D")
        results.setdefault(aid, []).append("W" if a > h else "L" if a < h else "D")
    return {tid: ",".join(r[-last:]) for tid, r in results.items()}


def _parse_scorers(data):
    out = []
    for s in data.get("scorers", []):
        out.append({
            "player": (s.get("player") or {}).get("name"),
            "team": (s.get("team") or {}).get("shortName") or (s.get("team") or {}).get("name"),
            "played": s.get("playedMatches"), "goals": s.get("goals") or 0,
            "assists": s.get("assists") or 0, "penalties": s.get("penalties") or 0,
        })
    return out


def update_if_due(token=None, path=None, force=False):
    """Descarga los datos si han pasado STANDINGS_EVERY_HOURS desde la última vez.
    Devuelve un texto con lo que ha hecho (para el registro de GitHub)."""
    token = token or os.environ.get("FOOTBALL_DATA_TOKEN")
    path = path or config.STANDINGS_FILE
    if not token:
        return "sin clave de football-data.org: no se actualizan las clasificaciones"
    data = load(path)
    last = data.get("_updated")
    if data.get("_version") != DATA_VERSION:
        force = True               # el formato ha cambiado (p. ej. se añadió la racha): descargar ya
    if last and not force:
        age = datetime.now(timezone.utc) - datetime.fromisoformat(last)
        if age < timedelta(hours=config.STANDINGS_EVERY_HOURS):
            return f"clasificaciones al día (hace {int(age.total_seconds() // 60)} min)"
    ok, errors, first = 0, [], True
    for league, code in config.STANDINGS_COMPETITIONS.items():
        try:
            if not first:
                time.sleep(PAUSE)
            first = False
            st = _get(f"/competitions/{code}/standings", token)
            time.sleep(PAUSE)
            sc = _get(f"/competitions/{code}/scorers?limit={config.STANDINGS_SCORERS_LIMIT}", token)
            table = _parse_table(st)
            if not any(t["form"] for t in table):
                try:
                    time.sleep(PAUSE)
                    forms = _forms(_get(f"/competitions/{code}/matches?status=FINISHED", token))
                    for t in table:
                        t["form"] = forms.get(t["id"], "")
                except Exception as exc:
                    errors.append(f"{league} (racha): {exc}")
            new = {
                "matchday": (st.get("season") or {}).get("currentMatchday"),
                "table": table,
                "scorers": _parse_scorers(sc),
            }
            old = data.get(league) or {}
            # "updated" = último cambio real de la tabla (alimenta el lastmod del sitemap), no la hora de la descarga
            same = old.get("updated") and all(old.get(k) == new[k] for k in new)
            new["updated"] = old["updated"] if same else datetime.now(timezone.utc).isoformat()
            data[league] = new
            ok += 1
        except Exception as exc:          # una liga que falla no borra lo que ya teníamos
            errors.append(f"{league}: {exc}")
    if ok:
        data["_updated"] = datetime.now(timezone.utc).isoformat()
        data["_version"] = DATA_VERSION
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
    msg = f"clasificaciones actualizadas: {ok} ligas"
    return msg + (" · errores: " + "; ".join(errors) if errors else "")
