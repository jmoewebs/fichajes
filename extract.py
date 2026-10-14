"""Extracción de rumores con la API de Claude (sin SDK, solo urllib)."""
import json
import os
import re
import urllib.request

import config
from pipeline import canonical_club, slugify

STATUSES = set(config.STATUS_BONUS)

PROMPT = """Eres un extractor de datos de fichajes de fútbol. Recibirás titulares de prensa con un id.
Para cada uno, decide si habla de un posible fichaje, renovación o salida de un jugador concreto.
Usa SOLO la información del titular y la entradilla. No inventes nada: si un dato no aparece, usa null.

Responde ÚNICAMENTE con un array JSON, sin texto adicional ni ```:
[{"id": 1, "rumors": [{"player": "Nombre completo", "from_club": "Club o null",
  "to_club": "Club o null", "status": "interes|negociacion|acuerdo|oficial|descartado",
  "fee_eur_m": número en millones de euros o null, "uncertain": true|false}]}]

- Si el titular no trata de fichajes, devuelve "rumors": [].
- "uncertain": true si dudas del jugador o de los clubes.
- Nombres de clubes en su forma habitual en español (FC Barcelona, Bayern Múnich, Inter de Milán).

Titulares:
"""


def call_claude(prompt):
    api_key = os.environ["ANTHROPIC_API_KEY"]
    body = json.dumps({
        "model": config.MODEL,
        "max_tokens": 4000,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={"x-api-key": api_key, "anthropic-version": "2023-06-01",
                 "content-type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read())
    return "".join(b.get("text", "") for b in data["content"] if b["type"] == "text")


def parse_response(text):
    text = re.sub(r"```(?:json)?", "", text).strip()
    return json.loads(text)


def extract_pending(db, llm=call_claude):
    """Procesa los titulares pendientes por lotes. Devuelve cuántos rumores ha guardado."""
    saved = 0
    while True:
        rows = db.execute(
            "SELECT id, title, summary FROM items WHERE processed = 0 ORDER BY id LIMIT ?",
            (config.BATCH_SIZE,),
        ).fetchall()
        if not rows:
            return saved
        lines = [f'{r["id"]}. {r["title"]} — {r["summary"] or ""}' for r in rows]
        try:
            results = parse_response(llm(PROMPT + "\n".join(lines)))
        except Exception as exc:
            print(f"[error] lote {rows[0]['id']}-{rows[-1]['id']}: {exc}")
            return saved  # se reintentará en la próxima ejecución
        valid_ids = {r["id"] for r in rows}
        for res in results:
            if res.get("id") not in valid_ids:
                continue
            for ru in res.get("rumors") or []:
                player = (ru.get("player") or "").strip()
                status = ru.get("status")
                if not player or status not in STATUSES:
                    continue
                db.execute(
                    """INSERT INTO rumors (item_id, player, player_slug, from_club, to_club,
                       status, fee_eur_m, needs_review) VALUES (?,?,?,?,?,?,?,?)""",
                    (res["id"], player, slugify(player), canonical_club(ru.get("from_club")),
                     canonical_club(ru.get("to_club")), status, ru.get("fee_eur_m"),
                     # "oficial" siempre se revisa: es el dato más delicado de publicar mal
                     int(bool(ru.get("uncertain")) or status == "oficial")),
                )
                saved += 1
        db.executemany("UPDATE items SET processed = 1 WHERE id = ?", [(i,) for i in valid_ids])
        db.commit()
