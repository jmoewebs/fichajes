"""Genera la web estática: web/index.html (portada) y web/archivo/AAAA-MM.html (un archivo por mes).
Las páginas se abren con doble clic, sin servidor."""
import html as html_lib
import json
import os
import re

import config
from datetime import datetime

MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
          "septiembre", "octubre", "noviembre", "diciembre"]

TEMPLATE = r"""<!DOCTYPE html>
<html lang="es">
<head>
__ADSENSE__
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<meta name="description" content="__DESCRIPTION__">
<link rel="canonical" href="__CANONICAL__">
<link rel="alternate" type="application/rss+xml" title="Movimientos del mercado de fichajes" href="__SITE_URL__/feed.xml">
<meta property="og:type" content="website">
<meta property="og:site_name" content="__SITE_NAME__">
<meta name="application-name" content="__SITE_NAME__">
<meta name="apple-mobile-web-app-title" content="__SITE_NAME__">
<meta property="og:title" content="__TITLE__">
<meta property="og:description" content="__DESCRIPTION__">
<meta property="og:url" content="__CANONICAL__">
<meta property="og:locale" content="es_ES">
<meta property="og:image" content="__SITE_URL__/compartir.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="__TITLE__">
<meta name="twitter:description" content="__DESCRIPTION__">
<meta name="twitter:image" content="__SITE_URL__/compartir.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<link rel="icon" href="__ROOT__favicon.svg" type="image/svg+xml">
<link rel="icon" href="__ROOT__favicon.png" type="image/png" sizes="48x48">
<link rel="apple-touch-icon" href="__ROOT__apple-touch-icon.png">
__VERIFICATION__
<script type="application/ld+json">__LDJSON__</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700&family=Barlow+Condensed:wght@500;600;700;800&display=swap" rel="stylesheet">
<style>
:root {
  --grass:#145a32; --grass-2:#1b6b3d; --chalk:#f2f6f3; --card:#ffffff; --ink:#10201a;
  --muted:#5d6d65; --line:#dbe3de; --soft:#e8eeea; --on:#145a32; --tab:#3d4d45;
  --cold:#2b78c5; --warm:#e9a100; --hot:#d93a1b; --ok:#1f8f4e; --off:#8a958f;
  --cond:"Barlow Condensed","Arial Narrow",system-ui,sans-serif;
  --body:"Barlow",system-ui,-apple-system,"Segoe UI",sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root { --chalk:#0c1611; --card:#14211a; --ink:#e4ece7; --muted:#93a39a; --line:#24352c;
          --soft:#1c2b23; --grass:#0f4426; --grass-2:#155230; --on:#7ee2a1; --tab:#b9c7bf; }
}
* { box-sizing:border-box; }
html { -webkit-text-size-adjust:100%; }
body { margin:0; background:var(--chalk); color:var(--ink); font:16px/1.5 var(--body); }
a { color:inherit; }
a:focus-visible, button:focus-visible, input:focus-visible, select:focus-visible {
  outline:3px solid var(--warm); outline-offset:2px; }
.wrap { max-width:1300px; margin:0 auto; padding:0 20px; }

/* Cabecera compacta: título a la izquierda, botones y visitas a la derecha */
.wrap { max-width:1240px; margin:0 auto; padding:0 24px; }
.pitch { position:relative; color:#fff; padding:14px 0 0; background-color:var(--grass);
  background-image:repeating-linear-gradient(90deg, rgba(255,255,255,.035) 0 90px, rgba(255,255,255,0) 90px 180px); }
.pitch .top { display:flex; justify-content:space-between; align-items:flex-start; gap:12px 24px; flex-wrap:wrap;
  padding-bottom:56px; }
.pitch.notools .top { padding-bottom:22px; }
.pitch .ttl { order:-1; flex:1 1 480px; max-width:780px; padding-top:2px; }
.updated { display:inline-flex; align-items:center; gap:8px; margin:0; font-weight:600; font-size:14px;
  letter-spacing:.06em; text-transform:uppercase; color:#d6f2e0; }
.updated::before { content:""; width:8px; height:8px; border-radius:50%; background:#7ee2a1; }
h1 { font:800 clamp(38px,6vw,52px)/1 var(--cond); margin:6px 0 8px; text-transform:uppercase; letter-spacing:-.005em; }
.tagline { margin:0; font-size:17px; line-height:1.4; color:#e3f4ea; max-width:56ch; }
.crumbs { display:flex; gap:16px; flex-wrap:wrap; margin:10px 0 0; font-size:15px; }
.crumbs a { color:#fff; }

/* Buscador y club: flotan sobre el borde inferior del verde */
.wrap.toolsrow { margin-top:-40px; position:relative; z-index:3; }
.toolsrow[hidden] { display:none; }
.tools { background:var(--card); border-radius:16px; box-shadow:0 10px 30px rgba(16,32,26,.18); padding:12px;
  display:flex; gap:12px; flex-wrap:wrap; align-items:center; }
.tools[hidden] { display:none !important; }
.qbox { flex:1 1 360px; display:flex; align-items:center; gap:12px; background:var(--chalk); border-radius:10px;
  padding:0 16px; height:56px; color:var(--muted); }
.qbox:focus-within { outline:3px solid var(--warm); outline-offset:2px; }
.qbox input { flex:1; min-width:0; border:0; background:transparent; font:500 18px var(--body); color:var(--ink); outline:none; }
.tools select { flex:0 1 240px; height:56px; border:0; border-radius:10px; background:var(--chalk); padding:0 16px;
  font:600 17px var(--body); color:var(--ink); }

/* Pestañas con icono y línea inferior en la activa */
.tabbar { background:var(--card); border-bottom:1px solid var(--line); margin-top:16px; }
.tabs { display:flex; gap:6px; overflow-x:auto; scrollbar-width:none; }
.tab { display:inline-flex; align-items:center; gap:8px; padding:18px 16px 15px; font:600 17px/1.2 var(--body);
  color:var(--tab); background:transparent; border:0; border-bottom:3px solid transparent; cursor:pointer;
  white-space:nowrap; text-decoration:none; }
.tab:hover { color:var(--ink); }
.tab.on { color:var(--on); border-bottom-color:var(--on); font-weight:700; }
.tab svg { flex:none; }
.tab .n { font-weight:500; opacity:.6; margin-left:2px; }
.sm-only { display:none; }
@media (max-width:560px) { .sm-only { display:inline; } .lg-only { display:none; } }

main { min-width:0; }
.page { padding-top:24px; padding-bottom:48px; }

/* Chips de competición: una sola línea, sin scroll lateral */
.chips { display:flex; flex-wrap:nowrap; gap:8px; position:relative; }
.chips[hidden] { display:none; }
.chip { flex:1 1 auto; display:inline-flex; align-items:center; justify-content:center; gap:6px;
  height:44px; padding:0 10px; border-radius:999px; border:1.5px solid var(--line); background:var(--card);
  color:var(--ink); font:600 15px/1 var(--body); white-space:nowrap; cursor:pointer; }
.chip:hover { border-color:var(--on); }
.chip .cnt { font-size:14px; font-weight:500; opacity:.75; font-variant-numeric:tabular-nums; }
.chip .cnt:empty { display:none; }
.chip[aria-pressed="true"] { background:var(--grass); border-color:var(--grass); color:#fff; }
.chip .chev { width:7px; height:7px; border-right:2px solid currentColor; border-bottom:2px solid currentColor;
  transform:rotate(45deg); margin:-3px 0 0 2px; flex:none; }
.chips .extras { display:contents; }
.chips .more { display:none; }
@media (max-width:1100px) { .chips { gap:6px; } .chip { font-size:14px; padding:0 8px; } }

/* Portada: noticia destacada y dos tarjetas */
.hero { display:grid; grid-template-columns:minmax(0,3fr) minmax(0,2fr); gap:20px; margin-top:24px; }
.hero[hidden] { display:none; }
.hero.one { grid-template-columns:minmax(0,1fr); }
.hero-main { position:relative; display:flex; flex-direction:column; justify-content:flex-end; min-height:420px;
  border-radius:18px; overflow:hidden; color:#fff; padding:32px; text-decoration:none; background-color:#0d3d22;
  background-image:repeating-linear-gradient(90deg, rgba(255,255,255,.04) 0 70px, rgba(255,255,255,0) 70px 140px); }
.hero-main .pitch-art { position:absolute; right:-60px; top:-30px; width:520px; height:338px; fill:none;
  stroke:rgba(255,255,255,.14); stroke-width:3; }
.hero-in { position:relative; }
.hero-tags { display:flex; gap:10px; align-items:center; margin-bottom:16px; }
.badge-live, .badge-rum { display:inline-flex; align-items:center; gap:6px; font-weight:700; font-size:13px;
  letter-spacing:.06em; text-transform:uppercase; padding:5px 10px; border-radius:6px; color:#fff; background:var(--hot); }
.badge-live::before { content:""; width:7px; height:7px; border-radius:50%; background:#fff; }
.badge-rum { background:var(--warm); color:#2a1d00; }
.hero-src { font-weight:600; font-size:15px; color:#cfeedb; }
.hero-main h2 { margin:0; font:700 48px/1.02 var(--cond); max-width:20ch; display:-webkit-box;
  -webkit-line-clamp:5; -webkit-box-orient:vertical; overflow:hidden; }
.hero-clubs { margin-top:18px; display:flex; gap:8px; flex-wrap:wrap; }
.hero-clubs span { background:rgba(255,255,255,.16); padding:5px 12px; border-radius:999px; font-weight:600; font-size:14px; }
.hero-side { display:flex; flex-direction:column; gap:20px; }
.hero-card { flex:1; display:flex; flex-direction:column; justify-content:space-between; background:var(--card);
  border:1px solid var(--line); border-top:5px solid var(--on); border-radius:18px; padding:26px;
  text-decoration:none; color:inherit; }
.hero-card.fichaje { border-top-color:var(--warm); }
.hero-card .kick { font-weight:700; font-size:13px; letter-spacing:.06em; text-transform:uppercase; color:var(--on); }
.hero-card.fichaje .kick { color:color-mix(in srgb, var(--warm) 70%, var(--ink)); }
.hero-card h3 { margin:10px 0 14px; font:700 28px/1.08 var(--cond); display:-webkit-box; -webkit-line-clamp:3;
  -webkit-box-orient:vertical; overflow:hidden; }
.hero-card .by { font-weight:600; font-size:14px; color:var(--muted); }
.hero-main:hover, .hero-card:hover { box-shadow:0 6px 20px rgba(16,32,26,.12); }

/* Contenido + columna derecha */
.layout { display:grid; grid-template-columns:minmax(0, 1fr) 340px; gap:28px; align-items:start; margin-top:28px; }
.side { display:flex; flex-direction:column; gap:20px; }
.side-box { background:var(--card); border:1px solid var(--line); border-radius:16px; padding:22px; }
.side-box .flabel { font:800 26px/1 var(--cond); text-transform:uppercase; margin:0 0 14px; }
.side .fgroup + .fgroup { margin-top:0; }
.cl-list { display:flex; flex-wrap:wrap; gap:8px; }
.cl-chip { padding:8px 14px; border-radius:999px; border:1.5px solid var(--line); font-weight:600; font-size:15px;
  text-decoration:none; }
a.cl-chip:hover { border-color:var(--on); }
.cta { background:var(--grass); color:#fff; border-radius:16px; padding:24px; }
.cta h2 { margin:0 0 8px; font:800 28px/1 var(--cond); text-transform:uppercase; }
.cta p { margin:0 0 16px; font-size:16px; line-height:1.45; color:#dff3e6; }
.cta a { display:inline-flex; align-items:center; height:44px; padding:0 20px; border-radius:999px; background:#fff;
  color:#145a32; font-weight:700; font-size:16px; text-decoration:none; }
.cta.tgc { background:var(--card); color:var(--ink); border:1px solid var(--line); }
.cta.tgc p { color:var(--muted); }
.cta.tgc a { background:var(--grass); color:#fff; }

@media (max-width:820px) {
  .hero { grid-template-columns:minmax(0,1fr); gap:14px; margin-top:12px; }
  .hero-main { min-height:260px; padding:20px; border-radius:16px; }
  .hero-main .pitch-art { width:300px; height:195px; right:-50px; top:-20px; }
  .hero-main h2 { font-size:32px; line-height:1.04; }
  .hero-tags { margin-bottom:12px; }
  .hero-card { padding:20px; border-radius:16px; } .hero-card h3 { font-size:26px; }
  .layout { display:flex; flex-direction:column; gap:16px; margin-top:16px; }
  .layout main { order:1; }
  .side { display:contents; }
  .side > * { order:2; }
  .side > .filters { order:0; }
  .chip { font-size:14px; padding:0 8px; } .chip .cnt { display:none; }
  .chips .more { display:inline-flex; }
  .chips .extras { display:none; }
  .chips.open .extras { display:flex; flex-wrap:wrap; gap:6px; position:absolute; z-index:6; left:0; right:0;
    top:calc(100% + 6px); padding:10px; background:var(--card); border:1px solid var(--line); border-radius:14px;
    box-shadow:0 10px 24px rgba(16,32,26,.18); }
  .chips.open .extras .chip { flex:0 0 auto; }
}
@media (max-width:700px) {
  .pitch .top { display:grid; grid-template-columns:1fr auto; gap:0 12px; align-items:center; padding-bottom:56px; }
  .pitch.notools .top { padding-bottom:22px; }
  .pitch .ttl, .kofi-top { display:contents; }
  .kofi-top .top-btns { order:1; grid-column:1 / -1; justify-content:space-between; margin-bottom:14px; }
  .pitch .updated { order:2; grid-column:1; font-size:13px; letter-spacing:.05em; }
  .kofi-top .visits { order:2; grid-column:2; font-size:13px !important; text-transform:uppercase; letter-spacing:.05em; }
  .pitch h1 { order:3; grid-column:1 / -1; margin:8px 0 6px; }
  .pitch .tagline { order:4; grid-column:1 / -1; font-size:15px; }
  .pitch .crumbs { order:5; grid-column:1 / -1; }
  .tools { padding:10px; border-radius:14px; gap:8px; box-shadow:0 10px 24px rgba(16,32,26,.18); }
  .qbox { flex-basis:100%; height:52px; padding:0 14px; }
  .qbox input { font-size:17px; }
  .tools select { flex:1 1 100%; height:48px; font-size:16px; }
}
@media (max-width:560px) {
  .wrap { padding:0 16px; }
  .hero-side { display:none; }
  .tab { padding:12px 12px; } .tab svg { display:none; }
}
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
/* Fantasy */
.layout.solo { grid-template-columns:minmax(0, 1fr); margin-top:0; }
.layout.solo .side { display:none; }
.layout.solo main { max-width:900px; }
.fx-intro { color:var(--muted); max-width:62ch; margin:22px 0 14px; }
.fx-add { display:flex; gap:10px; flex-wrap:wrap; margin-bottom:8px; }
.fx-add textarea { flex:1 1 320px; min-width:0; font:inherit; padding:10px 12px; border-radius:6px; resize:vertical;
  border:1px solid var(--line); background:var(--card); color:var(--ink); }
.fx-btns { display:flex; flex-direction:column; gap:8px; }
.fx-add .fx-clear { background:transparent; color:var(--ink); border-color:var(--line); font-weight:500; }
.fx-add button, .fx-clear { font:600 15px/1 var(--body); padding:10px 16px; border-radius:6px; cursor:pointer;
  border:1px solid var(--grass); background:var(--grass); color:#fff; }
.fx-clear { background:transparent; color:var(--muted); border-color:var(--line); font-weight:500; }
.fx-sum { display:flex; gap:8px; flex-wrap:wrap; margin:18px 0 10px; }
.fx-list { display:grid; gap:10px; }
.fx { display:grid; grid-template-columns:1fr auto; gap:6px 14px; align-items:start; background:var(--card);
  border:1px solid var(--line); border-left:5px solid var(--off); border-radius:14px; padding:14px 16px; }
.fx.out { border-left-color:var(--hot); } .fx.doubt { border-left-color:var(--warm); }
.fx.back { border-left-color:var(--ok); } .fx.none { border-left-color:var(--line); }
.fx h3 { font:700 22px/1.1 var(--cond); margin:0; }
.fx .why { grid-column:1 / -1; font-size:14px; }
.fx .why a { font-weight:500; }
.fx .rm { background:none; border:0; color:var(--muted); cursor:pointer; font:inherit; font-size:14px; text-decoration:underline; }
.st-out { background:var(--hot); } .st-doubt { background:var(--warm); color:#2a1d00; }
.st-back { background:var(--ok); }
.status.st-none { background:var(--soft); color:var(--ink); font-weight:500; }
.fx-group { font:600 20px/1.1 var(--cond); margin:22px 0 10px; }
.fx-team { font:500 14px/1 var(--body); color:var(--muted); margin-left:6px; }
.fx-note { font-size:14px; color:var(--muted); margin-top:16px; max-width:62ch; }

/* Clasificación */
.lg-pick { display:flex; flex-wrap:wrap; gap:6px; margin:22px 0 6px; }
.lg-pick a { font:500 15px/1 var(--body); padding:8px 14px; border-radius:20px; cursor:pointer; text-decoration:none;
  border:1px solid var(--line); background:var(--card); color:var(--ink); }
.lg-pick a[aria-pressed="true"] { background:var(--grass); border-color:var(--grass); color:#fff; }
.tb-h { font:700 26px/1.1 var(--cond); margin:26px 0 10px; display:flex; align-items:baseline; gap:10px; flex-wrap:wrap; }
.tb-h small { font:500 15px/1 var(--body); color:var(--muted); }
.tb-wrap { overflow-x:auto; background:var(--card); border:1px solid var(--line); border-radius:16px; }
table.tb { border-collapse:collapse; width:100%; font-size:15px; font-variant-numeric:tabular-nums; }
.tb th { font:600 13px/1 var(--body); color:var(--muted); text-align:right; padding:10px 8px; border-bottom:1px solid var(--line); white-space:nowrap; }
.tb td { padding:9px 8px; text-align:right; border-top:1px solid var(--line); white-space:nowrap; }
.tb tr:first-child td { border-top:0; }
.tb th.l, .tb td.l { text-align:left; }
.tb td.pos { color:var(--muted); width:28px; }
.tb td.team { font-weight:600; }
.tb td.pts { font-weight:700; font-size:16px; }
.tb td.big { font:700 18px/1 var(--cond); }
.tb .sub { color:var(--muted); font-size:13px; }
.form { display:inline-flex; gap:3px; }
.form i { width:18px; height:18px; border-radius:4px; display:inline-grid; place-items:center; font:700 11px/1 var(--body);
  font-style:normal; color:#fff; background:var(--off); }
.form i.W { background:var(--ok); } .form i.L { background:var(--hot); }
.tb-two { display:grid; grid-template-columns:1fr 1fr; gap:20px; }
.tb-note { font-size:13px; color:var(--muted); margin:8px 0 0; }
@media (max-width:720px) {
  .tb-two { grid-template-columns:1fr; }
  .tb .hide-sm { display:none; }
}

/* Ko-fi y contador */
.kofi-top { display:flex; flex-direction:column; align-items:flex-end; gap:8px; }
.kofi-top .visits { font-size:15px; font-weight:500; color:#d6f2e0; }
.kofi-top .visits b { color:#fff; font-weight:700; }
.kofi { display:inline-flex; align-items:center; gap:8px; font:600 15px/1 var(--body); text-decoration:none;
  padding:9px 14px; border-radius:20px; background:#fff; color:#145a32; }
.kofi:hover { background:#fff7e6; }
.top-btns { display:flex; gap:10px; flex-wrap:wrap; }
.kofi-top .kofi { height:44px; padding:0 18px; border-radius:999px; font-weight:700; }
.kofi-top .kofi.tg { background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.35); color:#fff; font-weight:600; }
.kofi-top .kofi.tg:hover { background:rgba(255,255,255,.24); }
.kofi svg { display:block; }
.foot .kofi { box-shadow:none; border:1px solid var(--line); background:var(--card); color:var(--ink); text-decoration:none; }
.visits { font-variant-numeric:tabular-nums; }
.visits b { color:var(--ink); }
.fbtn { display:none; }
@media (max-width:820px) {
  .fbtn { display:flex; align-items:center; justify-content:space-between; width:100%; font:600 16px var(--body);
    padding:12px 14px; border-radius:12px; border:1px solid var(--line); background:var(--card); color:var(--ink); cursor:pointer; }
  .side-box.filters { padding:0; border:0; border-radius:0; background:none; }
  .filters:not(.open) .fgroup { display:none; }
  .filters.open .fgroup { margin-top:12px; background:var(--card); border:1px solid var(--line); border-radius:14px; padding:14px; }
  .filters .flabel { display:none; }
}
@media (max-width:560px) { .kofi-top .pre { display:none; } .top-btns { gap:6px; } .kofi-top .kofi { padding:0 14px; font-size:14px; } }

.foot { border-top:1px solid var(--line); margin-top:20px; padding:22px 20px 40px; align-items:center; font-size:14px;
  color:var(--muted); display:flex; flex-wrap:wrap; gap:8px 22px; }
.foot a, .foot button { color:var(--muted); font:inherit; background:none; border:0; padding:0;
  text-decoration:underline; cursor:pointer; }
.cookies { position:fixed; left:16px; right:16px; bottom:16px; z-index:10; max-width:560px;
  margin:0 auto; background:var(--card); color:var(--ink); border:1px solid var(--line);
  border-radius:10px; padding:16px 18px; box-shadow:0 10px 30px rgba(0,0,0,.18); }
.cookies p { margin:0 0 12px; font-size:15px; }
.cookies .btns { display:flex; gap:10px; flex-wrap:wrap; align-items:center; }
.cookies button { font:600 15px/1 var(--body); padding:10px 16px; border-radius:6px; cursor:pointer;
  border:1px solid var(--grass); }
.cookies .yes { background:var(--grass); color:#fff; }
.cookies .no { background:transparent; color:var(--ink); border-color:var(--line); }
.cookies a { font-size:14px; color:var(--muted); }

@media (max-width:820px) {
  .year-h { margin:8px 0 6px 0; width:100%; }
  .fgroup + .fgroup { margin-top:12px; }
  .flist { display:flex; flex-wrap:wrap; gap:6px; }
  .chipbtn { width:auto; padding:6px 11px; border:1px solid var(--line); border-radius:20px;
    background:var(--card); font-size:14px; }
  .chipbtn .cnt, .chipbtn .dot { display:none; }
}
.empty { color:var(--muted); padding:48px 0; max-width:46ch; }
.day { font:800 30px/1.1 var(--cond); text-transform:uppercase; letter-spacing:.01em; margin:28px 0 12px; }
#list > .day:first-child { margin-top:0; }
.day:first-letter { text-transform:uppercase; }

/* Noticias */
.news { list-style:none; margin:0; padding:0; background:var(--card); border:1px solid var(--line);
  border-radius:16px; }
/* Lo más leído */
.side-read:empty { display:none; }
.top-read { display:none !important; }
@media (max-width:820px) { .top-read { display:block !important; } .side-read { display:none; } }
.side-read .hd { display:flex; flex-direction:column; align-items:flex-start; gap:8px; margin-bottom:8px; }
.side-read .seg { margin-left:0; } .side-read .seg button { white-space:nowrap; }
.side-read .flabel { margin:0; }
.side-read .seg button { padding:4px 8px; font-size:12px; }
.side-read ol { list-style:none; margin:0; padding:0; counter-reset:r; }
.side-read li { display:grid; grid-template-columns:20px 1fr; gap:6px; padding:9px 0; border-top:1px solid var(--line); }
.side-read li:first-child { border-top:0; padding-top:2px; }
.side-read li::before { counter-increment:r; content:counter(r); font:700 20px/1.1 var(--cond); color:var(--hot); }
.side-read li:nth-child(n+4)::before { color:var(--muted); }
.side-read a { font-size:14px; line-height:1.3; font-weight:500; text-decoration:none; display:-webkit-box;
  -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
.side-read a:hover { text-decoration:underline; }
.side-read .src-n { font-size:12px; color:var(--muted); margin-top:5px; display:flex; align-items:center; gap:5px; }
.side-read .src-n .src { width:16px; height:16px; border-radius:3px; font-size:8px; }
.side-read .src-n .src img { width:12px; height:12px; }
.top-read { background:var(--card); border:1px solid var(--line); border-radius:16px; padding:14px 16px 6px; margin:20px 0 4px; }
.top-read .hd { display:flex; align-items:center; gap:12px; flex-wrap:wrap; margin-bottom:6px; }
.top-read h2 { font:700 22px/1 var(--cond); margin:0; }
.seg { display:inline-flex; background:var(--soft); border-radius:20px; padding:3px; margin-left:auto; }
.seg button { font:500 13px/1 var(--body); border:0; background:transparent; color:var(--muted); padding:6px 11px;
  border-radius:16px; cursor:pointer; }
.seg button[aria-pressed="true"] { background:var(--card); color:var(--ink); box-shadow:0 1px 3px rgba(0,0,0,.12); }
.top-read ol { list-style:none; margin:0; padding:0; counter-reset:r; }
.top-read li { display:grid; grid-template-columns:34px 1fr; gap:8px; padding:9px 0; border-top:1px solid var(--line); }
.top-read li:first-child { border-top:0; }
.top-read li::before { counter-increment:r; content:counter(r); font:700 28px/1 var(--cond); color:var(--hot); text-align:center; }
.top-read li:nth-child(n+4)::before { color:var(--muted); }
.top-read a { font-weight:500; text-decoration:none; }
.top-read a:hover { text-decoration:underline; }
.top-read .none { color:var(--muted); font-size:14px; padding:6px 0 10px; }

details.slot { margin:0 0 18px; padding:0; background:var(--card); border:1px solid var(--line); border-radius:16px; overflow:hidden; }
.slot > summary { list-style:none; cursor:pointer; display:flex; align-items:center; gap:12px; padding:14px 22px;
  user-select:none; color:inherit; font-size:inherit; }
.slot > summary::-webkit-details-marker { display:none; }
.slot > summary:hover { background:var(--chalk); }
.slot[open] > summary { border-bottom:1px solid var(--line); }
.slot .hrs { font:800 24px/1 var(--cond); text-transform:uppercase; letter-spacing:.01em; font-variant-numeric:tabular-nums; color:var(--ink); }
.slot .lbl { font-size:14px; color:var(--muted); }
.slot .cnt { margin-left:auto; font-size:15px; font-weight:600; color:var(--muted); font-variant-numeric:tabular-nums; }
.slot .hrs, .slot .cnt { white-space:nowrap; }
@media (max-width:560px) { .slot .lbl { display:none; } .slot > summary { padding:12px 16px; gap:8px; } .slot .hrs { font-size:21px; } }
.slot .chev { width:9px; height:9px; border-right:2px solid var(--muted); border-bottom:2px solid var(--muted);
  transform:rotate(45deg); margin:-4px 4px 0 2px; transition:transform .15s; }
.slot[open] .chev { transform:rotate(-135deg); margin-top:4px; }
.slot > .news { border:0; border-radius:0; }
.news li { display:flex; gap:18px; align-items:flex-start; padding:18px 22px; border-top:1px solid var(--line); }
.news li:first-child { border-top:0; }
.news li:hover { background:var(--chalk); }
.news .tm { flex:none; width:54px; font:700 22px/1.2 var(--cond); color:var(--on); font-variant-numeric:tabular-nums; }
.news .bd { flex:1; min-width:0; }
.news .t { display:block; font-weight:600; font-size:19px; line-height:1.3; text-decoration:none; }
.news .t:hover { text-decoration:underline; }
.news .meta { margin-top:8px; gap:6px 8px; font-size:14px; }
.news .by { display:inline-flex; align-items:center; gap:6px; font-weight:600; }
.news .by .src { width:18px; height:18px; border-radius:4px; font-size:9px; }
.news .by .src img { width:14px; height:14px; }
@media (max-width:560px) {
  .news li { gap:12px; padding:14px 16px; }
  .news .tm { width:auto; min-width:46px; font-size:20px; }
  .news .t { font-size:17px; }
}
.meta { display:flex; flex-wrap:wrap; gap:6px 10px; align-items:center; margin-top:4px;
  font-size:13px; color:var(--muted); }
.time { font-variant-numeric:tabular-nums; }
.club { background:var(--soft); color:var(--ink); font-weight:600; font-size:13px; padding:2px 10px; border-radius:999px;
  text-decoration:none; }
a.club:hover { text-decoration:underline; }
.route a { color:inherit; text-decoration:none; } .route a:hover { text-decoration:underline; }
.share { display:inline-flex; align-items:center; gap:5px; font:500 13px/1 var(--body); color:var(--muted);
  background:transparent; border:1px solid var(--line); border-radius:20px; padding:5px 10px; cursor:pointer; }
.share:hover { color:var(--ink); border-color:var(--grass-2); }
.share.ico { padding:4px 7px; border-color:transparent; margin-left:auto; }
.share.ico:hover { border-color:var(--line); }
.promo { display:flex; gap:14px; align-items:center; flex-wrap:wrap; background:var(--card); border:1px solid var(--line);
  border-left:5px solid #2a9fd8; border-radius:16px; padding:14px 16px; margin:20px 0 4px; font-size:15px; }
.promo p { margin:0; flex:1 1 320px; }
.promo a.join { display:inline-flex; align-items:center; gap:7px; font:600 15px/1 var(--body); text-decoration:none;
  color:#fff; background:#1b6fa8; padding:10px 14px; border-radius:20px; white-space:nowrap; }
.sec-h { font:700 24px/1.1 var(--cond); margin:26px 0 4px; }
.sec-h small { font:500 14px/1 var(--body); color:var(--muted); margin-left:8px; }
.club-box { background:var(--card); border:1px solid var(--line); border-radius:16px; padding:16px 18px; margin:20px 0 6px; }
.club-box h2 { font:700 26px/1.1 var(--cond); margin:0 0 6px; }
.club-box p { margin:0; color:var(--muted); }
.club-box p + p { margin-top:10px; }
footer .pref { white-space:nowrap; }
.vote-row { display:flex; flex-wrap:wrap; align-items:center; gap:8px; margin-top:10px; font-size:14px; color:var(--muted); }
.vote-row button { font:600 14px/1 var(--body); padding:7px 13px; border-radius:999px; border:1px solid var(--line); background:var(--card); color:var(--ink); cursor:pointer; }
.vote-row button:hover { border-color:var(--ok); }
.vote-row .vbar { flex:1 1 110px; min-width:90px; max-width:220px; height:8px; border-radius:4px; background:var(--line); overflow:hidden; }
.vote-row .vbar i { display:block; height:100%; background:var(--ok); }
.crumbs .sep { opacity:.6; }
.club-box a { color:var(--ink); font-weight:600; }
details.foot-clubs { width:100%; font-size:13px; line-height:1.9; border-top:0; padding-top:0; margin-top:0; }
.foot-clubs > summary { cursor:pointer; font-size:14px; color:var(--muted); width:max-content; }
.foot-clubs > summary:hover { color:var(--ink); }
.foot-clubs nav { margin-top:8px; }
.foot-clubs a { margin-right:12px; white-space:nowrap; }
.tag { font-size:12px; font-weight:700; letter-spacing:.05em; text-transform:uppercase; padding:2px 8px; border-radius:5px; }
.tag.live { background:color-mix(in srgb, var(--hot) 14%, transparent); color:color-mix(in srgb, var(--hot) 80%, var(--ink)); }
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
  border:1px solid var(--line); border-radius:16px; padding:18px 20px; }
.player { font:700 28px/1 var(--cond); margin:0; }
.route { margin:6px 0 0; font-size:16px; }
.route .arrow { color:var(--muted); margin:0 6px; }
.also { margin:4px 0 0; font-size:14px; color:var(--muted); }
.also a { color:var(--ink); text-decoration:none; } .also a:hover { text-decoration:underline; }
.status-mini { font-size:12px; font-weight:600; padding:1px 7px; border-radius:20px; color:#fff; }
.route .unk { color:var(--muted); }
.row { display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-top:12px; }
.status { font-size:13px; font-weight:600; padding:2px 10px; border-radius:20px; color:#fff; }
.rlab { font-size:13px; font-weight:700; padding:2px 8px; border-radius:20px; border:1.5px solid var(--off); color:var(--muted); }
.rl-probable { border-color:var(--warm); color:var(--ink); } .rl-oficial { border-color:var(--hot); color:var(--hot); }
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
  border-radius:14px; padding:14px 16px; }
.month:hover { border-color:var(--grass-2); }
.month b { display:block; font:600 22px/1.1 var(--cond); }
.month:first-letter { text-transform:uppercase; }
.month span { font-size:14px; color:var(--muted); }

@media (max-width:560px) {
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
<header class="pitch__NOTOOLS__">
  <div class="wrap top">
    <div class="ttl">
      <p class="updated" id="updated" data-iso="__UPDATED_ISO__">Actualizado el __UPDATED__</p>
      <h1>__HEADING__</h1>
      <p class="tagline">__TAGLINE__Cada titular enlaza a la noticia original.</p>
      __CRUMBS__
    </div>
    __KOFI_TOP__
  </div>
</header>
<div class="wrap toolsrow"__TOOLS_HIDDEN__>
  <div class="tools">
    <label class="qbox"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
      <input id="q" type="search" placeholder="Buscar jugador, club o medio" aria-label="Buscar"></label>
    <select id="club" aria-label="Filtrar por club"><option value="">Todos los clubes</option></select>
  </div>
</div>
<div class="tabbar"><nav class="wrap tabs" id="tabs" aria-label="Secciones">__TABS__</nav></div>
<div class="wrap page">
  <div class="chips" id="f-leagues" role="group" aria-label="Filtrar por competición"></div>
  <section class="hero" id="hero" aria-label="Destacadas" hidden></section>
  <div class="layout">
    <main id="list">__STATIC__</main>
    <aside class="side" aria-label="Complementos">
      <div class="side-box" id="clubs-box" hidden><h2 class="flabel">Clubes en portada</h2><div class="cl-list" id="clubs-list"></div></div>
      <div class="cta"><h2>Liga Fantasy</h2><p>Comprueba si tus titulares están disponibles: lesiones, sanciones y dudas.</p><a href="__ROOT__fantasy/">Ver disponibilidad</a></div>
      __TG_CARD__
      <div class="fgroup side-read side-box" id="side-read"></div>
      <div class="side-box"><div class="flabel" id="days-title">Últimos días</div>
        <div class="flist" id="f-days" role="group" aria-label="Elegir día"></div></div>
      <div class="side-box filters" id="filters">
        <button type="button" class="fbtn" id="fbtn" aria-expanded="false">Filtrar por medio <span>▾</span></button>
        <div class="fgroup"><div class="flabel">Medios</div>
          <div class="flist" id="f-sources" role="group" aria-label="Elegir medios"></div></div>
      </div>
      <div class="side-box" id="history-box"><div class="flabel">Historial</div>
        <div class="flist" id="f-months"></div></div>
    </aside>
  </div>
</div>
<footer class="wrap foot">
  __CLUB_FOOTER__
  <span>Los titulares pertenecen a sus medios; cada uno enlaza a la noticia original.</span>
  __KOFI_FOOT__
  __TG_FOOT__
  __PREF_SOURCE__
  <a href="__ROOT__sobre">Sobre esta web</a>
  <a href="__ROOT__privacidad">Privacidad</a>
  <a href="__ROOT__cookies.html">Política de cookies</a>
  __COOKIE_BUTTON__
</footer>
__ANALYTICS__
<script>
// Contador de visitas: suma una vez por visitante y día (refrescar o cambiar de pestaña no cuenta)
(function () {
  if (!__VISITS__ || location.protocol === "file:") return;
  var KEY = "visita-contada", today = new Date().toISOString().slice(0, 10), last = null;
  try { last = localStorage.getItem(KEY); } catch (e) {}
  var count = last !== today;
  fetch("/api/visitas", { method: count ? "POST" : "GET" })
    .then(function (r) { if (!r.ok) throw r; return r.json(); })
    .then(function (d) {
      if (count) { try { localStorage.setItem(KEY, today); } catch (e) {} }
      var box = document.getElementById("visits");
      if (!box || typeof d.total !== "number") return;
      box.textContent = "";
      var b = document.createElement("b"); b.textContent = d.total.toLocaleString("es-ES");
      box.append(b, d.total === 1 ? " visita" : " visitas");
      box.hidden = false;
    })
    .catch(function () {});   // si el contador no responde, simplemente no se muestra
})();
</script>
<script id="d-rumors" type="application/json">__RUMORS__</script>
__NEWSTAG__
<script id="d-archive" type="application/json">__ARCHIVE__</script>
<script id="d-leagues" type="application/json">__LEAGUES__</script>
<script id="d-players" type="application/json">__PLAYERS__</script>
<script id="d-standings" type="application/json">__STANDINGS__</script>
<script id="d-domains" type="application/json">__DOMAINS__</script>
<script>const RECENT_DAYS = __RECENT_DAYS__; const TG_URL = "__TG_URL__"; const TAB_ICONS = __TAB_ICONS__;</script>
<script>
const rumors = JSON.parse(document.getElementById("d-rumors").textContent);
const DOMAINS = JSON.parse(document.getElementById("d-domains").textContent);
const news = window.__NEWS || JSON.parse(document.getElementById("d-news").textContent);
const archive = JSON.parse(document.getElementById("d-archive").textContent);
const IS_ARCHIVE = __IS_ARCHIVE__;
const PAGE = "__PAGE__";                 // news | rumors | table | fantasy
const ROOT = "__ROOT__";                 // camino hasta la portada ("", "../", "../../")
const COUNTS = __COUNTS__;
const TABLE_LEAGUE = __TABLE_LEAGUE__;
const LEAGUE_SLUGS = __LEAGUE_SLUGS__;
const FX_REPORT = __FX_REPORT__;
const FX_PLAYERS = __FX_PLAYERS__;       // jugadores conocidos y sus formas de nombrarlos (solo en Fantasy)
const FX_IGNORE = __FX_IGNORE__;         // fragmentos de titulares que se ignoran (fantasy_ignorar.txt)
const CLUB_SLUGS = __CLUB_SLUGS__;       // clubes con página propia
const PLAYER_PAGES = new Set(__PLAYER_PAGES__);   // jugadores con página propia
const CLUB = __CLUB__;                   // en una página de club: su nombre
const CLUB_INTRO = __CLUB_INTRO__;       // párrafos propios del club (generados con reglas)
const CLUB_INFO = __CLUB_INFO__;         // posición en la tabla del club de esta página
const SITE_URL = "__SITE_URL__";
const PLANE_SVG = '__PLANE__';
const STATUS = {interes:"Interés", negociacion:"Negociación", acuerdo:"Acuerdo", oficial:"Oficial", descartado:"Descartado"};
const ORDER = ["interes", "negociacion", "acuerdo", "oficial"];
const list = document.getElementById("list"), q = document.getElementById("q"), sel = document.getElementById("club");

const LEAGUES = JSON.parse(document.getElementById("d-leagues").textContent);
function load(key, fallback) { try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch (e) { return fallback; } }
function save(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch (e) {} }
let league = load("liga", "");
const hidden = new Set(load("medios-ocultos", []));

function dirUrl(path) {   // carpeta -> su index.html cuando se abre el archivo sin servidor
  return location.protocol === "file:" ? path + "index.html" : (path || "./");
}
function pageUrl(id) {
  if (id === "rumors") return dirUrl(ROOT + "rumores/");
  if (id === "fantasy") return dirUrl(ROOT + "fantasy/");
  if (id === "hoy") return dirUrl(ROOT + "rumores-fichajes-hoy/");
  if (id === "table") return dirUrl(ROOT + "clasificacion/" + (LEAGUE_SLUGS[load("liga-tabla", "LaLiga")] || "laliga") + "/");
  return dirUrl(ROOT);
}
const tabs = [["news", "Noticias", COUNTS.news], ["rumors", "Rumores", COUNTS.rumors]];
if (!IS_ARCHIVE) tabs.push(["table", "Clasificación", null], ["fantasy", "Fantasy", null], ["hoy", "Hoy", null]);
let tab = PAGE;
const hashTab = (location.hash || "").slice(1);
if (IS_ARCHIVE) { if (["news", "rumors"].includes(hashTab)) tab = hashTab; }
else if (["news", "rumors", "table", "fantasy"].includes(hashTab) && hashTab !== PAGE) location.replace(pageUrl(hashTab));  // enlaces antiguos con #
let day = "";   // "" = recientes (portada) o todo el mes (archivo); si no, AAAA-MM-DD
const nav = document.getElementById("tabs");
nav.replaceChildren();   // quita las pestañas en HTML normal; aquí se rehacen con contadores
for (const [id, label, n] of tabs) {
  const b = el(IS_ARCHIVE ? "button" : "a", "tab"); b.dataset.tab = id; b.innerHTML = TAB_ICONS[id] || "";
  if (id === "table") b.append(el("span", "lg-only", label), el("span", "sm-only", "Tabla"));
  else b.append(label);
  if (n !== null) b.append(el("span", "n", String(n)));
  if (IS_ARCHIVE) b.addEventListener("click", () => { tab = id; history.replaceState(null, "", "#" + id); render(); });
  else { b.href = pageUrl(id); if (id === PAGE) b.setAttribute("aria-current", "page"); }
  nav.append(b);
}
const clubs = [...new Set(rumors.flatMap(r => r.clubs || [r.from_club, r.to_club]).concat(news.flatMap(n => n.clubs)).filter(Boolean))].sort();
for (const c of clubs) sel.add(new Option(c, c));
if (PAGE === "club") {   // en una página de club: todos los clubes con página, y el actual seleccionado
  sel.replaceChildren(new Option("Todos los clubes", ""));
  for (const c of Object.keys(CLUB_SLUGS).sort()) sel.add(new Option(c, c));
  sel.value = CLUB;
}

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
    img.src = "https://www.google.com/s2/favicons?sz=64&domain=" + (DOMAINS[name] || new URL(url).hostname);
    img.onerror = () => { box.replaceChildren(initials); };
    box.append(img);
  } catch (e) { box.textContent = initials; }
  return box;
}
// Filtros de ligas y medios
const fLeagues = document.getElementById("f-leagues"), fSources = document.getElementById("f-sources");
const present = new Set(news.flatMap(n => n.leagues).concat(rumors.flatMap(r => r.leagues)));
const MAIN_CHIPS = 4;                       // en móvil, los principales; el resto, tras "Más"
const SHORT_LEAGUE = {"Premier League": "Premier"};      // solo en móvil
const NAME_LEAGUE = {"Champions League": "Champions", "Europa League": "Europa", "Otras ligas": "Otras"};
const extras = el("span", "extras");
[""].concat(LEAGUES.filter(l => present.has(l))).forEach((lg, i) => {
  const b = el("button", "chip"); b.type = "button";
  const full = NAME_LEAGUE[lg] || lg || "Todas";
  if (SHORT_LEAGUE[lg]) b.append(el("span", "nm lg-only", full), el("span", "nm sm-only", SHORT_LEAGUE[lg]));
  else b.append(el("span", "nm", full));
  if (!lg) b.append(el("span", "cnt"));   // el contador, solo en "Todas"
  b.addEventListener("click", () => { league = lg; save("liga", league); render(); });
  b.dataset.league = lg; (i < MAIN_CHIPS ? fLeagues : extras).append(b);
});
if (extras.children.length) {
  const more = el("button", "chip more"); more.type = "button"; more.setAttribute("aria-expanded", "false");
  more.append(el("span", "nm", "Más"), el("span", "chev"));
  more.addEventListener("click", e => { e.stopPropagation(); more.setAttribute("aria-expanded", String(fLeagues.classList.toggle("open"))); });
  fLeagues.append(more, extras);
  document.addEventListener("click", e => { if (!fLeagues.contains(e.target)) { fLeagues.classList.remove("open"); more.setAttribute("aria-expanded", "false"); } });
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
  const pool = tab === "rumors" ? rumors.filter(r => rumorDayOk(r) && r.mentions.some(m => !hidden.has(m.source)))
                                : news.filter(n => !hidden.has(n.source) && dayOk(n.date));
  for (const b of fLeagues.querySelectorAll("button[data-league]")) {
    b.setAttribute("aria-pressed", String(b.dataset.league === league));
    const lg = b.dataset.league;
    if (!lg) b.querySelector(".cnt").textContent = pool.length;
  }
  const moreBtn = fLeagues.querySelector(".more");
  if (moreBtn) {   // si la liga elegida está en "Más", el botón la muestra
    const act = extras.querySelector('[aria-pressed="true"]');
    moreBtn.setAttribute("aria-pressed", String(!!act));
    moreBtn.querySelector(".nm").textContent = act ? act.dataset.league : "Más";
    fLeagues.classList.remove("open"); moreBtn.setAttribute("aria-expanded", "false");
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
function rumorDayOk(r) { return !day || r.mentions.some(m => dkey(m.date) === day); }
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

function clubLink(name, cls) {
  const slug = CLUB_SLUGS[name];
  if (!slug) return el("span", cls, name);
  const a = el("a", cls, name); a.href = dirUrl(ROOT + "club/" + slug + "/");
  return a;
}
function shareBtn(text, url, iconOnly) {
  const b = el("button", "share" + (iconOnly ? " ico" : "")); b.type = "button"; b.title = "Compartir por WhatsApp u otra aplicación";
  if (iconOnly) b.setAttribute("aria-label", "Compartir");
  b.innerHTML = '<svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true"><path fill="currentColor" d="M18 16a3 3 0 0 0-2.4 1.2l-6.7-3.4a3 3 0 0 0 0-1.6l6.7-3.4A3 3 0 1 0 15 7l-6.7 3.4a3 3 0 1 0 0 3.2L15 17a3 3 0 1 0 3-1z"/></svg>';
  if (!iconOnly) b.append(" Compartir");
  b.addEventListener("click", async () => {
    if (navigator.share) {
      try { await navigator.share({text, url}); return; } catch (e) { if (e.name === "AbortError") return; }
    }
    window.open("https://wa.me/?text=" + encodeURIComponent(text + " " + url), "_blank", "noopener");
  });
  return b;
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


// ---------- Lo más leído: se cuenta un clic por noticia, visitante y día ----------
const CAN_COUNT = location.protocol !== "file:";
const byUrl = new Map();
for (const n of news) byUrl.set(n.url, n);
for (const r of rumors) for (const m of r.mentions) if (!byUrl.has(m.url)) byUrl.set(m.url, {title:m.title, url:m.url, source:m.source, date:m.date});
document.addEventListener("click", trackClick, true);
document.addEventListener("auxclick", trackClick, true);   // clic con la rueda (abrir en pestaña nueva)
function trackClick(e) {
  const a = e.target.closest && e.target.closest("a[href]");
  if (!a || !CAN_COUNT || !byUrl.has(a.href)) return;
  const key = "clics-" + new Date().toISOString().slice(0, 10);
  let done = [];
  try {
    done = JSON.parse(localStorage.getItem(key) || "[]");
    for (let i = localStorage.length - 1; i >= 0; i--) {     // limpia los días anteriores
      const k = localStorage.key(i);
      if (k && k.startsWith("clics-") && k !== key) localStorage.removeItem(k);
    }
  } catch (err) {}
  if (done.includes(a.href)) return;
  const body = JSON.stringify({url: a.href});
  const sent = navigator.sendBeacon && navigator.sendBeacon("/api/clics", new Blob([body], {type: "text/plain"}));
  if (!sent) fetch("/api/clics", {method: "POST", body, keepalive: true}).catch(() => {});
  done.push(a.href);
  try { localStorage.setItem(key, JSON.stringify(done.slice(-300))); } catch (err) {}
}

let readRange = load("leido-rango", 24);
const readCache = {};
function loadTopRead(h) {
  if (!CAN_COUNT || readCache[h] !== undefined) return;
  readCache[h] = null;                                        // pidiendo...
  fetch("/api/clics?horas=" + h).then(r => r.ok ? r.json() : {top: []})
    .then(d => { readCache[h] = (d.top || []).map(t => byUrl.get(t.url)).filter(Boolean).slice(0, 3); })
    .catch(() => { readCache[h] = []; })
    .then(() => { if (tab === "news") render(); });
}
function sideRead() {
  const box = document.getElementById("side-read"); box.replaceChildren();
  loadTopRead(readRange);
  const items = readCache[readRange];
  if (!CAN_COUNT || !items || !items.length) return;
  const hd = el("div", "hd"); hd.append(el("h2", "flabel", "Lo más leído"));
  const seg = el("div", "seg");
  for (const [h, label] of [[24, "24 h"], [168, "7 días"]]) {
    const b = el("button", null, label); b.setAttribute("aria-pressed", String(h === readRange));
    b.addEventListener("click", () => { readRange = h; save("leido-rango", h); render(); }); seg.append(b);
  }
  hd.append(seg); box.append(hd);
  const ol = el("ol");
  for (const n of items) {
    const li = el("li"), body = el("div"), a = el("a", null, n.title);
    a.href = n.url; a.target = "_blank"; a.rel = "noopener"; a.title = n.title;
    const s = el("div", "src-n"); s.append(outlet(n.url, n.source, true), el("span", null, n.source));
    body.append(a, s); li.append(body); ol.append(li);
  }
  box.append(ol);
}
function topReadBox() {
  loadTopRead(readRange);
  const items = readCache[readRange];
  if (!CAN_COUNT || (items && !items.length && readRange === 24 && readCache[168] && !readCache[168].length)) return null;
  const box = el("section", "top-read"), hd = el("div", "hd");
  hd.append(el("h2", null, "Lo más leído"));
  const seg = el("div", "seg");
  for (const [h, label] of [[24, "24 horas"], [168, "7 días"]]) {
    const b = el("button", null, label);
    b.setAttribute("aria-pressed", String(h === readRange));
    b.addEventListener("click", () => { readRange = h; save("leido-rango", h); render(); });
    seg.append(b);
  }
  hd.append(seg); box.append(hd);
  if (!items) { box.append(el("p", "none", "Cargando…")); return box; }
  if (!items.length) { box.append(el("p", "none", readRange === 24 ? "Todavía no hay lecturas en las últimas 24 horas." : "Todavía no hay lecturas esta semana.")); return box; }
  const ol = el("ol");
  for (const n of items) {
    const li = el("li"), body = el("div"), a = el("a", null, n.title);
    a.href = n.url; a.target = "_blank"; a.rel = "noopener";
    const meta = el("div", "meta");
    meta.append(outlet(n.url, n.source, true), el("span", null, n.source), el("span", "time", dayLabel(n.date) + ", " + hhmm(n.date)));
    body.append(a, meta); li.append(body); ol.append(li);
  }
  box.append(ol);
  return box;
}
if (CAN_COUNT) { loadTopRead(24); loadTopRead(168); }

const SLOTS = [[0, 7, "Madrugada"], [7, 10, "Mañana"], [10, 13, "Mañana"], [13, 16, "Mediodía"],
               [16, 19, "Tarde"], [19, 22, "Noche"], [22, 24, "Noche"]];
function slotOf(iso) { const h = new Date(iso).getHours(); return SLOTS.findIndex(s => h >= s[0] && h < s[1]); }
function two(n) { return String(n).padStart(2, "0") + ":00"; }

(function () {
  const fb = document.getElementById("fbtn"), fl = document.getElementById("filters");
  if (fb && fl) fb.addEventListener("click", () => { const o = fl.classList.toggle("open"); fb.setAttribute("aria-expanded", o); });
})();

function newsItem(n) {
  const li = el("li"), body = el("div", "bd"), a = el("a", "t", n.title);
  a.href = n.url; a.target = "_blank"; a.rel = "noopener";
  const meta = el("div", "meta"), by = el("span", "by");
  by.append(outlet(n.url, n.source, true), n.source);
  meta.append(by);
  if (n.live) meta.append(el("span", "tag live", "En directo"));
  if (n.rumor) meta.append(el("span", "tag rum", "Rumor"));
  for (const c of n.clubs) meta.append(clubLink(c, "club"));
  meta.append(shareBtn("📰 " + n.title + " (" + n.source + ")\n" + n.url + "\n\nMás noticias y rumores en", SITE_URL + "/", true));
  body.append(a, meta); li.append(el("span", "tm", hhmm(n.date)), body);
  return li;
}

function renderNews(text, club) {
  const shown = news.filter(n => dayOk(n.date) && (!club || n.clubs.includes(club)) && (!league || n.leagues.includes(league)) &&
                                 !hidden.has(n.source) && match(text, n.title, n.source, ...n.clubs));
  if (!shown.length) { list.append(el("p", "empty", "No hay noticias con ese filtro. Prueba con otro club o borra la búsqueda.")); return; }
  // Día -> franja -> noticias (ya vienen de la más reciente a la más antigua)
  const days = [];
  for (const n of shown) {
    const label = dayLabel(n.date), s = slotOf(n.date);
    let d = days[days.length - 1];
    if (!d || d.label !== label) { d = {label, key: dkey(n.date), slots: []}; days.push(d); }
    let sl = d.slots[d.slots.length - 1];
    if (!sl || sl.idx !== s) { sl = {idx: s, items: []}; d.slots.push(sl); }
    sl.items.push(n);
  }
  // Con un filtro activo hay pocas noticias: se abre todo. Si no, solo la franja más reciente.
  // Con búsqueda, club o liga hay pocas noticias: se abre todo (ocultar medios no cuenta como filtro)
  const filtered = !!(text || club || league);
  // Si no, solo la franja horaria actual y la anterior (si la actual es la madrugada, la anterior es ayer 22-24)
  const now = new Date(), todayKey = dkey(now.toISOString()), cur = slotOf(now.toISOString());
  const y = new Date(now); y.setDate(now.getDate() - 1);
  const yesterdayKey = dkey(y.toISOString());
  const isRecentSlot = (dayKey, idx) => (dayKey === todayKey && (idx === cur || idx === cur - 1)) ||
                                        (cur === 0 && dayKey === yesterdayKey && idx === SLOTS.length - 1);
  const anyRecent = !day && days.some(d => d.slots.some(sl => isRecentSlot(d.key, sl.idx)));
  sideRead();
  if (!filtered && !day && !IS_ARCHIVE) { const tr = topReadBox(); if (tr) list.append(tr); }
  let first = true;
  for (const d of days) {
    list.append(el("h2", "day", d.label));
    for (const sl of d.slots) {
      const [from, to, name] = SLOTS[sl.idx];
      const det = el("details", "slot");
      // Abiertas: franja actual y anterior; si no hay noticias en ellas (o eliges un día), la más reciente
      det.open = filtered || (anyRecent ? isRecentSlot(d.key, sl.idx) : first); first = false;
      const sum = el("summary");
      sum.append(el("span", "hrs", two(from) + " – " + two(to)), el("span", "lbl", name),
                 el("span", "cnt", sl.items.length + (sl.items.length === 1 ? " noticia" : " noticias")),
                 el("span", "chev"));
      const ul = el("ul", "news");
      for (const n of sl.items) ul.append(newsItem(n));
      det.append(sum, ul);
      list.append(det);
    }
  }
}

function bestStatus(r) {
  const statuses = r.mentions.map(m => m.status);
  return statuses.includes("oficial") ? "oficial" :
    (statuses.filter(s => ORDER.includes(s)).sort((a, b) => ORDER.indexOf(b) - ORDER.indexOf(a))[0] || statuses[0]);
}

// Votos de los lectores ("¿se hará el fichaje?"): un solo envío para todas las fichas con página de jugador
let votesPromise = null;
function loadVotes() {
  if (!votesPromise) {
    const slugs = [...PLAYER_PAGES].slice(0, 60);
    votesPromise = slugs.length
      ? fetch("/api/votos?rumores=" + slugs.join(",")).then(r => r.ok ? r.json() : null).catch(() => null)
      : Promise.resolve(null);
  }
  return votesPromise;
}
function myVote(slug) { try { return localStorage.getItem("voto-" + slug); } catch (e) { return null; } }
function voteRow(r) {
  const slug = r.player_slug;
  if (!PLAYER_PAGES.has(slug)) return null;
  const box = el("div", "vote-row"); box.hidden = true;
  let counts = {si: 0, no: 0};
  function paint() {
    box.replaceChildren();
    const mine = myVote(slug), n = counts.si + counts.no;
    if (!mine) {
      box.append(el("span", null, "¿Se hará el fichaje?"));
      for (const [v, label] of [["si", "Sí"], ["no", "No"]]) {
        const b = el("button", null, label); b.type = "button";
        b.addEventListener("click", () => {
          fetch("/api/votos", {method: "POST", body: JSON.stringify({rumor: slug, v})}).then(res => {
            if (!res.ok) return;
            try { localStorage.setItem("voto-" + slug, v); } catch (e) {}
            counts[v]++; paint();
          }).catch(() => {});
        });
        box.append(b);
      }
      return;
    }
    box.append(el("span", null, "Tu voto: " + (mine === "si" ? "sí" : "no")));
    if (n >= 5) {
      const pc = Math.round(counts.si * 100 / n), bar = el("span", "vbar"), fill = el("i");
      fill.style.width = pc + "%"; bar.append(fill);
      box.append(bar, el("span", null, pc + "% cree que sí (" + n + " votos)"));
    } else box.append(el("span", null, "· gracias, aún hay pocos votos"));
  }
  loadVotes().then(all => {
    if (!all) return;                     // sin base de datos: no se muestra nada
    counts = all[slug] || counts; box.hidden = false; paint();
  });
  return box;
}

function rumorCard(r) {
  const card = el("article", "rumor"), left = el("div");
  const hp = el("h3", "player");
  if (PLAYER_PAGES.has(r.player_slug)) { const pa = el("a", null, r.player); pa.href = ROOT + "jugador/" + r.player_slug + "/"; hp.append(pa); }
  else hp.textContent = r.player;
  left.append(hp);
  const route = el("p", "route");
  route.append(r.from_club ? clubLink(r.from_club) : el("span", "unk", "Origen sin confirmar"),
               el("span", "arrow", "→"),
               r.to_club ? clubLink(r.to_club) : el("span", "unk", "Destino sin confirmar"));
  left.append(route);
  if (r.others && r.others.length) {
    const also = el("p", "also");
    also.append("También: ");
    r.others.forEach((o, i) => {
      if (i) also.append(" · ");
      also.append(clubLink(o.to_club), " ", el("span", "status-mini st-" + o.status, STATUS[o.status] || o.status));
    });
    left.append(also);
  }
  const row = el("div", "row"), best = bestStatus(r);
  const lab = best === "oficial" || r.score >= 100 ? "Oficial" : r.score >= 40 ? "Probable" : "Rumor";
  row.append(el("span", "status st-" + best, STATUS[best] || best), el("span", "rlab rl-" + lab.toLowerCase(), lab));
  const outlets = el("span", "outlets"), seen = new Set();
  for (const m of r.mentions) if (!seen.has(m.source)) { seen.add(m.source); outlets.append(outlet(m.url, m.source, true)); }
  row.append(outlets);
  const fee = r.mentions.map(m => m.fee).find(f => f);
  if (fee) row.append(el("span", "fee", fee + " millones"));
  const shareText = (best === "oficial" ? "✅ Fichaje cerrado: " : "🔥 Rumor: ") + r.player + ", " +
    (r.from_club || "?") + " → " + (r.to_club || "?") + (best === "oficial" ? "" : " (" + r.score + "° en el termómetro)");
  row.append(shareBtn(shareText, SITE_URL + "/rumores/"));
  left.append(row);
  const vr = voteRow(r); if (vr) left.append(vr);

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
  return card;
}

function renderRumors(text, club) {
  const shown = rumors.filter(r => (!club || (r.clubs || [r.from_club, r.to_club]).includes(club)) &&
                                   (!league || r.leagues.includes(league)) && rumorDayOk(r) &&
                                   r.mentions.some(m => !hidden.has(m.source)) &&
                                   match(text, r.player, ...(r.clubs || [r.from_club, r.to_club]), ...r.mentions.map(m => m.source)));
  if (!shown.length) {
    list.append(el("p", "empty", rumors.length ? "Ningún rumor coincide con ese filtro."
      : "Ahora mismo no hay rumores de fichajes. Con el mercado cerrado es normal; en enero y en verano aparecerán aquí."));
    return;
  }
  if (PAGE === "rumors" && !text && !club && !league && !day) {
    const promo = el("aside", "promo"), p = el("p");
    if (TG_URL) {
      p.append(el("b", null, "Recibe los rumores calientes al momento"), " en nuestro canal de Telegram. ");
    }
    p.append("¿Uno te interesa? Compártelo por WhatsApp con el botón ", el("b", null, "Compartir"), " de cada rumor.");
    promo.append(p);
    if (TG_URL) {
      const a = el("a", "join"); a.href = TG_URL; a.target = "_blank"; a.rel = "noopener";
      a.innerHTML = PLANE_SVG; a.append(" Unirme al canal"); promo.append(a);
    }
    list.append(promo);
  }
  // Primero los fichajes ya cerrados, luego los rumores por termómetro
  const closed = shown.filter(r => bestStatus(r) === "oficial"), open = shown.filter(r => bestStatus(r) !== "oficial");
  for (const [rows, title] of [[closed, "Fichajes cerrados"], [open, closed.length ? "Rumores" : null]]) {
    if (!rows.length) continue;
    if (title) { const h = el("h2", "sec-h", title); h.append(el("small", null, String(rows.length))); list.append(h); }
    const grid = el("div", "rumors");
    for (const r of rows) grid.append(rumorCard(r));
    list.append(grid);
  }
}

function renderClub(text) {
  const box = el("section", "club-box");
  box.append(el("h2", null, "Fichajes, rumores y noticias del " + CLUB));
  if (CLUB_INFO) {
    const p = el("p");
    p.append("Va " + CLUB_INFO.pos + "º en ", (() => { const a = el("a", null, CLUB_INFO.league);
      a.href = dirUrl(ROOT + "clasificacion/" + LEAGUE_SLUGS[CLUB_INFO.league] + "/"); return a; })(),
      " con " + CLUB_INFO.points + " puntos en " + CLUB_INFO.played + " partidos.");
    box.append(p);
  }
  for (const t of CLUB_INTRO) box.append(el("p", null, t));
  list.append(box);
  if (rumors.length) renderRumors(text, "");
  list.append(el("h2", "sec-h", "Noticias del " + CLUB));
  renderNews(text, "");
}

// ---------- Fantasy: parte médico de tus titulares a partir de los titulares ----------
const PLAYERS = JSON.parse(document.getElementById("d-players").textContent);
const FX_KEY = "fantasy-equipo";
let team = load(FX_KEY, []);
const FXW = __FX_WORDS__, FXR = FXW.rules;
const FX_LABELS = {back:"Recuperado", susp:"Baja por sanción", out:"Baja", doubt:"Duda", ok:"Disponible"};
const FX_PRIORITY = ["back", "susp", "out", "doubt", "ok"];
const FX_PHRASES = [];
for (const cat of ["back", "susp", "out", "doubt", "ok"]) for (const w of FXW[cat]) FX_PHRASES.push([w.split(" "), cat]);
FX_PHRASES.sort((a, b) => b[0].length - a[0].length);

function nrm(s) { return s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim(); }
function fxSpans(toks, phrases) {          // todas las apariciones [inicio, fin, dato] de cada frase
  const out = [];
  for (const [p, data] of phrases) {
    const n = p.length;
    for (let i = 0; i + n <= toks.length; i++) {
      let ok = true;
      for (let j = 0; j < n; j++) if (toks[i + j] !== p[j]) { ok = false; break; }
      if (ok) out.push([i, i + n, data]);
    }
  }
  return out;
}
function fxNegated(toks, s, e) {
  if (s >= 1 && FXR.neg_adjacent.includes(toks[s - 1])) return true;
  if (s >= 2 && FXR.neg_adjacent.includes(toks[s - 2]) && FXR.neg_fillers.includes(toks[s - 1])) return true;
  if (toks.slice(Math.max(0, s - 3), s).some(t => FXR.avoid.includes(t))) return true;
  return FXR.neg_after.includes(toks[e]);
}
function fxVictim(toks, s, e, ps, pe) {   // "sanción por los cabezazos a X", "X ante las tres bajas": no es de X
  if (e < ps && FXR.victim.includes(toks[ps - 1]) && toks.slice(e, ps - 1).some(t => FXR.cause.includes(t))) return true;
  return pe <= s && toks.slice(pe, s).some(t => FXR.apart.includes(t));
}
// Estado de cada jugador de `players` ({nombre: [formas]}) en un titular
function fxAnalyze(title, players) {
  const toks = nrm(title).split(" ").filter(Boolean);
  for (const idiom of FXR.idioms)
    for (const [s, e] of fxSpans(toks, [[idiom.split(" "), null]])) for (let i = s; i < e; i++) toks[i] = "_";
  const spans = [];
  for (const [name, keys] of Object.entries(players))
    for (const k of keys) for (const [s, e] of fxSpans(toks, [[k.split(" "), name]])) spans.push([s, e, name]);
  if (!spans.length) return {};
  spans.sort((a, b) => a[0] - b[0] || a[1] - b[1] || (a[2] < b[2] ? -1 : a[2] > b[2] ? 1 : 0));
  const group = []; let gid = 0;           // jugadores enumerados ("A, B y C") forman un grupo
  spans.forEach((sp, i) => {
    if (i && sp[0] - spans[i - 1][1] > 0) {
      const between = toks.slice(spans[i - 1][1], sp[0]);
      if (!(between.length === 1 && ["y", "e", "and"].includes(between[0]))) gid++;
    }
    group.push(gid);
  });
  const found = {};
  for (const [s, e, cat] of fxSpans(toks, FX_PHRASES)) {
    if (cat === "susp" && toks.some(t => FXR.fine.includes(t))) continue;
    const gaps = spans.map((sp, i) => [fxVictim(toks, s, e, sp[0], sp[1]) ? 99 : Math.max(sp[0] - e, s - sp[1], 0), group[i], sp[2], sp[1]]);
    const best = Math.min(...gaps.map(g => g[0]));
    if (best > FXR.window) continue;
    const neg = fxNegated(toks, s, e);
    const eff = !neg ? cat : (cat === "back" || cat === "ok" ? "doubt" : "ok");
    const winners = new Set(gaps.filter(g => g[0] === best).map(g => g[1]));
    const groupEnd = {};
    for (const g of gaps) if (winners.has(g[1])) groupEnd[g[1]] = Math.max(groupEnd[g[1]] || 0, g[3]);
    for (const g of gaps)
      if ((winners.has(g[1]) && s >= groupEnd[g[1]]) || g[0] === best) (found[g[2]] = found[g[2]] || new Set()).add(eff);
  }
  const out = {};
  for (const [name, cats] of Object.entries(found)) out[name] = FX_PRIORITY.find(c => cats.has(c));
  return out;
}
// Lo que el usuario escribe ("Lamine") se asocia al jugador conocido si es una coincidencia clara
function fxResolve(name) {
  const k = nrm(name);
  let hit = Object.keys(FX_PLAYERS).find(full => nrm(full) === k || FX_PLAYERS[full].includes(k));
  if (!hit) {
    const t = k.split(" "), m = Object.keys(FX_PLAYERS).filter(full => { const ft = nrm(full).split(" "); return t.every(x => ft.includes(x)); });
    if (m.length === 1) hit = m[0];
  }
  if (hit) return {name: hit, keys: FX_PLAYERS[hit]};
  const keys = new Set([k]), parts = k.split(" ");
  if (parts.length > 1 && parts[parts.length - 1].length >= 4) keys.add(parts[parts.length - 1]);
  return {name, keys: [...keys].filter(x => x.length >= 3)};
}
function fxStatus(name) {
  const me = fxResolve(name), players = {...FX_PLAYERS, [me.name]: me.keys};
  const ign = FX_IGNORE.map(nrm).filter(Boolean);
  const hits = news.filter(n => { const t = nrm(n.title); return !ign.some(i => t.includes(i)); })
                   .sort((a, b) => b.date.localeCompare(a.date));
  const now = Date.now();
  let appears = 0;
  for (const h of hits) {   // manda el titular más reciente que hable de su estado y siga vigente
    const toks = nrm(h.title).split(" ");
    if (fxSpans(toks, me.keys.map(k => [k.split(" "), 1])).length) appears++;
    const st = fxAnalyze(h.title, players)[me.name];
    if (!st) continue;
    const age = (now - new Date(h.date).getTime()) / 86400000;
    if (age > FXR.stale[st]) {
      if (st !== "susp") continue;     // aviso caducado: se mira el siguiente más antiguo
      return {st: "doubt", label: "Sanción de hace " + Math.floor(age) + " días: comprueba si sigue", item: h};
    }
    if (st === "ok") return {st: "back", label: "Disponible", item: h};
    return {st: st === "susp" ? "out" : st, label: FX_LABELS[st], item: h};
  }
  return {st: "none", label: "Sin noticias de baja", item: null, count: appears};
}
function saveTeam() { save(FX_KEY, team); }

function renderFxReport() {
  if (!FX_REPORT.length) return;
  list.append(el("h2", "tb-h", "Parte médico de los últimos días"));
  list.append(el("p", "fx-intro", "Jugadores de la lista de la web y máximos goleadores de cada liga con noticias recientes de lesión, sanción, duda o recuperación."));
  for (const [st, title] of [["out", "Bajas"], ["doubt", "Dudas"], ["back", "Recuperados"]]) {
    const rows = FX_REPORT.filter(r => r.st === st);
    if (!rows.length) continue;
    list.append(el("h3", "fx-group", title + " (" + rows.length + ")"));
    const box = el("div", "fx-list");
    for (const r of rows) {
      const card = el("article", "fx " + r.st), h = el("h3", null, r.player);
      if (r.team) h.append(el("small", "fx-team", " " + r.team));
      const right = el("div"); right.append(el("span", "status st-" + r.st, r.label));
      const why = el("div", "why"), a = el("a", null, r.title);
      a.href = r.url; a.target = "_blank"; a.rel = "noopener";
      const meta = el("div", "meta");
      meta.append(outlet(r.url, r.source, true), el("span", null, r.source), el("span", "time", dayLabel(r.date) + ", " + hhmm(r.date)));
      meta.append(shareBtn((r.st === "back" ? "✅ " : "🚑 ") + r.player + ": " + r.label.toLowerCase() + ". " + r.title, SITE_URL + "/fantasy/"));
      why.append(a, meta); card.append(h, right, why); box.append(card);
    }
    list.append(box);
  }
}

function renderFantasy() {
  list.append(el("p", "fx-intro", "Escribe tu once separado por comas y te digo si hay noticias de lesión, sanción o duda en los titulares de los últimos " + __NEWS_DAYS__ + " días. Tu equipo se guarda solo en este dispositivo."));
  const form = el("form", "fx-add");
  const input = el("textarea"); input.rows = 2;
  input.placeholder = "Por ejemplo: Courtois, Carvajal, Cubarsí, Koundé, Lamine Yamal, Pedri, Mbappé…";
  input.setAttribute("aria-label", "Jugadores separados por comas");
  const add = el("button", null, team.length ? "Añadir" : "Añadir jugadores"); add.type = "submit";
  const replaceBtn = el("button", "fx-clear", "Sustituir mi equipo"); replaceBtn.type = "button";
  const btns = el("div", "fx-btns"); btns.append(add);
  if (team.length) btns.append(replaceBtn);
  form.append(input, btns);
  function names() {   // comas, punto y coma o saltos de línea; sin repetidos
    const seen = new Set(), out = [];
    for (const raw of input.value.split(/[,;\n]+/)) {
      const v = raw.trim().replace(/\s+/g, " ");
      if (v && !seen.has(nrm(v))) { seen.add(nrm(v)); out.push(v); }
    }
    return out;
  }
  form.addEventListener("submit", e => {
    e.preventDefault();
    for (const v of names()) if (!team.some(p => nrm(p) === nrm(v))) team.push(v);
    saveTeam(); render();
  });
  replaceBtn.addEventListener("click", () => {
    const list_ = names();
    if (!list_.length) { input.focus(); return; }
    team = list_; saveTeam(); render();
  });
  input.addEventListener("keydown", e => {   // Enter añade; Mayús+Enter hace salto de línea
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); form.requestSubmit(); }
  });
  list.append(form);
  if (!team.length) {
    list.append(el("p", "empty", "Todavía no has añadido jugadores."));
    renderFxReport();      // el parte médico general se ve aunque no tengas equipo
    return;
  }

  const results = team.map(p => [p, fxStatus(p)]);
  const order = {out:0, doubt:1, back:2, none:3};
  results.sort((a, b) => order[a[1].st] - order[b[1].st]);
  const sum = el("div", "fx-sum"), count = s => results.filter(r => r[1].st === s).length;
  if (count("out")) sum.append(el("span", "status st-out", count("out") + (count("out") === 1 ? " baja" : " bajas")));
  if (count("doubt")) sum.append(el("span", "status st-doubt", count("doubt") + (count("doubt") === 1 ? " duda" : " dudas")));
  sum.append(el("span", "status st-none", (count("back") + count("none")) + " sin problemas conocidos"));
  list.append(sum);

  const box = el("div", "fx-list");
  for (const [name, r] of results) {
    const card = el("article", "fx " + r.st);
    card.append(el("h3", null, name));
    const right = el("div");
    right.append(el("span", "status st-" + r.st, r.label));
    card.append(right);
    const why = el("div", "why");
    if (r.item) {
      const a = el("a", null, r.item.title); a.href = r.item.url; a.target = "_blank"; a.rel = "noopener";
      const meta = el("div", "meta");
      meta.append(outlet(r.item.url, r.item.source, true), el("span", null, r.item.source),
                  el("span", "time", dayLabel(r.item.date) + ", " + hhmm(r.item.date)));
      why.append(a, meta);
    } else {
      why.append(el("span", "meta", r.count ? "Aparece en " + r.count + " titular(es), ninguno con una baja vigente."
                                           : "No aparece en los titulares recientes."));
    }
    const rm = el("button", "rm", "Quitar");
    rm.addEventListener("click", () => { team = team.filter(p => p !== name); saveTeam(); render(); });
    why.append(rm);
    card.append(why);
    box.append(card);
  }
  list.append(box);
  const clear = el("button", "fx-clear", "Vaciar equipo");
  clear.style.marginTop = "14px";
  clear.addEventListener("click", () => { if (confirm("¿Quitar a todos los jugadores?")) { team = []; saveTeam(); render(); } });
  list.append(clear);
  renderFxReport();
  list.append(el("p", "fx-note", "Se basa en los titulares de prensa, así que \"Sin noticias de baja\" no garantiza que vaya a jugar: confirma siempre la convocatoria oficial antes de cerrar tu alineación."));
}

// ---------- Clasificación, goleadores y asistentes ----------
const STANDINGS = JSON.parse(document.getElementById("d-standings").textContent);
let tableLeague = TABLE_LEAGUE || load("liga-tabla", "LaLiga");
if (PAGE === "table" && TABLE_LEAGUE) save("liga-tabla", TABLE_LEAGUE);   // la pestaña recuerda la última liga vista
const FORM = {W:"G", D:"E", L:"P"};

function cell(tag, text, cls) { const c = el(tag, cls, text === null || text === undefined ? "" : String(text)); return c; }
function makeTable(headers, rows) {
  const wrap = el("div", "tb-wrap"), t = el("table", "tb"), thead = el("thead"), tr = el("tr");
  for (const [label, cls, title] of headers) { const th = cell("th", label, cls); if (title) th.title = title; tr.append(th); }
  thead.append(tr); t.append(thead);
  const tbody = el("tbody");
  for (const r of rows) tbody.append(r);
  t.append(tbody); wrap.append(t);
  return wrap;
}

function renderTable() {
  const leagues = Object.keys(STANDINGS);
  if (!leagues.length) {
    list.append(el("p", "empty", "La clasificación todavía no está disponible. Aparecerá en la próxima actualización."));
    return;
  }
  if (!leagues.includes(tableLeague)) tableLeague = leagues[0];
  const pick = el("div", "lg-pick");
  for (const lg of leagues) {
    const b = el("a", null, lg);
    b.href = dirUrl(ROOT + "clasificacion/" + LEAGUE_SLUGS[lg] + "/");
    b.setAttribute("aria-pressed", String(lg === tableLeague));
    if (lg === tableLeague) b.setAttribute("aria-current", "page");
    pick.append(b);
  }
  list.append(pick);
  const d = STANDINGS[tableLeague];

  // Clasificación
  const h = el("h2", "tb-h", "Clasificación de " + tableLeague);
  if (d.matchday) h.append(el("small", null, "Jornada " + d.matchday));
  list.append(h);
  const rows = d.table.map(t => {
    const tr = el("tr");
    tr.append(cell("td", t.pos, "pos"), cell("td", t.team, "l team"), cell("td", t.played),
              cell("td", t.won, "hide-sm"), cell("td", t.draw, "hide-sm"), cell("td", t.lost, "hide-sm"),
              cell("td", t.gf, "hide-sm"), cell("td", t.ga, "hide-sm"),
              cell("td", (t.gd > 0 ? "+" : "") + t.gd), cell("td", t.points, "pts"));
    const f = el("td", "hide-sm"), box = el("span", "form");
    for (const r of (t.form || "").split(",").filter(Boolean).slice(-5)) {
      const i = el("i", r, FORM[r] || r); i.title = {W:"Ganado", D:"Empatado", L:"Perdido"}[r] || r; box.append(i);
    }
    f.append(box); tr.append(f);
    return tr;
  });
  const hasForm = d.table.some(t => t.form);
  if (!hasForm) for (const r of rows) r.lastChild.remove();   // sin datos de racha: fuera la columna
  const headers = [["#", "l"], ["Equipo", "l"], ["PJ", "", "Partidos jugados"], ["G", "hide-sm", "Ganados"],
    ["E", "hide-sm", "Empatados"], ["P", "hide-sm", "Perdidos"], ["GF", "hide-sm", "Goles a favor"],
    ["GC", "hide-sm", "Goles en contra"], ["DG", "", "Diferencia de goles"], ["Pts", ""]];
  if (hasForm) headers.push(["Últimos 5", "hide-sm", "Del más antiguo (izquierda) al más reciente (derecha)"]);
  list.append(makeTable(headers, rows));

  // Goleadores y asistentes
  const two = el("div", "tb-two");
  const goals = [...d.scorers].sort((a, b) => b.goals - a.goals || a.played - b.played).slice(0, 20);
  const gBox = el("div");
  gBox.append(el("h2", "tb-h", "Goleadores"));
  gBox.append(makeTable([["#", "l"], ["Jugador", "l"], ["Goles", ""]], goals.map((s, i) => {
    const tr = el("tr"), who = el("td", "l");
    who.append(el("div", null, s.player), el("div", "sub", s.team));
    const g = cell("td", s.goals, "big");
    if (s.penalties) g.title = s.penalties + " de penalti";
    tr.append(cell("td", i + 1, "pos"), who, g);
    return tr;
  })));
  const assists = d.scorers.filter(s => s.assists > 0).sort((a, b) => b.assists - a.assists || b.goals - a.goals).slice(0, 20);
  const aBox = el("div");
  aBox.append(el("h2", "tb-h", "Asistentes"));
  if (assists.length) {
    aBox.append(makeTable([["#", "l"], ["Jugador", "l"], ["Asist.", ""]], assists.map((s, i) => {
      const tr = el("tr"), who = el("td", "l");
      who.append(el("div", null, s.player), el("div", "sub", s.team));
      tr.append(cell("td", i + 1, "pos"), who, cell("td", s.assists, "big"));
      return tr;
    })));
    aBox.append(el("p", "tb-note", "Calculado entre los máximos goleadores de la liga: no incluye a quien da asistencias sin haber marcado."));
  } else aBox.append(el("p", "empty", "Sin datos de asistencias todavía."));
  two.append(gBox, aBox);
  list.append(two);
  const upd = d.updated ? new Date(d.updated).toLocaleString("es-ES", {day:"numeric", month:"long", hour:"2-digit", minute:"2-digit"}) : "";
  const src = el("p", "tb-note", "Datos de football-data.org" + (upd ? ", actualizados el " + upd + "." : "."));
  list.append(src);
}

function render() {
  const text = q.value.trim().toLowerCase(), club = sel.value;
  for (const b of nav.children) b.classList.toggle("on", b.dataset.tab === tab);
  syncFilters(); syncDays();
  list.replaceChildren();
  const solo = tab === "fantasy" || tab === "table";
  document.querySelector(".layout").classList.toggle("solo", solo);
  fLeagues.hidden = solo;
  q.disabled = sel.disabled = solo;
  renderHero();
  if (tab === "fantasy") { renderFantasy(); return; }
  if (tab === "table") { renderTable(); return; }
  if (PAGE === "club") { renderClub(text); return; }
  if (tab === "news") renderNews(text, club);
  else renderRumors(text, club);
}
q.addEventListener("input", render);
sel.addEventListener("change", () => {
  if (PAGE === "club" && sel.value && CLUB_SLUGS[sel.value]) location.href = dirUrl(ROOT + "club/" + CLUB_SLUGS[sel.value] + "/");
  else render();
});

// "Actualizado hoy a las 17:57": el servidor da la hora de España; aquí se dice si fue hoy o ayer
(function () {
  const u = document.getElementById("updated"), d = u && new Date(u.dataset.iso);
  if (!d || isNaN(d)) return;
  const tz = {timeZone: "Europe/Madrid"}, ymd = x => x.toLocaleDateString("es-ES", tz);
  const t = new Date(), y = new Date(); y.setDate(t.getDate() - 1);
  const when = ymd(d) === ymd(t) ? "hoy" : ymd(d) === ymd(y) ? "ayer" : "el " + ymd(d);
  u.textContent = "Actualizado " + when + " a las " + d.toLocaleTimeString("es-ES", {...tz, hour: "2-digit", minute: "2-digit"});
})();

// Clubes en portada: los que más salen en las noticias recientes
(function () {
  const box = document.getElementById("clubs-box"), lst = document.getElementById("clubs-list"), cnt = {};
  for (const n of news) if (IS_ARCHIVE || new Date(n.date).getTime() >= recentFrom) for (const c of n.clubs) cnt[c] = (cnt[c] || 0) + 1;
  const top = Object.keys(cnt).sort((a, b) => cnt[b] - cnt[a] || (a < b ? -1 : 1)).slice(0, 8);
  for (const c of top) lst.append(clubLink(c, "cl-chip"));
  box.hidden = !top.length;
})();

// Portada: noticia destacada (la última "En directo" o, si no hay, el rumor mejor puntuado) y dos tarjetas
const heroBox = document.getElementById("hero");
const PITCH_SVG = '<svg class="pitch-art" viewBox="0 0 400 260" aria-hidden="true"><rect x="10" y="10" width="380" height="240" rx="4"/><path d="M200 10v240"/><circle cx="200" cy="130" r="42"/><rect x="10" y="70" width="60" height="120"/><rect x="330" y="70" width="60" height="120"/></svg>';
function heroLink(cls, href, external) {
  const a = el("a", cls); a.href = href;
  if (external) { a.target = "_blank"; a.rel = "noopener"; }
  return a;
}
function renderHero() {
  heroBox.replaceChildren(); heroBox.hidden = true;
  if (tab !== "news" || PAGE !== "news" || IS_ARCHIVE || day || league || sel.value || q.value.trim()) return;
  const live = news.find(n => n.live && !hidden.has(n.source) && Date.now() - new Date(n.date).getTime() < 12 * 3600000);
  const ranked = rumors.filter(r => r.mentions.some(m => !hidden.has(m.source))).sort((a, b) => b.score - a.score);
  const latest = r => r.mentions.filter(m => !hidden.has(m.source)).sort((a, b) => b.date.localeCompare(a.date))[0];
  let main = null, used = null;
  if (live) main = {title: live.title, url: live.url, source: live.source, date: live.date, live: true, clubs: live.clubs};
  else if (ranked.length) {
    used = ranked[0]; const m = latest(used);
    main = {title: m.title, url: m.url, source: m.source, date: m.date, live: false, clubs: [used.from_club, used.to_club].filter(Boolean)};
  }
  if (!main) return;
  const rest = ranked.filter(r => r !== used);
  const hot = rest.filter(r => bestStatus(r) !== "oficial"), closed = rest.filter(r => bestStatus(r) === "oficial");
  const cards = [hot[0], closed[0] || hot[1]].filter(Boolean);

  const a = heroLink("hero-main", main.url, true), inn = el("div", "hero-in"), tags = el("div", "hero-tags");
  a.innerHTML = PITCH_SVG;
  tags.append(el("span", main.live ? "badge-live" : "badge-rum", main.live ? "En directo" : "Rumor"),
              el("span", "hero-src", main.source + " · " + hhmm(main.date)));
  inn.append(tags, el("h2", null, main.title));
  if (main.clubs.length) { const cl = el("div", "hero-clubs"); for (const c of main.clubs.slice(0, 3)) cl.append(el("span", null, c)); inn.append(cl); }
  a.append(inn); heroBox.append(a);

  if (cards.length) {
    const side = el("div", "hero-side");
    for (const r of cards) {
      const m = latest(r), isClosed = bestStatus(r) === "oficial", cls = "hero-card" + (isClosed ? " fichaje" : "");
      const c = PLAYER_PAGES.has(r.player_slug) ? heroLink(cls, ROOT + "jugador/" + r.player_slug + "/", false) : heroLink(cls, m.url, true);
      const kick = isClosed ? "Fichaje cerrado" : "Rumor · " + (r.to_club || r.from_club || r.player) + " · " + r.score + "°";
      c.append(el("span", "kick", kick), el("h3", null, m.title), el("span", "by", m.source + " · " + hhmm(m.date)));
      side.append(c);
    }
    heroBox.append(side);
  }
  heroBox.classList.toggle("one", !cards.length);
  heroBox.hidden = false;
}

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


ANALYTICS = r"""<div class="cookies" id="cookies" hidden role="dialog" aria-label="Aviso de cookies">
  <p>Usamos cookies de Google Analytics para saber cuántas personas visitan la web y qué secciones se usan más. Solo se activan si las aceptas.</p>
  <div class="btns">
    <button class="yes" id="ck-yes">Aceptar</button>
    <button class="no" id="ck-no">Rechazar</button>
    <a href="__ROOT__cookies.html">Más información</a>
  </div>
</div>
<script>
(function () {
  var ID = "__GA_ID__", KEY = "cookies-analitica", bar = document.getElementById("cookies");
  function get() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function load() {
    if (window.gtag) return;
    var s = document.createElement("script");
    s.async = true; s.src = "https://www.googletagmanager.com/gtag/js?id=" + ID;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { dataLayer.push(arguments); };
    gtag("js", new Date()); gtag("config", ID);
  }
  function wipe() {   // borra las cookies de Analytics si se retira el consentimiento
    document.cookie.split(";").forEach(function (c) {
      var name = c.split("=")[0].trim();
      if (name.indexOf("_ga") === 0) {
        document.cookie = name + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/";
        document.cookie = name + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; domain=" + location.hostname;
      }
    });
  }
  function set(v) {
    try { localStorage.setItem(KEY, v); } catch (e) {}
    bar.hidden = true;
    if (v === "si") load(); else { wipe(); if (window.gtag) location.reload(); }
  }
  document.getElementById("ck-yes").onclick = function () { set("si"); };
  document.getElementById("ck-no").onclick = function () { set("no"); };
  var cfg = document.getElementById("ck-config");
  if (cfg) cfg.onclick = function () { bar.hidden = false; };
  var v = get();
  if (v === "si") load(); else if (!v) bar.hidden = false;
})();
</script>"""


def _label(score, status=None):
    """Etiqueta según el termómetro: Oficial (cerrado), Probable (≥40°) o Rumor."""
    return "Oficial" if status == "oficial" or score >= 100 else "Probable" if score >= 40 else "Rumor"


def _best_status(r):
    sts = {m["status"] for m in r["mentions"]}
    return next((x for x in ("oficial", "acuerdo", "negociacion", "interes") if x in sts), None)


def _sources_html(r, n=3):
    """Enlaces a las noticias originales de un rumor (un enlace por medio, hasta n)."""
    esc = html_lib.escape
    seen, out = set(), []
    for m in sorted(r["mentions"], key=lambda m: m["date"], reverse=True):
        if m["source"] not in seen and len(out) < n:
            seen.add(m["source"])
            out.append(f'<a href="{esc(m["url"], quote=True)}" target="_blank" rel="noopener nofollow">{esc(m["source"])}</a>')
    return ", ".join(out)


def _static_list(news, rumors, limit=60):
    """Titulares en HTML normal, para buscadores y para quien no ejecute JavaScript.
    Al cargar la página, el código la sustituye por la versión interactiva."""
    esc = html_lib.escape
    parts = []
    if rumors:
        parts.append("<h2>Rumores de fichajes</h2><ul>")
        for r in rumors[:20]:
            route = f"{r['from_club'] or 'origen sin confirmar'} → {r['to_club'] or 'destino sin confirmar'}"
            name = (f'<a href="/jugador/{esc(r["player_slug"], quote=True)}/">{esc(r["player"])}</a>'
                    if r.get("player_slug") in _PLAYER_PAGES else esc(r["player"]))
            parts.append(f"<li><b>{_label(r['score'], _best_status(r))}</b> · {name}: {esc(route)} "
                         f"({r['score']}°). Fuente: {_sources_html(r)}</li>")
        parts.append("</ul>")
    shown = list(news)[:limit]
    if shown:
        parts.append("<h2>Últimas noticias de fútbol</h2><ul>")
        for n in shown:
            parts.append(f'<li><a href="{esc(n["url"], quote=True)}">{esc(n["title"])}</a> ({esc(n["source"])})</li>')
        parts.append("</ul>")
    return "".join(parts)


def _domains():
    out = {}
    for f in config.FEEDS:
        if f.get("domain"):
            out.setdefault(f["source"], f["domain"])
    return out


def _standings():
    try:
        import standings
        data = standings.load()
        return {k: v for k, v in data.items() if not k.startswith("_")}
    except Exception:
        return {}


def _players():
    """Jugadores conocidos y sus otros nombres, para sugerirlos y reconocerlos en Fantasy."""
    try:
        import rules
        out = {}
        for alias, (name, _club) in rules.load_players():
            out.setdefault(name, []).append(alias)
        return out
    except Exception:
        return {}


_NEWS_FILES = set()    # archivos de noticias escritos en esta ejecución


def _news_tag(path, root, news, inline=False):
    """Las noticias (cientos de KB) van a un archivo externo con nombre por contenido: las páginas con la
    misma lista lo comparten y el navegador lo cachea. Las listas pequeñas (clubes) siguen en línea."""
    data = _json(news)
    if inline or len(data) < 30000:   # el archivo mensual no se regenera cada hora: va en línea
        return f'<script id="d-news" type="application/json">{data}</script>'
    import hashlib
    name = "n-" + hashlib.sha1(data.encode("utf-8")).hexdigest()[:10] + ".js"
    base = os.path.normpath(os.path.join(os.path.dirname(path), root))
    os.makedirs(os.path.join(base, "datos"), exist_ok=True)
    with open(os.path.join(base, "datos", name), "w", encoding="utf-8") as f:
        f.write("window.__NEWS=" + data + ";")
    _NEWS_FILES.add(name)
    return f'<script src="{root}datos/{name}"></script>'


def _write(path, *, title, heading, crumbs, rumors, news, archive, is_archive,
           description, canonical, root, tagline="", page="news", table_league=None,
           static_html=None, counts=None, fx_report=(), standings=None, club=None, club_info=None,
           fx_players=None, fx_ignore=(), club_intro=(), ld_page=()):
    esc = html_lib.escape
    verification = (f'<meta name="google-site-verification" content="{esc(config.GOOGLE_VERIFICATION, quote=True)}">'
                    if config.GOOGLE_VERIFICATION else "")
    ld = {"@context": "https://schema.org", "@type": "WebSite", "name": config.SITE_NAME,
          # Plan B de Google para subdominios: el subdominio en minúsculas como nombre alternativo
          "alternateName": ["RumoresyFichajes", config.SITE_URL.split("//", 1)[1].rstrip("/").lower()],
          "url": config.SITE_URL + "/", "inLanguage": "es-ES", "description": config.SITE_DESCRIPTION}
    if ld_page:
        ld = {"@context": "https://schema.org",
              "@graph": [{k: v for k, v in ld.items() if k != "@context"}] + list(ld_page)}
    now_es = _now_spain()
    html = (TEMPLATE
            .replace("__DESCRIPTION__", esc(description, quote=True))
            .replace("__CANONICAL__", esc(canonical, quote=True))
            .replace("__SITE_NAME__", esc(config.SITE_NAME, quote=True))
            .replace("__TAGLINE__", esc(tagline) + " " if tagline else "")
            .replace("__SITE_URL__", config.SITE_URL)
            .replace("__ROOT__", root)
            .replace("__VERIFICATION__", verification)
            .replace("__LDJSON__", _json(ld))
            .replace("__ADSENSE__", ADSENSE)
            .replace("__STATIC__", static_html if static_html is not None else _static_list(list(news), rumors))
            .replace("__ANALYTICS__", ANALYTICS.replace("__GA_ID__", config.GA_MEASUREMENT_ID)
                     if config.GA_MEASUREMENT_ID else "")
            .replace("__COOKIE_BUTTON__", '<button id="ck-config">Configurar cookies</button>'
                     if config.GA_MEASUREMENT_ID else "")
            .replace("__KOFI_TOP__", '<div class="kofi-top"><div class="top-btns">' + (
                         f'<a class="kofi tg" href="{esc(telegram_url(), quote=True)}" target="_blank" rel="noopener" '
                         f'aria-label="Síguenos en Telegram"><span>__PLANE__</span><span><span class="pre">Síguenos en </span>Telegram</span></a>'
                         if telegram_url() else "") + (
                         f'<a class="kofi" href="{esc(config.KOFI_URL, quote=True)}" target="_blank" rel="noopener">'
                         f'Invítame a un café</a>'
                         if config.KOFI_URL else "") + '</div><span class="visits" id="visits" hidden></span></div>')
            .replace("__PREF_SOURCE__", _pref_source_link())
            .replace("__TG_URL__", telegram_url())
            .replace("__TG_FOOT__", f'<a href="{esc(telegram_url(), quote=True)}" target="_blank" rel="noopener">'
                                    f'Canal de Telegram</a>' if telegram_url() else "")
            .replace("__KOFI_FOOT__", (f'<a class="kofi" href="{esc(config.KOFI_URL, quote=True)}" target="_blank" '
                                       f'rel="noopener"><span>☕</span><span>¿Te es útil? Invítame a un café en Ko-fi</span></a>') if config.KOFI_URL else "")
            .replace("__VISITS__", "true" if config.VISIT_COUNTER else "false")
            .replace("__PLANE__", PLANE_ICON)
            .replace("__TG_CARD__", (f'<div class="cta tgc"><h2>En tu móvil</h2><p>Los rumores nuevos llegan solos al canal de '
                                     f'Telegram.</p><a href="{esc(telegram_url(), quote=True)}" target="_blank" rel="noopener">'
                                     f'Unirme al canal</a></div>') if telegram_url() else "")
            .replace("__TAB_ICONS__", _json(TAB_ICONS))
            .replace("__ROOT__", root))
    html = (html
            .replace("__TITLE__", title).replace("__HEADING__", heading).replace("__CRUMBS__", crumbs)
            .replace("__UPDATED_ISO__", now_es.isoformat(timespec="minutes"))
            .replace("__UPDATED__", now_es.strftime("%d/%m/%Y a las %H:%M"))
            .replace("__IS_ARCHIVE__", "true" if is_archive else "false")
            .replace("__RUMORS__", _json(rumors)).replace("__NEWSTAG__", _news_tag(path, root, list(news), inline=is_archive))
            .replace("__ARCHIVE__", _json(archive)).replace("__LEAGUES__", _json(config.LEAGUES))
            .replace("__PLAYERS__", _json(_players()))
            .replace("__DOMAINS__", _json(_domains()))
            .replace("__STANDINGS__", _json(standings if standings is not None else ({} if is_archive else _standings())))
            .replace("__PAGE__", page)
            .replace("__TOOLS_HIDDEN__", " hidden" if page in ("table", "fantasy") else "")
            .replace("__NOTOOLS__", " notools" if page in ("table", "fantasy") else "")
            .replace("__COUNTS__", _json(counts or {"news": len(list(news)), "rumors": len(rumors)}))
            .replace("__TABLE_LEAGUE__", _json(table_league))
            .replace("__LEAGUE_SLUGS__", _json({lg: league_slug(lg) for lg in config.STANDINGS_COMPETITIONS}))
            .replace("__FX_REPORT__", _json(list(fx_report)))
            .replace("__FX_WORDS__", _json({**config.FANTASY_WORDS, "rules": config.FANTASY_RULES}))
            .replace("__FX_PLAYERS__", _json(fx_players or {}))
            .replace("__FX_IGNORE__", _json(list(fx_ignore)))
            .replace("__CLUB_SLUGS__", _json(_CLUB_PAGES))
            .replace("__PLAYER_PAGES__", _json(sorted(_PLAYER_PAGES)))
            .replace("__CLUB__", _json(club))
            .replace("__CLUB_INTRO__", _json(list(club_intro)))
            .replace("__CLUB_INFO__", _json(club_info))
            .replace("__CLUB_FOOTER__", _club_footer(root))
            .replace("__TABS__", _tabs_html(root, page, is_archive))
            .replace("__RECENT_DAYS__", str(config.RECENT_DAYS)).replace("__NEWS_DAYS__", str(config.NEWS_DAYS)))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return os.path.abspath(path)


ADSENSE = (f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={config.ADSENSE_CLIENT}" '
           'crossorigin="anonymous"></script>')   # solo verificación: aún no hay bloques de anuncio

PLANE_ICON = '<svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path fill="currentColor" d="M2.5 11.2 20.6 4.3c.8-.3 1.5.2 1.3 1.3l-3.1 14.5c-.2 1-.8 1.2-1.6.8l-4.6-3.4-2.2 2.1c-.3.3-.5.4-.9.4l.3-4.7 8.5-7.7c.4-.3-.1-.5-.6-.2L7.2 14.1l-4.5-1.4c-1-.3-1-1 .2-1.5z"/></svg>'

def _icon(*paths):
    return ('<svg class="ti" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" aria-hidden="true">' + "".join(paths) + '</svg>')


TAB_ICONS = {   # iconos de las pestañas (los mismos en el HTML estático y en las que crea el JS)
    "news": _icon('<path d="M4 5h13v14H6a2 2 0 0 1-2-2V5Zm13 4h3v8a2 2 0 0 1-2 2M8 9h5M8 13h5"/>'),
    "rumors": _icon('<path d="M7 17 17 7M9 7h8v8"/>'),
    "table": _icon('<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>'),
    "fantasy": _icon('<path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6l-8-3Z"/>', '<path d="m9 12 2 2 4-4"/>'),
    "hoy": _icon('<circle cx="12" cy="12" r="9"/>', '<path d="M12 7v5l3 2"/>'),
}

_CLUB_PAGES = {}     # {club: slug} de los clubes con página; se rellena en generate()


def telegram_url():
    """Enlace público al canal: config.TELEGRAM_URL, o el secreto TELEGRAM_CHAT_ID si es un @canal."""
    if getattr(config, "TELEGRAM_URL", ""):
        return config.TELEGRAM_URL
    chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    return f"https://t.me/{chat[1:]}" if chat.startswith("@") and len(chat) > 1 else ""


def _winter_year():
    """Año del próximo mercado de invierno (enero): el siguiente a partir de julio."""
    now = datetime.now()
    return now.year + 1 if now.month >= 7 else now.year


def _next_jornada(standings):
    """Jornada de LaLiga que se prepara en Fantasy: la API da la última jugada, así que es la siguiente."""
    md = (standings.get("LaLiga") or {}).get("matchday")
    return int(md) + 1 if md else None


def _fantasy_title(standings):
    md = _next_jornada(standings)
    return f"Lesionados y sancionados de la jornada {md} de LaLiga Fantasy" if md else \
        "Lesionados y sancionados para tu Fantasy"


def _tabs_html(root, page, is_archive):
    """Pestañas principales en HTML normal (buscadores y quien no ejecute JavaScript). El JS las sustituye
    por las interactivas. En el archivo las pestañas son botones, así que ahí no se pone nada."""
    if is_archive:
        return ""
    items = [("news", "Noticias", root or "./"), ("rumors", "Rumores", f"{root}rumores/"),
             ("table", '<span class="lg-only">Clasificación</span><span class="sm-only">Tabla</span>',
              f"{root}clasificacion/{league_slug('LaLiga')}/"),
             ("fantasy", "Fantasy", f"{root}fantasy/"), ("hoy", "Hoy", f"{root}rumores-fichajes-hoy/")]
    return "".join(f'<a class="tab{" on" if page == id_ else ""}" data-tab="{id_}" href="{href}"'
                   f'{" aria-current=" + chr(34) + "page" + chr(34) if page == id_ else ""}>{TAB_ICONS[id_]}{label}</a>'
                   for id_, label, href in items)


def _sections_footer(root):
    """Enlaces visibles a todas las secciones en el pie de cada página."""
    esc = html_lib.escape
    links = [("Noticias", root or "./"), ("Rumores de fichajes", f"{root}rumores/"),
             ("Rumores de fichajes de hoy", f"{root}rumores-fichajes-hoy/"),
             ("LaLiga Fantasy", f"{root}fantasy/")]
    links += [(f"Clasificación de {lg}", f"{root}clasificacion/{league_slug(lg)}/") for lg in config.STANDINGS_COMPETITIONS]
    links += [(f"Lesionados jornada {md}", f"{root}fantasy/jornada-{md}/") for md in _JORNADAS[:4]]
    if _PLAYER_PAGES:
        links += [("Últimos movimientos del mercado", f"{root}rumores/movimientos/"),
                  ("Jugadores con rumores de fichaje", f"{root}jugador/")]
    return (f'<details class="foot-clubs"><summary>Secciones ({len(links)})</summary>'
            '<nav aria-label="Secciones de la web">'
            + " ".join(f'<a href="{esc(h, quote=True)}">{esc(t)}</a>' for t, h in links) + "</nav></details>")


def _club_footer(root):
    """Enlaces a todas las páginas de club en el pie (ayudan a Google a encontrarlas)."""
    if not _CLUB_PAGES:
        return _sections_footer(root)
    links = " ".join(f'<a href="{root}club/{slug}/">{html_lib.escape(club)}</a>'
                    for club, slug in sorted(_CLUB_PAGES.items(), key=lambda x: x[0]))
    return (_sections_footer(root) + f'<details class="foot-clubs"><summary>Equipos ({len(_CLUB_PAGES)})</summary>'
            f'<nav aria-label="Páginas de cada equipo">{links}</nav></details>')


def _club_of_team(team):
    """Nombre de un equipo en la API (p. ej. "Barça", "Man United") -> nuestro nombre de club."""
    from pipeline import canonical_club, norm
    c = canonical_club(team)
    if c in config.CLUBS:
        return c
    t = f" {' '.join(norm(team).split())} "
    for club, aliases in config.CLUBS.items():
        if any(f" {' '.join(norm(a).split())} " in t for a in aliases if len(a) > 3):
            return club
    return None


def _club_info(standings):
    """{club: {league, pos, points, played}} a partir de las clasificaciones."""
    out = {}
    for lg, d in standings.items():
        for row in d.get("table", []):
            club = _club_of_team(row.get("team") or "")
            if club and club not in out:
                out[club] = {"league": lg, "pos": row["pos"], "points": row["points"], "played": row["played"]}
    return out


def _crumbs(root, *items):
    """Migas de pan: Rumores y Fichajes › ... › página actual (la última, sin enlace).
    items = (texto, ruta del sitio como "/clasificacion/laliga/" o None)."""
    esc = html_lib.escape
    parts = [f'<a href="{root}">{esc(config.SITE_NAME)}</a>']
    for text, path in items:
        parts.append('<span class="sep" aria-hidden="true">›</span>')
        parts.append(f'<a href="{esc(root + path.lstrip("/"), quote=True)}">{esc(text)}</a>' if path
                     else f"<span>{esc(text)}</span>")
    return '<nav class="crumbs" aria-label="Migas de pan">' + "".join(parts) + "</nav>"


def _iso_max(*values):
    """La fecha más reciente de varias (texto ISO), en formato W3C para sitemap y datos estructurados."""
    best = None
    for v in values:
        if not v:
            continue
        try:
            d = datetime.fromisoformat(str(v).replace("Z", "+00:00"))
        except ValueError:
            continue
        if d.tzinfo is None:
            d = d.replace(tzinfo=_now_spain().tzinfo)
        if best is None or d > best:
            best = d
    if best is None:
        return None
    from datetime import timezone
    return best.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")


def _page_ld(path, name, description, crumbs=(), modified=None, about=None):
    """Datos estructurados de una página: CollectionPage y, si no es la portada, BreadcrumbList
    (las mismas migas que se ven en la página). path = ruta del sitio, p. ej. "/club/fc-barcelona/"."""
    url = config.SITE_URL + path
    page = {"@type": "CollectionPage", "@id": url + "#pagina", "url": url, "name": name,
            "description": description, "inLanguage": "es-ES",
            "isPartOf": {"@type": "WebSite", "url": config.SITE_URL + "/"}}
    if modified:
        page["dateModified"] = modified
    out = [page]
    if about:
        team = {"@type": "SportsTeam", "@id": url + "#club", "name": about, "sport": "Fútbol", "url": url}
        page["about"] = {"@id": team["@id"]}
        out.append(team)
    if crumbs:
        items = [(config.SITE_NAME, "/")] + list(crumbs)
        out.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i, "name": text, "item": config.SITE_URL + (p or path)}
            for i, (text, p) in enumerate(items, 1)]})
    return out


def _item_list(rumors, url, limit=20):
    """ItemList de datos estructurados con los rumores más calientes (ficha propia si la tienen)."""
    items = []
    for i, r in enumerate(rumors[:limit], 1):
        href = (f"{config.SITE_URL}/jugador/{r['player_slug']}/" if r.get("player_slug") in _PLAYER_PAGES else url)
        items.append({"@type": "ListItem", "position": i, "url": href,
                      "name": f"{r['player']}: {r['from_club'] or '?'} → {r['to_club'] or '?'} ({r['score']}°)"})
    return {"@type": "ItemList", "@id": url + "#lista", "url": url, "numberOfItems": len(items),
            "itemListOrder": "https://schema.org/ItemListOrderDescending", "itemListElement": items}


def _hoy_page(rumors, out_dir):
    """/rumores-fichajes-hoy/: dirección estable, con la fecha de hoy visible; se regenera cada hora."""
    esc = html_lib.escape
    root = "../"
    now = _now_spain()
    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    fecha = f"{dias[now.weekday()]} {now.day} de {MONTHS[now.month - 1].lower()} de {now.year}"
    iso = now.isoformat(timespec="minutes")
    cerrados = [r for r in rumors if _label(r["score"], _best_status(r)) == "Oficial"]
    abiertos = [r for r in rumors if r not in cerrados]
    def li(r):
        nm = (f'<a href="{root}jugador/{esc(r["player_slug"], quote=True)}/"><strong>{esc(r["player"])}</strong></a>'
              if r.get("player_slug") in _PLAYER_PAGES else f'<strong>{esc(r["player"])}</strong>')
        route = f"{esc(r['from_club'] or 'origen sin confirmar')} → {esc(r['to_club'] or 'destino sin confirmar')}"
        return (f'<li><span class="lb">{_label(r["score"], _best_status(r))}</span> · {nm}: {route} '
                f'<span class="mt">({r["score"]}°)</span><br><span class="mt">Fuente: {_sources_html(r)}</span></li>')
    parts = [f'<p class="mt">Actualizado el <time datetime="{iso}">{fecha}, a las {now.strftime("%H:%M")}</time>. '
             'Esta página se regenera cada hora.</p>',
             f"<p>Los rumores de fichajes de hoy, ordenados por el termómetro de {esc(config.SITE_NAME)}: "
             "<b>Oficial</b> si el fichaje está cerrado, <b>Probable</b> si marca 40° o más y <b>Rumor</b> en el resto. "
             "Cada rumor enlaza a las noticias originales, que conservan su autoría.</p>"]
    if cerrados:
        parts.append("<h2>Fichajes cerrados</h2><ul>" + "".join(li(r) for r in cerrados) + "</ul>")
    if abiertos:
        parts.append("<h2>Rumores y fichajes probables</h2><ul>" + "".join(li(r) for r in abiertos) + "</ul>")
    if not rumors:
        parts.append("<p>Ahora mismo no hay rumores de fichajes publicados. Con el mercado cerrado es normal.</p>")
    parts.append(f'<p><a href="{root}rumores/">Todos los rumores</a> · <a href="{root}rumores/movimientos/">Últimos movimientos</a>'
                 f' · <a href="{root}jugador/">Jugadores con rumores</a></p>')
    title = f"Rumores de fichajes hoy: {now.day} de {MONTHS[now.month - 1].lower()} de {now.year}"
    desc = (f"Rumores de fichajes de hoy, {fecha}: {_plural(len(rumors), 'rumor', 'rumores')} con etiqueta "
            "Rumor, Probable u Oficial y enlace a cada fuente. Actualizado cada hora.")
    url = "/rumores-fichajes-hoy/"
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebSite", "name": config.SITE_NAME, "url": config.SITE_URL + "/", "inLanguage": "es-ES"},
        *_page_ld(url, title, desc, [("Rumores de fichajes hoy", None)], _iso_max(now.isoformat())),
        _item_list(rumors, config.SITE_URL + url)]}
    _write_info_page(out_dir, "rumores-fichajes-hoy", root=root, nav_on="hoy", title=title, description=desc,
                     h1=f"Rumores de fichajes hoy: {fecha}", crumbs=_crumbs(root, ("Rumores de fichajes hoy", None)),
                     body="".join(parts), ld=ld)
    return _iso_max(now.isoformat())


def _plural(n, one, many):
    return f"{n} {one if n == 1 else many}"


def _club_intro(club, ci, standings, rumors, news, fx):
    """Texto propio de la página de un club, generado con reglas a partir de sus datos (sin IA ni coste).
    Devuelve una lista de párrafos en texto plano."""
    import hashlib
    v = int(hashlib.md5(club.encode("utf-8")).hexdigest(), 16)      # variante estable por club
    out = []

    # 1) Liga: balance, diferencia con el líder y máximo goleador
    d = standings.get(ci["league"]) if ci else None
    if d and d.get("table"):
        table = d["table"]
        row = next((t for t in table if _club_of_team(t.get("team") or "") == club), None)
        if row:
            n = len(table)
            zona = ("en zona de descenso" if row["pos"] > n - 3 else
                    "en la zona alta" if row["pos"] <= 4 else "en la zona media")
            bal = (f"{_plural(row['won'], 'victoria', 'victorias')}, {_plural(row['draw'], 'empate', 'empates')} "
                   f"y {_plural(row['lost'], 'derrota', 'derrotas')}, con {row['gf']} goles a favor y {row['ga']} en contra")
            if row["pos"] == 1 and n > 1:
                gap = f"Lidera con {table[0]['points'] - table[1]['points']} puntos de ventaja sobre el {table[1]['team']}."
            elif table[0]["points"] == row["points"]:
                gap = f"Está empatado a puntos con el líder, el {table[0]['team']}."
            else:
                gap = f"Está a {table[0]['points'] - row['points']} puntos del líder, el {table[0]['team']}."
            first = (f"En {ci['league']} el {club} está {zona} de la tabla" if v % 2 else
                     f"El {club} se mueve {zona} de la clasificación de {ci['league']}")
            sc = [x for x in d.get("scorers", []) if _club_of_team(str(x.get("team") or "")) == club]
            top = max(sc, key=lambda x: x["goals"], default=None)
            tail = (f" Su máximo goleador es {top['player']}, con {_plural(top['goals'], 'gol', 'goles')}."
                    if top and top["goals"] else "")
            out.append(f"{first}: {bal}. {gap}{tail}")

    # 2) Mercado: rumores del club y el más caliente
    inc = [r for r in rumors if r.get("to_club") == club]
    sal = [r for r in rumors if r.get("from_club") == club]
    allr = sorted(inc + [r for r in sal if r not in inc], key=lambda r: -r["score"])
    if allr:
        top = allr[0]
        if top.get("to_club") == club:
            ruta = f"que podría llegar desde {top.get('from_club') or 'un club sin confirmar'}"
        else:
            ruta = f"que podría salir hacia {top.get('to_club') or 'un destino sin confirmar'}"
        fuerza = ("muy avanzado" if top["score"] >= 70 else "con opciones reales" if top["score"] >= 40 else
                  "en fase de interés" if top["score"] >= 15 else "todavía frío")
        txt = (f"En el mercado seguimos {_plural(len(allr), 'rumor', 'rumores')} del {club}: "
               f"{_plural(len(inc), 'de posible llegada', 'de posibles llegadas')} y "
               f"{_plural(len(sal), 'de posible salida', 'de posibles salidas')}. "
               f"El más caliente es {top['player']}, {ruta}, con {top['score']}° en el termómetro ({fuerza}).")
        otros = [r["player"] for r in allr[1:4]]
        if otros:
            txt += (" También suenan " if len(otros) > 1 else " También suena ") + \
                   (", ".join(otros[:-1]) + " y " + otros[-1] if len(otros) > 1 else otros[0]) + "."
        out.append(txt)
    else:
        out.append(f"Ahora mismo no seguimos ningún rumor de fichaje del {club}. Cuando los medios publiquen "
                   "alguno lo verás aquí con su termómetro de probabilidad (de 0° a 100°).")

    # 3) Fantasy: bajas y dudas del club según la prensa
    fxc = [r for r in fx if r.get("team") and _club_of_team(str(r["team"])) == club and r.get("st") in ("out", "susp", "doubt")]
    if fxc:
        items = [f"{r['player']} ({str(r['label']).lower()})" for r in fxc[:5]]
        out.append("Parte médico para tu Fantasy: según la prensa de los últimos días, " + ", ".join(items) + ".")

    # 4) Prensa: cuántas noticias y qué medios
    if news:
        from collections import Counter
        cnt = Counter(n["source"] for n in news).most_common(3)
        medios = [m for m, _ in cnt]
        fuentes = ", ".join(medios[:-1]) + " y " + medios[-1] if len(medios) > 1 else medios[0]
        out.append(f"En los últimos {config.NEWS_DAYS} días hay {_plural(len(news), 'noticia', 'noticias')} del {club} "
                   f"en la web, sobre todo de {fuentes}. Cada titular enlaza a la noticia original.")
    return out


_PLAYER_PAGES = set()   # slugs de jugador con página propia
_JORNADAS = []          # jornadas con página (de la más reciente a la más antigua)


def _update_jornadas(fx, md, info):
    """Guarda el parte médico de la jornada actual (se sobrescribe cada hora) y conserva el de las anteriores.
    Solo equipos de LaLiga. Devuelve {jornada: {"updated", "rows"}}."""
    import sqlite3
    db = sqlite3.connect(config.DB_PATH)      # la base ya se guarda en el repositorio tras cada ejecución
    db.execute("CREATE TABLE IF NOT EXISTS fx_jornadas (jornada INTEGER PRIMARY KEY, data TEXT NOT NULL)")
    snaps = {str(j): json.loads(d) for j, d in db.execute("SELECT jornada, data FROM fx_jornadas")}
    rows = []
    for r in fx:
        club = _club_of_team(str(r.get("team") or ""))
        if club and (info.get(club) or {}).get("league") == "LaLiga":
            rows.append({k: r[k] for k in ("player", "st", "label", "title", "url", "source", "date")} | {"team": club})
    if md and rows:
        snaps[str(md)] = {"updated": datetime.now().astimezone().isoformat(), "rows": rows}
        db.execute("INSERT OR REPLACE INTO fx_jornadas VALUES (?, ?)", (md, json.dumps(snaps[str(md)], ensure_ascii=False)))
        db.commit()
    db.close()
    return snaps


def _dmy(iso, with_time=False):
    d = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    if d.tzinfo is not None:
        d = d.astimezone(_now_spain().tzinfo)
    return d.strftime("%d/%m/%Y a las %H:%M" if with_time else "%d/%m")


def _jornada_page(md, snap, mds, out_dir):
    """/fantasy/jornada-N/: página estática con las bajas y dudas por equipo y los recuperados."""
    esc = html_lib.escape
    root = "../../"
    rows = snap["rows"]
    bajas = [r for r in rows if r["st"] == "out"]
    dudas = [r for r in rows if r["st"] == "doubt"]
    back = [r for r in rows if r["st"] == "back"]
    url = f"{config.SITE_URL}/fantasy/jornada-{md}/"
    upd = _dmy(snap["updated"], True)
    title = f"Lesionados y sancionados de la jornada {md} de LaLiga Fantasy"

    def item(r, with_team=False):
        team = f" ({esc(r['team'])})" if with_team else ""
        return (f'<li><strong>{esc(r["player"])}</strong>{team} · <span class="lb {r["st"]}">{esc(r["label"])}</span>. '
                f'<a href="{esc(r["url"], quote=True)}" target="_blank" rel="noopener">{esc(r["title"])}</a> '
                f'<span class="mt">({esc(r["source"])}, {_dmy(r["date"])})</span></li>')

    by_team = {}
    for r in bajas + dudas:
        by_team.setdefault(r["team"], []).append(r)
    order = sorted(by_team, key=lambda t: (-len(by_team[t]), t))

    # texto propio con reglas
    intro = [f"Este es el parte médico de LaLiga para la jornada {md} de LaLiga Fantasy (Biwenger, Comunio, Mister y "
             f"similares): {_plural(len(bajas), 'baja', 'bajas')} por lesión o sanción, {_plural(len(dudas), 'duda', 'dudas')} "
             f"y {_plural(len(back), 'jugador recuperado', 'jugadores recuperados')} según los titulares de los últimos "
             f"{config.FANTASY_DAYS} días. Actualizado el {upd}."]
    if order:
        top = [f"{t} ({len(by_team[t])})" for t in order[:3]]
        intro.append("Los equipos con más jugadores en la enfermería son " + ", ".join(top[:-1]) +
                     (" y " if len(top) > 1 else "") + top[-1] + ". Antes de cerrar tu once, comprueba cada nombre "
                     "en su equipo, o prueba la herramienta de tu plantilla en la página de Fantasy.")

    body = [f"<p>{esc(t)}</p>" for t in intro]
    body.append(f'<p><a class="btn" href="{root}fantasy/">Comprueba tu once en la herramienta de Fantasy</a></p>')
    if order:
        body.append("<h2>Bajas y dudas por equipo</h2>")
        for t in order:
            slug = _CLUB_PAGES.get(t)
            lis = "".join(item(r) for r in by_team[t])
            more = (f'<p class="mt2"><a class="mt" href="{root}club/{slug}/">Rumores y noticias del {esc(t)}</a></p>'
                    if slug else "")
            body.append(f"<h3>Lesionados y sancionados del {esc(t)}</h3><ul>{lis}</ul>{more}")
    else:
        body.append("<p>Ahora mismo no hay bajas ni dudas detectadas en la prensa para esta jornada.</p>")
    body.append("<h2>Recuperados</h2>")
    if back:
        body.append("<ul>" + "".join(item(r, True) for r in sorted(back, key=lambda r: (r["team"], r["player"]))) + "</ul>")
    else:
        body.append("<p>Todavía no hay jugadores que la prensa dé por recuperados en esta jornada.</p>")
    body.append("<h2>Cómo se elabora este parte</h2>"
                "<p>Un programa lee cada hora los titulares de los principales medios deportivos y detecta el jugador y "
                "si se habla de baja, duda, sanción o recuperación. No es un parte médico oficial: cada línea enlaza a la "
                "noticia original para que compruebes el detalle y la fecha de vuelta. Si un dato no está al día, "
                "escríbenos desde la página Sobre esta web.</p>")
    others = [m for m in mds if m != md]
    if others:
        body.append("<h2>Otras jornadas</h2><p>" + " · ".join(
            f'<a href="{root}fantasy/jornada-{m}/">Jornada {m}</a>' for m in others[:12]) + "</p>")

    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebSite", "name": config.SITE_NAME, "url": config.SITE_URL + "/", "inLanguage": "es-ES"},
        *_page_ld(f"/fantasy/jornada-{md}/", title,
                  f"Bajas, dudas y recuperados de LaLiga para la jornada {md} de Fantasy, por equipo.",
                  [("LaLiga Fantasy", "/fantasy/"), (f"Jornada {md}", None)], _iso_max(snap["updated"]))]}
    desc = (f"Bajas, dudas y recuperados de LaLiga para la jornada {md} de Fantasy, por equipo: "
            f"{_plural(len(bajas), 'baja', 'bajas')} y {_plural(len(dudas), 'duda', 'dudas')}. Actualizado {_dmy(snap['updated'])}.")
    analytics = (ANALYTICS.replace("__GA_ID__", config.GA_MEASUREMENT_ID).replace("__ROOT__", root)
                 if config.GA_MEASUREMENT_ID else "")
    html = (JORNADA_PAGE.replace("__ADSENSE__", ADSENSE).replace("__NAV__", _nav(root, "fantasy")).replace("__OGTYPE__", "article")
            .replace("__PREF_SOURCE__", _pref_source_link()).replace("__SITE_URL__", config.SITE_URL)
            .replace("__TITLE__", esc(_fit_title(title)))
            .replace("__DESCRIPTION__", esc(desc[:160], quote=True))
            .replace("__CANONICAL__", url).replace("__LDJSON__", _json(ld))
            .replace("__SITE_NAME__", esc(config.SITE_NAME)).replace("__ROOT__", root)
            .replace("__H1__", esc(title))
            .replace("__CRUMBS__", _crumbs(root, ("LaLiga Fantasy", "/fantasy/"), (f"Jornada {md}", None)))
            .replace("__BODY__", "".join(body))
            .replace("__FOOTER__", _sections_footer(root))
            .replace("__ANALYTICS__", analytics)
            .replace("__COOKIE_BUTTON__", '<button id="ck-config">Configurar cookies</button>'
                     if config.GA_MEASUREMENT_ID else ""))
    path = os.path.join(out_dir, "fantasy", f"jornada-{md}", "index.html")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


JORNADA_PAGE = r"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
__ADSENSE__
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<meta name="description" content="__DESCRIPTION__">
<link rel="canonical" href="__CANONICAL__">
<link rel="alternate" type="application/rss+xml" title="Movimientos del mercado de fichajes" href="__SITE_URL__/feed.xml">
<meta property="og:type" content="__OGTYPE__"><meta property="og:site_name" content="__SITE_NAME__">
<meta property="og:title" content="__TITLE__"><meta property="og:description" content="__DESCRIPTION__">
<meta property="og:url" content="__CANONICAL__"><meta property="og:locale" content="es_ES">
<link rel="icon" href="__ROOT__favicon.svg" type="image/svg+xml">
<link rel="icon" href="__ROOT__favicon.png" type="image/png" sizes="48x48">
<script type="application/ld+json">__LDJSON__</script>
<style>
:root { --chalk:#f2f6f3; --card:#fff; --ink:#10201a; --muted:#5d6d65; --line:#dbe3de; --grass:#145a32; --ok:#1f8f4e; --hot:#b3361b; --warm:#a96f00; }
@media (prefers-color-scheme: dark) { :root { --chalk:#0c1611; --card:#14211a; --ink:#e4ece7; --muted:#93a39a; --line:#24352c; --grass:#0f4426; --hot:#ff8a6d; --warm:#f0c24a; --ok:#5fd08a; } }
* { box-sizing:border-box; }
body { margin:0; background:var(--chalk); color:var(--ink); font:17px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif; }
a { color:inherit; }
header { background:var(--grass); color:#fff; padding:14px 20px; }
header nav { max-width:760px; margin:0 auto; display:flex; flex-wrap:wrap; gap:6px 18px; align-items:baseline; }
header a { color:#fff; text-decoration:none; font-weight:600; } header .site { font-size:19px; margin-right:auto; }
header a.on { text-decoration:underline; }
main { max-width:760px; margin:0 auto; padding:22px 20px 40px; }
h1 { font-size:30px; line-height:1.15; margin:8px 0 14px; } h2 { font-size:22px; margin:30px 0 8px; } h3 { font-size:18px; margin:20px 0 6px; }
.crumbs { display:flex; flex-wrap:wrap; align-items:center; gap:4px 8px; font-size:14px; color:var(--muted); } .crumbs a { color:inherit; } .crumbs .sep { opacity:.6; }
ul { padding-left:20px; } li { margin:7px 0; }
.lb { font-weight:700; } .lb.out { color:var(--hot); } .lb.doubt { color:var(--warm); } .lb.back { color:var(--ok); }
.mt { color:var(--muted); font-size:14px; } .mt2 { margin:4px 0 0; }
.btn { display:inline-block; padding:10px 16px; border-radius:8px; background:var(--grass); color:#fff; text-decoration:none; font-weight:600; }
footer { max-width:760px; margin:0 auto; padding:0 20px 50px; font-size:14px; color:var(--muted); }
footer a { margin-right:12px; white-space:nowrap; } footer details { line-height:1.9; margin-bottom:12px; } footer summary { cursor:pointer; }
footer button { font:inherit; background:none; border:0; color:inherit; text-decoration:underline; cursor:pointer; padding:0; }
.cookies { position:fixed; left:16px; right:16px; bottom:16px; z-index:10; max-width:560px; background:var(--card); border:1px solid var(--line); border-radius:10px; padding:16px; box-shadow:0 6px 24px #0003; }
.cookies p { margin:0 0 12px; font-size:15px; } .cookies .btns { display:flex; gap:10px; flex-wrap:wrap; align-items:center; }
.cookies button { font:600 15px/1 inherit; padding:10px 16px; border-radius:6px; cursor:pointer; border:1px solid var(--line); background:var(--card); color:var(--ink); }
.cookies .yes { background:var(--grass); color:#fff; border-color:var(--grass); } .cookies[hidden] { display:none; }
:root { --acc:#1b6b3d; } @media (prefers-color-scheme: dark) { :root { --acc:#5fd08a; } }
table.tb { border-collapse:collapse; width:100%; font-size:15px; } .tb th, .tb td { text-align:left; padding:7px 8px; border-bottom:1px solid var(--line); vertical-align:top; }
.chart { width:100%; height:auto; max-width:640px; } .chart text { fill:var(--muted); font-size:11px; font-family:inherit; }
.chart .ax { stroke:var(--line); } .chart .ln { fill:none; stroke:var(--acc); stroke-width:2.5; } .chart .pt { fill:var(--acc); }
.vote { border:1px solid var(--line); background:var(--card); border-radius:10px; padding:14px 16px; margin:18px 0; }
.vote p { margin:0 0 8px; font-weight:600; } .vote .vb { display:flex; gap:10px; flex-wrap:wrap; }
.vote button { font:inherit; font-weight:600; padding:9px 18px; border-radius:8px; border:1px solid var(--line); background:var(--chalk); color:var(--ink); cursor:pointer; }
.vote button:hover { border-color:var(--acc); } .vote .bar { height:10px; border-radius:5px; background:var(--line); overflow:hidden; margin:6px 0 2px; } .vote .bar i { display:block; height:100%; background:var(--acc); }
.vote .small { font-size:14px; color:var(--muted); font-weight:400; }
.ev { list-style:none; padding:0; } .ev li { padding:8px 0; border-bottom:1px solid var(--line); } .ev time { color:var(--muted); font-size:14px; margin-right:8px; font-variant-numeric:tabular-nums; }
</style></head><body>
<header><nav>__NAV__</nav></header>
<main>__CRUMBS__<h1>__H1__</h1>__BODY__</main>
<footer>__FOOTER__<p>__PREF_SOURCE__<a href="__ROOT__sobre">Sobre esta web</a><a href="__ROOT__privacidad">Privacidad</a><a href="__ROOT__cookies.html">Cookies</a>__COOKIE_BUTTON__</p></footer>
__ANALYTICS__
</body></html>
"""


def _pref_source_link():
    """Enlace para que el lector añada la web como fuente preferida en Google (gratis, sin código externo)."""
    domain = config.SITE_URL.split("//", 1)[1].rstrip("/")
    return (f'<a class="pref" href="https://www.google.com/preferences/source?q={html_lib.escape(domain, quote=True)}" '
            'target="_blank" rel="noopener">⭐ Añádenos como fuente preferida en Google</a>')


def _player_page_entries(rumors):
    """Rumores con ficha propia: al menos dos titulares y un nombre de URL seguro; los 150 más calientes."""
    ok = [e for e in rumors if len(e["mentions"]) >= 2 and re.fullmatch(r"[a-z0-9-]{2,60}", e.get("player_slug") or "")]
    return sorted(ok, key=lambda e: -e["score"])[:150]


def _write_feed(events, out_dir):
    """feed.xml (RSS 2.0) con los últimos movimientos del mercado."""
    esc = html_lib.escape
    from email.utils import format_datetime
    items = []
    for ev in sorted(events, key=lambda ev: ev["date"], reverse=True)[:40]:
        e = ev["entry"]
        route = f"{e['from_club'] or '?'} → {e['to_club'] or '?'}"
        if ev["kind"] == "entra":
            title = f"{e['player']} ({route}) entra en el termómetro con {ev['score']}°"
        elif ev["kind"] == "estado":
            title = f"{e['player']}: el rumor pasa a «{STAT_ES.get(ev['status'], ev['status'])}» ({ev['score']}°)"
        else:
            title = f"{e['player']} sube a {ev['score']}° en el termómetro"
        link = (f"{config.SITE_URL}/jugador/{e['player_slug']}/" if e["player_slug"] in _PLAYER_PAGES
                else f"{config.SITE_URL}/rumores/movimientos/")
        when = datetime.fromisoformat(ev["date"].replace("Z", "+00:00"))
        items.append(f"<item><title>{esc(title)}</title><link>{esc(link)}</link>"
                     f'<guid isPermaLink="false">{esc(e["player_slug"])}|{esc(ev["date"])}|{ev["kind"]}</guid>'
                     f"<pubDate>{format_datetime(when)}</pubDate>"
                     f"<description>{esc(title + '. Según ' + ev['source'] + '.')}</description></item>")
    now = format_datetime(datetime.now().astimezone())
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
           f"<title>{esc(config.SITE_NAME)}: movimientos del mercado</title><link>{config.SITE_URL}/rumores/movimientos/</link>"
           "<description>Cada vez que un rumor de fichaje entra, sube o avanza de estado.</description>"
           f"<language>es-ES</language><lastBuildDate>{now}</lastBuildDate>{''.join(items)}</channel></rss>\n")
    with open(os.path.join(out_dir, "feed.xml"), "w", encoding="utf-8") as f:
        f.write(xml)


STAT_ES = {"interes": "Interés", "negociacion": "Negociación", "acuerdo": "Acuerdo", "oficial": "Oficial",
           "descartado": "Descartado"}


def _nav(root, on):
    items = [("news", "Noticias", root or "./"), ("rumors", "Rumores", f"{root}rumores/"),
             ("table", "Clasificación", f"{root}clasificacion/{league_slug('LaLiga')}/"),
             ("fantasy", "Fantasy", f"{root}fantasy/"), ("hoy", "Hoy", f"{root}rumores-fichajes-hoy/")]
    return (f'<a class="site" href="{root or "./"}">{html_lib.escape(config.SITE_NAME)}</a>'
            + "".join(f'<a{" class=" + chr(34) + "on" + chr(34) if k == on else ""} href="{h}">{t}</a>' for k, t, h in items))


def _day_label(iso, now):
    d = datetime.fromisoformat(str(iso).replace("Z", "+00:00")).astimezone(now.tzinfo)
    delta = (now.date() - d.date()).days
    if delta == 0:
        return "Hoy"
    if delta == 1:
        return "Ayer"
    return f"{d.day} de {MONTHS[d.month - 1]}"


def _series(entry):
    """Evolución del termómetro de un rumor: [(fecha ISO, grados, estado, medios)] y eventos."""
    import score
    ms = sorted(entry["mentions"], key=lambda m: m["date"])
    need = config.AUTO_PUBLISH_MIN_SOURCES
    sources, statuses, pts, events = set(), set(), [], []
    entered, last_ev, best_rank = False, None, -1
    for m in ms:
        sources.add(m["source"]); statuses.add(m["status"])
        sc = score.thermometer(sources, statuses)
        st = score.best_status(statuses)
        rank = score.ORDER.index(st) if st in score.ORDER else -1
        pts.append((m["date"], sc, st, len(sources)))
        if not entered and len(sources) >= need:
            entered = True
            events.append({"date": m["date"], "kind": "entra", "score": sc, "status": st, "source": m["source"],
                           "n": len(sources)})
            last_ev, best_rank = sc, rank
        elif entered:
            if rank > best_rank:
                events.append({"date": m["date"], "kind": "estado", "score": sc, "status": st, "source": m["source"],
                               "n": len(sources)})
                last_ev, best_rank = sc, rank
            elif sc - last_ev >= 10:
                events.append({"date": m["date"], "kind": "sube", "score": sc, "status": st, "source": m["source"],
                               "n": len(sources)})
                last_ev = sc
    if not entered and ms:                       # publicado a mano con menos medios
        events.append({"date": ms[0]["date"], "kind": "entra", "score": pts[0][1], "status": pts[0][2],
                       "source": ms[0]["source"], "n": 1})
    return pts, events


def _chart_svg(pts, now_iso):
    """Gráfico del termómetro (escalón) en SVG, sin librerías."""
    W, H, L, R, T, B = 640, 190, 34, 12, 12, 28
    t0 = datetime.fromisoformat(pts[0][0].replace("Z", "+00:00")).timestamp()
    t1 = max(datetime.fromisoformat(now_iso).timestamp(),
             datetime.fromisoformat(pts[-1][0].replace("Z", "+00:00")).timestamp())
    span = max(t1 - t0, 3600)
    x = lambda t: L + (t - t0) / span * (W - L - R)
    y = lambda v: T + (100 - v) / 100 * (H - T - B)
    path, cur = [], None
    for iso, sc, _, _ in pts:
        t = datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()
        if cur is not None:
            path.append(f"{x(t):.1f},{y(cur):.1f}")
        path.append(f"{x(t):.1f},{y(sc):.1f}")
        cur = sc
    path.append(f"{x(t1):.1f},{y(cur):.1f}")
    dots = "".join(f'<circle class="pt" cx="{x(datetime.fromisoformat(i.replace("Z", "+00:00")).timestamp()):.1f}" '
                   f'cy="{y(sc):.1f}" r="3.5"/>' for i, sc, _, _ in pts)
    grid = "".join(f'<line class="ax" x1="{L}" x2="{W - R}" y1="{y(v):.1f}" y2="{y(v):.1f}"/>'
                   f'<text x="{L - 6}" y="{y(v) + 4:.1f}" text-anchor="end">{v}°</text>' for v in (0, 50, 100))
    d0 = datetime.fromtimestamp(t0, _now_spain().tzinfo).strftime("%d/%m")
    d1 = datetime.fromtimestamp(t1, _now_spain().tzinfo).strftime("%d/%m")
    return (f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Evolución del termómetro de {d0} a {d1}">'
            f'{grid}<polyline class="ln" points="{" ".join(path)}"/>{dots}'
            f'<text x="{L}" y="{H - 8}">{d0}</text><text x="{W - R}" y="{H - 8}" text-anchor="end">{d1}</text></svg>')


def _force(sc):
    return ("muy avanzado" if sc >= 70 else "con opciones reales" if sc >= 40 else
            "en fase de interés" if sc >= 15 else "todavía frío")


def _write_info_page(out_dir, rel, *, root, nav_on, title, description, h1, crumbs, body, ld, ogtype="website"):
    esc = html_lib.escape
    analytics = (ANALYTICS.replace("__GA_ID__", config.GA_MEASUREMENT_ID).replace("__ROOT__", root)
                 if config.GA_MEASUREMENT_ID else "")
    html = (JORNADA_PAGE.replace("__ADSENSE__", ADSENSE).replace("__NAV__", _nav(root, nav_on)).replace("__OGTYPE__", ogtype)
            .replace("__PREF_SOURCE__", _pref_source_link()).replace("__SITE_URL__", config.SITE_URL)
            .replace("__TITLE__", esc(_fit_title(title))).replace("__DESCRIPTION__", esc(description[:160], quote=True))
            .replace("__CANONICAL__", f"{config.SITE_URL}/{rel}").replace("__LDJSON__", _json(ld))
            .replace("__SITE_NAME__", esc(config.SITE_NAME)).replace("__ROOT__", root).replace("__H1__", esc(h1))
            .replace("__CRUMBS__", crumbs).replace("__BODY__", body).replace("__FOOTER__", _sections_footer(root))
            .replace("__ANALYTICS__", analytics)
            .replace("__COOKIE_BUTTON__", '<button id="ck-config">Configurar cookies</button>'
                     if config.GA_MEASUREMENT_ID else ""))
    path = os.path.join(out_dir, rel, "index.html")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


VOTE_JS = r"""<script>
(function () {
  var box = document.getElementById("vote"); if (!box) return;
  var slug = box.getAttribute("data-slug"), KEY = "voto-" + slug;
  function get() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function put(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  function show(c, mine) {
    var yes = c.si || 0, no = c.no || 0, n = yes + no;
    box.replaceChildren();
    var p = document.createElement("p"); p.textContent = "Tu voto: " + (mine === "si" ? "sí se hará" : "no se hará"); box.append(p);
    if (n >= 5) {
      var pc = Math.round(yes * 100 / n), bar = document.createElement("div"); bar.className = "bar";
      var i = document.createElement("i"); i.style.width = pc + "%"; bar.append(i);
      var t = document.createElement("div"); t.className = "small";
      t.textContent = pc + "% de los lectores cree que sí se hará (" + n + " votos). Es solo una opinión, no un dato oficial.";
      box.append(bar, t);
    } else {
      var t2 = document.createElement("div"); t2.className = "small"; t2.textContent = "Gracias. Aún hay pocos votos para mostrar el resultado.";
      box.append(t2);
    }
  }
  function load(mine) {
    fetch("/api/votos?rumor=" + encodeURIComponent(slug)).then(function (r) { return r.ok ? r.json() : null; })
      .then(function (c) { if (c) show(c, mine); }).catch(function () {});
  }
  function send(v) {
    fetch("/api/votos", { method: "POST", body: JSON.stringify({ rumor: slug, v: v }) })
      .then(function (r) { if (r.ok) { put(v); load(v); } }).catch(function () {});
  }
  fetch("/api/votos?rumor=" + encodeURIComponent(slug)).then(function (r) { if (!r.ok) throw 0; return r.json(); }).then(function () {
    box.hidden = false;
    var mine = get(); if (mine) { load(mine); return; }
    box.querySelectorAll("button").forEach(function (b) { b.addEventListener("click", function () { send(b.getAttribute("data-v")); }); });
  }).catch(function () { box.hidden = true; });
})();
</script>"""


def _player_page(e, pts, events, out_dir):
    esc = html_lib.escape
    root = "../../"
    slug, name = e["player_slug"], e["player"]
    now = _now_spain()
    route = f"{e['from_club'] or 'origen sin confirmar'} → {e['to_club'] or 'destino sin confirmar'}"
    ms = sorted(e["mentions"], key=lambda m: m["date"])
    best = pts[-1][2]
    fee = next((m["fee"] for m in reversed(ms) if m.get("fee")), None)
    srcs = sorted({m["source"] for m in ms})
    first, last = ms[0], ms[-1]
    fmt = lambda iso: datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(now.tzinfo).strftime("%d/%m/%Y")
    paras = [f"El rumor del fichaje de {name} ({route}) está ahora en {e['score']}° en el termómetro de {config.SITE_NAME}, "
             f"es decir, {_force(e['score'])}. Lo cuentan {_plural(len(srcs), 'medio', 'medios')} "
             f"({', '.join(srcs)}) en {_plural(len(ms), 'titular', 'titulares')} de los últimos {config.WINDOW_DAYS} días. "
             f"El estado más avanzado es «{STAT_ES.get(best, best)}»."]
    t2 = f"El primer titular que seguimos es del {fmt(first['date'])} ({first['source']}) y el último, del {fmt(last['date'])} ({last['source']})."
    if fee:
        t2 += f" Según los titulares, la operación rondaría los {fee:g} millones de euros."
    paras.append(t2)
    if e.get("others"):
        alt = ", ".join(f"{o['to_club']} ({o['score']}°)" for o in e["others"] if o.get("to_club"))
        if alt:
            paras.append(f"También suenan otros destinos para {name}: {alt}.")
    def club_link(c):
        sl = _CLUB_PAGES.get(c)
        return f'<a href="{root}club/{sl}/">{esc(c)}</a>' if sl else esc(c)
    related = " · ".join(club_link(c) for c in e.get("clubs", []) if c)
    rows = "".join(
        f'<tr><td>{fmt(m["date"])}</td><td>{esc(m["source"])}</td><td>{esc(STAT_ES.get(m["status"], m["status"]))}</td>'
        f'<td><a href="{esc(m["url"], quote=True)}" target="_blank" rel="noopener">{esc(m["title"])}</a></td></tr>'
        for m in reversed(ms))
    ch_rows = "".join(f'<li>{fmt(d)}: {sc}° ({STAT_ES.get(st, st)}, {_plural(n, "medio", "medios")})</li>'
                      for d, sc, st, n in pts)
    body = ("".join(f"<p>{esc(t)}</p>" for t in paras)
            + f'<div class="vote" id="vote" data-slug="{esc(slug, quote=True)}" hidden><p>¿Crees que el fichaje de {esc(name)} se hará?</p>'
              '<div class="vb"><button type="button" data-v="si">Sí, se hará</button><button type="button" data-v="no">No se hará</button></div></div>'
            + "<h2>Evolución del termómetro</h2>" + _chart_svg(pts, now.isoformat())
            + f'<details><summary class="small">Ver los datos del gráfico</summary><ul>{ch_rows}</ul></details>'
            + f'<h2>Todos los titulares sobre {esc(name)}</h2><div style="overflow-x:auto"><table class="tb"><thead><tr><th>Fecha</th><th>Medio</th><th>Estado</th><th>Titular</th></tr></thead><tbody>{rows}</tbody></table></div>'
            + (f"<h2>Clubes implicados</h2><p>{related}</p>" if related else "")
            + f'<p><a href="{root}rumores/">Todos los rumores de fichajes</a> · <a href="{root}rumores/movimientos/">Últimos movimientos del mercado</a> · <a href="{root}jugador/">Más jugadores</a></p>'
            + "<h2>Cómo se calcula</h2><p>El termómetro (de 0° a 100°) es una estimación automática: cuenta cuántos medios distintos hablan del rumor, cuánto se fía la web de cada uno y lo avanzado que está el estado de la operación. No es información oficial ni una predicción. Cada titular enlaza a la noticia original, que conserva su autoría.</p>"
            + VOTE_JS)
    title = f"Fichaje de {name}: rumores, termómetro e historial"
    desc = (f"{name}: {e['score']}° en el termómetro, {_plural(len(srcs), 'medio', 'medios')} y {_plural(len(ms), 'titular', 'titulares')}. "
            f"Rumor {route}, con enlaces a cada fuente.")
    modified = _iso_max(*(m["date"] for m in ms))
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebSite", "name": config.SITE_NAME, "url": config.SITE_URL + "/", "inLanguage": "es-ES"},
        *_page_ld(f"/jugador/{slug}/", title, desc, [("Jugadores con rumores", "/jugador/"), (name, None)], modified),
        {"@type": "Person", "@id": f"{config.SITE_URL}/jugador/{slug}/#jugador", "name": name,
         "url": f"{config.SITE_URL}/jugador/{slug}/", "jobTitle": "Futbolista",
         **({"affiliation": {"@type": "SportsTeam", "name": e["from_club"]}} if e.get("from_club") else {})}]}
    ld["@graph"][1]["about"] = {"@id": f"{config.SITE_URL}/jugador/{slug}/#jugador"}
    crumbs = _crumbs(root, ("Jugadores con rumores", "/jugador/"), (name, None))
    _write_info_page(out_dir, f"jugador/{slug}", root=root, nav_on="rumors", title=title, description=desc,
                     h1=f"Fichaje de {name}: rumores y termómetro", crumbs=crumbs, body=body, ld=ld, ogtype="article")
    return modified


def _players_hub(entries, out_dir):
    esc = html_lib.escape
    root = "../"
    now = _now_spain()
    items = "".join(
        f'<li><a href="{root}jugador/{esc(e["player_slug"], quote=True)}/"><strong>{esc(e["player"])}</strong></a>: '
        f'{esc(e["from_club"] or "origen sin confirmar")} → {esc(e["to_club"] or "destino sin confirmar")} '
        f'<span class="mt">({e["score"]}° · {esc(STAT_ES.get(pts_best, pts_best))})</span></li>'
        for e, pts_best in entries)
    intro = (f"Estos son los jugadores con un rumor de fichaje que siguen al menos dos titulares en los últimos {config.WINDOW_DAYS} días, "
             f"ordenados de más a menos caliente según el termómetro de {config.SITE_NAME}. Cada ficha reúne todos los titulares, "
             "la evolución del rumor y la opinión de los lectores.")
    body = f"<p>{esc(intro)}</p><ol>{items}</ol><p><a href=\"{root}rumores/movimientos/\">Últimos movimientos del mercado</a></p>"
    title, desc = "Jugadores con rumores de fichaje", "Todos los jugadores con rumores de fichaje, ordenados por termómetro: historial, titulares y opinión de los lectores."
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebSite", "name": config.SITE_NAME, "url": config.SITE_URL + "/", "inLanguage": "es-ES"},
        *_page_ld("/jugador/", title, desc, [("Jugadores con rumores", None)], _iso_max(now.isoformat()))]}
    _write_info_page(out_dir, "jugador", root=root, nav_on="rumors", title=title, description=desc, h1=title,
                     crumbs=_crumbs(root, ("Jugadores con rumores", None)), body=body, ld=ld)


def _movimientos_page(events, out_dir):
    """Últimos movimientos del mercado: cada vez que un rumor entra, sube o avanza de estado."""
    esc = html_lib.escape
    root = "../../"
    now = _now_spain()
    events = sorted(events, key=lambda ev: ev["date"], reverse=True)[:80]
    parts, cur = [], None
    for ev in events:
        day = _day_label(ev["date"], now)
        if day != cur:
            if cur is not None:
                parts.append("</ul>")
            parts.append(f"<h2>{esc(day)}</h2><ul class=\"ev\">")
            cur = day
        hhmm = datetime.fromisoformat(ev["date"].replace("Z", "+00:00")).astimezone(now.tzinfo).strftime("%H:%M")
        e = ev["entry"]
        nm = (f'<a href="{root}jugador/{esc(e["player_slug"], quote=True)}/">{esc(e["player"])}</a>'
              if e["player_slug"] in _PLAYER_PAGES else esc(e["player"]))
        route = f"{esc(e['from_club'] or '?')} → {esc(e['to_club'] or '?')}"
        if ev["kind"] == "entra":
            txt = f"{nm} ({route}) entra en el termómetro con {ev['score']}°, según {esc(ev['source'])}."
        elif ev["kind"] == "estado":
            txt = f"El rumor de {nm} ({route}) pasa a «{esc(STAT_ES.get(ev['status'], ev['status']))}» y marca {ev['score']}° ({esc(ev['source'])})."
        else:
            txt = f"{nm} ({route}) sube a {ev['score']}° con {_plural(ev['n'], 'medio', 'medios')}."
        parts.append(f"<li><time>{hhmm}</time>{txt}</li>")
    if cur is not None:
        parts.append("</ul>")
    if not events:
        parts.append("<p>Todavía no hay movimientos recientes que mostrar.</p>")
    intro = ("Cada vez que un rumor entra en el termómetro, sube de forma notable o pasa a un estado más avanzado "
             "(negociación, acuerdo u oficial), queda anotado aquí con su hora. La lista se actualiza cada hora a partir "
             "de los titulares de la prensa deportiva.")
    body = f"<p>{esc(intro)}</p>" + "".join(parts) + f'<p><a href="{root}rumores/">Todos los rumores</a> · <a href="{root}jugador/">Jugadores con rumores</a></p>'
    title, desc = "Últimos movimientos del mercado de fichajes", "Qué rumores suben, entran o avanzan de estado en el mercado de fichajes, con la hora de cada cambio. Actualizado cada hora."
    mod = _iso_max(*(ev["date"] for ev in events)) if events else None
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebSite", "name": config.SITE_NAME, "url": config.SITE_URL + "/", "inLanguage": "es-ES"},
        *_page_ld("/rumores/movimientos/", title, desc, [("Rumores de fichajes", "/rumores/"), ("Últimos movimientos", None)], mod)]}
    _write_info_page(out_dir, "rumores/movimientos", root=root, nav_on="rumors", title=title, description=desc, h1=title,
                     crumbs=_crumbs(root, ("Rumores de fichajes", "/rumores/"), ("Últimos movimientos", None)),
                     body=body, ld=ld)
    return mod


def _build_player_pages(rumors, out_dir):
    """Páginas de jugador (solo con 2 o más titulares), hub y feed de movimientos. Devuelve {ruta: lastmod}."""
    lm, events, hub = {}, [], []
    ok = _player_page_entries(rumors)
    _PLAYER_PAGES.clear()
    _PLAYER_PAGES.update(e["player_slug"] for e in ok)
    for e in rumors:
        pts, evs = _series(e)
        for ev in evs:
            if ev["status"] == "descartado" or (ev["kind"] == "entra" and ev["score"] < 10):
                continue                       # rumores fríos o descartados no son un "movimiento"
            events.append({**ev, "entry": e})
    for e in ok:
        pts, _ = _series(e)
        lm[f"/jugador/{e['player_slug']}/"] = _player_page(e, pts, _, out_dir)
        hub.append((e, pts[-1][2]))
    if ok:
        _players_hub(hub, out_dir)
        lm["/jugador/"] = _iso_max(*(v for v in lm.values()))
    lm["/rumores/movimientos/"] = _movimientos_page(events, out_dir)
    _write_feed(events, out_dir)
    return lm


def _fit_title(text, limit=62):
    """Añade " | nombre de la web" solo si cabe sin que Google corte el título."""
    full = f"{text} | {config.SITE_NAME}"
    return full if len(full) <= limit else text


def league_slug(league):
    from pipeline import slugify
    return slugify(league)


def _static_table(league, d):
    """Clasificación, goleadores y asistentes en HTML normal (para buscadores)."""
    esc = html_lib.escape
    md = f" (jornada {d['matchday']})" if d.get("matchday") else ""
    p = [f"<h2>Clasificación de {esc(league)}{md}</h2><table><tr><th>#</th><th>Equipo</th><th>PJ</th>"
         "<th>G</th><th>E</th><th>P</th><th>GF</th><th>GC</th><th>Pts</th></tr>"]
    for t in d.get("table", []):
        p.append(f"<tr><td>{t['pos']}</td><td>{esc(str(t['team']))}</td><td>{t['played']}</td><td>{t['won']}</td>"
                 f"<td>{t['draw']}</td><td>{t['lost']}</td><td>{t['gf']}</td><td>{t['ga']}</td><td>{t['points']}</td></tr>")
    p.append("</table>")
    goals = sorted(d.get("scorers", []), key=lambda s: -s["goals"])[:20]
    p.append(f"<h2>Máximos goleadores de {esc(league)}</h2><ol>")
    p += [f"<li>{esc(str(s['player']))} ({esc(str(s['team']))}): {s['goals']} goles</li>" for s in goals]
    p.append("</ol>")
    assists = sorted((s for s in d.get("scorers", []) if s["assists"]), key=lambda s: -s["assists"])[:20]
    if assists:
        p.append(f"<h2>Máximos asistentes de {esc(league)}</h2><ol>")
        p += [f"<li>{esc(str(s['player']))} ({esc(str(s['team']))}): {s['assists']} asistencias</li>" for s in assists]
        p.append("</ol>")
    return "".join(p)


def _static_fantasy(rep_):
    esc = html_lib.escape
    p = ["<h2>Parte médico para tu Fantasy</h2>"]
    for st, title in [("out", "Bajas"), ("doubt", "Dudas"), ("back", "Recuperados")]:
        rows = [r for r in rep_ if r["st"] == st]
        if rows:
            p.append(f"<h3>{title}</h3><ul>")
            p += [f'<li>{esc(r["player"])}{" (" + esc(str(r["team"])) + ")" if r["team"] else ""}: {esc(r["label"])}. '
                  f'<a href="{esc(r["url"], quote=True)}">{esc(r["title"])}</a> ({esc(r["source"])})</li>' for r in rows]
            p.append("</ul>")
    if len(p) == 1:
        p.append("<p>No hay noticias recientes de lesiones ni sanciones.</p>")
    return "".join(p)


def generate(data, news=(), months=(), out_dir="web"):
    """Todas las páginas de la web. months = [(AAAA-MM, nº noticias, nº rumores)], de más reciente a más antiguo.
    Portada (noticias), /rumores/, /clasificacion/<liga>/ y /fantasy/: cada una con su título y descripción."""
    news = list(news)
    rumors = _flatten(data)
    standings = _standings()
    from pipeline import slugify
    info = _club_info(standings)
    # Página propia para cada club con noticias o rumores recientes, o con sitio en una clasificación
    _CLUB_PAGES.clear()
    for club in config.CLUBS:
        if club in info or any(club in n["clubs"] for n in news) or \
           any(club in (r.get("clubs") or [r["from_club"], r["to_club"]]) for r in rumors):
            _CLUB_PAGES[club] = slugify(club)
    counts = {"news": len(news), "rumors": len(rumors)}
    # Fantasy: parte médico general + herramienta para tu once
    try:
        import fantasy, rules
        cands = fantasy.candidates(rules.load_players(), standings)
        ignore = fantasy.load_ignore()
        fx = fantasy.report(news, cands, ignore=ignore)
        fx_players = {name: sorted(c["keys"]) for name, c in cands.items()}
    except Exception as exc:
        print("[aviso] parte médico:", exc)
        fx, fx_players, ignore = [], {}, []
    # Páginas fijas por jornada de Fantasy (las pasadas se conservan)
    snaps = _update_jornadas(fx, _next_jornada(standings), info)
    _JORNADAS[:] = sorted((int(k) for k in snaps), reverse=True)
    # Páginas de jugador, hub y movimientos (antes que el resto, para poder enlazarlas)
    player_lm = _build_player_pages(rumors, out_dir)
    # Fecha real de cada página (para el sitemap y dateModified)
    news_date = _iso_max(*(n.get("date") for n in news))
    rum_date = _iso_max(*(r.get("last_update") for r in rumors))
    lastmod = {"/": _iso_max(news_date, rum_date), "/rumores/": _iso_max(news_date, rum_date),
               "/fantasy/": news_date}
    for lg, d_ in standings.items():
        lastmod[f"/clasificacion/{league_slug(lg)}/"] = _iso_max(d_.get("updated"))
    for club, slug in _CLUB_PAGES.items():
        lastmod[f"/club/{slug}/"] = _iso_max(
            *(n.get("date") for n in news if club in n["clubs"]),
            *(r.get("last_update") for r in rumors if club in (r.get("clubs") or [r["from_club"], r["to_club"]])),
            (standings.get((info.get(club) or {}).get("league")) or {}).get("updated"))
    for md_ in _JORNADAS:
        lastmod[f"/fantasy/jornada-{md_}/"] = _iso_max(snaps[str(md_)]["updated"])
    lastmod["/rumores-fichajes-hoy/"] = _hoy_page(rumors, out_dir)
    lastmod.update({k: v for k, v in player_lm.items() if v})
    for k in player_lm:
        lastmod.setdefault(k, None)
    write_static(months, out_dir, list(standings), list(_CLUB_PAGES.values()), lastmod)
    common = dict(is_archive=False,
                  tagline=config.SITE_TAGLINE, counts=counts, standings=standings)

    # Portada: noticias
    index = _write(os.path.join(out_dir, "index.html"), page="news", root="",
                   heading=config.SITE_NAME, crumbs="",
                   ld_page=_page_ld("/", config.SITE_TITLE, config.SITE_DESCRIPTION, modified=lastmod["/"]),
                   title=config.SITE_TITLE, description=config.SITE_DESCRIPTION,
                   canonical=config.SITE_URL + "/", rumors=rumors, news=news,
                   archive=_archive(months, prefix="archivo/"), **common)

    # Rumores
    _write(os.path.join(out_dir, "rumores", "index.html"), page="rumors", root="../",
           heading=f"Rumores de fichajes y mercado de invierno {_winter_year()}",
           crumbs=_crumbs("../", ("Rumores de fichajes", None)),
           ld_page=_page_ld("/rumores/", f"Rumores de fichajes y mercado de invierno {_winter_year()}",
                            f"Fichajes cerrados y los rumores más calientes del mercado de invierno {_winter_year()}",
                            [("Rumores de fichajes", None)], lastmod["/rumores/"])
                   + [_item_list(rumors, config.SITE_URL + "/rumores/")],
           title=_fit_title(f"Rumores de fichajes y mercado de invierno {_winter_year()}"),
           description=(f"Fichajes cerrados y los rumores más calientes del mercado de invierno {_winter_year()} "
                        "de LaLiga, Premier y Serie A, con termómetro de probabilidad. Cada hora."),
           canonical=config.SITE_URL + "/rumores/", rumors=rumors, news=news,
           archive=_archive(months, prefix="../archivo/"),
           static_html=_static_list([], rumors, limit=0) + _static_list(news, [], limit=30), **common)

    # Clasificación: una página por liga (no llevan noticias: así pesan poco)
    for lg, d in standings.items():
        art = "la " if lg in ("Premier League", "Serie A", "Bundesliga", "Ligue 1") else ""
        top = "pichichi" if lg == "LaLiga" else "goleadores"
        _write(os.path.join(out_dir, "clasificacion", league_slug(lg), "index.html"), page="table",
               root="../../", table_league=lg,
               heading=f"Clasificación de {art}{lg}",
               crumbs=_crumbs("../../", (f"Clasificación de {art}{lg}", None)),
               ld_page=_page_ld(f"/clasificacion/{league_slug(lg)}/", f"Clasificación de {art}{lg}",
                                f"Clasificación, máximos goleadores y asistentes de {art}{lg}.",
                                [(f"Clasificación de {art}{lg}", None)], lastmod.get(f"/clasificacion/{league_slug(lg)}/")),
               title=_fit_title(f"Clasificación de {art}{lg}: {top} y asistencias"),
               description=(f"Clasificación de {art}{lg} actualizada tras cada jornada: puntos, goles y racha de cada "
                            f"equipo, y las tablas de máximos goleadores y asistentes."),
               canonical=f"{config.SITE_URL}/clasificacion/{league_slug(lg)}/", rumors=[], news=[],
               archive=[], static_html=_static_table(lg, d), **common)

    # Clubes: rumores, noticias y posición en la tabla de cada uno (solo sus datos: pesan poco)
    for club, slug in _CLUB_PAGES.items():
        c_news = [n for n in news if club in n["clubs"]]
        c_rumors = [r for r in rumors if club in (r.get("clubs") or [r["from_club"], r["to_club"]])]
        ci = info.get(club)
        where = f" y su posición en {ci['league']}" if ci else ""
        intro = _club_intro(club, ci, standings, c_rumors, c_news, fx)
        liga_crumb = ((f"Clasificación de {ci['league']}", f"/clasificacion/{league_slug(ci['league'])}/"),) if ci else ()
        _write(os.path.join(out_dir, "club", slug, "index.html"), page="club", root="../../",
               club=club, club_info=ci, club_intro=intro,
               heading=f"Fichajes y rumores del {club}",
               crumbs=_crumbs("../../", *liga_crumb, (club, None)),
               ld_page=_page_ld(f"/club/{slug}/", f"Fichajes y rumores del {club}",
                                f"Rumores de fichajes, noticias y situación en la tabla del {club}.",
                                [*liga_crumb, (club, None)], lastmod.get(f"/club/{slug}/"), about=club),
               title=_fit_title(f"Fichajes y rumores del {club}: últimas noticias"),
               description=(f"Rumores de fichajes del {club} con termómetro de probabilidad, sus noticias de hoy"
                            f"{where}. Actualizado cada hora.")[:160],
               canonical=f"{config.SITE_URL}/club/{slug}/", rumors=c_rumors, news=c_news,
               archive=_archive(months, prefix="../../archivo/"),
               static_html=(f"<h2>Fichajes, rumores y noticias del {html_lib.escape(club)}</h2>"
                            + "".join(f"<p>{html_lib.escape(t)}</p>" for t in intro)
                            + _static_list(c_news, c_rumors, limit=40)), **common)

    _write(os.path.join(out_dir, "fantasy", "index.html"), page="fantasy", root="../",
           heading=_fantasy_title(standings),
           crumbs=_crumbs("../", ("LaLiga Fantasy", None)),
           ld_page=_page_ld("/fantasy/", _fantasy_title(standings),
                            "Bajas por lesión o sanción y jugadores en duda para LaLiga Fantasy.",
                            [("LaLiga Fantasy", None)], lastmod["/fantasy/"]),
           title=_fit_title(_fantasy_title(standings)),
           description=("Bajas por lesión o sanción y jugadores en duda según la prensa de los últimos días. "
                        "Comprueba tu once de LaLiga Fantasy antes de cada jornada."),
           canonical=config.SITE_URL + "/fantasy/", rumors=[], news=news, archive=[],
           static_html=_static_fantasy(fx), fx_report=fx, fx_players=fx_players, fx_ignore=ignore, **common)
    for md_ in _JORNADAS:
        _jornada_page(md_, snaps[str(md_)], _JORNADAS, out_dir)
    _clean_news_files(out_dir)
    return index


def _archive(months, prefix="", current=None):
    return [{"year": int(ym[:4]), "label": MONTHS[int(ym[5:]) - 1], "href": f"{prefix}{ym}.html",
             "news": n, "rumors": r, "current": ym == current} for ym, n, r in months]


def _clean_news_files(out_dir):
    """Borra los archivos de noticias de ejecuciones anteriores (el nombre cambia con el contenido)."""
    datos = os.path.join(out_dir, "datos")
    if os.path.isdir(datos):
        for old in os.listdir(datos):
            if old.startswith("n-") and old.endswith(".js") and old not in _NEWS_FILES:
                try:
                    os.remove(os.path.join(datos, old))
                except OSError:
                    pass


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


def write_static(months, out_dir="web", leagues=(), clubs=(), lastmod=None):
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
    with open(os.path.join(out_dir, "cookies.html"), "w", encoding="utf-8") as f:
        f.write(COOKIES_PAGE.replace("__ADSENSE__", ADSENSE).replace("__SITE_NAME__", html_lib.escape(config.SITE_NAME)))
    with open(os.path.join(out_dir, "_headers"), "w", encoding="utf-8") as f:
        f.write("/*\n  X-Frame-Options: SAMEORIGIN\n  Permissions-Policy: camera=(), microphone=(), geolocation=()\n\n"
                "/datos/*\n  Cache-Control: public, max-age=31536000, immutable\n")
    tg = telegram_url()
    contact = (f'<a href="{html_lib.escape(tg, quote=True)}" rel="noopener">nuestro canal de Telegram</a>'
               if tg else "el canal de contacto indicado en la web")
    for fname, tpl in (("sobre.html", SOBRE_PAGE), ("privacidad.html", PRIVACIDAD_PAGE), ("404.html", NOTFOUND_PAGE)):
        with open(os.path.join(out_dir, fname), "w", encoding="utf-8") as f:
            f.write(tpl.replace("__ADSENSE__", ADSENSE).replace("__SITE_NAME__", html_lib.escape(config.SITE_NAME))
                       .replace("__SITE_URL__", config.SITE_URL).replace("__CONTACT__", contact))
    if getattr(config, "INDEXNOW_KEY", ""):
        with open(os.path.join(out_dir, f"{config.INDEXNOW_KEY}.txt"), "w", encoding="utf-8") as f:
            f.write(config.INDEXNOW_KEY)
    with open(os.path.join(out_dir, "ads.txt"), "w", encoding="utf-8") as f:
        f.write(f"google.com, {config.ADSENSE_CLIENT.replace('ca-pub-', 'pub-')}, DIRECT, f08c47fec0942fa0\n")
    with open(os.path.join(out_dir, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\n\nSitemap: {config.SITE_URL}/sitemap.xml\n")
    lastmod = lastmod or {}
    # Fecha de cada página = la de su contenido más reciente (no la de hoy para todas).
    # Páginas sin fecha fiable (legales, meses cerrados del archivo): sin <lastmod>, que es opcional.
    urls = [(config.SITE_URL + "/", lastmod.get("/")),
            (config.SITE_URL + "/rumores/", lastmod.get("/rumores/")),
            (config.SITE_URL + "/rumores-fichajes-hoy/", lastmod.get("/rumores-fichajes-hoy/")),
            (config.SITE_URL + "/fantasy/", lastmod.get("/fantasy/"))]
    urls += [(config.SITE_URL + k, v) for k, v in sorted(lastmod.items())
             if k.startswith(("/fantasy/jornada-", "/jugador/", "/rumores/movimientos"))]
    urls += [(f"{config.SITE_URL}/sobre", None), (f"{config.SITE_URL}/privacidad", None)]
    urls += [(f"{config.SITE_URL}/clasificacion/{league_slug(lg)}/", lastmod.get(f"/clasificacion/{league_slug(lg)}/"))
             for lg in leagues]
    urls += [(f"{config.SITE_URL}/club/{slug}/", lastmod.get(f"/club/{slug}/")) for slug in clubs]
    current = _now_spain().strftime("%Y-%m")
    for ym, _, _ in months:
        urls.append((f"{config.SITE_URL}/archivo/{ym}", lastmod.get("/") if ym == current else None))
    body = "".join(f"<url><loc>{u}</loc>" + (f"<lastmod>{m}</lastmod>" if m else "") + "</url>" for u, m in urls)
    with open(os.path.join(out_dir, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>\n')


SOBRE_PAGE = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
__ADSENSE__
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sobre esta web | __SITE_NAME__</title>
<meta name="description" content="Qué es Rumores y Fichajes, de dónde salen los titulares y cómo funciona el termómetro de rumores.">
<link rel="canonical" href="__SITE_URL__/sobre">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>
body { margin:0; font:17px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif; background:#f2f6f3; color:#10201a; }
@media (prefers-color-scheme: dark) { body { background:#0c1611; color:#e4ece7; } }
main { max-width:720px; margin:0 auto; padding:40px 20px 60px; }
h1 { font-size:34px; line-height:1.1; margin:0 0 20px; } h2 { font-size:22px; margin:32px 0 8px; }
a { color:inherit; }
</style></head><body><main>
<p><a href="/">Volver a __SITE_NAME__</a></p>
<h1>Sobre esta web</h1>
<p>__SITE_NAME__ es un rastreador de rumores y noticias de fútbol. Recoge cada hora los titulares de medios deportivos de España y del extranjero y los ordena en un solo sitio: rumores de fichajes con termómetro, clasificaciones, goleadores, asistentes y bajas para LaLiga Fantasy.</p>
<h2>Cómo funciona</h2>
<p>La web es un índice, no una redacción: no reescribe las noticias. Cada titular enlaza a la noticia original del medio que la publicó, que conserva toda la autoría y los derechos. Un programa detecta de forma automática el jugador, el club y el tipo de movimiento (rumor, acuerdo u oficial) a partir del titular.</p>
<h2>El termómetro de rumores</h2>
<p>El termómetro (de 0° a 100°) es una estimación automática de cuánto se repite y se confirma un rumor en distintos medios. Es orientativo: no es información oficial ni una predicción. Para confirmar un fichaje, consulta siempre la comunicación oficial de los clubes.</p>
<h2>Actualización</h2>
<p>Los datos se actualizan cada hora. La fecha y hora de la última actualización aparece en la cabecera de cada página.</p>
<h2>Contacto</h2>
<p>Si eres un medio y quieres que retiremos un enlace, o si has detectado un error, escríbenos por __CONTACT__.</p>
<p><a href="privacidad">Política de privacidad</a> · <a href="cookies.html">Política de cookies</a></p>
</main></body></html>
"""

PRIVACIDAD_PAGE = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
__ADSENSE__
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Política de privacidad | __SITE_NAME__</title>
<meta name="description" content="Qué datos trata Rumores y Fichajes, para qué y qué derechos tienes.">
<link rel="canonical" href="__SITE_URL__/privacidad">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>
body { margin:0; font:17px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif; background:#f2f6f3; color:#10201a; }
@media (prefers-color-scheme: dark) { body { background:#0c1611; color:#e4ece7; } }
main { max-width:720px; margin:0 auto; padding:40px 20px 60px; }
h1 { font-size:34px; line-height:1.1; margin:0 0 20px; } h2 { font-size:22px; margin:32px 0 8px; }
a { color:inherit; }
</style></head><body><main>
<p><a href="/">Volver a __SITE_NAME__</a></p>
<h1>Política de privacidad</h1>
<p>En __SITE_NAME__ no hay registro de usuarios, formularios ni comentarios, y no pedimos datos personales.</p>
<h2>Qué datos se tratan</h2>
<p>Solo si aceptas las cookies de análisis, Google Analytics mide de forma agregada las visitas (páginas vistas, país, dispositivo). Si las rechazas, no se instala ninguna cookie de análisis. Más detalle en la <a href="cookies.html">política de cookies</a>.</p>
<p>La web guarda en tu navegador, sin enviarlo a ningún servidor, tus preferencias (filtros, equipo de Fantasy, los votos que emites en los rumores y tu respuesta al aviso de cookies). Los votos se suman de forma anónima: solo se guarda el total de síes y noses de cada rumor, sin ningún dato tuyo.</p>
<h2>Servicios de terceros</h2>
<p>Para mostrar el icono de cada medio, tu navegador solicita una imagen a Google, que puede registrar tu dirección IP según su <a href="https://policies.google.com/privacy?hl=es">política de privacidad</a>. La web se aloja en Cloudflare, que puede tratar datos técnicos de la conexión (IP, navegador) para entregar y proteger el sitio. Los enlaces a medios, Telegram o Ko-fi te llevan a sitios externos con su propia política.</p>
<h2>Tus derechos</h2>
<p>Puedes retirar tu consentimiento de cookies cuando quieras desde "Configurar cookies" en el pie de página, y ejercer tus derechos de acceso, rectificación o supresión escribiéndonos por __CONTACT__.</p>
</main></body></html>
"""

NOTFOUND_PAGE = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
__ADSENSE__
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Página no encontrada | __SITE_NAME__</title>
<meta name="robots" content="noindex">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>
body { margin:0; font:17px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif; background:#f2f6f3; color:#10201a; }
@media (prefers-color-scheme: dark) { body { background:#0c1611; color:#e4ece7; } }
main { max-width:720px; margin:0 auto; padding:40px 20px 60px; }
h1 { font-size:34px; line-height:1.1; margin:0 0 20px; } h2 { font-size:22px; margin:32px 0 8px; }
a { color:inherit; }
</style></head><body><main>
<p><a href="/">Volver a __SITE_NAME__</a></p>
<h1>Página no encontrada</h1>
<p>La página que buscas no existe o se ha movido.</p>
<p><a href="/">Ir a la portada</a> · <a href="/rumores/">Rumores de fichajes</a> · <a href="/fantasy/">Bajas para Fantasy</a></p>
</main></body></html>
"""

COOKIES_PAGE = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
__ADSENSE__
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Política de cookies | __SITE_NAME__</title>
<meta name="robots" content="noindex">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<style>
body { margin:0; font:17px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif; background:#f2f6f3; color:#10201a; }
@media (prefers-color-scheme: dark) { body { background:#0c1611; color:#e4ece7; } table, th, td { border-color:#24352c !important; } }
main { max-width:720px; margin:0 auto; padding:40px 20px 60px; }
h1 { font-size:34px; line-height:1.1; margin:0 0 20px; } h2 { font-size:22px; margin:32px 0 8px; }
table { border-collapse:collapse; width:100%; font-size:15px; } th, td { border:1px solid #dbe3de; padding:8px 10px; text-align:left; vertical-align:top; }
a { color:inherit; }
</style></head><body><main>
<p><a href="./">Volver a __SITE_NAME__</a></p>
<h1>Política de cookies</h1>
<p>Esta web solo usa cookies de análisis, y únicamente si las aceptas en el aviso que aparece al entrar. Si las rechazas o no respondes, no se instala ninguna.</p>
<h2>Qué cookies usamos</h2>
<table>
<tr><th>Cookie</th><th>Proveedor</th><th>Para qué sirve</th><th>Duración</th></tr>
<tr><td>_ga</td><td>Google Analytics</td><td>Distinguir visitantes de forma anónima para contar cuántas personas visitan la web.</td><td>2 años</td></tr>
<tr><td>_ga_*</td><td>Google Analytics</td><td>Mantener el estado de la visita (páginas vistas, duración).</td><td>2 años</td></tr>
</table>
<p>Además, la web guarda en tu navegador (no en una cookie) tu respuesta a este aviso, los filtros que elijas (como la liga o los medios ocultos) y tu equipo de Fantasy, para recordarlos en tu próxima visita. Esa información no sale de tu dispositivo.</p>
<h2>Contador de visitas</h2>
<p>El contador del pie de página solo suma un número total. Para no contarte dos veces el mismo día, la web guarda en tu navegador la fecha de tu última visita contada. No se guarda ni se envía ningún dato que te identifique.</p>
<h2>Google Analytics</h2>
<p>Google Analytics es un servicio de Google que nos muestra estadísticas agregadas de uso. Google puede tratar estos datos según su propia <a href="https://policies.google.com/privacy?hl=es">política de privacidad</a>.</p>
<h2>Cómo cambiar tu elección</h2>
<p>Puedes aceptar o retirar tu consentimiento en cualquier momento con el enlace "Configurar cookies" del pie de cada página. También puedes borrar las cookies desde la configuración de tu navegador.</p>
<h2>Contenido de terceros</h2>
<p>Los titulares mostrados pertenecen a sus respectivos medios. Al pulsar uno, sales de esta web y pasas a la del medio, que tiene su propia política de cookies.</p>
</main></body></html>
"""
