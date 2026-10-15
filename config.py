"""Configuración del rastreador de rumores de fichajes."""

# Datos de la web para Google y redes sociales
SITE_URL = "https://rumoresyfichajes.pages.dev"   # sin barra al final; cámbialo si usas otro dominio
SITE_NAME = "Rumores y Fichajes"
# Lo que Google muestra: título (máx. ~60 caracteres) y descripción (máx. ~155)
SITE_TITLE = "Rumores y Fichajes | Fichajes y rumores de fútbol de hoy"
SITE_DESCRIPTION = ("Rumores de fichajes de LaLiga, Premier y Serie A con termómetro de probabilidad, "
                    "clasificaciones y noticias de Marca, AS y Sport actualizadas cada hora.")
SITE_TAGLINE = "Fichajes, rumores y noticias de fútbol, actualizados cada hora."
# Código de verificación de Google Search Console (solo el valor de content="...")
GOOGLE_VERIFICATION = "UlSzLwyxSoXaFmkbcCi2i-11eWegnuhRbMtCd54l2CU"

# ID de medición de Google Analytics (empieza por G-). Vacío = sin Analytics ni aviso de cookies
GA_MEASUREMENT_ID = "G-LJ44H4TZ4Y"

# Clasificaciones (football-data.org, gratis con clave). Código de cada liga en la API.
STANDINGS_COMPETITIONS = {"LaLiga": "PD", "Premier League": "PL", "Serie A": "SA",
                          "Bundesliga": "BL1", "Ligue 1": "FL1"}
STANDINGS_EVERY_HOURS = 3        # cada cuántas horas se descargan (ahorra minutos de GitHub)
STANDINGS_SCORERS_LIMIT = 100    # goleadores que se piden; de ellos salen los asistentes
STANDINGS_FILE = "clasificaciones.json"

# Cómo se extraen los rumores: "reglas" (gratis, sin IA) o "claude" (API de pago).
EXTRACTOR = "reglas"

# Abrir la página en el navegador al terminar "python run.py"
OPEN_BROWSER = True

# Fuentes RSS. "weight" = fiabilidad de 1 (baja) a 5 (alta). Ajústalo con el tiempo.
# Si una fuente falla verás un [aviso] y el resto seguirá funcionando.
# "fallbacks" (opcional): otras direcciones del mismo medio que se prueban si la primera falla.
# "domain" (opcional): web del medio, para mostrar su icono cuando el enlace pasa por otro sitio.
# "google_news" (opcional): el feed es de Google Noticias; se quita " - Medio" del final del titular.
FEEDS = [
    {"source": "Marca", "url": "https://e00-marca.uecdn.es/rss/futbol.xml", "weight": 3},
    {"source": "AS", "url": "https://feeds.as.com/mrss-s/pages/as/site/as.com/section/futbol/portada/", "weight": 3},
    {"source": "Mundo Deportivo", "url": "https://www.mundodeportivo.com/feed/rss/futbol", "weight": 3},
    {"source": "Mundo Deportivo", "url": "https://www.mundodeportivo.com/feed/rss/futbol/internacional", "weight": 3},
    # Sport bloquea las descargas automáticas (cortafuegos), así que sus titulares
    # llegan a través del RSS público de Google Noticias. Cada titular enlaza a Sport.
    {"source": "Sport", "weight": 2, "domain": "sport.es", "google_news": True,
     "url": "https://news.google.com/rss/search?q=site:sport.es+when:2d&hl=es&gl=ES&ceid=ES:es"},
    {"source": "BBC Sport", "url": "https://feeds.bbci.co.uk/sport/football/rss.xml", "weight": 4},
    {"source": "Sky Sports", "url": "https://www.skysports.com/rss/12040", "weight": 4},
]

DB_PATH = "fichajes.db"
PLAYERS_FILE = "jugadores.csv"
IGNORED_FILE = "ignorados.txt"
MODEL = "claude-haiku-5-5"   # solo si EXTRACTOR = "claude"
BATCH_SIZE = 20
SUMMARY_MAX_CHARS = 280      # solo guardamos una entradilla breve, nunca el artículo
MAX_AGE_DAYS = 30            # se ignoran las noticias más antiguas que esto al descargarlas
HISTORY_START = "2026-09-15"  # se borra lo anterior a esta fecha (noticias viejas colada en los feeds)
WINDOW_DAYS = 45             # rumores que cuentan para el termómetro
NEWS_DAYS = 14               # días que aparecen en la columna de fechas de la portada
RECENT_DAYS = 3              # días que se ven en la vista "Recientes"
NEWS_MAX = 6000              # máximo de noticias en la portada

# Titulares que contengan alguna de estas palabras no son de fútbol y no se muestran
NOT_FOOTBALL = ["f1", "formula 1", "grand prix", "gran premio", "motogp", "pit wall", "mclaren",
                "ferrari", "verstappen", "golf", "pga", "liv golf", "ryder cup", "rugby",
                "red roses", "six nations", "starting xv", "nfl", "nba", "euroliga", "baloncesto",
                "tennis", "tenis", "atp", "wta", "wimbledon", "roland garros", "cricket", "boxing",
                "boxeo", "ufc", "mma", "snooker", "darts", "ciclismo", "cycling", "tour de francia",
                "tour de france", "atletismo", "athletics", "balonmano", "handball", "team boss",
                "sabalenka", "alcaraz", "sinner", "djokovic", "swiatek", "gauff", "wuhan",
                "mekies", "fernando alonso", "carlos sainz", "marc marquez"]
LIVE_WORDS = ["en directo", "en vivo", "live"]

# Un rumor dudoso (jugador desconocido, "oficial", varios jugadores...) se publica solo
# cuando lo dicen al menos estos medios distintos. Si lo dice uno solo, espera a revisión.
AUTO_PUBLISH_MIN_SOURCES = 2

STATUS_BONUS = {"interes": 0, "negociacion": 10, "acuerdo": 25, "oficial": 100, "descartado": 0}

# Nombre canónico de cada club y las formas en que aparece en los titulares.
# Escribe las formas en minúsculas y sin tildes. Evita palabras comunes ("como", "real").
CLUBS = {
    "Real Madrid": ["real madrid", "madrid"],
    "FC Barcelona": ["fc barcelona", "barcelona", "barca"],
    "Atlético de Madrid": ["atletico de madrid", "atletico madrid", "atletico", "atleti"],
    "Athletic Club": ["athletic club", "athletic bilbao", "athletic"],
    "Real Sociedad": ["real sociedad"],
    "Sevilla": ["sevilla"],
    "Real Betis": ["real betis", "betis"],
    "Valencia": ["valencia cf", "valencia"],
    "Villarreal": ["villarreal"],
    "Girona": ["girona"],
    "Getafe": ["getafe"],
    "Celta": ["celta de vigo", "celta"],
    "Osasuna": ["osasuna"],
    "Mallorca": ["rcd mallorca", "mallorca"],
    "Rayo Vallecano": ["rayo vallecano", "rayo"],
    "Espanyol": ["espanyol"],
    "Alavés": ["deportivo alaves", "alaves"],
    "Las Palmas": ["ud las palmas", "las palmas"],
    "Levante": ["levante"],
    "Elche": ["elche"],
    "Real Oviedo": ["real oviedo", "oviedo"],
    "Liverpool": ["liverpool"],
    "Arsenal": ["arsenal"],
    "Chelsea": ["chelsea"],
    "Manchester City": ["manchester city", "man city"],
    "Manchester United": ["manchester united", "man united", "man utd"],
    "Tottenham": ["tottenham hotspur", "tottenham", "spurs"],
    "Newcastle": ["newcastle united", "newcastle"],
    "Aston Villa": ["aston villa"],
    "West Ham": ["west ham united", "west ham"],
    "Brighton": ["brighton"],
    "Bayern Múnich": ["bayern de munich", "bayern munich", "bayern munchen", "bayern"],
    "Borussia Dortmund": ["borussia dortmund", "dortmund", "bvb"],
    "Bayer Leverkusen": ["bayer leverkusen", "leverkusen"],
    "RB Leipzig": ["rb leipzig", "leipzig"],
    "PSG": ["paris saint germain", "paris sg", "psg"],
    "Olympique de Marsella": ["olympique de marsella", "marsella", "marseille"],
    "Mónaco": ["as monaco", "monaco"],
    "Juventus": ["juventus", "juve"],
    "Inter de Milán": ["inter de milan", "inter milan", "internazionale", "inter"],
    "AC Milan": ["ac milan", "milan"],
    "Napoli": ["napoli", "napoles"],
    "Roma": ["as roma", "roma"],
    "Atalanta": ["atalanta"],
    "Benfica": ["benfica"],
    "Oporto": ["fc porto", "oporto", "porto"],
    "Sporting de Portugal": ["sporting de portugal", "sporting cp", "sporting lisbon"],
    "Ajax": ["ajax"],
    "Galatasaray": ["galatasaray"],
    "Al Hilal": ["al hilal"],
    "Al Nassr": ["al nassr"],
}

# Liga de cada club (los que no estén aquí cuentan como "Otras ligas")
LEAGUES = ["LaLiga", "Premier League", "Serie A", "Bundesliga", "Ligue 1",
           "Champions League", "Europa League", "Selecciones", "Otras ligas"]
CLUB_LEAGUE = {
    **dict.fromkeys(["Real Madrid", "FC Barcelona", "Atlético de Madrid", "Athletic Club",
                     "Real Sociedad", "Sevilla", "Real Betis", "Valencia", "Villarreal", "Girona",
                     "Getafe", "Celta", "Osasuna", "Mallorca", "Rayo Vallecano", "Espanyol",
                     "Alavés", "Las Palmas", "Levante", "Elche", "Real Oviedo"], "LaLiga"),
    **dict.fromkeys(["Liverpool", "Arsenal", "Chelsea", "Manchester City", "Manchester United",
                     "Tottenham", "Newcastle", "Aston Villa", "West Ham", "Brighton"], "Premier League"),
    **dict.fromkeys(["Juventus", "Inter de Milán", "AC Milan", "Napoli", "Roma", "Atalanta"], "Serie A"),
    **dict.fromkeys(["Bayern Múnich", "Borussia Dortmund", "Bayer Leverkusen", "RB Leipzig"], "Bundesliga"),
    **dict.fromkeys(["PSG", "Olympique de Marsella", "Mónaco"], "Ligue 1"),
}
# Palabras del titular que indican la competición (minúsculas, sin tildes)
COMPETITION_KEYWORDS = {
    "Champions League": ["champions"],
    "Europa League": ["europa league", "conference league"],
    "Premier League": ["premier league", "premier"],
    "LaLiga": ["laliga", "la liga", "liga ea sports", "primera division"],
    "Serie A": ["serie a", "calcio"],
    "Bundesliga": ["bundesliga"],
    "Ligue 1": ["ligue 1"],
    "Selecciones": ["seleccion", "la roja", "mundial", "world cup", "nations league",
                    "eurocopa", "national team", "international break"],
}

# Palabras clave por estado (minúsculas, sin tildes). Gana el primer estado de esta lista
# que aparezca en el titular, así que "rechaza la oferta" cuenta como descartado.
STATUS_KEYWORDS = [
    ("oficial", ["oficial", "official", "officially", "confirmed", "here we go", "firma por",
                 "ficha por", "signs for", "nuevo jugador", "anuncia el fichaje", "joins", "completes"]),
    ("descartado", ["descarta", "descartado", "descartada", "rechaza", "rechazada", "rules out",
                    "rejected", "no saldra", "se queda", "cierra la puerta", "renueva", "renovacion",
                    "new contract", "extends contract", "contract extension"]),
    ("acuerdo", ["acuerdo", "agreement", "agreed", "agree", "deal done", "cierra el fichaje",
                 "pacto", "ficha a", "reconocimiento medico", "medical"]),
    ("negociacion", ["negocia", "negociacion", "negociaciones", "talks", "oferta", "offer", "bid",
                     "puja", "conversaciones", "contactos", "propuesta", "approach", "ofrece",
                     "ofrecen", "offers", "bids", "sondea", "tantea", "pregunta por",
                     "llama a la puerta", "negociando"]),
    ("interes", ["interes", "interesa", "objetivo", "target", "quiere", "pretende", "linked",
                 "candidato", "suena para", "suenan para", "radar", "sigue a", "siguen a", "eyes", "eyeing",
                 "monitoring", "keen", "pide", "piden", "orbita", "fichaje", "fichar", "traspaso",
                 "transfer", "cesion", "cedido", "loan", "clausula", "release clause", "mercado",
                 "salida", "move"]),
]

# Palabras demasiado genéricas: valen para jugadores de jugadores.csv, pero NO bastan
# para dar por bueno un rumor de un nombre desconocido.
WEAK_KEYWORDS = {"target", "objetivo", "quiere", "move", "mercado", "salida", "pide", "piden",
                 "keen", "eyes", "eyeing", "monitoring", "radar", "orbita", "suena para", "suenan para", "linked",
                 "candidato", "interes", "interesa", "pretende", "sigue a", "siguen a",
                 "approach", "talks", "contactos", "propuesta", "conversaciones", "offer",
                 "offers", "oferta", "official", "oficial", "confirmed", "completes", "joins",
                 "medical", "agree", "agreed", "renueva", "renovacion", "se queda", "rechaza"}

# Titulares que hablan del PASADO (entrevistas, historias): nunca son rumores actuales
PAST_WORDS = ["leyenda", "exjugador", "ex jugador", "historico", "recuerda", "recuerdo", "recuerdos",
              "hace anos", "en su dia", "en su momento", "estuvo decidido", "estuvo a punto",
              "pudo fichar", "pudo jugar", "estuvo cerca", "cuando dejo", "cuando era", "cuando jugaba",
              "por que rechazo", "legend", "former", "when he left", "when he was", "years ago",
              "nearly signed", "almost signed", "could have signed", "looking back", "remembers", "recalls"]

# Si el nombre desconocido viene acompañado de estas palabras, no es un jugador
STAFF_WORDS = ["director", "director deportivo", "presidente", "president", "ceo", "consejero",
               "ejecutivo", "executive", "directivo", "secretario tecnico", "entrenador", "tecnico",
               "manager", "head coach", "coach", "segundo entrenador", "preparador", "ojeador",
               "scout", "fisio", "medico", "portavoz", "superliga", "a22", "chairman", "owner", "dueno"]

# Expresiones que indican el club de ORIGEN cuando aparecen justo antes del club
FROM_MARKERS = ["from", "desde el", "deja el", "dejar el", "leaves", "salida del", "saldria del", "adios al"]
