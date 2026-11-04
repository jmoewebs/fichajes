# Cambios en .github/workflows/actualizar.yml

1. **Nuevo paso "Publicar la clave de IndexNow en la web"**, justo después de "Añadir ads.txt y código de AdSense".
   Usa `INDEXNOW_KEY: ${{ secrets.INDEXNOW_KEY }}`. Si la clave está vacía, falla con un `::error::` claro (exit 1);
   si no, ejecuta `test -n "$INDEXNOW_KEY" && printf '%s' "$INDEXNOW_KEY" > "web/$INDEXNOW_KEY.txt"`.
   Nota: `web.write_static` ya escribe ese mismo archivo durante `python run.py` cuando la variable existe; el paso nuevo lo repite y, sobre todo, hace que la falta de secreto rompa el workflow en vez de pasar en silencio.
2. **Paso "Guardar el histórico"**: quitado `2>/dev/null ||`. Ahora `git add` va por fichero (`fichajes.db`, `jugadores.csv`, `ignorados.txt`, `clasificaciones.json`) con `[ -f ]` antes; si falta uno, avisa con `::warning::` y los demás se añaden igual. Un error real de `git add` ya no se oculta.
3. **run.py**: ya escribía `nuevos=N` en `$GITHUB_OUTPUT` (líneas 39-41, en los comandos `all` y `fetch`). No se ha tocado.
4. **comprobar_seo.py**: existe en la rama (commit 6190a80) y acepta la carpeta como primer argumento (`python comprobar_seo.py web`). Sin argumento usa `web`.
5. **Archivo de la clave**: `web/` está en `.gitignore` entero (sin excepciones; `git check-ignore` confirma que `web/<clave>.txt` queda ignorado) y el paso de histórico solo añade los 4 ficheros listados, así que la clave no se sube a git.

## Pendiente / a vigilar
- El secreto `INDEXNOW_KEY` debe existir en GitHub; si no, el workflow fallará en el paso nuevo (es lo pedido), antes de commitear datos y desplegar.
- Los cambios no están commiteados ni empujados. No se ha ejecutado el workflow ni `run.py`.
