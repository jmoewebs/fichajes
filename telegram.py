"""Publica en un canal de Telegram los rumores calientes y un resumen diario de "Lo más leído".

Necesita dos secretos en GitHub: TELEGRAM_BOT_TOKEN (el token del bot) y TELEGRAM_CHAT_ID
(el canal, por ejemplo @rumoresyfichajes). Sin ellos no hace nada.
Recuerda lo publicado en la tabla "publicados" de fichajes.db para no repetir nunca."""
import html
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone

import config

STATUS = {"interes": "Interés", "negociacion": "Negociación", "acuerdo": "Acuerdo", "oficial": "Oficial"}
ORDER = ["interes", "negociacion", "acuerdo", "oficial"]


def _ensure(db):
    db.execute("CREATE TABLE IF NOT EXISTS publicados (clave TEXT PRIMARY KEY, fecha TEXT NOT NULL)")


def _done(db, key):
    return db.execute("SELECT 1 FROM publicados WHERE clave = ?", (key,)).fetchone() is not None


def _mark(db, key):
    db.execute("INSERT OR IGNORE INTO publicados (clave, fecha) VALUES (?, ?)",
               (key, datetime.now(timezone.utc).isoformat()))


def _send(token, chat, text):
    body = urllib.parse.urlencode({"chat_id": chat, "text": text, "parse_mode": "HTML",
                                   "disable_web_page_preview": "false"}).encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=body)
    with urllib.request.urlopen(req, timeout=20) as r:
        res = json.loads(r.read())
    if not res.get("ok"):
        raise RuntimeError(res.get("description", "error de Telegram"))


def best_status(r):
    st = [m["status"] for m in r["mentions"]]
    if "oficial" in st:
        return "oficial"
    known = [s for s in st if s in ORDER]
    return max(known, key=ORDER.index) if known else st[0]


def rumor_key(r):
    # Incluye el estado: si un rumor pasa de "interés" a "acuerdo", se vuelve a publicar
    return f"rumor|{r['player_slug']}|{r['to_club'] or '?'}|{best_status(r)}"


def rumor_text(r):
    e = html.escape
    st = best_status(r)
    head = "✅ <b>FICHAJE CERRADO</b>" if st == "oficial" else f"🔥 <b>RUMOR</b> · {STATUS.get(st, st)}"
    route = f"{e(r['from_club'] or '?')} → {e(r['to_club'] or '?')}"
    lines = [head, f"<b>{e(r['player'])}</b>: {route}"]
    if st != "oficial":
        lines.append(f"🌡️ {r['score']}° en el termómetro · {r['sources']} medio(s)")
    lines.append(f"📰 {e(r['mentions'][0]['source'])}: <a href=\"{e(r['mentions'][0]['url'], quote=True)}\">"
                 f"{e(r['mentions'][0]['title'])}</a>")
    lines.append(f"\n👉 <a href=\"{config.SITE_URL}/rumores/\">Todos los rumores en {e(config.SITE_NAME)}</a>")
    return "\n".join(lines)


def _top_read(news):
    """Lo más leído de las últimas 24 h, pidiéndoselo a la propia web."""
    try:
        with urllib.request.urlopen(f"{config.SITE_URL}/api/clics?horas=24", timeout=20) as r:
            top = json.loads(r.read()).get("top", [])
    except Exception:
        return []
    by_url = {n["url"]: n for n in news}
    return [by_url[t["url"]] for t in top if t["url"] in by_url][:3]


def digest_text(items):
    e = html.escape
    lines = ["📊 <b>Lo más leído hoy</b>"]
    for i, n in enumerate(items, 1):
        lines.append(f"{i}. <a href=\"{e(n['url'], quote=True)}\">{e(n['title'])}</a> ({e(n['source'])})")
    lines.append(f"\n👉 <a href=\"{config.SITE_URL}/\">Más en {e(config.SITE_NAME)}</a>")
    return "\n".join(lines)


def _page_is_live(url):
    """La página de la jornada responde 200 (el aviso puede salir antes de que Cloudflare termine de publicar)."""
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status == 200
    except Exception:
        return False


def _fantasy_message(db, now_spain):
    """(clave, texto) del aviso de la jornada más reciente si toca publicarlo; None si no."""
    try:
        row = db.execute("SELECT jornada, data FROM fx_jornadas ORDER BY jornada DESC LIMIT 1").fetchone()
    except Exception:
        return None                      # todavía no existe la tabla
    if not row or now_spain.hour < 10:   # nada de avisos de madrugada
        return None
    md, snap = row[0], json.loads(row[1])
    key = f"fantasy|{md}"
    rows = snap.get("rows", [])
    bajas = [r for r in rows if r["st"] == "out"]
    dudas = [r for r in rows if r["st"] == "doubt"]
    if _done(db, key) or len(bajas) + len(dudas) < 3:
        return None
    url = f"{config.SITE_URL}/fantasy/jornada-{md}/"
    if not _page_is_live(url):
        return None
    e = html.escape
    by_team = {}
    for r in bajas + dudas:
        by_team[r["team"]] = by_team.get(r["team"], 0) + 1
    top = ", ".join(f"{e(t)} ({n})" for t, n in sorted(by_team.items(), key=lambda x: (-x[1], x[0]))[:3])
    lines = [f"🚑 <b>Parte médico de la jornada {md}</b> · LaLiga Fantasy",
             f"{len(bajas)} baja(s) y {len(dudas)} duda(s) detectadas en la prensa.",
             f"Más afectados: {top}.",
             f"\n👉 <a href=\"{url}\">Lesionados y sancionados por equipo</a>"]
    return key, "\n".join(lines)


def run(db, rumors, news, now_spain=None, sender=None):
    """rumors = lista de rumores publicados (como en la web); news = noticias recientes."""
    token, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not (token and chat) and sender is None:
        return "sin configurar"
    send = sender or (lambda text: _send(token, chat, text))
    _ensure(db)
    first_time = db.execute("SELECT COUNT(*) FROM publicados").fetchone()[0] == 0
    candidates = [r for r in rumors
                  if r["score"] >= config.TELEGRAM_MIN_SCORE or best_status(r) in ("acuerdo", "oficial")]
    if first_time:
        # La primera vez no se publica el atasco de rumores antiguos: solo se apuntan
        for r in candidates:
            _mark(db, rumor_key(r))
        db.commit()
        return f"primera ejecución: {len(candidates)} rumores apuntados sin publicar"
    sent, errors = 0, []
    for r in sorted(candidates, key=lambda r: r["last_update"]):
        if sent >= config.TELEGRAM_MAX_PER_RUN:
            break
        key = rumor_key(r)
        if _done(db, key):
            continue
        try:
            send(rumor_text(r))
            _mark(db, key)
            sent += 1
        except Exception as exc:
            errors.append(str(exc))
            break
    # Parte médico de Fantasy: un solo aviso por jornada, cuando la página ya está publicada
    try:
        txt = _fantasy_message(db, now_spain or datetime.now())
        if txt:
            send(txt[1])
            _mark(db, txt[0])
            sent += 1
    except Exception as exc:
        errors.append(f"fantasy: {exc}")
    # Resumen diario a la hora indicada (hora de España)
    now_spain = now_spain or datetime.now()
    day_key = f"resumen|{now_spain.strftime('%Y-%m-%d')}"
    if now_spain.hour >= config.TELEGRAM_DIGEST_HOUR and not _done(db, day_key):
        items = _top_read(news)
        if items:
            try:
                send(digest_text(items))
                _mark(db, day_key)
                sent += 1
            except Exception as exc:
                errors.append(str(exc))
    db.commit()
    return f"{sent} mensaje(s) publicados" + (" · errores: " + "; ".join(errors) if errors else "")


def welcome_text():
    e = html.escape
    return (f"👋 <b>Bienvenido al canal de {e(config.SITE_NAME)}</b>\n\n"
            "Aquí publicamos automáticamente:\n"
            "🔥 Los rumores de fichajes más calientes, con su termómetro\n"
            "✅ Los fichajes que se cierran\n"
            "📊 Cada noche, las noticias más leídas del día\n\n"
            f"👉 Todo en <a href=\"{config.SITE_URL}/\">{e(config.SITE_URL.split('//', 1)[1])}</a>")


def welcome():
    token, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not (token and chat):
        return "sin configurar: faltan los secretos TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID"
    try:
        _send(token, chat, welcome_text())
        return "mensaje de bienvenida enviado"
    except Exception as exc:
        return f"error: {exc}"
