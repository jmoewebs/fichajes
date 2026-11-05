"""Migración idempotente: una BD antigua (sin tabla seguimiento ni items.lang) se actualiza sola al abrirla.
Ejecuta desde la carpeta del proyecto: python tests/test_migracion.py"""
import os, pathlib, sqlite3, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import pipeline

OLD = """CREATE TABLE items (id INTEGER PRIMARY KEY, source TEXT NOT NULL, url TEXT NOT NULL UNIQUE, title TEXT NOT NULL,
  summary TEXT, published TEXT NOT NULL, processed INTEGER NOT NULL DEFAULT 0);
CREATE TABLE rumors (id INTEGER PRIMARY KEY, item_id INTEGER NOT NULL, player TEXT NOT NULL, player_slug TEXT NOT NULL,
  from_club TEXT, to_club TEXT, status TEXT NOT NULL, fee_eur_m REAL, needs_review INTEGER NOT NULL DEFAULT 0);
INSERT INTO items (source, url, title, published) VALUES ('Marca', 'https://x/1', 'titular', '2026-10-01T10:00:00+00:00');"""

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "vieja.db")
    c = sqlite3.connect(path); c.executescript(OLD); c.close()
    for _ in range(3):                                     # idempotente: se puede abrir las veces que sea
        db = pipeline.connect(path)
        tablas = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        cols = [r[1] for r in db.execute("PRAGMA table_info(items)")]
        assert "seguimiento" in tablas and cols.count("lang") == 1 and cols.count("rumor_only") == 1, (tablas, cols)
        assert db.execute("SELECT COUNT(*), MAX(lang) FROM items").fetchone()[:] == (1, None), "los datos no se tocan"
        db.close()
print("OK: migración idempotente")
