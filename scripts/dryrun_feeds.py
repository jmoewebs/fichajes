"""Prueba (sin tocar fichajes.db ni web/) cuántos rumores nuevos aportaría cada feed candidato.
Copia la BD a un archivo temporal, descarga el feed, aplica las reglas y enseña una muestra de titulares.

Uso (desde la carpeta del proyecto):
    python scripts/dryrun_feeds.py                  # todos los de config.FEEDS_DESACTIVADOS
    python scripts/dryrun_feeds.py Kicker "A Bola"  # solo esos medios
    python scripts/dryrun_feeds.py --activos        # también los de config.FEEDS (para ver lo que aportan hoy)
    python scripts/dryrun_feeds.py --muestra 25     # tamaño de la muestra (15 por defecto)
"""
import os
import pathlib
import shutil
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import config
import pipeline
import rules
import score


def _published(db):
    return {k: len(v) for k, v in score.published_groups(db).items()}


def probar(feed, base_db, muestra):
    tmp = tempfile.mkdtemp()
    try:
        path = os.path.join(tmp, "copia.db")
        shutil.copy(base_db, path)
        db = pipeline.connect(path)
        antes = _published(db)
        max_id = db.execute("SELECT COALESCE(MAX(id), 0) FROM items").fetchone()[0]
        n_nuevos = pipeline.fetch_all(db, [feed])
        rules.extract_pending(db)
        filas = db.execute("""SELECT i.title, r.player, r.from_club, r.to_club, r.status, r.needs_review
                              FROM rumors r JOIN items i ON i.id = r.item_id WHERE i.id > ?
                              ORDER BY i.published DESC""", (max_id,)).fetchall()
        despues = _published(db)
        nuevos_grupos = [k for k in despues if k not in antes]
        crecen = [k for k in despues if k in antes and despues[k] > antes[k]]
        auto = sum(1 for f in filas if not f["needs_review"])
        print()
        print(f"=== {feed['source']} [{feed.get('lang', 'es')}] {feed['url'][:90]}")
        print(f"   titulares nuevos: {n_nuevos} | rumores detectados: {len(filas)} ({auto} sin revisión, {len(filas) - auto} a revisar)")
        print(f"   rumores publicados: {len(antes)} -> {len(despues)} (nuevos: {len(nuevos_grupos)}, con más menciones: {len(crecen)})")
        for f in filas[:muestra]:
            flag = "REVISAR" if f["needs_review"] else "auto   "
            print(f"   - {flag} {f['title'][:95]}")
            print(f"       => {f['player']}: {f['from_club'] or '?'} -> {f['to_club'] or '?'} [{f['status']}]")
        db.close()
        return {"source": feed["source"], "url": feed["url"], "nuevos": n_nuevos, "rumores": len(filas), "auto": auto,
                "grupos_nuevos": len(nuevos_grupos), "grupos_crecen": len(crecen)}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv):
    muestra = 15
    if "--muestra" in argv:
        i = argv.index("--muestra")
        muestra = int(argv[i + 1])
        del argv[i:i + 2]
    activos = "--activos" in argv
    nombres = [a.lower() for a in argv[1:] if not a.startswith("--")]
    feeds = list(config.FEEDS_DESACTIVADOS) + (list(config.FEEDS) if activos else [])
    if nombres:
        feeds = [f for f in feeds if f["source"].lower() in nombres]
    base = config.DB_PATH
    if not os.path.exists(base):
        sys.exit(f"No existe {base}: ejecuta el script desde la carpeta del proyecto.")
    res = [probar(f, base, muestra) for f in feeds]
    print()
    print("RESUMEN")
    for r in res:
        print(f"  {r['source']:22} nuevos={r['nuevos']:4} rumores={r['rumores']:3} sin_revision={r['auto']:3} "
              f"grupos_nuevos={r['grupos_nuevos']} grupos_con_mas_menciones={r['grupos_crecen']}  {r['url'][:60]}")


if __name__ == "__main__":
    main(sys.argv)
