"""Configuración del rastreador de rumores de fichajes."""
import os

# Datos de la web para Google y redes sociales
SITE_URL = "https://rumoresyfichajes.com"   # única fuente del dominio (sin barra ni www); todo el generador, Telegram e IndexNow salen de aquí
SITE_NAME = "Rumores y Fichajes"
# Lo que Google muestra: título (máx. ~60 caracteres) y descripción (máx. ~155)
SITE_TITLE = "Rumores y Fichajes | Noticias de fútbol, mercado y Fantasy"
SITE_DESCRIPTION = ("Noticias de fútbol y rumores de fichajes con termómetro, clasificación de LaLiga, Premier y "
                    "Serie A, y bajas para tu Fantasy. Cada hora.")
SITE_TAGLINE = "Fichajes, rumores y noticias de fútbol, actualizados cada hora."
# Código de verificación de Google Search Console (solo el valor de content="...")
# Google AdSense: solo el script de verificación en el <head> y ads.txt (aún sin bloques de anuncio)
ADSENSE_CLIENT = "ca-pub-6680488121204410"
GOOGLE_VERIFICATION = "UlSzLwyxSoXaFmkbcCi2i-11eWegnuhRbMtCd54l2CU"

# Ko-fi para donaciones (vacío = sin botón)
KOFI_URL = "https://ko-fi.com/generadorplus"
# Contador de visitas (necesita el KV "VISITAS" vinculado al proyecto en Cloudflare)
VISIT_COUNTER = True

# ID de medición de Google Analytics (empieza por G-). Vacío = sin Analytics ni aviso de cookies
GA_MEASUREMENT_ID = "G-LJ44H4TZ4Y"

# Clasificaciones (football-data.org, gratis con clave). Código de cada liga en la API.
STANDINGS_COMPETITIONS = {"LaLiga": "PD", "Premier League": "PL", "Serie A": "SA",
                          "Bundesliga": "BL1", "Ligue 1": "FL1",
                          "Champions League": "CL", "Championship": "ELC",
                          "Eredivisie": "DED", "Primeira Liga": "PPL"}   # CL: fase de liga (una sola tabla de 36 equipos); gratis en football-data.org
STANDINGS_EVERY_HOURS = 3        # cada cuántas horas se descargan (ahorra minutos de GitHub)
STANDINGS_SCORERS_LIMIT = 100    # goleadores que se piden; de ellos salen los asistentes
STANDINGS_FILE = "clasificaciones.json"

# Parte médico de Fantasy: palabras del titular que indican cada estado (minúsculas, sin tildes)
FANTASY_IGNORE_FILE = "fantasy_ignorar.txt"
FANTASY_DAYS = 10            # días de titulares que se miran para el parte médico general
# Titulares de otros deportes que se cuelan por un apellido ("Ravens QB Jackson", "Mitchell" del rugby): fuera del parte
FANTASY_NOT_FOOTBALL = ["nfl", "qb", "quarterback", "rugby", "nba", "nhl", "mlb", "ravens", "super bowl", "touchdown",
                        "nations championship", "six nations", "cricket", "formula 1", "motogp", "tenis", "atp", "wta"]
CLUB_MIN_NEWS = 3            # club con menos noticias (en NEWS_DAYS) y ningun rumor: noindex y fuera del sitemap

# Mercado de invierno: {año: [(liga, abre, cierra, hora de cierre, oficial?, fuente)]}. Fechas ISO.
# Comprobadas el 2026-11-02. oficial=False: solo en prensa; revisar cuando el organismo lo publique.
WINTER_WINDOWS = {
    2027: [
        ("LaLiga", "2027-01-02", "2027-02-02", "", True,
         "https://www.laliga.com/fichajes/laliga-easports"),            # web oficial de LaLiga: 2 ene - 2 feb, ambos incluidos
        ("Premier League", "2027-01-01", "2027-02-01", "23:00 (hora de Londres)", True,
         "https://www.arsenal.com/news/transfer-windows-confirmed-for-202627-season-aKDa80B8CnMD"),                             # la Premier fija el cierre el lunes 1 feb (31 ene es domingo)
        ("Serie A", "2027-01-02", "2027-02-01", "20:00", False,
         "https://www.zonacalciofaidate.it/serie-a/calciomercato-2026-27-ufficiali-le-date-quando-apre-e-chiude-il-mercato-di-serie-a-b-e-c/"),  # calendario FIGC 2026/27 segun prensa; falta el comunicado
        ("Bundesliga", "2027-01-01", "2027-02-01", "20:00", False,
         "https://ran.joyn.de/sports/fussball/transfers"),              # solo prensa; falta confirmacion de DFL/DFB
        ("Ligue 1", "2027-01-01", "2027-02-01", "19:59", True,
         "https://sports.orange.fr/football/mercato/article/mercato-les-dates-du-mercato-2026-2027-devoilees-exclu-CNT000002pw3ub.html"),                                        # LFP, consejo de administracion del 21 mayo 2026
    ],
}

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

# IndexNow: aviso tras cada ejecución a Bing y otros buscadores de las páginas que han cambiado.
# La clave NO va en el código: se lee de la variable de entorno INDEXNOW_KEY (secreto de GitHub Actions).
INDEXNOW_KEY = os.environ.get("INDEXNOW_KEY", "").strip()
INDEXNOW_RECENT_HOURS = 3    # se avisan las páginas del sitemap con lastmod de las últimas N horas
# Meses del archivo que existieron y ya no se generan (AAAA-MM). Se redirigen con 301 al mes más cercano
# que exista (o a la portada si no hay ninguno cerca) mediante web/_redirects. Añade aquí los que retires.
ARCHIVO_RETIRADOS = ["2025-04", "2026-08"]

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
    # Feed de mercado de Marca (dry-run 2026-11-05: 3 rumores en 30 titulares, sin falsos positivos claros)
    {"source": "Marca", "url": "https://e00-marca.uecdn.es/rss/futbol/mercado-fichajes.xml", "weight": 3, "only_rumors": True},
    {"source": "BBC Sport", "url": "https://feeds.bbci.co.uk/sport/football/rss.xml", "weight": 4},
    {"source": "Sky Sports", "url": "https://www.skysports.com/rss/12040", "weight": 4},
]

# ---- Idioma de la fuente ----
# "lang" (opcional) en cada feed: "es" (por defecto), "en", "it", "de", "fr" o "pt". Se guarda en items.lang y rules.py
# usa las palabras de LANG_WORDS[lang] SOLO para los titulares de ese idioma (se suman a las generales).
# Todo en minúsculas y sin tildes (ü->u, ç->c...), como el resto de listas. Claves:
#   interes / negociacion / acuerdo / oficial / descartado: palabras de estado (como STATUS_KEYWORDS)
#   weak: palabras demasiado genéricas (valen para jugadores conocidos, no para nombres desconocidos)
#   transfer: palabras claras de fichaje (como TRANSFER_WORDS); match: partido, lesión o sanción (MATCH_WORDS)
#   incident: incidencias de partido (MATCH_INCIDENT_WORDS); past: titulares sobre el pasado (PAST_WORDS)
#   renewal / keep: renovaciones (RENEWAL_WORDS) y las palabras que las salvan (RENEWAL_KEEP)
LANG_WORDS = {
    "it": {
        "oficial": ["ufficiale", "ufficializzato", "ufficializza", "ufficializzata", "firma con", "ha firmato"],
        "descartado": ["sfuma", "tramonta", "rifiuta", "rifiutato", "dice no", "rinnova", "rinnovo", "resta alla"],
        "acuerdo": ["accordo", "intesa", "visite mediche", "visita medica", "trattativa chiusa"],
        "negociacion": ["trattativa", "contatti", "contatto", "offerta", "offre", "proposta", "assalto", "avviati i contatti"],
        "interes": ["interesse", "interessa", "obiettivo", "nel mirino", "occhi su", "piace", "pista", "candidato",
                    "calciomercato", "acquisto", "colpo", "trasferimento", "prestito", "clausola"],
        "weak": ["interesse", "interessa", "obiettivo", "piace", "pista", "candidato", "calciomercato", "acquisto",
                 "colpo", "trasferimento", "prestito", "clausola", "offerta", "proposta", "contatto"],
        "transfer": ["calciomercato", "mercato", "acquisto", "colpo", "trasferimento", "prestito", "clausola",
                     "ingaggio", "contratto", "trattativa", "offerta", "riscatto"],
        "match": ["partita", "gara", "derby", "formazione", "convocati", "convocazione", "infortunio", "infortunato",
                  "squalifica", "squalificato", "pagelle", "moviola", "arbitro", "sconfitta", "vittoria", "pareggio",
                  "diretta", "probabili formazioni", "contro il", "contro la"],
        "incident": ["gol", "rigore", "cronaca", "highlights", "autogol", "espulso", "espulsione", "diretta"],
        "past": ["leggenda", "ex giocatore", "ricordo", "anni fa", "storia di"],
        "renewal": ["rinnova", "rinnovo", "rinnovato", "rinnovare", "prolungamento"],
        "keep": ["cessione", "offerta", "interesse", "calciomercato", "addio", "trattativa"],
    },
    "de": {
        "oficial": ["offiziell", "perfekt", "unterschreibt", "verpflichtet", "vorgestellt", "bestatigt"],
        "descartado": ["absage", "sagt ab", "lehnt ab", "kein wechsel", "geplatzt", "bleibt bei", "verlangert"],
        "acuerdo": ["einigung", "einigen sich", "medizincheck", "handschlag", "einig"],
        "negociacion": ["verhandlungen", "verhandlung", "verhandelt", "angebot", "gesprache", "bietet", "konkretisiert"],
        "interes": ["interesse", "interessiert", "im visier", "auf dem zettel", "im blick", "wunschspieler", "kandidat",
                    "wechselgerucht", "wechselgeruchte", "gerucht", "geruchte", "transfer", "wechsel", "leihe", "ausleihe", "ablose"],
        "weak": ["interesse", "interessiert", "im blick", "kandidat", "gerucht", "geruchte", "transfer", "wechsel",
                 "leihe", "ausleihe", "ablose", "angebot", "verhandlungen"],
        "transfer": ["transfer", "wechsel", "wechselt", "verpflichtung", "leihe", "ausleihe", "ablose", "vertrag",
                     "angebot", "verhandlungen", "transfermarkt", "wechselgerucht"],
        "match": ["spiel", "partie", "aufstellung", "kader", "verletzung", "verletzt", "sperre", "gesperrt",
                  "schiedsrichter", "niederlage", "remis", "spieltag", "gegen den", "gegen die", "gegen das"],
        "incident": ["tor", "tore", "elfmeter", "ticker", "highlights", "eigentor", "rote karte", "platzverweis"],
        "past": ["legende", "ehemalige", "erinnert", "vor jahren", "damals"],
        "renewal": ["verlangert", "verlangerung", "vertragsverlangerung", "verlangern"],
        "keep": ["wechsel", "angebot", "interesse", "abgang", "verhandlungen"],
    },
    "fr": {
        "oficial": ["officiel", "officialise", "officialisee", "officialisation", "signe a", "signe au", "recrute"],
        "descartado": ["refuse", "rejette", "ferme la porte", "prolonge", "prolongation", "pas de depart", "abandonne", "piste abandonnee"],
        "acuerdo": ["accord", "accord trouve", "visite medicale", "entente"],
        "negociacion": ["negociations", "negociation", "negocie", "offre", "contacts", "discussions", "approche", "proposition"],
        "interes": ["interesse", "interet", "cible", "dans le viseur", "surveille", "convoite", "piste", "mercato",
                    "transfert", "pret", "clause", "candidat"],
        "weak": ["interesse", "interet", "cible", "piste", "mercato", "transfert", "pret", "clause", "candidat",
                 "offre", "contacts", "discussions", "approche", "proposition", "accord"],
        "transfer": ["mercato", "transfert", "pret", "clause", "contrat", "offre", "recrue", "recrute", "negociations"],
        "match": ["match", "rencontre", "composition", "blesse", "blessure", "suspendu", "suspension", "arbitre",
                  "defaite", "victoire", "journee", "ou voir", "a quelle heure", "sur quelle chaine", "contre le", "contre la"],
        "incident": ["but", "buts", "penalty", "resume", "direct", "highlights", "carton rouge", "expulse"],
        "past": ["legende", "ancien joueur", "souvenir", "il y a des annees", "retour sur"],
        "renewal": ["prolonge", "prolongation", "prolonger", "prolongee", "renouvelle", "renouvellement"],
        "keep": ["transfert", "offre", "interesse", "depart", "mercato"],
    },
    "pt": {
        "oficial": ["oficial", "oficializa", "oficializado", "oficializou", "assina", "assinou", "apresentado"],
        "descartado": ["recusa", "recusou", "rejeita", "rejeitou", "afasta", "descarta", "renova", "renovacao", "porta fechada", "nao sai"],
        "acuerdo": ["acordo", "acordado", "exames medicos", "exame medico", "negocio fechado"],
        "negociacion": ["negociacoes", "negociacao", "negoceia", "proposta", "oferta", "contactos", "conversas", "abordagem"],
        "interes": ["interesse", "interessa", "alvo", "visado", "na mira", "no radar", "cobica", "mercado",
                    "transferencia", "emprestimo", "clausula", "candidato", "reforco"],
        "weak": ["interesse", "interessa", "alvo", "visado", "mercado", "transferencia", "emprestimo", "clausula",
                 "candidato", "reforco", "proposta", "oferta", "contactos", "conversas"],
        "transfer": ["mercado", "transferencia", "emprestimo", "clausula", "contrato", "proposta", "oferta", "reforco", "rescisao"],
        "match": ["jogo", "partida", "onze", "convocados", "convocatoria", "lesao", "lesionado", "castigo", "suspenso",
                  "arbitro", "derrota", "vitoria", "empate", "contra o", "contra a"],
        "incident": ["golo", "golos", "penalti", "cronica", "resumo", "direto", "cartao vermelho", "expulso"],
        "past": ["lenda", "antigo jogador", "recorda", "ha anos", "historia de"],
        "renewal": ["renova", "renovacao", "renovou", "renovar"],
        "keep": ["transferencia", "proposta", "interesse", "saida", "mercado"],
    },
}

# ---- Feeds candidatos (NO se descargan en el Action) ----
# Se prueban con: python scripts/dryrun_feeds.py   (no toca fichajes.db). Para activar uno, pásalo a FEEDS
# y añade su dominio a ALLOWED en functions/api/clics.js. Todos son RSS públicos (comprobado el 2026-11-05: HTTP 200,
# XML válido, robots.txt lo permite). Resultado del dry-run del 2026-11-05 (rumores detectados / titulares nuevos):
#   Kicker 0/18 (el feed "aktuell" son solo crónicas de partido; su feed de fichajes da 404) · L'Équipe 0/50 ·
#   Relevo 0/13 (casi todo otros deportes) · Gazzetta 1/88 (era un entrenador, a revisar) · Record 1/97 ·
#   A Bola 1/364 (feed de todos los deportes: llenaría la BD de titulares inútiles) · Marca por club 0-1 · MD por club 0 ·
#   AS primera 0/5. Aportan casi nada nuevo y cada titular guardado engorda fichajes.db (se sube cada hora).
FEEDS_DESACTIVADOS = [
    {"source": "Relevo", "url": "https://www.relevo.com/rss/", "weight": 3, "domain": "relevo.com", "only_rumors": True},
    {"source": "Kicker", "url": "https://newsfeed.kicker.de/news/aktuell", "weight": 4, "domain": "kicker.de",
     "lang": "de", "only_rumors": True},
    {"source": "L'Équipe", "url": "https://dwh.lequipe.fr/api/edito/rss?path=/Football/", "weight": 4, "domain": "lequipe.fr",
     "lang": "fr", "only_rumors": True},
    {"source": "A Bola", "url": "https://www.abola.pt/rss-articles.xml", "weight": 3, "domain": "abola.pt",
     "lang": "pt", "only_rumors": True},
    # Gazzetta: sus feeds directos (/rss/calcio.xml, /rss/home.xml) están congelados desde 2023-24; solo sirve Google Noticias.
    {"source": "Gazzetta dello Sport", "weight": 4, "domain": "gazzetta.it", "google_news": True, "lang": "it",
     "only_rumors": True, "url": "https://news.google.com/rss/search?q=site:gazzetta.it+calciomercato+when:2d&hl=it&gl=IT&ceid=IT:it"},
    # Record: su RSS directo (record.pt/rss/) falla la verificación SSL en Python local (cadena incompleta); vía Google Noticias.
    {"source": "Record", "weight": 3, "domain": "record.pt", "google_news": True, "lang": "pt", "only_rumors": True,
     "url": "https://news.google.com/rss/search?q=site:record.pt+mercado+when:2d&hl=pt-PT&gl=PT&ceid=PT:pt-150"},
    # Feeds de mercado / por club de los medios que ya usamos
    {"source": "Marca", "url": "https://e00-marca.uecdn.es/rss/futbol/real-madrid.xml", "weight": 3, "only_rumors": True},
    {"source": "Marca", "url": "https://e00-marca.uecdn.es/rss/futbol/barcelona.xml", "weight": 3, "only_rumors": True},
    {"source": "Marca", "url": "https://e00-marca.uecdn.es/rss/futbol/atletico.xml", "weight": 3, "only_rumors": True},
    {"source": "Mundo Deportivo", "url": "https://www.mundodeportivo.com/feed/rss/futbol/fc-barcelona", "weight": 3, "only_rumors": True},
    {"source": "Mundo Deportivo", "url": "https://www.mundodeportivo.com/feed/rss/futbol/real-madrid", "weight": 3, "only_rumors": True},
    {"source": "Mundo Deportivo", "url": "https://www.mundodeportivo.com/feed/rss/futbol/laliga", "weight": 3, "only_rumors": True},
    {"source": "AS", "url": "https://feeds.as.com/mrss-s/pages/as/site/as.com/section/futbol/subsection/primera/", "weight": 3, "only_rumors": True},
]
# Sin RSS utilizable (no añadir): Sport (WAF 406 incluso para sus RSS; ya entra por Google Noticias), AS /fichajes (HTTP 370),
# Mundo Deportivo /fichajes y /atletico-de-madrid (HTTP 403), A Bola/Relevo por club (404).

DB_PATH = "fichajes.db"
PLAYERS_FILE = "jugadores.csv"
IGNORED_FILE = "ignorados.txt"
PLAYER_EXCLUDE_FILE = "jugadores_excluir.txt"   # palabras genéricas que nunca son jugadores (editable a mano)
MODEL = "claude-haiku-5-5"   # solo si EXTRACTOR = "claude"
BATCH_SIZE = 20
SUMMARY_MAX_CHARS = 280      # solo guardamos una entradilla breve, nunca el artículo
MAX_AGE_DAYS = 30            # se ignoran las noticias más antiguas que esto al descargarlas
HISTORY_START = "2026-09-15"  # se borra lo anterior a esta fecha (noticias viejas colada en los feeds)
WINDOW_DAYS = 45             # rumores que cuentan para el termómetro
HOT_DAYS = 21                # la portada y /rumores/ ocultan rumores sin ninguna mención en estos días (las fichas se mantienen)
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
# Un titular con palabra de otro deporte (NOT_FOOTBALL) se descarta SOLO si no nombra ningún club ni estos términos de fútbol
FOOTBALL_TERMS = ["futbol", "football", "soccer", "laliga", "la liga", "premier league", "serie a", "bundesliga",
                  "ligue 1", "champions", "europa league", "conference league", "copa del rey", "fichaje", "fichajes",
                  "fichar", "futbolista", "futbolistas", "gol", "goles", "balon de oro", "seleccion espanola",
                  "mundial de clubes", "uefa", "fifa"]
# Rutas de URL de otros deportes (se descarta el titular aunque sea de un feed generalista)
OTHER_SPORT_URL_PARTS = ["/cricket/", "/golf/", "/tennis/", "/formula1/", "/formula-1/", "/f1/", "/basketball/",
                         "/baloncesto/", "/rugby-union/", "/rugby-league/", "/rugby/", "/boxing/", "/cycling/",
                         "/motorsport/", "/motogp/", "/nba/", "/nfl/", "/athletics/", "/darts/", "/snooker/",
                         "/tenis/", "/ciclismo/"]
# URLs y titulares de resúmenes o directos de partido: no son rumores
MATCH_URL_PARTS = ["/report/", "/match/", "/matches/", "/en-directo", "/directo/", "/minuto-a-minuto", "/live/",
                   "/liveblog", "/cronica"]
MATCH_TITLE_PHRASES = ["en directo", "minuto a minuto", "live blog", "como te lo contamos"]

# Termómetro: única fuente de las etiquetas y descripciones (portada, /hoy, clubes, fichas y página de enero).
# "probable": a partir de este valor un rumor se etiqueta Probable (Oficial solo si el estado es oficial; Rumor por debajo).
# "niveles": (mínimo, descripción) de mayor a menor; web.py (_force) y el JS de la portada leen esta misma tabla.
TERMOMETRO = {"probable": 50,
              "niveles": [(75, "muy avanzado"), (50, "con opciones reales"), (25, "en fase de interés"), (0, "todavía frío")]}

# Nombre que se muestra en las clasificaciones para equipos con nombre corto o distinto del de la API
# (los equipos con ficha de club usan el nombre de la ficha, p. ej. "Barça" -> "FC Barcelona"; esto manda sobre ello).
TEAM_DISPLAY = {
    "Santander": "Racing de Santander", "Deportivo": "Deportivo de La Coruña", "Málaga": "Málaga CF",
    "Celta": "Celta de Vigo", "Alavés": "Deportivo Alavés", "Athletic": "Athletic Club",
    "Nottingham": "Nottingham Forest", "Newcastle": "Newcastle United", "Wolverhampton": "Wolverhampton Wanderers",
    "Sheffield Utd": "Sheffield United", "West Brom": "West Bromwich Albion", "Preston NE": "Preston North End",
    "QPR": "Queens Park Rangers", "Bremen": "Werder Bremen", "Frankfurt": "Eintracht Frankfurt", "Mainz": "Mainz 05",
    "HSV": "Hamburgo", "M'gladbach": "Borussia Mönchengladbach", "PSG": "Paris Saint-Germain",
    "Olympique Lyon": "Olympique de Lyon", "Shaktar": "Shakhtar Donetsk", "PAE AEK": "AEK Atenas",
    "Sl. Bratislava": "Slovan Bratislava", "Acad. Viseu": "Académico de Viseu", "Sittard": "Fortuna Sittard",
    "AZ": "AZ Alkmaar", "Go Ahead": "Go Ahead Eagles", "Den Haag": "ADO Den Haag", "Angers SCO": "Angers",
}

# Clubes con artículo femenino ("la Juventus", "la Real Sociedad"); el resto va con "el" ("el Girona").
CLUBES_FEMENINOS = {"Real Sociedad", "Juventus", "Roma", "AS Roma", "Lazio", "Fiorentina", "Atalanta", "Sampdoria",
                    "Cremonese", "Salernitana", "Udinese", "Spezia", "Reggiana", "Ponferradina", "Cultural Leonesa"}

# Un rumor dudoso (jugador desconocido, "oficial", varios jugadores...) se publica solo
# cuando lo dicen al menos estos medios distintos. Si lo dice uno solo, espera a revisión.
AUTO_PUBLISH_MIN_SOURCES = 2

STATUS_BONUS = {"interes": 0, "negociacion": 10, "acuerdo": 25, "oficial": 100, "descartado": 0}

# Nombre canónico de cada club y las formas en que aparece en los titulares.
# Escribe las formas en minúsculas y sin tildes. Evita palabras comunes ("como", "real").
CLUBS = {
    "Real Madrid": ["real madrid", "madrid"],
    "FC Barcelona": ["fc barcelona", "barcelona", "barca", "barcelone", "barcellona"],
    "Atlético de Madrid": ["atletico de madrid", "atletico madrid", "atletico", "atleti"],
    "Athletic Club": ["athletic club", "athletic bilbao", "athletic"],
    "Real Sociedad": ["real sociedad"],
    "Sevilla": ["sevilla", "siviglia", "seville", "sevilha"],
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
    "Bayern Múnich": ["bayern de munich", "bayern munich", "bayern munchen", "bayern monaco", "bayern munique", "fc bayern", "bayern"],
    "Borussia Dortmund": ["borussia dortmund", "dortmund", "bvb"],
    "Bayer Leverkusen": ["bayer leverkusen", "leverkusen"],
    "RB Leipzig": ["rb leipzig", "leipzig"],
    "PSG": ["paris saint germain", "paris sg", "psg"],
    "Olympique de Marsella": ["olympique de marsella", "marsella", "marseille", "marsiglia", "marselha", "olympique de marseille"],
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

# Renovación de un jugador con SU PROPIO club (solo si el titular no nombra ningún otro club): no es un fichaje.
# Palabras que la delatan, y palabras que indican que en realidad se habla de una salida (entonces sí es rumor).
OWN_CLUB_RENEWAL_WORDS = ["renueva", "renovacion", "renovar", "renovara", "renovado", "renovada", "amplia", "ampliacion",
                          "ata a", "atan a", "atar a", "blinda", "blindan", "blindar", "blindaje", "prolonga", "prolongacion",
                          "extiende", "continuidad", "vinculo", "vinculacion"]
OWN_CLUB_LEAVE_WORDS = ["salida", "salir", "sale", "salgan", "deja", "dejar", "dejaria", "adios", "marcha", "marcharse",
                        "traspaso", "fichaje", "fichar", "venta", "vender", "venderia", "clausula", "irse", "se va", "cesion",
                        "cedido", "no renueva", "rechaza renovar", "sin renovar", "no renovara", "libre"]
# Con el estado en estos valores y solo su club en el titular, tampoco hay destino ("Principio de acuerdo Bayern-Kane")
OWN_CLUB_STATUSES = ["negociacion", "acuerdo", "oficial"]
