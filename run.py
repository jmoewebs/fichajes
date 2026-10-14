"""Uso:
    python run.py                 # todo: leer feeds, detectar rumores y abrir la página
    python run.py ver             # abrir la página sin actualizar
    python run.py review          # ver rumores pendientes de revisión
    python run.py approve 12 15   # aprobar rumores por número
    python run.py reject 13 14    # descartar rumores por número
    python run.py rehacer         # volver a analizar todos los titulares con las reglas actuales
    python run.py fetch | extract | export   # pasos sueltos
"""
import os
import pathlib
import sys
import webbrowser

import config
import pipeline
import score


def extract(db):
    if config.EXTRACTOR == "claude":
        import extract as claude_extract
        return claude_extract.extract_pending(db)
    import rules
    return rules.extract_pending(db)


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "all"
    open_after = cmd in ("all", "rehacer")
    db = pipeline.connect()
    page = None
    if cmd in ("all", "fetch"):
        nuevos = pipeline.fetch_all(db)
        print(f"Titulares nuevos: {nuevos}")
        if os.environ.get("GITHUB_OUTPUT"):   # en GitHub: avisa si hay algo nuevo que publicar
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write(f"nuevos={nuevos}\n")
    if cmd == "rehacer":
        db.execute("DELETE FROM rumors")
        db.execute("UPDATE items SET processed = 0")
        db.commit()
        print(f"Rumores detectados de nuevo: {extract(db)}")
        n, pending, page = score.export(db, all_months=True)
        print(f"Jugadores en la página: {n} · pendientes de revisión: {pending}")
    if cmd in ("all", "extract"):
        print(f"Rumores detectados: {extract(db)}")
    if cmd in ("all", "export"):
        n, pending, page = score.export(db)
        print(f"Jugadores en la página: {n} · pendientes de revisión: {pending}")
        if pending:
            print("  (escribe 'python run.py review' para revisarlos)")
    if open_after and config.OPEN_BROWSER and not os.environ.get("CI"):  # en GitHub no hay navegador
        webbrowser.open(pathlib.Path(page).as_uri())
    if cmd == "ver":
        webbrowser.open(pathlib.Path("web/index.html").resolve().as_uri())
    if cmd == "review":
        rows = db.execute("""SELECT r.id, r.player, r.from_club, r.to_club, r.status, i.source, i.title
                             FROM rumors r JOIN items i ON i.id = r.item_id
                             WHERE r.needs_review = 1 ORDER BY r.id""").fetchall()
        if not rows:
            print("No hay nada pendiente de revisión.")
        for r in rows:
            print(f"#{r['id']}  {r['player']}: {r['from_club'] or '?'} -> {r['to_club'] or '?'} [{r['status']}]"
                  f"\n      {r['source']}: {r['title']}\n")
    if cmd in ("approve", "reject"):
        ids = [int(x) for x in argv[2:]]
        if cmd == "approve":
            import rules
            for (name,) in db.execute(
                    f"SELECT player FROM rumors WHERE id IN ({','.join('?' * len(ids))})", ids):
                rules.add_player(name)   # así la próxima vez lo reconocerá solo
            db.executemany("UPDATE rumors SET needs_review = 0 WHERE id = ?", [(i,) for i in ids])
        else:
            import rules
            for (name,) in db.execute(
                    f"SELECT player FROM rumors WHERE id IN ({','.join('?' * len(ids))})", ids):
                if not rules.is_known_player(name):
                    rules.add_ignored(name)   # no volverá a confundirlo con un jugador
                    print(f"  '{name}' añadido a ignorados.txt")
            db.executemany("DELETE FROM rumors WHERE id = ?", [(i,) for i in ids])
        db.commit()
        score.export(db, all_months=True)
        print(f"{len(ids)} rumor(es) actualizados y página regenerada.")


if __name__ == "__main__":
    main(sys.argv)
