"""Configuración del rastreador de rumores de fichajes."""

# Datos de la web para Google y redes sociales
SITE_URL = "https://rumoresyfichajes.com"   # única fuente del dominio (sin barra ni www); todo el generador, Telegram e IndexNow salen de aquí
SITE_NAME = "Rumores y Fichajes"
# Lo que Google muestra: título (máx. ~60 caracteres) y descripción (máx. ~155)
SITE_TITLE = "Rumores y Fichajes | Noticias de fútbol, mercado y Fantasy"
SITE_DESCRIPTION = ("Noticias de fútbol y rumores de fichajes con termómetro, clasificación de LaLiga, Premier y "
                    "Serie A, y bajas para tu Fantasy. Cada hora.")
SITE_TAGLINE = "Fichajes, rumores y noticias de fútbol, actualizados cada hora."
# Código de verificación de Google Search Console (solo el valor de content="...")
GOOGLE_VERIFICATION = "UlSzLwyxSoXaFmkbcCi2i-11eWegnuhRbMtCd54l2CU"

# Ko-fi para donaciones (vacío = sin botón)
KOFI_URL = "https://ko-fi.com/generadorplus"
# Contador de visitas (necesita el KV "VISITAS" vinculado al proyecto en Cloudflare)
VISIT_COUNTER = True

# ID de medición de Google Analytics (empieza por G-). Vacío = sin Analytics ni aviso de cookies
GA_MEASUREMENT_ID = "G-LJ44H4TZ4Y"

# Clasificaciones (football-data.org, gratis con clave). Código de cada liga en la API.
STANDINGS_COMPETITIONS = {"LaLiga": "PD", "Premier League": "PL", "Serie A": "SA",
                          "Bundesliga": "BL1", "Ligue 1": "FL1"}
STANDINGS_EVERY_HOURS = 3        # cada cuántas horas se descargan (ahorra minutos de GitHub)
STANDINGS_SCORERS_LIMIT = 100    # goleadores que se piden; de ellos salen los asistentes
STANDINGS_FILE = "clasificaciones.json"

# Parte médico de Fantasy: palabras del titular que indican cada estado (minúsculas, sin tildes)
FANTASY_IGNORE_FILE = "fantasy_ignorar.txt"
FANTASY_DAYS = 10            # días de titulares que se miran para el parte médico general
FANTASY_WORDS = {
    "back": ["recibe el alta", "alta medica", "recuperado", "recuperados", "se recupera", "vuelve a entrenar",
             "vuelve a la convocatoria", "entra en la convocatoria", "ya entrena", "back in training",
             "returns from injury", "fit again", "available again", "disponible", "back in contention",
             "disponibles", "regresa a la convocatoria", "regresan a la convocatoria", "vuelven a la convocatoria",
             "se reincorpora", "reaparece", "vuelve de una lesion", "vuelve de su lesion", "vuelve tras su lesion",
             "vuelve tras una lesion"],
    # Juega con normalidad: anula una lesión antigua si el titular es más reciente
    "ok": ["titular", "listo", "listos"],
    "susp": ["sancion", "sancionado", "sancionada", "sancionados", "sancionadas", "suspendido", "suspendidos", "expulsion", "expulsado", "tarjeta roja",
             "ciclo de amarillas", "suspended", "suspension", "ban", "banned", "red card"],
    "out": ["lesion", "lesionado", "lesionada", "lesionados", "lesionadas", "se pierde", "se perdera", "se perderan", "baja", "bajas",
            "rotura", "rotura fibrilar", "esguince", "operado", "quirofano", "fuera de la convocatoria",
            "no convocado", "injury", "injured", "ruled out", "to miss", "will miss", "misses", "sidelined",
            "out for", "surgery"],
    "doubt": ["duda", "en duda", "molestias", "tocado", "entre algodones", "se retira", "retirado",
              "doubt", "doubtful", "fitness test", "late fitness test", "knock", "fitness concern",
              "race against time"],
}
# Reglas para no atribuir mal un estado (siempre en minúsculas y sin tildes)
FANTASY_RULES = {
    # El estado solo cuenta si su palabra está a esta distancia (en palabras) del nombre del jugador
    # y no hay otro jugador más cerca de ella. Así "Sanción a Vinicius; Lamine Yamal titular" no es de Lamine.
    "window": 4,
    # Expresiones que contienen palabras de estado pero no hablan de lesiones ni sanciones
    "idioms": ["sin duda", "sin ninguna duda", "no cabe duda", "no hay duda", "fuera de duda", "sin lugar a dudas",
               "no queda duda", "altas y bajas", "altas bajas", "baja forma", "a la baja", "dar de baja",
               "de baja forma", "baja el precio", "baja su precio", "baja la clausula", "bajas de la",
               "mercado de altas", "sancion economica", "sancion al club", "sancion a la federacion",
               # "deja tocado a Carrick": el jugador lo deja tocado, no lo está él
               "deja tocado", "deja tocada", "dejan tocado", "dejan tocada", "dejo tocado", "dejar tocado",
               "deja muy tocado", "dejan muy tocado"],
    # Multa interna del club: no es una sanción que lo deje sin jugar ("El Bayern descarta multar a Olise por su expulsión")
    # Palabras de "susp" que describen una incidencia de partido y no una sanción: caducada la noticia, se descarta
    "red_only": ["expulsion", "expulsado", "tarjeta roja", "red card"],
    "fine": ["multa", "multas", "multar", "multarle", "multado", "multada", "multan"],
    # Palabras que niegan lo que viene justo después: "sin lesión", "no es baja"
    "neg_adjacent": ["sin", "ni", "nunca", "no"],
    "neg_fillers": ["es", "esta", "sera", "hay", "tiene", "tendra", "sufre", "ninguna", "ningun", "la", "el", "una", "un",
                    "de", "mas", "otra", "otro"],
    # Verbos que anulan lo que sigue en las 3 palabras siguientes: "se libra de la sanción", "descartada la lesión"
    "avoid": ["libra", "librarse", "libran", "evita", "evitar", "evitan", "salva", "esquiva", "elude", "escapa",
              "descartada", "descartado", "descarta", "descartan", "desmiente", "desmienten"],
    # Palabras que anulan lo que tienen justo delante: "lesión descartada"
    "neg_after": ["descartada", "descartado", "descartadas", "desmentida", "desmentido", "superada", "superado"],
    # "Sanción por los cabezazos a X": X es la víctima, no el sancionado (causa + una de estas justo antes del nombre)
    "cause": ["por", "tras"],
    "victim": ["a", "sobre", "contra"],
    # "El cartucho Rodri ante las tres bajas": entre el jugador y el estado que va detrás, el estado es de otros
    "apart": ["ante", "frente"],
    # Días que sigue valiendo un aviso (pasado ese tiempo se ignora, salvo las sanciones, que se avisan como antiguas)
    "stale": {"susp": 5, "doubt": 3, "out": 21, "back": 10, "ok": 7},
}

# Apellidos tan comunes que, solos, no sirven para reconocer a un jugador
COMMON_SURNAMES = {"junior", "jr", "silva", "santos", "fernandes", "fernandez", "rodriguez", "garcia",
                   "martinez", "lopez", "gonzalez", "perez", "sanchez", "gomez", "diaz", "alvarez",
                   "hernandez", "moreno", "munoz", "romero", "navarro", "torres", "ramos", "ruiz",
                   "jimenez", "mendes", "costa", "souza", "pereira", "oliveira", "williams", "johnson",
                   "smith", "jones", "brown", "davies", "wilson", "taylor", "neto", "rodrigo", "pedro"}

# Canal de Telegram (necesita los secretos TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID en GitHub)
TELEGRAM_MIN_SCORE = 30      # rumores a partir de este termómetro (los acuerdos y oficiales, siempre)
TELEGRAM_MAX_PER_RUN = 2     # como mucho, mensajes por ejecución (cada hora), para no saturar
TELEGRAM_DIGEST_HOUR = 21    # hora (España) del resumen diario de "Lo más leído"
FANTASY_SEND_WEEKDAYS = (1, 4)   # parte médico de Fantasy: martes (1) y viernes (4)
FANTASY_SEND_HOUR = 12           # a partir de esta hora (España)

# IndexNow: aviso diario a Bing y otros buscadores de todas las páginas
INDEXNOW_KEY = "14ca996f61e8e8c39c670c73dc9243e6"
INDEXNOW_HOUR = 8            # hora (España) del aviso diario

# Cómo se extraen los rumores: "reglas" (gratis, sin IA) o "claude" (API de pago).
EXTRACTOR = "reglas"

# Abrir la página en el navegador al terminar "python run.py"
OPEN_BROWSER = True

# Fuentes RSS. "weight" = fiabilidad de 1 (baja) a 5 (alta). Ajústalo con el tiempo.
# Si una fuente falla verás un [aviso] y el resto seguirá funcionando.
# "fallbacks" (opcional): otras direcciones del mismo medio que se prueban si la primera falla.
# "domain" (opcional): web del medio, para mostrar su icono cuando el enlace pasa por otro sitio.
# OJO: si añades un medio nuevo, añade también su dominio a ALLOWED en functions/api/clics.js
# para que sus noticias cuenten en "Lo más leído".
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
    # ---- Solo para la página de Rumores (no salen en Noticias): "only_rumors": True ----
    # "low_trust": True = fiabilidad baja: no basta para confirmar un rumor dudoso sin un medio fiable
    {"source": "AS", "weight": 3, "domain": "as.com", "google_news": True, "only_rumors": True,
     "url": "https://news.google.com/rss/search?q=site:as.com+fichajes+when:2d&hl=es&gl=ES&ceid=ES:es"},
    {"source": "Mundo Deportivo", "weight": 3, "domain": "mundodeportivo.com", "google_news": True, "only_rumors": True,
     "url": "https://news.google.com/rss/search?q=site:mundodeportivo.com+fichajes+when:2d&hl=es&gl=ES&ceid=ES:es"},
    {"source": "BeSoccer", "weight": 2, "domain": "besoccer.com", "google_news": True, "only_rumors": True,
     "url": "https://news.google.com/rss/search?q=site:besoccer.com+fichajes+when:2d&hl=es&gl=ES&ceid=ES:es"},
    {"source": "Fichajes.net", "weight": 1, "domain": "fichajes.net", "google_news": True, "only_rumors": True,
     "low_trust": True, "url": "https://news.google.com/rss/search?q=site:fichajes.net+when:2d&hl=es&gl=ES&ceid=ES:es"},
    {"source": "Fichajes.com", "weight": 1, "domain": "fichajes.com", "google_news": True, "only_rumors": True,
     "low_trust": True, "url": "https://news.google.com/rss/search?q=site:fichajes.com+when:2d&hl=es&gl=ES&ceid=ES:es"},
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
              "nearly signed", "almost signed", "could have signed", "looking back", "remembers", "recalls",
              "fallido", "frustrado"]

# Titulares de PARTIDO, lesión o sanción ("descartado ante el Barça", "deberá frenar a...").
# Si aparecen y no hay ninguna palabra clara de fichaje (TRANSFER_WORDS), no es un rumor.
MATCH_WORDS = ["ante el", "ante la", "ante los", "ante las", "frente al", "frente a", "contra el",
               "contra la", "partido", "partidos", "duelo", "once inicial", "alineacion", "convocatoria",
               "convocado", "convocados", "lesion", "lesionado", "lesionada", "baja", "bajas", "frenar",
               "jornada", "derbi", "clasico", "expulsion", "expulsado", "multa", "multar", "sancion",
               "sancionado", "sin sitio", "se queda sin", "se queda fuera", "titular", "titularidad",
               "suplente", "banquillo", "minutos", "rival", "previa", "arbitro", "vs", "injury", "injured",
               "ruled out of", "match", "clash", "against", "lineup", "line up", "suspended", "suspension",
               "red card", "fined", "fixture"]
TRANSFER_WORDS = ["fichaje", "fichajes", "fichar", "ficha por", "ficha a", "firma por", "traspaso", "transfer",
                  "oferta", "offer", "bid", "bids", "puja", "clausula", "release clause", "cesion", "cedido",
                  "loan", "contrato", "contract", "renovacion", "renueva", "renovar", "mercado", "signs for",
                  "here we go", "negocia", "negociacion", "deal", "move", "enero", "verano", "january", "summer"]

# Si el nombre desconocido viene acompañado de estas palabras, no es un jugador
STAFF_WORDS = ["director", "director deportivo", "presidente", "president", "ceo", "consejero",
               "ejecutivo", "executive", "directivo", "secretario tecnico", "entrenador", "tecnico",
               "manager", "head coach", "coach", "segundo entrenador", "preparador", "ojeador",
               "scout", "fisio", "medico", "portavoz", "superliga", "a22", "chairman", "owner", "dueno"]

# Expresiones que indican el club de ORIGEN cuando aparecen justo antes del club
FROM_MARKERS = ["from", "desde el", "deja el", "dejar el", "leaves", "salida del", "saldria del", "adios al"]


# Ruido que no es un rumor de fichaje (se comprueba sobre el titular sin tildes y en minúsculas)
MATCH_INCIDENT_WORDS = ["gol", "goles", "falta", "faltas", "penalti", "penalty", "var", "cronica",
                        "resumen", "en directo", "minuto a minuto", "tarjeta", "autogol", "remontada",
                        "goal", "foul", "highlights", "live"]
REPLACEMENT_PHRASES = ["sustituir a", "sustituto de", "sustituta de", "sustituirlo", "suplir a", "relevo de",
                       "relevar a", "sucesor de", "heredero de", "reemplazo de", "reemplazar a",
                       "replace", "replacement for", "successor to", "sucesor para", "recambio de",
                       "alternativa a", "como ", "al estilo de", "tipo "]
RENEWAL_WORDS = ["renovacion", "renueva", "renovar", "renovado", "renews", "new contract", "extends contract",
                 "contract extension", "amplia su contrato", "amplia contrato", "ampliacion de contrato"]
RENEWAL_KEEP = ["fichaje", "fichar", "traspaso", "oferta", "clausula", "salida", "interes", "negocia",
                "cesion", "transfer", "bid", "offer", "interested", "cierra la puerta", "rechaza"]
