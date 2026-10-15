// "Lo más leído": cuenta los clics en las noticias (Cloudflare Pages Function + base de datos D1).
// Necesita una base de datos D1 vinculada al proyecto con el nombre de variable DB.
// POST /api/clics          {"url": "..."}  -> suma un clic a esa noticia
// GET  /api/clics?horas=24                  -> las noticias con más clics en esas horas
// La página solo envía un clic por noticia, visitante y día.

const HEADERS = { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" };
// Solo se cuentan enlaces a los medios que sigue la web (nadie puede colar otras webs)
const ALLOWED = ["marca.com", "as.com", "mundodeportivo.com", "sport.es", "news.google.com",
                 "bbc.co.uk", "bbc.com", "skysports.com"];

function json(body, status = 200) { return new Response(JSON.stringify(body), { status, headers: HEADERS }); }

function allowedUrl(raw) {
  try {
    const u = new URL(raw);
    if (u.protocol !== "https:" && u.protocol !== "http:") return null;
    if (raw.length > 600) return null;
    const host = u.hostname.toLowerCase();
    return ALLOWED.some(d => host === d || host.endsWith("." + d)) ? u.toString() : null;
  } catch (e) { return null; }
}

async function ensureTable(env) {
  await env.DB.prepare(
    "CREATE TABLE IF NOT EXISTS clics (url TEXT NOT NULL, hora TEXT NOT NULL, n INTEGER NOT NULL DEFAULT 0, PRIMARY KEY (url, hora))"
  ).run();
}

export async function onRequestPost({ env, request }) {
  if (!env.DB) return json({ error: "sin base de datos" }, 503);
  const origin = request.headers.get("origin") || "";
  if (origin && new URL(origin).host !== new URL(request.url).host) return json({}, 403);
  let data;
  try { data = JSON.parse(await request.text()); } catch (e) { return json({ error: "formato" }, 400); }
  const url = allowedUrl(String((data && data.url) || ""));
  if (!url) return json({ error: "enlace no permitido" }, 400);
  const hora = new Date().toISOString().slice(0, 13);   // AAAA-MM-DDTHH (UTC)
  const sql = "INSERT INTO clics (url, hora, n) VALUES (?, ?, 1) ON CONFLICT(url, hora) DO UPDATE SET n = n + 1";
  try {
    await env.DB.prepare(sql).bind(url, hora).run();
  } catch (e) {                     // la primera vez la tabla todavía no existe
    await ensureTable(env);
    await env.DB.prepare(sql).bind(url, hora).run();
  }
  return json({ ok: true });
}

export async function onRequestGet({ env, request }) {
  if (!env.DB) return json({ error: "sin base de datos" }, 503);
  const horas = Math.min(Math.max(parseInt(new URL(request.url).searchParams.get("horas") || "24", 10) || 24, 1), 24 * 14);
  const desde = new Date(Date.now() - horas * 3600 * 1000).toISOString().slice(0, 13);
  const sql = "SELECT url, SUM(n) AS clics FROM clics WHERE hora >= ? GROUP BY url ORDER BY clics DESC LIMIT 30";
  try {
    const { results } = await env.DB.prepare(sql).bind(desde).all();
    return json({ horas, top: results || [] });
  } catch (e) {
    await ensureTable(env);
    return json({ horas, top: [] });
  }
}
