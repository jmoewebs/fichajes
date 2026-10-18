# Rastreador de rumores de fichajes

Lee los RSS de Marca, AS, Mundo Deportivo, BBC y Sky Sports y genera una página en
web/index.html con dos pestañas: Noticias (titulares de fútbol de los últimos 3 días,
sin otros deportes) y Rumores (detectados con reglas: palabras clave + clubes + jugadores).
Gratis: no usa IA de pago. Solo guarda titular, entradilla breve y enlace.

## Uso diario

    python run.py

Descarga lo nuevo, detecta rumores y abre la página en el navegador.
Ejecútalo las veces que quieras: los titulares ya vistos no se repiten.

## Revisión

Los rumores dudosos (jugador desconocido, varios jugadores, "oficial") no se publican
hasta que los revisas:

    python run.py review          # lista con números
    python run.py approve 12 15   # publicar
    python run.py reject 13       # descartar

Al aprobar un jugador nuevo se añade a jugadores.csv y la próxima vez se reconoce solo.
Al descartar un nombre desconocido se añade a ignorados.txt y no vuelve a salir.

## Personalizar

- jugadores.csv: jugadores conocidos y su club actual (revisa los clubes).
- config.py: fuentes RSS, clubes y palabras clave.

## Archivo

Todo lo descargado se guarda en fichajes.db, sin borrarse nunca. La portada muestra los
últimos 3 días; la pestaña Archivo enlaza a una página por mes (web/archivo/AAAA-MM.html).
Haz copia de fichajes.db de vez en cuando: es tu histórico.

## Fantasy: avisos que no son correctos

Si el parte médico dice que alguien está de baja y no es así, mira el titular que aparece en su tarjeta.
Copia un trozo de ese titular en `fantasy_ignorar.txt` (uno por línea) y deja de contar. Las reglas
(negaciones, expresiones que no cuentan, días que dura un aviso) están en `FANTASY_RULES` de `config.py`.

Prueba sin internet: python tests/test_pipeline.py
