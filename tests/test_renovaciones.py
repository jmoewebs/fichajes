"""Renovaciones con el propio club: no son rumores de fichaje (sin red).
Ejecuta desde la carpeta del proyecto: python tests/test_renovaciones.py"""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import config
config.PLAYERS_FILE = str(ROOT / "jugadores.csv")
config.IGNORED_FILE = str(ROOT / "ignorados.txt")
import rules

P, I = rules.load_players(), rules.load_ignored()


def rumores(titulo):
    return rules.extract_one(titulo, "", P, I, excluded=set())


NO_ES_RUMOR = [
    "Principio de acuerdo Bayern-Kane",                                      # el caso real de Marca (renovación de Kane)
    "El Real Madrid negocia con Vinícius su continuidad hasta 2030",
    "Oficial: Lamine Yamal, hasta 2031 en el Barça",
    "El Bayern amplía el contrato de Kane hasta 2029",
    "El Barcelona ata a Pedri con un contrato hasta 2030 y el acuerdo es oficial",
    "El Real Madrid blinda a Vinícius: acuerdo cerrado",
]
for t in NO_ES_RUMOR:
    assert rumores(t) == [], (t, rumores(t))

SI_ES_RUMOR = [
    ("El Chelsea ofrece a Lamine Yamal un contrato hasta 2030", "Chelsea"),    # hay otro club: destino
    ("Kane, del Bayern al Barcelona: acuerdo cerrado", "FC Barcelona"),
    ("El Getafe negocia el fichaje de Jadon Sancho", "Getafe"),
]
for t, destino in SI_ES_RUMOR:
    r = rumores(t)
    assert r and r[0]["to_club"] == destino, (t, r)
# Hablar de una salida del propio club sigue siendo rumor
for t in ["Lamine Yamal quiere salir del Barcelona", "El Bayern estudia la salida de Kane"]:
    assert rumores(t), t
print("OK: renovaciones con el propio club")
