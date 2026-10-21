// Votos de los lectores en cada rumor (Cloudflare Pages Function + la misma base de datos D1 que "clics").
// POST /api/votos  {"rumor": "viktor-gyokeres", "v": "si" | "no"}  -> suma un voto
// GET  /api/votos?rumor=viktor-gyokeres                            -> {"si": n, "no": n}
// Solo se guardan totales por rumor (nada del visitante). La página permite un voto por rumor y navegador.

const HEADERS = { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" };
const SLUG = /^[a-z0-9-]{2,60}$/;

function json(body, status = 200) { return new Response(JSON.stringify(body), { status, headers: HEADERS }); }

async function ensureTable(env) {
  await env.DB.prepare(
    "CREATE TABLE IF NOT EXISTS votos (rumor TEXT NOT NULL, v TEXT NOT NULL, n INTEGER NOT NULL DEFAULT 0, PRIMARY KEY (rumor, v))"
  ).run();
}

// Solo vale un rumor que tenga página en la web (así nadie llena la base de datos con nombres inventados)
async function rumorExists(env, request, slug) {
  if (!env.ASSETS) return false;
  try {
    const res = await env.ASSETS.fetch(new URL(`/jugador/${slug}/`, request.url));
    return res.status === 200;
  } catch (e) { return false; }
}

export async function onRequestPost({ env, request }) {
  if (!env.DB) return json({ error: "sin base de datos" }, 503);
  const origin = request.headers.get("origin") || "";
  if (origin && new URL(origin).host !== new URL(request.url).host) return json({}, 403);
  let data;
  try { data = JSON.parse(await request.text()); } catch (e) { return json({ error: "formato" }, 400); }
  const slug = String((data && data.rumor) || ""), v = String((data && data.v) || "");
  if (!SLUG.test(slug) || (v !== "si" && v !== "no")) return json({ error: "datos no válidos" }, 400);
  if (!(await rumorExists(env, request, slug))) return json({ error: "rumor desconocido" }, 404);
  const sql = "INSERT INTO votos (rumor, v, n) VALUES (?, ?, 1) ON CONFLICT(rumor, v) DO UPDATE SET n = n + 1";
  try {
    await env.DB.prepare(sql).bind(slug, v).run();
  } catch (e) {                        // la primera vez la tabla todavía no existe
    await ensureTable(env);
    await env.DB.prepare(sql).bind(slug, v).run();
  }
  return json({ ok: true });
}

export async function onRequestGet({ env, request }) {
  if (!env.DB) return json({ error: "sin base de datos" }, 503);
  const many = new URL(request.url).searchParams.get("rumores");
  if (many !== null) {                 // varios rumores de una vez (la lista de rumores): {slug: {si, no}}
    const slugs = [...new Set(many.split(",").filter(x => SLUG.test(x)))].slice(0, 60);
    const out = {};
    for (const x of slugs) out[x] = { si: 0, no: 0 };
    if (!slugs.length) return json(out);
    try {
      const marks = slugs.map(() => "?").join(",");
      const { results } = await env.DB.prepare(`SELECT rumor, v, n FROM votos WHERE rumor IN (${marks})`).bind(...slugs).all();
      for (const r of results || []) if (out[r.rumor] && (r.v === "si" || r.v === "no")) out[r.rumor][r.v] = r.n;
    } catch (e) { await ensureTable(env); }
    return json(out);
  }
  const slug = String(new URL(request.url).searchParams.get("rumor") || "");
  if (!SLUG.test(slug)) return json({ error: "rumor no válido" }, 400);
  const out = { si: 0, no: 0 };
  try {
    const { results } = await env.DB.prepare("SELECT v, n FROM votos WHERE rumor = ?").bind(slug).all();
    for (const r of results || []) if (r.v === "si" || r.v === "no") out[r.v] = r.n;
  } catch (e) { await ensureTable(env); }
  return json(out);
}
