// Contador de visitas de la web (Cloudflare Pages Function).
// Necesita un espacio KV vinculado al proyecto con el nombre de variable VISITAS.
// GET  /api/visitas -> devuelve el total sin sumar
// POST /api/visitas -> suma una visita y devuelve el total
// Quién cuenta y quién no lo decide la página: una vez por visitante y día.

const HEADERS = { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" };

async function total(env) {
  return parseInt((await env.VISITAS.get("total")) || "0", 10) || 0;
}

export async function onRequestGet({ env }) {
  if (!env.VISITAS) return new Response(JSON.stringify({ error: "sin KV" }), { status: 503, headers: HEADERS });
  return new Response(JSON.stringify({ total: await total(env) }), { headers: HEADERS });
}

export async function onRequestPost({ env, request }) {
  if (!env.VISITAS) return new Response(JSON.stringify({ error: "sin KV" }), { status: 503, headers: HEADERS });
  // Solo se aceptan visitas que vienen de la propia web
  const origin = request.headers.get("origin") || "";
  const host = new URL(request.url).host;
  if (origin && new URL(origin).host !== host) return new Response("{}", { status: 403, headers: HEADERS });
  const n = (await total(env)) + 1;
  await env.VISITAS.put("total", String(n));
  return new Response(JSON.stringify({ total: n }), { headers: HEADERS });
}
