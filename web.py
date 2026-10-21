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
.pitch::before { content:""; position:absolute; top:-90px; right:calc(var(--line-right, calc(8% + 120px)) - 120px);
  width:240px; height:240px; border:3px solid rgba(255,255,255,.28); border-radius:50%; }
.pitch::after { content:""; position:absolute; top:0; bottom:0; right:var(--line-right, calc(8% + 120px));
  border-left:3px solid rgba(255,255,255,.28); }
/* La columna derecha y el selector de clubes se estiran hasta la línea de medio campo (ver alignToHalfway) */
@media (min-width:1101px) {
  .layout .dates, .tools select { margin-right:calc(-1 * var(--to-halfway, 0px)); }
}
.pitch .wrap { position:relative; z-index:1; padding-top:30px; }
h1 { font:700 clamp(34px,6vw,52px)/.95 var(--cond); margin:0; letter-spacing:-.005em; }
.updated { margin:8px 0 0; font-size:14px; opacity:.85; }
.crumbs { display:flex; gap:16px; flex-wrap:wrap; margin:10px 0 0; font-size:15px; }
.crumbs a { color:#fff; }
.tools { display:flex; gap:10px; flex-wrap:wrap; margin-top:20px; }
.tools input, .tools select { font:inherit; font-size:15px; padding:10px 12px; border-radius:6px;
  border:0; background:rgba(255,255,255,.95); color:#10201a; }
.tools input { flex:1; min-width:200px; }
.tools[hidden] { display:none !important; }
/* En pantalla ancha, el buscador acaba donde acaba la columna de noticias
   y el selector de clubes ocupa el ancho de la columna derecha */
@media (min-width:1101px) {
  .tools { display:grid; grid-template-columns:minmax(0, 1fr) 200px; column-gap:36px; }
  .tools input { min-width:0; }
}
.tabs { display:flex; gap:4px; margin-top:22px; overflow-x:auto; scrollbar-width:none; }
.tab { font:600 19px/1 var(--cond); letter-spacing:.01em; color:#fff; background:transparent;
  border:0; border-radius:6px 6px 0 0; padding:11px 18px 10px; cursor:pointer; opacity:.8; }
.tab:hover { opacity:1; }
.tab.on { background:var(--chalk); color:var(--ink); opacity:1; }
.tab .n { font-weight:500; opacity:.6; margin-left:4px; }
a.tab { text-decoration:none; display:inline-block; }
.sm-only { display:none; }
@media (max-width:560px) { .sm-only { display:inline; } .lg-only { display:none; } }

main { padding:6px 0 60px; max-width:860px; }
.layout { display:grid; grid-template-columns:210px minmax(0, 1fr) 200px; gap:36px; align-items:start; }
.filters, .dates { padding:22px 0 30px; }
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
.layout.solo { grid-template-columns:minmax(0, 860px); }
.layout.solo .filters, .layout.solo .dates { display:none; }
.layout.solo main { grid-column:1 !important; grid-row:auto !important; }
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
  border:1px solid var(--line); border-left:5px solid var(--off); border-radius:8px; padding:14px 16px; }
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
.tb-wrap { overflow-x:auto; background:var(--card); border:1px solid var(--line); border-radius:8px; }
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
.pitch .wrap { padding-right:20px; }
.kofi-top { position:absolute; top:22px; right:20px; z-index:2; display:flex; flex-direction:column;
  align-items:flex-end; gap:8px; }
.kofi-top .visits { font-size:13px; color:#fff; background:rgba(255,255,255,.16); padding:4px 10px;
  border-radius:20px; }
.kofi-top .visits b { color:#fff; }
.kofi { display:inline-flex; align-items:center; gap:8px; font:600 15px/1 var(--body); text-decoration:none;
  padding:9px 14px; border-radius:20px; background:#fff; color:#145a32; box-shadow:0 2px 8px rgba(0,0,0,.15); }
.kofi:hover { background:#fff7e6; }
.top-btns { display:flex; gap:8px; }
.kofi.tg { color:#1b6fa8; } .kofi.tg:hover { background:#eaf5fd; }
.kofi svg { display:block; }
.foot .kofi { box-shadow:none; border:1px solid var(--line); background:var(--card); color:var(--ink); text-decoration:none; }
.visits { font-variant-numeric:tabular-nums; }
.visits b { color:var(--ink); }
@media (max-width:560px) { .top-btns { gap:6px; } .kofi.tg .tg-txt { display:none; } .kofi-top { top:14px; right:12px; gap:6px; } .kofi-top .visits { font-size:12px; padding:3px 8px; } .kofi-top .kofi { padding:7px 11px; font-size:13px; } .kofi-top .kofi .long { display:none; } }

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
/* Lo más leído */
.side-read:empty { display:none; }
.top-read { display:none !important; }
@media (max-width:820px) { .top-read { display:block !important; } .side-read { display:none; } }
.side-read .hd { display:flex; flex-direction:column; align-items:flex-start; gap:8px; margin-bottom:8px; }
.side-read .seg { margin-left:0; } .side-read .seg button { white-space:nowrap; }
.side-read .flabel { margin:0; }
.side-read .seg button { padding:4px 8px; font-size:12px; }
.side-read ol { list-style:none; margin:0; padding:0; counter-reset:r; }
.side-read { padding-bottom:16px; border-bottom:1px solid var(--line); }
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
.top-read { background:var(--card); border:1px solid var(--line); border-radius:8px; padding:14px 16px 6px; margin:20px 0 4px; }
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

details.slot { margin:8px 0; border-top:0; padding-top:0; }
.slot > summary { list-style:none; cursor:pointer; display:flex; align-items:center; gap:12px; padding:11px 16px;
  background:var(--card); border:1px solid var(--line); border-radius:8px; user-select:none; }
.slot > summary::-webkit-details-marker { display:none; }
.slot > summary:hover { border-color:var(--grass-2); }
.slot .hrs { font:600 19px/1 var(--cond); font-variant-numeric:tabular-nums; color:var(--ink); }
.slot .lbl { font-size:13px; color:var(--muted); }
.slot .cnt { margin-left:auto; font-size:14px; color:var(--muted); font-variant-numeric:tabular-nums; }
.slot .hrs, .slot .cnt { white-space:nowrap; }
@media (max-width:560px) { .slot .lbl { display:none; } .slot > summary { padding:10px 12px; gap:8px; } .slot .hrs { font-size:18px; } }
.slot .chev { width:9px; height:9px; border-right:2px solid var(--muted); border-bottom:2px solid var(--muted);
  transform:rotate(45deg); margin:-4px 4px 0 2px; transition:transform .15s; }
.slot[open] .chev { transform:rotate(-135deg); margin-top:4px; }
.slot[open] > summary { border-radius:8px 8px 0 0; border-bottom-color:transparent; }
.slot > .news { border-radius:0 0 8px 8px; border-top:0; }
.news li { display:grid; grid-template-columns:28px 1fr; gap:12px; padding:12px 16px;
  border-top:1px solid var(--line); }
.news li:first-child { border-top:0; }
.news .t { font-weight:500; text-decoration:none; }
.news .t:hover { text-decoration:underline; }
.meta { display:flex; flex-wrap:wrap; gap:6px 10px; align-items:center; margin-top:4px;
  font-size:13px; color:var(--muted); }
.time { font-variant-numeric:tabular-nums; }
.club { color:var(--ink); font-weight:500; text-decoration:none; }
a.club:hover { text-decoration:underline; }
.route a { color:inherit; text-decoration:none; } .route a:hover { text-decoration:underline; }
.share { display:inline-flex; align-items:center; gap:5px; font:500 13px/1 var(--body); color:var(--muted);
  background:transparent; border:1px solid var(--line); border-radius:20px; padding:5px 10px; cursor:pointer; }
.share:hover { color:var(--ink); border-color:var(--grass-2); }
.share.ico { padding:4px 7px; border-color:transparent; margin-left:auto; }
.share.ico:hover { border-color:var(--line); }
.promo { display:flex; gap:14px; align-items:center; flex-wrap:wrap; background:var(--card); border:1px solid var(--line);
  border-left:5px solid #2a9fd8; border-radius:8px; padding:14px 16px; margin:20px 0 4px; font-size:15px; }
.promo p { margin:0; flex:1 1 320px; }
.promo a.join { display:inline-flex; align-items:center; gap:7px; font:600 15px/1 var(--body); text-decoration:none;
  color:#fff; background:#1b6fa8; padding:10px 14px; border-radius:20px; white-space:nowrap; }
.sec-h { font:700 24px/1.1 var(--cond); margin:26px 0 4px; }
.sec-h small { font:500 14px/1 var(--body); color:var(--muted); margin-left:8px; }
.club-box { background:var(--card); border:1px solid var(--line); border-radius:8px; padding:16px 18px; margin:20px 0 6px; }
.club-box h2 { font:700 26px/1.1 var(--cond); margin:0 0 6px; }
.club-box p { margin:0; color:var(--muted); }
.club-box p + p { margin-top:10px; }
.crumbs .sep { opacity:.6; }
.club-box a { color:var(--ink); font-weight:600; }
details.foot-clubs { width:100%; font-size:13px; line-height:1.9; border-top:0; padding-top:0; margin-top:0; }
.foot-clubs > summary { cursor:pointer; font-size:14px; color:var(--muted); width:max-content; }
.foot-clubs > summary:hover { color:var(--ink); }
.foot-clubs nav { margin-top:8px; }
.foot-clubs a { margin-right:12px; white-space:nowrap; }
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
.also { margin:4px 0 0; font-size:14px; color:var(--muted); }
.also a { color:var(--ink); text-decoration:none; } .also a:hover { text-decoration:underline; }
.status-mini { font-size:12px; font-weight:600; padding:1px 7px; border-radius:20px; color:#fff; }
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
    __KOFI_TOP__
    <h1>__HEADING__</h1>
    <p class="updated">__TAGLINE__Actualizado el __UPDATED__. Cada titular enlaza a la noticia original.</p>
    __CRUMBS__
    <div class="tools"__TOOLS_HIDDEN__>
      <input id="q" type="search" placeholder="Buscar jugador, club o medio" aria-label="Buscar">
      <select id="club" aria-label="Filtrar por club"><option value="">Todos los clubes</option></select>
    </div>
    <nav class="tabs" id="tabs" aria-label="Secciones">__TABS__</nav>
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
    <div class="fgroup side-read" id="side-read"></div>
    <div class="fgroup"><h2 class="flabel" id="days-title">Últimos días</h2>
      <div class="flist" id="f-days" role="group" aria-label="Elegir día"></div></div>
    <div class="fgroup" id="history-box"><h2 class="flabel">Historial</h2>
      <div class="flist" id="f-months"></div></div>
  </aside>
</div>
<footer class="wrap foot">
  __CLUB_FOOTER__
  <span>Los titulares pertenecen a sus medios; cada uno enlaza a la noticia original.</span>
  __KOFI_FOOT__
  __TG_FOOT__
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
<script>const RECENT_DAYS = __RECENT_DAYS__; const TG_URL = "__TG_URL__";</script>
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
  if (id === "table") return dirUrl(ROOT + "clasificacion/" + (LEAGUE_SLUGS[load("liga-tabla", "LaLiga")] || "laliga") + "/");
  return dirUrl(ROOT);
}
const tabs = [["news", "Noticias", COUNTS.news], ["rumors", "Rumores", COUNTS.rumors]];
if (!IS_ARCHIVE) tabs.push(["table", "Clasificación", null], ["fantasy", "Fantasy", null]);
let tab = PAGE;
const hashTab = (location.hash || "").slice(1);
if (IS_ARCHIVE) { if (["news", "rumors"].includes(hashTab)) tab = hashTab; }
else if (["news", "rumors", "table", "fantasy"].includes(hashTab) && hashTab !== PAGE) location.replace(pageUrl(hashTab));  // enlaces antiguos con #
let day = "";   // "" = recientes (portada) o todo el mes (archivo); si no, AAAA-MM-DD
const nav = document.getElementById("tabs");
nav.replaceChildren();   // quita las pestañas en HTML normal; aquí se rehacen con contadores
for (const [id, label, n] of tabs) {
  const b = el(IS_ARCHIVE ? "button" : "a", "tab"); b.dataset.tab = id;
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
  const pool = tab === "rumors" ? rumors.filter(r => rumorDayOk(r) && r.mentions.some(m => !hidden.has(m.source)))
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

function newsItem(n) {
  const li = el("li"), body = el("div"), a = el("a", "t", n.title);
  a.href = n.url; a.target = "_blank"; a.rel = "noopener";
  const meta = el("div", "meta");
  meta.append(el("span", "time", hhmm(n.date)), el("span", null, n.source));
  if (n.live) meta.append(el("span", "tag live", "En directo"));
  if (n.rumor) meta.append(el("span", "tag rum", "Rumor"));
  for (const c of n.clubs) meta.append(clubLink(c, "club"));
  meta.append(shareBtn("📰 " + n.title + " (" + n.source + ")\n" + n.url + "\n\nMás noticias y rumores en", SITE_URL + "/", true));
  body.append(a, meta); li.append(outlet(n.url, n.source), body);
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

function rumorCard(r) {
  const card = el("article", "rumor"), left = el("div");
  left.append(el("h3", "player", r.player));
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
  row.append(el("span", "status st-" + best, STATUS[best] || best));
  const outlets = el("span", "outlets"), seen = new Set();
  for (const m of r.mentions) if (!seen.has(m.source)) { seen.add(m.source); outlets.append(outlet(m.url, m.source, true)); }
  row.append(outlets);
  const fee = r.mentions.map(m => m.fee).find(f => f);
  if (fee) row.append(el("span", "fee", fee + " millones"));
  const shareText = (best === "oficial" ? "✅ Fichaje cerrado: " : "🔥 Rumor: ") + r.player + ", " +
    (r.from_club || "?") + " → " + (r.to_club || "?") + (best === "oficial" ? "" : " (" + r.score + "° en el termómetro)");
  row.append(shareBtn(shareText, SITE_URL + "/rumores/"));
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
for (const cat of ["back", "susp", "out", "doubt"]) for (const w of FXW[cat]) FX_PHRASES.push([w.split(" "), cat]);
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
    const gaps = spans.map((sp, i) => [Math.max(sp[0] - e, s - sp[1], 0), group[i], sp[2], sp[1]]);
    const best = Math.min(...gaps.map(g => g[0]));
    if (best > FXR.window) continue;
    const neg = fxNegated(toks, s, e);
    const eff = !neg ? cat : (cat === "back" ? "doubt" : "ok");
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
  q.disabled = sel.disabled = solo;
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

// La línea de medio campo va a "8% + 120px" del borde derecho de la cabecera (como en el diseño original).
// Si así queda a la derecha del contenido, la columna derecha y el selector se estiran hasta ella;
// si caería encima de la columna, la línea se coloca justo en el borde del contenido.
function alignToHalfway() {
  const pitch = document.querySelector(".pitch"), layout = document.querySelector(".layout");
  const root = document.documentElement.style;
  if (!pitch || !layout || window.innerWidth <= 1100) {
    root.removeProperty("--to-halfway"); root.removeProperty("--line-right"); return;
  }
  const r = pitch.getBoundingClientRect(), lr = layout.getBoundingClientRect();
  const contentRight = lr.right - parseFloat(getComputedStyle(layout).paddingRight);
  const original = r.right - (r.width * 0.08 + 120) - 1.5;      // centro de la línea en el diseño original
  const target = Math.max(original, contentRight);
  root.setProperty("--to-halfway", Math.round(target - contentRight) + "px");
  root.setProperty("--line-right", (r.right - Math.round(target) - 1.5) + "px");
}
alignToHalfway();
window.addEventListener("resize", alignToHalfway);
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
    html = (TEMPLATE
            .replace("__DESCRIPTION__", esc(description, quote=True))
            .replace("__CANONICAL__", esc(canonical, quote=True))
            .replace("__SITE_NAME__", esc(config.SITE_NAME, quote=True))
            .replace("__TAGLINE__", esc(tagline) + " " if tagline else "")
            .replace("__SITE_URL__", config.SITE_URL)
            .replace("__ROOT__", root)
            .replace("__VERIFICATION__", verification)
            .replace("__LDJSON__", _json(ld))
            .replace("__STATIC__", static_html if static_html is not None else _static_list(list(news), rumors))
            .replace("__ANALYTICS__", ANALYTICS.replace("__GA_ID__", config.GA_MEASUREMENT_ID)
                     if config.GA_MEASUREMENT_ID else "")
            .replace("__COOKIE_BUTTON__", '<button id="ck-config">Configurar cookies</button>'
                     if config.GA_MEASUREMENT_ID else "")
            .replace("__KOFI_TOP__", '<div class="kofi-top"><div class="top-btns">' + (
                         f'<a class="kofi tg" href="{esc(telegram_url(), quote=True)}" target="_blank" rel="noopener" '
                         f'aria-label="Síguenos en Telegram"><span>__PLANE__</span><span class="tg-txt">Síguenos en Telegram</span></a>'
                         if telegram_url() else "") + (
                         f'<a class="kofi" href="{esc(config.KOFI_URL, quote=True)}" target="_blank" rel="noopener">'
                         f'<span>☕</span><span><span class="long">Invítame a un </span>café</span></a>'
                         if config.KOFI_URL else "") + '</div><span class="visits" id="visits" hidden></span></div>')
            .replace("__TG_URL__", telegram_url())
            .replace("__TG_FOOT__", f'<a href="{esc(telegram_url(), quote=True)}" target="_blank" rel="noopener">'
                                    f'Canal de Telegram</a>' if telegram_url() else "")
            .replace("__KOFI_FOOT__", (f'<a class="kofi" href="{esc(config.KOFI_URL, quote=True)}" target="_blank" '
                                       f'rel="noopener"><span>☕</span><span>¿Te es útil? Invítame a un café en Ko-fi</span></a>') if config.KOFI_URL else "")
            .replace("__VISITS__", "true" if config.VISIT_COUNTER else "false")
            .replace("__PLANE__", PLANE_ICON)
            .replace("__ROOT__", root))
    html = (html
            .replace("__TITLE__", title).replace("__HEADING__", heading).replace("__CRUMBS__", crumbs)
            .replace("__UPDATED__", _now_spain().strftime("%d/%m/%Y a las %H:%M"))
            .replace("__IS_ARCHIVE__", "true" if is_archive else "false")
            .replace("__RUMORS__", _json(rumors)).replace("__NEWSTAG__", _news_tag(path, root, list(news), inline=is_archive))
            .replace("__ARCHIVE__", _json(archive)).replace("__LEAGUES__", _json(config.LEAGUES))
            .replace("__PLAYERS__", _json(_players()))
            .replace("__DOMAINS__", _json(_domains()))
            .replace("__STANDINGS__", _json(standings if standings is not None else ({} if is_archive else _standings())))
            .replace("__PAGE__", page)
            .replace("__TOOLS_HIDDEN__", " hidden" if page in ("table", "fantasy") else "")
            .replace("__COUNTS__", _json(counts or {"news": len(list(news)), "rumors": len(rumors)}))
            .replace("__TABLE_LEAGUE__", _json(table_league))
            .replace("__LEAGUE_SLUGS__", _json({lg: league_slug(lg) for lg in config.STANDINGS_COMPETITIONS}))
            .replace("__FX_REPORT__", _json(list(fx_report)))
            .replace("__FX_WORDS__", _json({**config.FANTASY_WORDS, "rules": config.FANTASY_RULES}))
            .replace("__FX_PLAYERS__", _json(fx_players or {}))
            .replace("__FX_IGNORE__", _json(list(fx_ignore)))
            .replace("__CLUB_SLUGS__", _json(_CLUB_PAGES))
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


PLANE_ICON = '<svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path fill="currentColor" d="M2.5 11.2 20.6 4.3c.8-.3 1.5.2 1.3 1.3l-3.1 14.5c-.2 1-.8 1.2-1.6.8l-4.6-3.4-2.2 2.1c-.3.3-.5.4-.9.4l.3-4.7 8.5-7.7c.4-.3-.1-.5-.6-.2L7.2 14.1l-4.5-1.4c-1-.3-1-1 .2-1.5z"/></svg>'

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


def _fantasy_title(standings):
    md = (standings.get("LaLiga") or {}).get("matchday")
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
             ("fantasy", "Fantasy", f"{root}fantasy/")]
    return "".join(f'<a class="tab{" on" if page == id_ else ""}" data-tab="{id_}" href="{href}"'
                   f'{" aria-current=" + chr(34) + "page" + chr(34) if page == id_ else ""}>{label}</a>'
                   for id_, label, href in items)


def _sections_footer(root):
    """Enlaces visibles a todas las secciones en el pie de cada página."""
    esc = html_lib.escape
    links = [("Noticias", root or "./"), ("Rumores de fichajes", f"{root}rumores/"),
             ("LaLiga Fantasy", f"{root}fantasy/")]
    links += [(f"Clasificación de {lg}", f"{root}clasificacion/{league_slug(lg)}/") for lg in config.STANDINGS_COMPETITIONS]
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
    if about:
        page["about"] = {"@type": "SportsTeam", "name": about}
    out = [page]
    if crumbs:
        items = [(config.SITE_NAME, "/")] + list(crumbs)
        out.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i, "name": text, "item": config.SITE_URL + (p or path)}
            for i, (text, p) in enumerate(items, 1)]})
    return out


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
                            [("Rumores de fichajes", None)], lastmod["/rumores/"]),
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
        f.write(COOKIES_PAGE.replace("__SITE_NAME__", html_lib.escape(config.SITE_NAME)))
    with open(os.path.join(out_dir, "_headers"), "w", encoding="utf-8") as f:
        f.write("/*\n  X-Frame-Options: SAMEORIGIN\n  Permissions-Policy: camera=(), microphone=(), geolocation=()\n\n"
                "/datos/*\n  Cache-Control: public, max-age=31536000, immutable\n")
    tg = telegram_url()
    contact = (f'<a href="{html_lib.escape(tg, quote=True)}" rel="noopener">nuestro canal de Telegram</a>'
               if tg else "el canal de contacto indicado en la web")
    for fname, tpl in (("sobre.html", SOBRE_PAGE), ("privacidad.html", PRIVACIDAD_PAGE), ("404.html", NOTFOUND_PAGE)):
        with open(os.path.join(out_dir, fname), "w", encoding="utf-8") as f:
            f.write(tpl.replace("__SITE_NAME__", html_lib.escape(config.SITE_NAME))
                       .replace("__SITE_URL__", config.SITE_URL).replace("__CONTACT__", contact))
    if getattr(config, "INDEXNOW_KEY", ""):
        with open(os.path.join(out_dir, f"{config.INDEXNOW_KEY}.txt"), "w", encoding="utf-8") as f:
            f.write(config.INDEXNOW_KEY)
    with open(os.path.join(out_dir, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\n\nSitemap: {config.SITE_URL}/sitemap.xml\n")
    lastmod = lastmod or {}
    # Fecha de cada página = la de su contenido más reciente (no la de hoy para todas).
    # Páginas sin fecha fiable (legales, meses cerrados del archivo): sin <lastmod>, que es opcional.
    urls = [(config.SITE_URL + "/", lastmod.get("/")),
            (config.SITE_URL + "/rumores/", lastmod.get("/rumores/")),
            (config.SITE_URL + "/fantasy/", lastmod.get("/fantasy/"))]
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
<p>La web guarda en tu navegador, sin enviarlo a ningún servidor, tus preferencias (filtros, equipo de Fantasy y tu respuesta al aviso de cookies).</p>
<h2>Servicios de terceros</h2>
<p>Para mostrar el icono de cada medio, tu navegador solicita una imagen a Google, que puede registrar tu dirección IP según su <a href="https://policies.google.com/privacy?hl=es">política de privacidad</a>. La web se aloja en Cloudflare, que puede tratar datos técnicos de la conexión (IP, navegador) para entregar y proteger el sitio. Los enlaces a medios, Telegram o Ko-fi te llevan a sitios externos con su propia política.</p>
<h2>Tus derechos</h2>
<p>Puedes retirar tu consentimiento de cookies cuando quieras desde "Configurar cookies" en el pie de página, y ejercer tus derechos de acceso, rectificación o supresión escribiéndonos por __CONTACT__.</p>
</main></body></html>
"""

NOTFOUND_PAGE = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
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
