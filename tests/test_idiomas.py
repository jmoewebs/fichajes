"""Palabras de rumor por idioma (it, de, fr, pt): solo se aplican al feed de ese idioma (sin red).
Ejecuta desde la carpeta del proyecto: python tests/test_idiomas.py"""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import config
config.PLAYERS_FILE = str(ROOT / "jugadores.csv")
config.IGNORED_FILE = str(ROOT / "ignorados.txt")
import rules

P, I, X = rules.load_players(), rules.load_ignored(), set()


def rumores(titulo, lang):
    return rules.extract_one(titulo, "", P, I, excluded=X, lang=lang)


# (idioma, titular, estado esperado)
BUENOS = [
    ("it", "Trattativa avviata: il Napoli offre 40 milioni al Barcellona per Lamine Yamal", "negociacion"),
    ("it", "Accordo raggiunto tra la Juventus e il Real Madrid per Vinícius", "acuerdo"),
    ("de", "Bayern verhandelt mit Barcelona über Lamine Yamal", "negociacion"),
    ("de", "Einigung: Lamine Yamal wechselt zum FC Bayern", "acuerdo"),
    ("fr", "Mercato : le PSG négocie avec le Real Madrid pour Vinícius", "negociacion"),
    ("fr", "Accord trouvé entre l'OM et le FC Barcelone pour Lamine Yamal", "acuerdo"),
    ("pt", "Benfica faz proposta ao Real Madrid por Vinícius", "negociacion"),
    ("pt", "Acordo fechado: Lamine Yamal vai para o Benfica", "acuerdo"),
]
for lang, titulo, estado in BUENOS:
    r = rumores(titulo, lang)
    assert r and r[0]["status"] == estado, (lang, titulo, r)
    # Sin el idioma de la fuente esas palabras no cuentan (solo las generales de siempre)
    sin = rumores(titulo, None)
    assert not sin or sin[0]["status"] != estado or "mercato" in titulo.lower() or "accord" in titulo.lower() \
        or "acordo" in titulo.lower(), ("no debe aplicarse sin idioma", titulo, sin)

# Ruido que no es rumor: renovaciones, crónicas y partidos en cada idioma
RUIDO = [
    ("it", "Lamine Yamal rinnova con il Barcellona fino al 2030"),
    ("de", "Lamine Yamal verlängert beim FC Barcelona bis 2030"),
    ("fr", "Le FC Barcelone prolonge Lamine Yamal jusqu'en 2030"),
    ("pt", "Barcelona renova com Lamine Yamal até 2030"),
    ("it", "Real Madrid-Juventus: probabili formazioni, Vinícius contro la Juve"),
    ("de", "Spielbericht: Bayern gegen Real Madrid, Tor von Vinícius"),
    ("fr", "Real Madrid-PSG : où voir le match, avec Vinícius"),
    ("pt", "Real Madrid vence Benfica: golo de Vinícius na vitória"),
]
for lang, titulo in RUIDO:
    assert rumores(titulo, lang) == [], (lang, titulo, rumores(titulo, lang))

# Un titular en español no cambia con el parche de idiomas
assert rumores("El Getafe negocia el fichaje de Jadon Sancho", None)
assert rumores("El Getafe negocia el fichaje de Jadon Sancho", "it") == rumores("El Getafe negocia el fichaje de Jadon Sancho", None)
print("OK: palabras por idioma")
