"""Las clasificaciones van a datos/s-HASH.js (sin sitio en la portada). Ejecuta: python tests/test_clasificaciones_externas.py"""
import os, pathlib, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import web

with tempfile.TemporaryDirectory() as tmp:
    st = {"LaLiga": {"table": [{"team": "X", "pos": 1}], "scorers": [], "matchday": 5}}
    n1 = web._write_standings_file(st, tmp)
    assert n1 and n1.startswith("s-") and n1.endswith(".js"), n1
    assert web._write_standings_file(st, tmp) == n1, "el nombre solo depende del contenido"
    txt = open(os.path.join(tmp, "datos", n1), encoding="utf-8").read()
    assert txt.startswith("window.__STANDINGS=") and '"LaLiga"' in txt
    st["LaLiga"]["matchday"] = 6
    n2 = web._write_standings_file(st, tmp)
    assert n2 != n1, "contenido nuevo = nombre nuevo (caché)"
    web._clean_news_files(tmp)
    assert os.listdir(os.path.join(tmp, "datos")) == [n2], "se borra el archivo viejo"
    assert web._write_standings_file({}, tmp) is None and web._STANDINGS_FILE[0] is None
print("OK: clasificaciones externas")
