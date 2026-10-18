"""Avisa a Bing (y a los buscadores que usan IndexNow: DuckDuckGo, Ecosia, Yandex...) de las páginas
de la web, una vez al día. Google no usa IndexNow; para Google ya está el sitemap.
La clave se publica como archivo en la raíz de la web para demostrar que la web es nuestra."""
import json
import os
import re
import urllib.request

import config


def ping(force=False, sitemap="web/sitemap.xml"):
    import web
    if not config.INDEXNOW_KEY:
        return "sin clave"
    if not force and web._now_spain().hour != config.INDEXNOW_HOUR:
        return "hoy ya se avisó o no es la hora"
    try:
        urls = re.findall(r"<loc>([^<]+)</loc>", open(sitemap, encoding="utf-8").read())
    except OSError:
        return "no hay sitemap"
    host = config.SITE_URL.split("//", 1)[1].rstrip("/")
    body = json.dumps({"host": host, "key": config.INDEXNOW_KEY,
                       "keyLocation": f"{config.SITE_URL}/{config.INDEXNOW_KEY}.txt",
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
