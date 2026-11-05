"""Mercado de invierno: cuenta atrás y hora relativa (sin red). Ejecuta: python tests/test_invierno.py"""
import pathlib, sys
from datetime import date, datetime, timezone
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import config, web

A, C = "2027-01-02", "2027-02-02"      # LaLiga: ambas fechas incluidas (32 días)
assert web.winter_status(A, C, date(2026, 11, 5)) == "Faltan 58 días para que abra el mercado"
assert web.winter_status(A, C, date(2027, 1, 1)) == "Falta 1 día para que abra el mercado"
assert web.winter_status(A, C, date(2027, 1, 2)) == "Mercado abierto: día 1 de 32"
assert web.winter_status(A, C, date(2027, 2, 2)) == "Mercado abierto: día 32 de 32"
assert web.winter_status(A, C, date(2027, 2, 3)) == "Mercado cerrado"
ahora = datetime(2026, 11, 5, 12, 0, tzinfo=timezone.utc)
assert web.hace("2026-11-05T11:59:30+00:00", ahora) == "hace 1 min"
assert web.hace("2026-11-05T11:15:00+00:00", ahora) == "hace 45 min"
assert web.hace("2026-11-05T09:00:00Z", ahora) == "hace 3 h"
assert web.hace("2026-11-03T12:00:00+00:00", ahora) == "hace 2 d"
assert web.hace("2026-11-05T09:00:00", ahora) == "hace 3 h"     # sin zona = UTC
# Las fechas de ventana viven solo en config.WINTER_WINDOWS (una fila por liga)
for y, wins in config.WINTER_WINDOWS.items():
    for lg, abre, cierra, *_ in wins:
        assert abre < cierra and abre[:4] == str(y), (lg, abre, cierra)
print("OK: mercado de invierno")
