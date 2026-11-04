"""Pruebas de los filtros de calidad: otros deportes, resúmenes de partido, nombres excluidos y fichas retiradas.
Ejecuta desde la carpeta del proyecto: python tests/test_filtros.py"""
import os, pathlib, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import config
config.PLAYERS_FILE = str(ROOT / "jugadores.csv")
config.IGNORED_FILE = str(ROOT / "ignorados.txt")
config.PLAYER_EXCLUDE_FILE = str(ROOT / "jugadores_excluir.txt")
import pipeline, rules, web

P, I = rules.load_players(), rules.load_ignored()
RUMOR = "El Getafe ya negocia el fichaje de Jadon Sancho"

# 1. URL de resumen de partido (/report/): no hay rumor aunque el titular lo parezca
assert rules.extract_one(RUMOR, "", P, I), "sin URL de partido sí es un rumor"
assert rules.extract_one(RUMOR, "", P, I, url="https://www.skysports.com/football/getafe-vs-x/report/559521") == []
assert rules.extract_one(RUMOR, "", P, I, url="https://ejemplo.com/match/12345") == []
assert rules.extract_one("Fichajes en directo: el Getafe negocia por Jadon Sancho", "", P, I) == [], "los directos no son rumores"

# 2. Nombre de una palabra en jugadores_excluir.txt: no se crea ficha
assert "europa" in rules.load_excluded(), "Europa debe estar en jugadores_excluir.txt"
titulo = "Europa llega al Getafe: el club negocia su fichaje"
assert rules.extract_one(titulo, "", P, I, excluded=set()), "sin exclusión, Europa saldría como jugador"
assert rules.extract_one(titulo, "", P, I) == [], "con jugadores_excluir.txt no debe salir"
assert rules.extract_one(titulo, "", P, I, excluded={"europa"}) == []
assert rules.extract_one(RUMOR, "", P, I, excluded={"europa"}), "un jugador real no se ve afectado"

# 3. Otros deportes: se descartan solo sin club ni término de fútbol; Nadal con "tenis" y fútbol se conserva
assert not rules.is_other_sport("Rafa Nadal, el tenis y el Real Madrid: homenaje en el Bernabéu")
assert not rules.is_other_sport("Nadal deja el tenis y ficha por la presidencia del Mallorca, según la prensa")
assert rules.is_other_sport("Nadal gana su partido de tenis en Roland Garros")
assert rules.is_other_sport("England clinch the cricket series with a record chase")
assert rules.is_other_sport("Verstappen takes pole at the Grand Prix")
assert rules.is_other_sport("Cualquier titular", url="https://www.bbc.com/sport/golf/12345")
assert rules.is_other_sport("Cualquier titular", url="https://www.skysports.com/cricket/news/1")
assert not rules.is_other_sport("Nadal appointed to Real Madrid board", url="https://www.skysports.com/tennis/news/12110/1")
assert not rules.is_other_sport("Messi y el fichaje que sacude la MLS", url="https://www.marca.com/futbol/x.html")

# 4. fetch_all no guarda otros deportes pero sí el fútbol
with tempfile.TemporaryDirectory() as tmp:
    feed = pathlib.Path(tmp) / "f.xml"
    feed.write_text("""<?xml version="1.0"?><rss version="2.0"><channel><title>t</title>
<item><title>Nadal gana su partido de tenis en Roland Garros</title><link>https://ej.com/a</link><pubDate>Mon, 02 Nov 2026 10:00:00 GMT</pubDate></item>
<item><title>Rafa Nadal, el tenis y el Real Madrid: homenaje en el Bernabéu</title><link>https://ej.com/b</link><pubDate>Mon, 02 Nov 2026 10:00:00 GMT</pubDate></item>
<item><title>Hamilton gana el gran premio</title><link>https://ej.com/f1/c</link><pubDate>Mon, 02 Nov 2026 10:00:00 GMT</pubDate></item>
</channel></rss>""", encoding="utf-8")
    config.MAX_AGE_DAYS, config.HISTORY_START = 100000, "2000-01-01"
    db = pipeline.connect(os.path.join(tmp, "t.db"))
    assert pipeline.fetch_all(db, [{"source": "Marca", "url": feed.as_uri(), "weight": 3}]) == 1
    assert db.execute("SELECT title FROM items").fetchone()[0].startswith("Rafa Nadal")

    # 5. revalidate borra la ficha antigua, la recuerda y la redirige con 301 a /jugador/ (y no queda en el sitemap)
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    for n, url in enumerate(["https://sky.com/football/a-vs-b/report/1", "https://sky.com/football/a-vs-b/report/2"]):
        cur = db.execute("INSERT INTO items (source, url, title, published, processed) VALUES ('Sky', ?, ?, ?, 1)", (url, RUMOR + str(n), now))
        db.execute("INSERT INTO rumors (item_id, player, player_slug, from_club, to_club, status, needs_review) "
                   "VALUES (?, 'Jadon Sancho', 'jadon-sancho', 'Manchester United', 'Getafe', 'negociacion', 0)", (cur.lastrowid,))
    assert rules.revalidate(db, P, I) == 2
    assert db.execute("SELECT COUNT(*) FROM rumors").fetchone()[0] == 0
    assert [r[0] for r in db.execute("SELECT slug FROM retirados")] == ["jadon-sancho"]
    import score
    web.RETIRED_PLAYERS[:] = score._retired_slugs(db)
    web._PLAYER_PAGES.clear()
    web._write_redirects([], tmp)
    red = open(os.path.join(tmp, "_redirects"), encoding="utf-8").read()
    assert "/jugador/jadon-sancho/ /jugador/ 301" in red, red
    web._PLAYER_PAGES.add("jadon-sancho")       # si la ficha vuelve a existir, ya no se redirige
    web._write_redirects([], tmp)
    assert "jadon-sancho" not in open(os.path.join(tmp, "_redirects"), encoding="utf-8").read()
    db.close()
print("OK: filtros de calidad")
