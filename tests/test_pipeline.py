"""Prueba completa sin red ni IA: feed de ejemplo + extractor de reglas.
Ejecuta desde la carpeta del proyecto: python tests/test_pipeline.py"""
import os, pathlib, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import config
config.FEEDS = [{"source": "Marca", "url": (ROOT / "tests" / "sample_feed.xml").as_uri(), "weight": 3}]
config.PLAYERS_FILE = str(ROOT / "jugadores.csv")
config.IGNORED_FILE = str(ROOT / "ignorados.txt")
config.MAX_AGE_DAYS = 100000          # el feed de ejemplo tiene fechas fijas
config.HISTORY_START = "2000-01-01"
import pipeline, rules, score
score.WEIGHTS = {"Marca": 3}

with tempfile.TemporaryDirectory() as tmp:
    os.chdir(tmp)
    db = pipeline.connect(os.path.join(tmp, "t.db"))
    assert pipeline.fetch_all(db) == 6
    assert pipeline.fetch_all(db) == 0, "no debe duplicar"
    assert rules.extract_pending(db) == 5, "el partido de Vigo no es un rumor"
    n, pending, page = score.export(db)
    data = score.build(db)
    m = data["players"]["jamal-musiala"]["rumors"]
    assert len(m) == 1 and m[0]["to_club"] == "FC Barcelona" and m[0]["from_club"] == "Bayern Múnich", m
    lau = data["players"]["lautaro-martinez"]["rumors"][0]
    assert lau["to_club"] == "Atlético de Madrid"
    assert "nico-williams" not in data["players"], "oficial debe esperar revisión"
    assert pending == 2, pending   # Nico Williams (oficial) y António Silva (jugador nuevo)
    assert os.path.exists(page) and "Musiala" in open(page, encoding="utf-8").read()
    print("Musiala -> Barça, termómetro:", m[0]["score"], "| noticias:", len(m[0]["mentions"]))
    print("Lautaro -> Atlético:", data["players"]["lautaro-martinez"]["rumors"][0]["mentions"][0]["title"])
    print("Pendientes de revisión:", pending)
    # Un rumor dudoso confirmado por 2 medios distintos se publica sin revisión manual
    db.execute("INSERT INTO items (source, url, title, published, processed) VALUES "
               "('AS', 'https://ejemplo.com/7', 'Chelsea bid for Benfica defender António Silva', ?, 0)",
               (db.execute("SELECT published FROM items WHERE id=5").fetchone()[0],))
    rules.extract_pending(db)
    assert "antonio-silva" in score.build(db)["players"], "2 medios distintos deben bastar"
    # Los falsos positivos que salieron con noticias reales ya no se detectan
    P, I = rules.load_players(), rules.load_ignored()
    for bad in ["Gasperini activa su 'arma secreta' antes del Madrid",
                "Así es la nueva colección del Real Madrid inspirada en Brasil",
                "Wilcox the target again in another damaging Man Utd fallout",
                "The star is Luis Enrique - inside the plans to keep PSG at the top",
                "Huijsen vuelve a Roma tras su negro derbi",
                "El jugador del Bayern que comparan con Rodri y sueña con el Balón de Oro",
                "Bretos, muy tranquilo con Kubo, Gorrotxa, Oyarzabal y la renovación de Remiro",
                "Why Souness rejected Barcelona when he left Liverpool",
                "Francesco Totti, leyenda de la Roma: 'Mi fichaje por el Real Madrid estuvo decidido al 80%'",
                "El Real Madrid ficha al director ejecutivo Bernd Reichart"]:
        assert rules.extract_one(bad, "oferta de fichaje", P, I) == [], bad
    # Y los rumores reales de nombres desconocidos se siguen detectando
    assert rules.extract_one("El Getafe ya negocia el fichaje de Jadon Sancho", "", P, I), "Sancho sí es un rumor"
    db.close()
    os.chdir(ROOT)
print("OK: todas las pruebas pasan")
