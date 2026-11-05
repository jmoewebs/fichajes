"""Fiabilidad histórica: seguimiento de desenlaces y umbral de 10 rumores cerrados (sin red).
Ejecuta desde la carpeta del proyecto: python tests/test_fiabilidad.py"""
import os, pathlib, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import pipeline, score, web

with tempfile.TemporaryDirectory() as tmp:
    os.chdir(tmp)
    db = pipeline.connect(os.path.join(tmp, "t.db"))
    n = [0]

    def add(slug, club, status, day, source):
        n[0] += 1
        db.execute("INSERT INTO items (source, url, title, published, processed) VALUES (?,?,?,?,1)",
                   (source, f"https://x.com/{n[0]}", f"t{n[0]}", f"2026-10-{day:02d}T10:00:00+00:00"))
        db.execute("INSERT INTO rumors (item_id, player, player_slug, to_club, status, needs_review) VALUES (?,?,?,?,?,0)",
                   (n[0], slug.title(), slug, club, status))
    for i in range(12):                          # 12 cumplidos y 2 desmentidos en el mismo club
        add(f"jug{i}", "Girona", "interes", 1, "Marca"); add(f"jug{i}", "Girona", "oficial", 5, "AS")
    for i in range(2):
        add(f"des{i}", "Girona", "interes", 1, "Marca"); add(f"des{i}", "Girona", "descartado", 6, "AS")
    add("solo", "Getafe", "negociacion", 7, "Marca"); add("solo", "Getafe", "negociacion", 7, "AS")
    add("sindest", None, "interes", 7, "Marca"); add("sindest", None, "interes", 7, "AS")
    db.commit()
    assert score.track_rumors(db) == 15, "el rumor sin destino no se registra"
    r = score.reliability(db)
    g = r["clubs"]["Girona"]
    assert (g["cumplidos"], g["desmentidos"], g["abiertos"], g["cerrados"], g["pct"]) == (12, 2, 0, 14, 86), g
    assert r["clubs"]["Getafe"]["pct"] is None and r["clubs"]["Getafe"]["abiertos"] == 1
    assert r["players"]["solo"]["total"] == 1
    # Es acumulativo: aunque el rumor desaparezca de `rumors`, el seguimiento no se pierde
    db.execute("DELETE FROM rumors"); db.commit()
    score.track_rumors(db)
    assert score.reliability(db)["clubs"]["Girona"]["cumplidos"] == 12
    # Con menos de 10 cerrados solo recuentos; con 10 o más, porcentaje
    web.RELIABILITY.update(r)
    pocos = web._reliability_html(r["clubs"]["Getafe"], "con destino Getafe")
    assert "Aún son pocos datos" in pocos and "%" not in pocos, pocos
    assert "86 %" in web._reliability_html(g, "con destino Girona")
    assert "Aún no hay" in web._reliability_html(None, "de nadie")
    print("fiabilidad OK:", g)
    db.close(); os.chdir(ROOT)
