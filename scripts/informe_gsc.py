"""Informe semanal de Search Console (solo lectura).

Lee la clave de la cuenta de servicio de GSC_SERVICE_ACCOUNT_JSON (nunca de un archivo),
consulta las propiedades y escribe un informe en Markdown. No imprime la clave ni el correo.
Salida: GSC_INFORME_PATH (por defecto informe/informe-gsc.md).
"""
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
PROPIEDADES = ["sc-domain:generadorplus.es", "sc-domain:rumoresyfichajes.com"]
DIAS = 28
RETRASO = 3            # los datos de GSC llegan con retraso
TOP = 10
CTR_BAJO = 0.02        # consultas con CTR por debajo de este valor...
IMPR_MIN = 50          # ...y al menos estas impresiones
FILAS = 1000


def periodos(hoy):
    fin = hoy - timedelta(days=RETRASO)
    ini = fin - timedelta(days=DIAS - 1)
    fin_ant = ini - timedelta(days=1)
    ini_ant = fin_ant - timedelta(days=DIAS - 1)
    return (ini, fin), (ini_ant, fin_ant)


def consulta(svc, sitio, periodo, dims):
    body = {
        "startDate": periodo[0].isoformat(),
        "endDate": periodo[1].isoformat(),
        "dimensions": dims,
        "rowLimit": FILAS,
        "dataState": "final",
    }
    r = svc.searchanalytics().query(siteUrl=sitio, body=body).execute()
    return r.get("rows", [])


def totales(filas):
    if not filas:
        return None
    f = filas[0]
    return {"clics": f["clicks"], "impr": f["impressions"], "ctr": f["ctr"], "pos": f["position"]}


def esc(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def pct(x):
    return f"{x * 100:.2f}%"


def var(a, b, es_pct=False, invertido=False):
    """Variación de a (actual) frente a b (anterior)."""
    d = a - b
    if es_pct:
        return f"{d * 100:+.2f} pp"
    if invertido:  # posición: menos es mejor
        return f"{d:+.1f}"
    rel = f" ({d / b * 100:+.0f}%)" if b else ""
    return f"{d:+.0f}{rel}"


def seccion_totales(act, ant):
    out = ["### Totales", ""]
    if act is None:
        return out + ["Sin datos en el periodo actual.", ""]
    if ant is None:
        return out + [
            "Sin datos del periodo anterior: no se calculan variaciones.", "",
            "| Métrica | Actual |", "|---|---|",
            f"| Clics | {act['clics']:.0f} |", f"| Impresiones | {act['impr']:.0f} |",
            f"| CTR | {pct(act['ctr'])} |", f"| Posición media | {act['pos']:.1f} |", ""]
    return out + [
        "| Métrica | Actual | Anterior | Variación |", "|---|---|---|---|",
        f"| Clics | {act['clics']:.0f} | {ant['clics']:.0f} | {var(act['clics'], ant['clics'])} |",
        f"| Impresiones | {act['impr']:.0f} | {ant['impr']:.0f} | {var(act['impr'], ant['impr'])} |",
        f"| CTR | {pct(act['ctr'])} | {pct(ant['ctr'])} | {var(act['ctr'], ant['ctr'], es_pct=True)} |",
        f"| Posición media | {act['pos']:.1f} | {ant['pos']:.1f} | "
        f"{var(act['pos'], ant['pos'], invertido=True)} (menos es mejor) |", ""]


def tabla_consultas(filas):
    out = ["| Consulta | Impr. | Clics | CTR | Pos. |", "|---|---|---|---|---|"]
    return out + [f"| {esc(f['keys'][0])} | {f['impressions']:.0f} | {f['clicks']:.0f} | "
                  f"{pct(f['ctr'])} | {f['position']:.1f} |" for f in filas]


def seccion_consultas(filas):
    out = [f"### Top {TOP} consultas por impresiones", ""]
    if not filas:
        return out + ["Sin datos.", ""]
    out += tabla_consultas(sorted(filas, key=lambda f: -f["impressions"])[:TOP])
    out += ["", f"### Muchas impresiones y CTR bajo (≥{IMPR_MIN} impr., CTR <{CTR_BAJO * 100:.0f}%)", ""]
    bajas = sorted((f for f in filas if f["impressions"] >= IMPR_MIN and f["ctr"] < CTR_BAJO),
                   key=lambda f: -f["impressions"])[:TOP]
    return out + (tabla_consultas(bajas) if bajas else ["Ninguna."]) + [""]


def seccion_paginas(act, ant):
    out = ["### Páginas que más suben y más bajan (clics)", ""]
    if not ant:
        return out + ["Sin datos de páginas del periodo anterior: no se calculan variaciones.", ""]
    a = {f["keys"][0]: f["clicks"] for f in act}
    b = {f["keys"][0]: f["clicks"] for f in ant}
    difs = sorted(((u, a.get(u, 0), b.get(u, 0)) for u in set(a) | set(b)), key=lambda t: t[1] - t[2])
    suben = [t for t in reversed(difs) if t[1] - t[2] > 0][:5]
    bajan = [t for t in difs if t[1] - t[2] < 0][:5]
    for titulo, lista in (("Suben", suben), ("Bajan", bajan)):
        out += [f"**{titulo}**", ""]
        if not lista:
            out += ["Ninguna.", ""]
            continue
        out += ["| Página | Actual | Anterior | Dif. |", "|---|---|---|---|"]
        out += [f"| {esc(u)} | {x:.0f} | {y:.0f} | {x - y:+.0f} |" for u, x, y in lista] + [""]
    return out


def seccion_sitemaps(svc, sitio):
    out = ["### Sitemaps", ""]
    lista = svc.sitemaps().list(siteUrl=sitio).execute().get("sitemap", [])
    if not lista:
        return out + ["No hay sitemaps enviados.", ""]
    out += ["| Sitemap | Último envío | Última descarga | Errores | Avisos | URLs enviadas | Pendiente |",
            "|---|---|---|---|---|---|---|"]
    for s in lista:
        enviadas = sum(int(c.get("submitted", 0)) for c in s.get("contents", []))
        out.append(f"| {esc(s.get('path', ''))} | {s.get('lastSubmitted', '-')[:10]} | "
                   f"{s.get('lastDownloaded', '-')[:10]} | {s.get('errors', 0)} | {s.get('warnings', 0)} | "
                   f"{enviadas} | {'sí' if s.get('isPending') else 'no'} |")
    return out + [""]


def error_http(e):
    # Solo código y motivo genérico: el texto completo podría incluir datos de la cuenta.
    motivo = ""
    try:
        motivo = e.error_details[0].get("reason", "") if e.error_details else ""
    except Exception:
        pass
    return f"error {e.resp.status}" + (f", {motivo}" if motivo else "")


def informe_propiedad(svc, sitio, per_act, per_ant):
    out = [f"## {sitio}", ""]
    try:
        act = totales(consulta(svc, sitio, per_act, []))
        ant = totales(consulta(svc, sitio, per_ant, []))
        out += seccion_totales(act, ant)
        out += seccion_consultas(consulta(svc, sitio, per_act, ["query"]))
        out += seccion_paginas(consulta(svc, sitio, per_act, ["page"]),
                               consulta(svc, sitio, per_ant, ["page"]) if ant else [])
        try:
            out += seccion_sitemaps(svc, sitio)
        except HttpError as e:
            out += ["### Sitemaps", "",
                    f"No se pudo leer el estado de los sitemaps ({error_http(e)}).", ""]
        return out, True
    except HttpError as e:
        if e.resp.status in (401, 403):
            out += [f"⚠️ **Sin permisos** para esta propiedad ({error_http(e)}). "
                    "Comprueba que la cuenta de servicio está añadida como usuario en Search Console.", ""]
        else:
            out += [f"⚠️ **Error de la API** ({error_http(e)}). Propiedad omitida.", ""]
        return out, False


def main():
    clave = os.environ.get("GSC_SERVICE_ACCOUNT_JSON", "").strip()
    if not clave:
        print("Falta la variable de entorno GSC_SERVICE_ACCOUNT_JSON (secreto del repositorio).", file=sys.stderr)
        return 1
    try:
        cred = service_account.Credentials.from_service_account_info(json.loads(clave), scopes=SCOPES)
    except Exception as e:  # no mostrar el mensaje: puede contener fragmentos de la clave
        print(f"No se pudo leer GSC_SERVICE_ACCOUNT_JSON ({type(e).__name__}).", file=sys.stderr)
        return 1
    svc = build("searchconsole", "v1", credentials=cred, cache_discovery=False)

    hoy = date.today()
    per_act, per_ant = periodos(hoy)
    md = ["# Informe semanal de Search Console", "",
          f"Generado: {hoy.isoformat()} · Periodo: {per_act[0]} a {per_act[1]} "
          f"(comparado con {per_ant[0]} a {per_ant[1]})", ""]
    ok_alguna = False
    for sitio in PROPIEDADES:
        bloque, ok = informe_propiedad(svc, sitio, per_act, per_ant)
        md += bloque
        ok_alguna = ok_alguna or ok

    ruta = Path(os.environ.get("GSC_INFORME_PATH", "informe/informe-gsc.md"))
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Informe escrito en {ruta} (alguna propiedad con datos: {'sí' if ok_alguna else 'no'}).")
    return 0 if ok_alguna else 1


if __name__ == "__main__":
    sys.exit(main())
