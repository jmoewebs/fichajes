# Rumores y Fichajes (rumoresyfichajes.pages.dev)

Web estática de rumores y noticias de fútbol, hecha en Python, **gratuita y sin IA en la actualización**. Idioma de la web y de las respuestas: español. El usuario trabaja en Windows (PowerShell).

## Reglas del proyecto
- **Todo gratis.** Nada de APIs, hostings ni servicios de pago. Válido: GitHub, GitHub Actions, Cloudflare Pages/Functions/KV/D1, Search Console, Analytics, Ko-fi.
- Editar solo lo necesario, no reescribir archivos enteros. Respuestas cortas. Preguntar lo mínimo.
- No exponer el nombre real del usuario en enlaces públicos.
- Antes de editar: `git pull` (el Action sube commits cada hora y toca `fichajes.db`, `jugadores.csv`, `ignorados.txt` y `clasificaciones.json`).
- Nunca subas una copia vieja de esos datos: pisarías lo que el Action actualizó.

## Cómo funciona
- `run.py` es el punto de entrada. Descarga feeds RSS (`pipeline.py`, `config.FEEDS`), extrae rumores con reglas (`rules.py`, sin IA), puntúa (`score.py`) y genera la web en `web/` (`web.py`).
- Base de datos SQLite `fichajes.db`: tablas `items` (titulares), `rumors`, `fx_jornadas` (Fantasy).
- `fantasy.py` (bajas y dudas por jornada), `standings.py` (clasificaciones), `telegram.py` (avisos al canal).
- GitHub Actions (`.github/workflows/actualizar.yml`) corre cada hora, commitea los datos y despliega con `wrangler pages deploy web`. El paso de Telegram va antes del despliegue, por eso los enlaces a páginas nuevas se comprueban con `_page_is_live`.
- Cloudflare Pages Functions en `functions/api/`: `clics.js` (D1, binding `DB`), `visitas.js` (KV `VISITAS`), `votos.js` (D1). Comprueba el árbol con `ls` antes de tocarlas.
- Páginas generadas: portada (Noticias, Rumores, Clasificación, Fantasy), `/fantasy/jornada-N/`, `/jugador/` y `/jugador/slug/` (rumores con ≥2 menciones), `/rumores/movimientos/`, `feed.xml`, clubes, archivo.

## Reglas de calidad de los rumores (no romper)
- Un rumor exige palabra de estado en el titular, club y no ser partido, pasado, modismo ("a lo X"), sustituto ("sustituir a X"), renovación simple ni incidencia de partido (`MATCH_WORDS`, `PAST_WORDS`, `MATCH_INCIDENT_WORDS`, `REPLACEMENT_PHRASES`, `RENEWAL_WORDS` en `config.py`).
- Duplicados: la misma noticia llega por el feed del medio y por Google Noticias. Se considera la misma si coinciden medio + titular normalizado + día. Se queda el enlace directo, no el de `news.google.com` (`score.dedupe`, `pipeline.purge_duplicates`).
- `revalidate` borra rumores guardados que ya no pasen las reglas.
- Nombres que no son jugadores (entrenadores, directivos, palabras sueltas) van a `ignorados.txt`, **una por línea** (cuida que el archivo termine en salto de línea).
- Un grupo (jugador, destino) se publica si está aprobado a mano o lo cuentan ≥2 medios distintos, con al menos uno fiable. Ventanas: `WINDOW_DAYS=45`, `NEWS_DAYS=14`.
- Las noticias que ya son rumores publicados no se repiten en la pestaña Noticias.

## Móvil
Se revisa siempre a 390 px. Los filtros de Ligas y Medios van plegados tras el botón "Filtrar por liga o medio" (≤820 px). No hay imágenes de noticias: solo titular, medio, fecha y enlace (los titulares pertenecen a sus medios).

## Despliegue
`git add . ; git commit -m "..." ; git push`. Si el cambio no cambia datos, el siguiente ciclo horario del Action lo publica; también se puede lanzar el workflow a mano desde la pestaña Actions de GitHub.

## Pendiente de vigilar
- Search Console: la cuota diaria de "solicitar indexación" se agota rápido; pedir de una en una (`/jugador/`, `/rumores/movimientos/`, `/fantasy/jornada-10/`).
- Revisión semanal (lunes): el usuario pega el CSV de Search Console para analizarlo.
- AdSense: ambas webs esperan aprobación.

## La otra web: generadorplus.es
Generadores y validadores de datos de prueba (DNI, NIE, IBAN, CIF, matrículas, UUID), calculadora de letra del DNI y guías. **No está en este repositorio ni en GitHub**: se sube a mano con "New deployment" de Cloudflare Pages desde la carpeta `generadorplus-web`. No asumas que hay git ahí.
