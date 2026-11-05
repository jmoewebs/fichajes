"""Fiabilidad histórica: estados de cierre, umbral de 10 y oficiales confirmados a mano (sin red).
Ejecuta desde la carpeta del proyecto: python tests/test_fiabilidad.py"""
import os, pathlib, sys, tempfile
from datetime import datetime, timezone
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import config, pipeline, score, web

AHORA = datetime(2026, 11, 5, 12, 0, tzinfo=timezone.utc)

with tempfile.TemporaryDirectory() as tmp:
    os.chdir(tmp)
    config.CONFIRMED_FILE = os.path.join(tmp, "oficiales_confirmados.txt")
    db = pipeline.connect(os.path.join(tmp, "t.db"))
    n = [0]

    def add(slug, club, status, month_day, source, frm=None, title=None):
        n[0] += 1
        db.execute("INSERT INTO items (source, url, title, published, processed) VALUES (?,?,?,?,1)",
                   (source, f"https://x.com/{n[0]}", title or f"t{n[0]}", f"2026-{month_day}T10:00:00+00:00"))
        db.execute("INSERT INTO rumors (item_id, player, player_slug, from_club, to_club, status, needs_review) VALUES (?,?,?,?,?,?,0)",
                   (n[0], slug.title(), slug, frm, club, status))
    for i in range(12):                          # 12 cumplidos y 2 desmentidos en el mismo club
        add(f"jug{i}", "Girona", "interes", "10-20", "Marca"); add(f"jug{i}", "Girona", "oficial", "10-25", "AS")
    for i in range(2):
        add(f"des{i}", "Girona", "interes", "10-20", "Marca"); add(f"des{i}", "Girona", "descartado", "10-26", "AS")
    add("viejo", "Getafe", "negociacion", "10-07", "Marca"); add("viejo", "Getafe", "negociacion", "10-07", "AS")   # 29 días
    add("fresco", "Getafe", "negociacion", "11-03", "Marca"); add("fresco", "Getafe", "negociacion", "11-04", "AS")  # abierto
    add("sindest", None, "interes", "11-04", "Marca"); add("sindest", None, "interes", "11-04", "AS")
    db.commit()
    assert score.track_rumors(db, now=AHORA) == 16, "el rumor sin destino no se registra"
    r = score.reliability(db)
    g = r["clubs"]["Girona"]
    assert (g["cumplidos"], g["desmentidos"], g["cerrados"], g["pct"]) == (12, 2, 14, 86), g
    ge = r["clubs"]["Getafe"]
    assert (ge["sin_novedades"], ge["abiertos"], ge["cerrados"], ge["pct"]) == (1, 1, 0, None), ge
    assert ge["total"] == 2, "sin novedades cuenta en el recuento"

    # "Sin novedades" no entra en el porcentaje, aunque haya muchos
    for i in range(20):
        add(f"frio{i}", "Girona", "interes", "10-01", "Marca"); add(f"frio{i}", "Girona", "interes", "10-01", "AS")
    db.commit(); score.track_rumors(db, now=AHORA)
    g = score.reliability(db)["clubs"]["Girona"]
    assert (g["sin_novedades"], g["cerrados"], g["pct"]) == (20, 14, 86), g

    # Se reabre con una mención nueva
    add("viejo", "Getafe", "negociacion", "11-05", "Sport"); db.commit()
    score.track_rumors(db, now=AHORA)
    assert db.execute("SELECT outcome FROM seguimiento WHERE player_slug='viejo'").fetchone()[0] == "abierto"

    # "No materializado": cierra la ventana de su liga sin oficial (Getafe = LaLiga, cierra el 2027-02-02)
    score.track_rumors(db, now=datetime(2027, 2, 3, 12, tzinfo=timezone.utc))
    ge = score.reliability(db)["clubs"]["Getafe"]
    assert (ge["no_materializados"], ge["abiertos"], ge["sin_novedades"]) == (2, 0, 0), ge
    assert score.reliability(db)["clubs"]["Girona"]["cumplidos"] == 12, "un cumplido no se pierde"

    # Una renovación o una fuente poco fiable no cuentan como "cumplido"
    add("renov", "Bayern Múnich", "interes", "11-01", "AS")
    add("renov", "Bayern Múnich", "oficial", "11-02", "AS", frm="Bayern Múnich", title="Oficial: renueva hasta 2029")
    add("flojo", "PSG", "interes", "11-01", "AS")
    add("flojo", "PSG", "oficial", "11-02", "Fichajes.net", frm="FC Barcelona", title="Oficial: ficha por el PSG")
    db.commit(); score.track_rumors(db, now=AHORA)
    out = dict(db.execute("SELECT player_slug, outcome FROM seguimiento WHERE player_slug IN ('renov','flojo')").fetchall())
    assert out == {"renov": "abierto", "flojo": "abierto"}, out

    # oficiales_confirmados.txt fuerza "cumplido" (mismo jugador y destino)
    with open(config.CONFIRMED_FILE, "w", encoding="utf-8") as f:
        f.write("# comentario\n\nFlojo;PSG\nRenov;Otro Club\n")
    assert score.load_confirmed() == {("flojo", "PSG"), ("renov", "Otro Club")}
    score.track_rumors(db, now=AHORA)
    out = dict(db.execute("SELECT player_slug, outcome FROM seguimiento WHERE player_slug IN ('renov','flojo')").fetchall())
    assert out == {"renov": "abierto", "flojo": "cumplido"}, ("solo el destino que coincide", out)
    os.remove(config.CONFIRMED_FILE)
    assert score.load_confirmed() == set(), "sin archivo no hay confirmados"

    # Textos: con menos de 10 cerrados solo recuentos; con 10 o más, porcentaje (y "sin novedades" aparte)
    web.RELIABILITY.update(r)
    c_poco = {"cumplidos": 1, "desmentidos": 0, "no_materializados": 0, "sin_novedades": 3, "abiertos": 1,
              "cerrados": 1, "total": 5, "pct": None}
    pocos = web._reliability_html(c_poco, "con destino Getafe")
    assert "3 sin novedades" in pocos and "Aún son pocos datos" in pocos and "%" not in pocos, pocos
    g = {"cumplidos": 12, "desmentidos": 2, "no_materializados": 0, "sin_novedades": 20, "abiertos": 0,
         "cerrados": 14, "total": 34, "pct": 86}
    txt = web._reliability_html(g, "con destino Girona")
    assert "86 %" in txt and "20 sin novedades" in txt and "no entran en el porcentaje" in txt, txt
    assert "Aún no hay" in web._reliability_html(None, "de nadie")
    print("fiabilidad OK:", g)
    db.close(); os.chdir(ROOT)
