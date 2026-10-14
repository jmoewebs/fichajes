"""Genera la web estática: web/index.html (portada) y web/archivo/AAAA-MM.html (un archivo por mes).
Las páginas se abren con doble clic, sin servidor."""
import html as html_lib
import json
import os

import config
from datetime import datetime

MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
          "septiembre", "octubre", "noviembre", "diciembre"]

TEMPLATE = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<meta name="description" content="__DESCRIPTION__">
<link rel="canonical" href="__CANONICAL__">
<meta property="og:type" content="website">
<meta property="og:site_name" content="__SITE_NAME__">
<meta property="og:title" content="__TITLE__">
<meta property="og:description" content="__DESCRIPTION__">
<meta property="og:url" content="__CANONICAL__">
<meta property="og:locale" content="es_ES">
<meta property="og:image" content="__SITE_URL__/compartir.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="__ROOT__favicon.svg" type="image/svg+xml">
<link rel="icon" href="__ROOT__favicon.png" type="image/png" sizes="48x48">
<link rel="apple-touch-icon" href="__ROOT__apple-touch-icon.png">
__VERIFICATION__
<script type="application/ld+json">__LDJSON__</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600&family=Barlow+Condensed:wght@500;600;700&display=swap" rel="stylesheet">
<style>
:root {
  --grass:#145a32; --grass-2:#1b6b3d; --chalk:#f2f6f3; --card:#ffffff; --ink:#10201a;
  --muted:#5d6d65; --line:#dbe3de; --soft:#e8eeea;
  --cold:#2b78c5; --warm:#e9a100; --hot:#d93a1b; --ok:#1f8f4e; --off:#8a958f;
  --cond:"Barlow Condensed","Arial Narrow",system-ui,sans-serif;
  --body:"Barlow",system-ui,-apple-system,"Segoe UI",sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root { --chalk:#0c1611; --card:#14211a; --ink:#e4ece7; --muted:#93a39a; --line:#24352c;
          --soft:#1c2b23; --grass:#0f4426; --grass-2:#155230; }
}
* { box-sizing:border-box; }
html { -webkit-text-size-adjust:100%; }
body { margin:0; background:var(--chalk); color:var(--ink); font:16px/1.5 var(--body); }
a { color:inherit; }
a:focus-visible, button:focus-visible, input:focus-visible, select:focus-visible {
  outline:3px solid var(--warm); outline-offset:2px; }
.wrap { max-width:1300px; margin:0 auto; padding:0 20px; }

/* Cabecera: césped con las líneas de cal del centro del campo */
.pitch { position:relative; overflow:hidden; color:#fff;
  background:repeating-linear-gradient(90deg, var(--grass) 0 80px, var(--grass-2) 80px 160px); }
.pitch::before { content:""; position:absolute; top:-90px; right:8%; width:240px; height:240px;
  border:3px solid rgba(255,255,255,.28); border-radius:50%; }
.pitch::after { content:""; position:absolute; top:0; bottom:0; right:calc(8% + 120px);
  border-left:3px solid rgba(255,255,255,.28); }
.pitch .wrap { position:relative; z-index:1; padding-top:30px; }
h1 { font:700 clamp(34px,6vw,52px)/.95 var(--cond); margin:0; letter-spacing:-.005em; }
.updated { margin:8px 0 0; font-size:14px; opacity:.85; }
.crumbs { display:flex; gap:16px; flex-wrap:wrap; margin:10px 0 0; font-size:15px; }
.crumbs a { color:#fff; }
.tools { display:flex; gap:10px; flex-wrap:wrap; margin-top:20px; }
.tools input, .tools select { font:inherit; font-size:15px; padding:10px 12px; border-radius:6px;
  border:0; background:rgba(255,255,255,.95); color:#10201a; }
.tools input { flex:1; min-width:200px; }
.tabs { display:flex; gap:4px; margin-top:22px; overflow-x:auto; scrollbar-width:none; }
.tab { font:600 19px/1 var(--cond); letter-spacing:.01em; color:#fff; background:transparent;
  border:0; border-radius:6px 6px 0 0; padding:11px 18px 10px; cursor:pointer; opacity:.8; }
.tab:hover { opacity:1; }
.tab.on { background:var(--chalk); color:var(--ink); opacity:1; }
.tab .n { font-weight:500; opacity:.6; margin-left:4px; }

main { padding:6px 0 60px; max-width:860px; }
.layout { display:grid; grid-template-columns:210px minmax(0, 1fr) 200px; gap:36px; align-items:start; }
.filters, .dates { position:sticky; top:0; max-height:100vh; overflow-y:auto; padding:22px 0 30px; }
.year-h { font:600 15px/1 var(--cond); color:var(--muted); margin:12px 0 4px 10px; }
a.chipbtn { text-decoration:none; }
.chipbtn[data-day][aria-pressed="true"], a.chipbtn.current { background:var(--grass); color:#fff; }
.chipbtn[data-day][aria-pressed="true"] .cnt, a.chipbtn.current .cnt { color:#fff; opacity:.75; }
.chipbtn .nm::first-letter { text-transform:uppercase; }
.fgroup + .fgroup { margin-top:24px; }
.flabel { font:600 18px/1 var(--cond); margin:0 0 8px; }
.flist { display:grid; gap:2px; }
.chipbtn { font:500 15px/1.2 var(--body); display:flex; align-items:center; gap:8px; width:100%;
  text-align:left; padding:8px 10px; border-radius:6px; border:0; background:transparent;
  color:var(--ink); cursor:pointer; }
.chipbtn:hover { background:var(--soft); }
.chipbtn .nm { flex:1; }
.chipbtn .cnt { font-size:13px; color:var(--muted); font-variant-numeric:tabular-nums; }
.chipbtn[data-league][aria-pressed="true"] { background:var(--grass); color:#fff; }
.chipbtn[data-league][aria-pressed="true"] .cnt { color:#fff; opacity:.75; }
.chipbtn .src { width:20px; height:20px; border-radius:4px; font-size:10px; }
.chipbtn .src img { width:15px; height:15px; }
.chipbtn .dot { width:16px; height:16px; border-radius:4px; border:2px solid var(--grass-2);
  display:grid; place-items:center; color:#fff; font-size:11px; flex:none; }
.chipbtn[aria-pressed="true"] .dot { background:var(--grass-2); }
.chipbtn.src-off .nm { color:var(--muted); text-decoration:line-through; }
.chipbtn.src-off .src { opacity:.4; }
@media (max-width:1100px) {
  .layout { grid-template-columns:210px minmax(0, 1fr); }
  .layout main { grid-column:2; grid-row:1 / span 2; }
  .filters, .dates { position:static; max-height:none; overflow:visible; }
  .dates { grid-column:1; grid-row:2; padding-top:0; }
}
@media (max-width:820px) {
  .layout { grid-template-columns:1fr; gap:0; }
  .layout main { grid-column:1; grid-row:auto; }
  .dates { grid-column:1; grid-row:auto; padding-top:16px; }
  .filters { position:static; max-height:none; overflow:visible; padding:16px 0 0; }
  .year-h { margin:8px 0 6px 0; width:100%; }
  .fgroup + .fgroup { margin-top:12px; }
  .flist { display:flex; flex-wrap:wrap; gap:6px; }
  .chipbtn { width:auto; padding:6px 11px; border:1px solid var(--line); border-radius:20px;
    background:var(--card); font-size:14px; }
  .chipbtn .cnt, .chipbtn .dot { display:none; }
}
.empty { color:var(--muted); padding:48px 0; max-width:46ch; }
.day { font:600 22px/1.1 var(--cond); margin:28px 0 8px; }
.day:first-letter { text-transform:uppercase; }

/* Noticias */
.news { list-style:none; margin:0; padding:0; background:var(--card); border:1px solid var(--line);
  border-radius:8px; }
.news li { display:grid; grid-template-columns:28px 1fr; gap:12px; padding:12px 16px;
  border-top:1px solid var(--line); }
.news li:first-child { border-top:0; }
.news .t { font-weight:500; text-decoration:none; }
.news .t:hover { text-decoration:underline; }
.meta { display:flex; flex-wrap:wrap; gap:6px 10px; align-items:center; margin-top:4px;
  font-size:13px; color:var(--muted); }
.time { font-variant-numeric:tabular-nums; }
.club { color:var(--ink); font-weight:500; }
.tag { font-size:12px; font-weight:600; padding:1px 8px; border-radius:20px; }
.tag.live { background:color-mix(in srgb, var(--hot) 14%, transparent); color:var(--hot); }
.tag.rum { background:color-mix(in srgb, var(--warm) 20%, transparent); color:color-mix(in srgb, var(--warm) 70%, var(--ink)); }

/* Icono del medio */
.src { width:28px; height:28px; border-radius:6px; background:var(--soft); display:grid;
  place-items:center; overflow:hidden; flex:none; font:700 12px/1 var(--cond); color:var(--muted); }
.src img { width:20px; height:20px; }
.src.sm { width:22px; height:22px; border-radius:5px; }
.src.sm img { width:16px; height:16px; }

/* Rumores */
.rumors { display:grid; gap:12px; margin-top:20px; }
.rumor { display:grid; grid-template-columns:1fr auto; gap:18px; background:var(--card);
  border:1px solid var(--line); border-radius:8px; padding:18px 20px; }
.player { font:700 28px/1 var(--cond); margin:0; }
.route { margin:6px 0 0; font-size:16px; }
.route .arrow { color:var(--muted); margin:0 6px; }
.route .unk { color:var(--muted); }
.row { display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-top:12px; }
.status { font-size:13px; font-weight:600; padding:2px 10px; border-radius:20px; color:#fff; }
.st-interes { background:var(--cold); } .st-negociacion { background:var(--warm); color:#2a1d00; }
.st-acuerdo { background:var(--ok); } .st-oficial { background:var(--hot); } .st-descartado { background:var(--off); }
.outlets { display:flex; gap:4px; }
.fee { font-size:14px; color:var(--muted); }
details { grid-column:1 / -1; border-top:1px solid var(--line); padding-top:10px; margin-top:-4px; }
summary { cursor:pointer; font-size:14px; color:var(--muted); }
.mentions { list-style:none; padding:0; margin:8px 0 0; }
.mentions li { display:grid; grid-template-columns:22px 1fr; gap:10px; padding:8px 0; font-size:15px; }

/* Termómetro */
.thermo { display:flex; align-items:flex-end; gap:10px; }
.tube { position:relative; width:12px; height:76px; border-radius:6px; background:var(--soft);
  overflow:hidden; }
.tube span { position:absolute; left:0; right:0; bottom:0; border-radius:6px;
  background:linear-gradient(0deg, var(--cold), var(--warm) 55%, var(--hot)); background-size:100% 76px;
  background-position:bottom; }
.deg { font:700 46px/.8 var(--cond); font-variant-numeric:tabular-nums; }

/* Archivo */
.year { font:700 30px/1 var(--cond); margin:30px 0 10px; }
.months { display:grid; grid-template-columns:repeat(auto-fill,minmax(180px,1fr)); gap:10px; }
.month { display:block; text-decoration:none; background:var(--card); border:1px solid var(--line);
  border-radius:8px; padding:14px 16px; }
.month:hover { border-color:var(--grass-2); }
.month b { display:block; font:600 22px/1.1 var(--cond); }
.month:first-letter { text-transform:uppercase; }
.month span { font-size:14px; color:var(--muted); }

@media (max-width:560px) {
  .tab { padding:10px 12px 9px; font-size:17px; flex:none; }
  .rumor { grid-template-columns:1fr; }
  .thermo { order:-1; }
  .tube { height:12px; width:100%; max-width:160px; }
  .tube span { top:0; right:auto; width:var(--w); height:auto !important;
    background:linear-gradient(90deg, var(--cold), var(--warm) 55%, var(--hot)); background-size:160px 100%; }
  .thermo { align-items:center; }
  .deg { font-size:34px; }
}
@media (prefers-reduced-motion: no-preference) {
  .tube span { transition:height .6s ease-out; }
}
</style>
</head>
<body>
<header class="pitch">
  <div class="wrap">
    <h1>__HEADING__</h1>
    <p class="updated">Actualizado el __UPDATED__. Cada titular enlaza a la noticia original.</p>
    __CRUMBS__
    <div class="tools">
      <input id="q" type="search" placeholder="Buscar jugador, club o medio" aria-label="Buscar">
      <select id="club" aria-label="Filtrar por club"><option value="">Todos los clubes</option></select>
    </div>
    <nav class="tabs" id="tabs"></nav>
  </div>
</header>
<div class="wrap layout">
  <aside class="filters" id="filters">
    <div class="fgroup"><h2 class="flabel">Ligas</h2>
      <div class="flist" id="f-leagues" role="group" aria-label="Filtrar por liga"></div></div>
    <div class="fgroup"><h2 class="flabel">Medios</h2>
      <div class="flist" id="f-sources" role="group" aria-label="Elegir medios"></div></div>
  </aside>
  <main id="list">__STATIC__</main>
  <aside class="dates" id="dates">
    <div class="fgroup"><h2 class="flabel" id="days-title">Últimos días</h2>
      <div class="flist" id="f-days" role="group" aria-label="Elegir día"></div></div>
    <div class="fgroup" id="history-box"><h2 class="flabel">Historial</h2>
      <div class="flist" id="f-months"></div></div>
  </aside>
</div>
<script id="d-rumors" type="application/json">__RUMORS__</script>
<script id="d-news" type="application/json">__NEWS__</script>
<script id="d-archive" type="application/json">__ARCHIVE__</script>
<script id="d-leagues" type="application/json">__LEAGUES__</script>
<script>const RECENT_DAYS = __RECENT_DAYS__;</script>
<script>
const rumors = JSON.parse(document.getElementById("d-rumors").textContent);
const news = JSON.parse(document.getElementById("d-news").textContent);
const archive = JSON.parse(document.getElementById("d-archive").textContent);
const IS_ARCHIVE = __IS_ARCHIVE__;
const STATUS = {interes:"Interés", negociacion:"Negociación", acuerdo:"Acuerdo", oficial:"Oficial", descartado:"Descartado"};
const ORDER = ["interes", "negociacion", "acuerdo", "oficial"];
const list = document.getElementById("list"), q = document.getElementById("q"), sel = document.getElementById("club");

const LEAGUES = JSON.parse(document.getElementById("d-leagues").textContent);
function load(key, fallback) { try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch (e) { return fallback; } }
function save(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch (e) {} }
let league = load("liga", "");
const hidden = new Set(load("medios-ocultos", []));

const tabs = [["news", "Noticias", news.length], ["rumors", "Rumores", rumors.length]];
let tab = (location.hash || "").slice(1);
if (!["news", "rumors"].includes(tab)) tab = rumors.length && !IS_ARCHIVE ? "rumors" : "news";
let day = "";   // "" = recientes (portada) o todo el mes (archivo); si no, AAAA-MM-DD
const nav = document.getElementById("tabs");
for (const [id, label, n] of tabs) {
  const b = el("button", "tab", label); b.dataset.tab = id;
  if (n !== null) b.append(el("span", "n", String(n)));
  b.addEventListener("click", () => { tab = id; history.replaceState(null, "", "#" + id); render(); });
  nav.append(b);
}
const clubs = [...new Set(rumors.flatMap(r => [r.from_club, r.to_club]).concat(news.flatMap(n => n.clubs)).filter(Boolean))].sort();
for (const c of clubs) sel.add(new Option(c, c));

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined && text !== null) e.textContent = text;
  return e;
}
function outlet(url, name, small) {
  // Icono oficial de la web del medio; sin internet, sus iniciales
  const box = el("span", "src" + (small ? " sm" : ""));
  box.title = name;
  const initials = name.split(/\s+/).map(w => w[0]).join("").slice(0, 2).toUpperCase();
  try {
    const img = new Image();
    img.alt = name; img.loading = "lazy";
    img.src = "https://www.google.com/s2/favicons?sz=64&domain=" + new URL(url).hostname;
    img.onerror = () => { box.replaceChildren(initials); };
    box.append(img);
  } catch (e) { box.textContent = initials; }
  return box;
}
// Filtros de ligas y medios
const fLeagues = document.getElementById("f-leagues"), fSources = document.getElementById("f-sources");
const present = new Set(news.flatMap(n => n.leagues).concat(rumors.flatMap(r => r.leagues)));
for (const lg of [""].concat(LEAGUES.filter(l => present.has(l)))) {
  const b = el("button", "chipbtn");
  b.append(el("span", "nm", lg || "Todas"), el("span", "cnt"));
  b.addEventListener("click", () => { league = lg; save("liga", league); render(); });
  b.dataset.league = lg; fLeagues.append(b);
}
if (league && !present.has(league)) league = "";
const sourceUrl = {};
for (const n of news) sourceUrl[n.source] ??= n.url;
for (const r of rumors) for (const m of r.mentions) sourceUrl[m.source] ??= m.url;
for (const name of Object.keys(sourceUrl).sort()) {
  const b = el("button", "chipbtn");
  b.append(outlet(sourceUrl[name], name, true), el("span", "nm", name), el("span", "dot", "✓"));
  b.addEventListener("click", () => {
    hidden.has(name) ? hidden.delete(name) : hidden.add(name);
    if (hidden.size === Object.keys(sourceUrl).length) hidden.delete(name);  // al menos uno visible
    save("medios-ocultos", [...hidden]); render();
  });
  b.dataset.source = name; fSources.append(b);
}
function syncFilters() {
  const pool = tab === "rumors" ? rumors.filter(r => r.mentions.some(m => !hidden.has(m.source) && dayOk(m.date)))
                                : news.filter(n => !hidden.has(n.source) && dayOk(n.date));
  for (const b of fLeagues.querySelectorAll("button")) {
    b.setAttribute("aria-pressed", String(b.dataset.league === league));
    const lg = b.dataset.league;
    b.querySelector(".cnt").textContent = lg ? pool.filter(x => x.leagues.includes(lg)).length : pool.length;
  }
  for (const b of fSources.querySelectorAll("button")) {
    const off = hidden.has(b.dataset.source);
    b.setAttribute("aria-pressed", String(!off)); b.classList.toggle("src-off", off);
    b.title = off ? "Mostrar " + b.dataset.source : "Ocultar " + b.dataset.source;
  }

}

// Columna de fechas: días con noticias + historial de meses
function dkey(iso) { const d = new Date(iso); return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0"); }
const recentFrom = Date.now() - RECENT_DAYS * 86400000;
function dayOk(iso) { return day ? dkey(iso) === day : (IS_ARCHIVE || new Date(iso).getTime() >= recentFrom); }
const fDays = document.getElementById("f-days");
function shortDay(k) {
  const d = new Date(k + "T12:00:00"), t = new Date(), y = new Date(); y.setDate(t.getDate() - 1);
  if (!IS_ARCHIVE && d.toDateString() === t.toDateString()) return "hoy";
  if (!IS_ARCHIVE && d.toDateString() === y.toDateString()) return "ayer";
  const wd = d.toLocaleDateString("es-ES", {weekday:"long"});
  const sameMonth = IS_ARCHIVE || d.getMonth() === t.getMonth();
  return wd + " " + d.getDate() + (sameMonth ? "" : " " + d.toLocaleDateString("es-ES", {month:"short"}).replace(".", ""));
}
document.getElementById("days-title").textContent = IS_ARCHIVE ? "Días del mes" : "Últimos " + __NEWS_DAYS__ + " días";
const dayCount = {};
for (const n of news) dayCount[dkey(n.date)] = (dayCount[dkey(n.date)] || 0) + 1;
const firstBtn = el("button", "chipbtn");
firstBtn.append(el("span", "nm", IS_ARCHIVE ? "Todo el mes" : "Recientes"), el("span", "cnt"));
firstBtn.dataset.day = ""; fDays.append(firstBtn);
for (const k of Object.keys(dayCount).sort().reverse()) {
  const b = el("button", "chipbtn");
  b.append(el("span", "nm", shortDay(k)), el("span", "cnt", String(dayCount[k])));
  b.dataset.day = k; fDays.append(b);
}
for (const b of fDays.children) b.addEventListener("click", () => { day = b.dataset.day; render(); });
const fMonths = document.getElementById("f-months");
if (!archive.length) document.getElementById("history-box").style.display = "none";
let yearShown = null;
for (const m of archive) {
  if (m.year !== yearShown) { yearShown = m.year; fMonths.append(el("div", "year-h", String(m.year))); }
  const a = el("a", "chipbtn" + (m.current ? " current" : ""));
  a.href = m.href;
  a.append(el("span", "nm", m.label), el("span", "cnt", String(m.news)));
  fMonths.append(a);
}
function syncDays() {
  for (const b of fDays.children) b.setAttribute("aria-pressed", String(b.dataset.day === day));
  firstBtn.querySelector(".cnt").textContent = IS_ARCHIVE ? news.length
    : news.filter(n => new Date(n.date).getTime() >= recentFrom).length;
}

function color(s) { return s >= 60 ? "var(--hot)" : s >= 30 ? "var(--warm)" : "var(--cold)"; }
function hhmm(iso) { return new Date(iso).toLocaleTimeString("es-ES", {hour:"2-digit", minute:"2-digit"}); }
function dayLabel(iso) {
  const d = new Date(iso), t = new Date(), y = new Date(); y.setDate(t.getDate() - 1);
  if (!IS_ARCHIVE && d.toDateString() === t.toDateString()) return "hoy";
  if (!IS_ARCHIVE && d.toDateString() === y.toDateString()) return "ayer";
  return d.toLocaleDateString("es-ES", {weekday:"long", day:"numeric", month:"long"});
}
function plural(n, one, many) { return n + " " + (n === 1 ? one : many); }
function match(text, ...fields) { return !text || fields.join(" ").toLowerCase().includes(text); }

function renderNews(text, club) {
  const shown = news.filter(n => dayOk(n.date) && (!club || n.clubs.includes(club)) && (!league || n.leagues.includes(league)) &&
                                 !hidden.has(n.source) && match(text, n.title, n.source, ...n.clubs));
  if (!shown.length) { list.append(el("p", "empty", "No hay noticias con ese filtro. Prueba con otro club o borra la búsqueda.")); return; }
  let current = null, ul = null;
  for (const n of shown) {
    const label = dayLabel(n.date);
    if (label !== current) { current = label; list.append(el("h2", "day", label)); ul = el("ul", "news"); list.append(ul); }
    const li = el("li"), body = el("div"), a = el("a", "t", n.title);
    a.href = n.url; a.target = "_blank"; a.rel = "noopener";
    const meta = el("div", "meta");
    meta.append(el("span", "time", hhmm(n.date)), el("span", null, n.source));
    if (n.live) meta.append(el("span", "tag live", "En directo"));
    if (n.rumor) meta.append(el("span", "tag rum", "Rumor"));
    for (const c of n.clubs) meta.append(el("span", "club", c));
    body.append(a, meta); li.append(outlet(n.url, n.source), body); ul.append(li);
  }
}

function renderRumors(text, club) {
  const shown = rumors.filter(r => (!club || r.from_club === club || r.to_club === club) &&
                                   (!league || r.leagues.includes(league)) && r.mentions.some(m => dayOk(m.date)) &&
                                   r.mentions.some(m => !hidden.has(m.source)) &&
                                   match(text, r.player, r.from_club, r.to_club, ...r.mentions.map(m => m.source)));
  if (!shown.length) {
    list.append(el("p", "empty", rumors.length ? "Ningún rumor coincide con ese filtro."
      : "Ahora mismo no hay rumores de fichajes. Con el mercado cerrado es normal; en enero y en verano aparecerán aquí."));
    return;
  }
  const grid = el("div", "rumors");
  for (const r of shown) {
    const card = el("article", "rumor"), left = el("div");
    left.append(el("h3", "player", r.player));
    const route = el("p", "route");
    route.append(el("span", r.from_club ? null : "unk", r.from_club || "Origen sin confirmar"),
                 el("span", "arrow", "→"),
                 el("span", r.to_club ? null : "unk", r.to_club || "Destino sin confirmar"));
    left.append(route);
    const row = el("div", "row");
    const statuses = r.mentions.map(m => m.status);
    const best = statuses.includes("oficial") ? "oficial" :
      (statuses.filter(s => ORDER.includes(s)).sort((a, b) => ORDER.indexOf(b) - ORDER.indexOf(a))[0] || statuses[0]);
    row.append(el("span", "status st-" + best, STATUS[best] || best));
    const outlets = el("span", "outlets"), seen = new Set();
    for (const m of r.mentions) if (!seen.has(m.source)) { seen.add(m.source); outlets.append(outlet(m.url, m.source, true)); }
    row.append(outlets);
    const fee = r.mentions.map(m => m.fee).find(f => f);
    if (fee) row.append(el("span", "fee", fee + " millones"));
    left.append(row);

    const thermo = el("div", "thermo"), tube = el("div", "tube"), fill = el("span");
    fill.style.height = r.score + "%"; fill.style.setProperty("--w", r.score + "%");
    tube.append(fill);
    const deg = el("div", "deg", r.score + "°"); deg.style.color = color(r.score);
    thermo.append(tube, deg);
    thermo.title = "Termómetro: " + r.score + " sobre 100";

    const det = el("details");
    det.append(el("summary", null, r.mentions.length === 1 ? "Ver la noticia" : "Ver las " + r.mentions.length + " noticias"));
    const ul = el("ul", "mentions");
    for (const m of r.mentions) {
      const li = el("li"), body = el("div"), a = el("a", null, m.title);
      a.href = m.url; a.target = "_blank"; a.rel = "noopener";
      const meta = el("div", "meta");
      meta.append(el("span", null, m.source), el("span", "time", dayLabel(m.date) + ", " + hhmm(m.date)),
                  el("span", "status st-" + m.status, STATUS[m.status] || m.status));
      body.append(a, meta); li.append(outlet(m.url, m.source, true), body); ul.append(li);
    }
    det.append(ul);
    card.append(left, thermo, det);
    grid.append(card);
  }
  list.append(grid);
}

function render() {
  const text = q.value.trim().toLowerCase(), club = sel.value;
  for (const b of nav.children) b.classList.toggle("on", b.dataset.tab === tab);
  syncFilters(); syncDays();
  list.replaceChildren();
  if (tab === "news") renderNews(text, club);
  else renderRumors(text, club);
}
q.addEventListener("input", render); sel.addEventListener("change", render);
render();
</script>
</body>
</html>
"""


def _now_spain():
    """Hora de España también cuando se ejecuta en GitHub (cuyos ordenadores usan hora UTC)."""
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("Europe/Madrid"))
    except Exception:          # en Windows sin datos de zonas horarias: hora local del PC
        return datetime.now()


def _flatten(data):
    rumors = [e for p in data["players"].values() for e in p["rumors"]]
    rumors.sort(key=lambda e: e["last_update"], reverse=True)   # a igual termómetro, lo más reciente
    rumors.sort(key=lambda e: e["score"], reverse=True)
    return rumors


def _json(obj):
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")


def month_label(ym):
    y, m = ym.split("-")
    return f"{MONTHS[int(m) - 1]} de {y}"


def _static_list(news, rumors, limit=60):
    """Titulares en HTML normal, para buscadores y para quien no ejecute JavaScript.
    Al cargar la página, el código la sustituye por la versión interactiva."""
    esc = html_lib.escape
    parts = []
    if rumors:
        parts.append("<h2>Rumores de fichajes</h2><ul>")
        for r in rumors[:20]:
            route = f"{r['from_club'] or 'origen sin confirmar'} → {r['to_club'] or 'destino sin confirmar'}"
            parts.append(f"<li>{esc(r['player'])}: {esc(route)} ({r['score']}°)</li>")
        parts.append("</ul>")
    parts.append("<h2>Últimas noticias de fútbol</h2><ul>")
    for n in list(news)[:limit]:
        parts.append(f'<li><a href="{esc(n["url"], quote=True)}">{esc(n["title"])}</a> ({esc(n["source"])})</li>')
    parts.append("</ul>")
    return "".join(parts)


def _write(path, *, title, heading, crumbs, rumors, news, archive, is_archive,
           description, canonical, root):
    esc = html_lib.escape
    verification = (f'<meta name="google-site-verification" content="{esc(config.GOOGLE_VERIFICATION, quote=True)}">'
                    if config.GOOGLE_VERIFICATION else "")
    ld = {"@context": "https://schema.org", "@type": "WebSite", "name": config.SITE_NAME,
          "url": config.SITE_URL + "/", "inLanguage": "es", "description": config.SITE_DESCRIPTION}
    html = (TEMPLATE
            .replace("__DESCRIPTION__", esc(description, quote=True))
            .replace("__CANONICAL__", esc(canonical, quote=True))
            .replace("__SITE_NAME__", esc(config.SITE_NAME, quote=True))
            .replace("__SITE_URL__", config.SITE_URL)
            .replace("__ROOT__", root)
            .replace("__VERIFICATION__", verification)
            .replace("__LDJSON__", _json(ld))
            .replace("__STATIC__", _static_list(list(news), rumors)))
    html = (html
            .replace("__TITLE__", title).replace("__HEADING__", heading).replace("__CRUMBS__", crumbs)
            .replace("__UPDATED__", _now_spain().strftime("%d/%m/%Y a las %H:%M"))
            .replace("__IS_ARCHIVE__", "true" if is_archive else "false")
            .replace("__RUMORS__", _json(rumors)).replace("__NEWS__", _json(list(news)))
            .replace("__ARCHIVE__", _json(archive)).replace("__LEAGUES__", _json(config.LEAGUES))
            .replace("__RECENT_DAYS__", str(config.RECENT_DAYS)).replace("__NEWS_DAYS__", str(config.NEWS_DAYS)))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return os.path.abspath(path)


def generate(data, news=(), months=(), out_dir="web"):
    """Portada. months = [(AAAA-MM, nº noticias, nº rumores)], del más reciente al más antiguo."""
    archive = _archive(months, prefix="archivo/")
    write_static(months, out_dir)
    return _write(os.path.join(out_dir, "index.html"),
                  title=f"{config.SITE_NAME}: noticias de fútbol y rumores del mercado",
                  heading="Fútbol: noticias y rumores", crumbs="", rumors=_flatten(data),
                  news=news, archive=archive, is_archive=False,
                  description=config.SITE_DESCRIPTION, canonical=config.SITE_URL + "/", root="")


def _archive(months, prefix="", current=None):
    return [{"year": int(ym[:4]), "label": MONTHS[int(ym[5:]) - 1], "href": f"{prefix}{ym}.html",
             "news": n, "rumors": r, "current": ym == current} for ym, n, r in months]


def generate_month(ym, data, news, prev_ym=None, next_ym=None, out_dir="web", months=()):
    links = ['<a href="../index.html">Volver a la portada</a>']
    if prev_ym:
        links.append(f'<a href="{prev_ym}.html">← {month_label(prev_ym)}</a>')
    if next_ym:
        links.append(f'<a href="{next_ym}.html">{month_label(next_ym)} →</a>')
    crumbs = '<nav class="crumbs">' + "".join(links) + "</nav>"
    label = month_label(ym)
    return _write(os.path.join(out_dir, "archivo", f"{ym}.html"),
                  title=f"Noticias y rumores de fútbol de {label} | {config.SITE_NAME}",
                  heading=f"Archivo de {label}", crumbs=crumbs, rumors=_flatten(data),
                  news=news, archive=_archive(months, current=ym), is_archive=True,
                  description=(f"Todas las noticias de fútbol y los rumores de fichajes de {label}, "
                               "día a día, con enlace a cada medio."),
                  canonical=f"{config.SITE_URL}/archivo/{ym}", root="../")


FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="14" fill="#145a32"/>
<circle cx="32" cy="32" r="21" fill="none" stroke="#fff" stroke-width="3" opacity=".35"/>
<line x1="32" y1="6" x2="32" y2="58" stroke="#fff" stroke-width="3" opacity=".35"/>
<rect x="26" y="12" width="12" height="30" rx="6" fill="#fff"/>
<rect x="29.5" y="22" width="5" height="22" rx="2.5" fill="#d93a1b"/>
<circle cx="32" cy="47" r="9" fill="#fff"/>
<circle cx="32" cy="47" r="6" fill="#d93a1b"/>
</svg>"""


def _png_icon(size):
    """Mismo icono que el SVG (termómetro sobre césped), dibujado como PNG."""
    from PIL import Image, ImageDraw
    s = size / 64
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=int(14 * s), fill="#145a32")
    soft = "#5b8f6f"   # blanco al 35 % sobre el verde, en color sólido
    d.ellipse([11 * s, 11 * s, 53 * s, 53 * s], outline=soft, width=max(1, int(3 * s)))
    d.line([32 * s, 6 * s, 32 * s, 58 * s], fill=soft, width=max(1, int(3 * s)))
    d.rounded_rectangle([26 * s, 12 * s, 38 * s, 42 * s], radius=int(6 * s), fill="white")
    d.rounded_rectangle([29.5 * s, 22 * s, 34.5 * s, 44 * s], radius=int(2.5 * s), fill="#d93a1b")
    d.ellipse([23 * s, 38 * s, 41 * s, 56 * s], fill="white")
    d.ellipse([26 * s, 41 * s, 38 * s, 53 * s], fill="#d93a1b")
    return im


def _share_image():
    """Imagen para cuando se comparte el enlace (1200x630)."""
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGB", (1200, 630), "#145a32")
    d = ImageDraw.Draw(im)
    for x in range(0, 1200, 160):
        d.rectangle([x + 80, 0, x + 159, 630], fill="#1b6b3d")
    d.ellipse([820, -140, 1180, 220], outline=(255, 255, 255), width=5)
    d.line([1000, 0, 1000, 630], fill=(255, 255, 255), width=5)
    im.paste(_png_icon(180), (80, 90), _png_icon(180))
    def font(size):
        for name in ["DejaVuSans-Bold.ttf", "arialbd.ttf", "Arial Bold.ttf"]:
            try:
                return ImageFont.truetype(name, size)
            except OSError:
                pass
        return ImageFont.load_default()
    d.text((80, 320), config.SITE_NAME, font=font(84), fill="white")
    d.text((80, 430), "Noticias de fútbol y rumores del mercado", font=font(40), fill=(230, 240, 234))
    d.text((80, 490), config.SITE_URL.replace("https://", ""), font=font(32), fill=(190, 215, 200))
    return im


def write_static(months, out_dir="web"):
    """favicon, imagen para compartir, robots.txt y sitemap.xml."""
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(FAVICON_SVG)
    try:
        _png_icon(48).save(os.path.join(out_dir, "favicon.png"))
        _png_icon(180).save(os.path.join(out_dir, "apple-touch-icon.png"))
        _share_image().save(os.path.join(out_dir, "compartir.png"))
    except ImportError:
        pass   # sin Pillow no hay PNG; el icono SVG sigue funcionando
    with open(os.path.join(out_dir, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\n\nSitemap: {config.SITE_URL}/sitemap.xml\n")
    today = _now_spain().strftime("%Y-%m-%d")
    urls = [(config.SITE_URL + "/", today, "hourly", "1.0")]
    current = _now_spain().strftime("%Y-%m")
    for ym, _, _ in months:
        urls.append((f"{config.SITE_URL}/archivo/{ym}", today if ym == current else f"{ym}-28",
                     "daily" if ym == current else "monthly", "0.6"))
    body = "".join(f"<url><loc>{u}</loc><lastmod>{m}</lastmod><changefreq>{c}</changefreq>"
                   f"<priority>{p}</priority></url>" for u, m, c, p in urls)
    with open(os.path.join(out_dir, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>\n')
