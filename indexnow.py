"""Avisa a Bing (y a los buscadores que usan IndexNow: DuckDuckGo, Ecosia, Yandex...) tras cada ejecución,
solo de las páginas que han cambiado (lastmod reciente en el sitemap). Google no usa IndexNow; para Google ya está el sitemap.
La clave viene de la variable de entorno INDEXNOW_KEY (nunca en el código) y se publica como archivo en la raíz de la
web (lo escribe web.write_static) para demostrar que la web es nuestra."""
import json
import re
import urllib.request
from datetime import datetime, timedelta, timezone

import config


def recent_urls(sitemap="web/sitemap.xml", hours=None, now=None):
    """URLs del sitemap con <lastmod> de las últimas `hours` horas."""
    hours = hours or config.INDEXNOW_RECENT_HOURS
    now = now or datetime.now(timezone.utc)
    xml = open(sitemap, encoding="utf-8").read()
    out = []
    for loc, lastmod in re.findall(r"<url><loc>([^<]+)</loc>(?:<lastmod>([^<]+)</lastmod>)?", xml):
        if not lastmod:
            continue
        try:
            d = datetime.fromisoformat(lastmod.replace("Z", "+00:00"))
        except ValueError:
            continue
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        if now - d <= timedelta(hours=hours):
            out.append(loc)
    return out


def ping(sitemap="web/sitemap.xml"):
    key = config.INDEXNOW_KEY
    if not key:
        return "sin clave (define la variable de entorno INDEXNOW_KEY)"
    try:
        urls = recent_urls(sitemap)
    except OSError:
        return "no hay sitemap"
    if not urls:
        return "ninguna página ha cambiado: no se avisa"
    host = config.SITE_URL.split("//", 1)[1].rstrip("/")
    body = json.dumps({"host": host, "key": key, "keyLocation": f"{config.SITE_URL}/{key}.txt",
                       "urlList": urls[:10000]}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return f"aviso enviado ({len(urls)} páginas): respuesta {r.status}"
    except urllib.error.HTTPError as exc:
        return f"respuesta {exc.code}: {exc.reason}"
    except Exception as exc:
        return f"error: {exc}"
