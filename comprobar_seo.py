"""Revisión de SEO de la web generada (equivale a la skill revisar-seo-antes-de-subir, pero portable: sirve en GitHub Actions).
Uso: python comprobar_seo.py [carpeta_web]     Sin salida de problemas = todo correcto (código 0)."""
import pathlib
import re
import sys

BASE = "https://rumoresyfichajes.com"


def comprobar(web="web"):
    web = pathlib.Path(web)
    fallos = []
    for f in sorted(web.rglob("*.html")):
        if f.name == "404.html":
            continue
        t = f.read_text(encoding="utf-8")
        rel = f.relative_to(web).as_posix()
        noindex = re.search(r'<meta[^>]+name=["\']robots["\'][^>]+noindex', t)
        if not noindex and not re.search(rf'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']{re.escape(BASE)}', t):
            fallos.append(f"CANONICAL: {rel}")
        n = len(re.findall(r"<h1[\s>]", t))
        if n != 1:
            fallos.append(f"H1 ({n}): {rel}")
    sm = web / "sitemap.xml"
    if not sm.exists():
        fallos.append("SITEMAP: no existe")
    else:
        s = sm.read_text(encoding="utf-8")
        u, l = s.count("<url>"), s.count("<lastmod>")
        if u == 0 or u != l:
            fallos.append(f"SITEMAP: {u} urls, {l} lastmod")
    for f in web.rglob("*"):
        if f.suffix in (".html", ".xml", ".txt") and "pages.dev" in f.read_text(encoding="utf-8", errors="ignore"):
            fallos.append(f"PAGES.DEV: {f.relative_to(web).as_posix()}")
    return fallos


if __name__ == "__main__":
    problemas = comprobar(sys.argv[1] if len(sys.argv) > 1 else "web")
    print("\n".join(problemas) if problemas else "SEO OK")
    sys.exit(1 if problemas else 0)
