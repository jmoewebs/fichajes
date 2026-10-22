"""Parte médico general para Fantasy: bajas, dudas y recuperados según los titulares recientes.

Los jugadores que se buscan salen de jugadores.csv y de los goleadores de cada liga
(clasificaciones.json). Para cada uno manda el titular más reciente que hable de su estado.
Usa las mismas palabras que la herramienta de la web (config.FANTASY_WORDS)."""
from datetime import datetime, timedelta, timezone

import config
from pipeline import norm


def _n(text):
    return " ".join(norm(text or "").split())


def _has(padded, words):
    return next((w for w in words if f" {w} " in padded), None)


def load_ignore(path=None):
    """Fragmentos de titulares que Fantasy debe ignorar (uno por línea; # = comentario)."""
    import os
    path = path or config.FANTASY_IGNORE_FILE
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return [l.strip() for l in fh if l.strip() and not l.lstrip().startswith("#")]


def candidates(players_index=(), standings=None):
    """{nombre: {"keys": set(formas normalizadas), "team": equipo o None}}"""
    out = {}
    for alias, (name, club) in players_index:
        c = out.setdefault(name, {"keys": set(), "team": club})
        c["keys"].update({alias, _n(name)})
    for league in (standings or {}).values():
        for s in league.get("scorers", []):
            if not s.get("player"):
                continue
            c = out.setdefault(s["player"], {"keys": set(), "team": s.get("team")})
            c["keys"].add(_n(s["player"]))
            c["team"] = c["team"] or s.get("team")
    # El apellido solo vale si es largo, poco común y no lo comparte nadie más de la lista
    last = {}
    for name in out:
        parts = _n(name).split()
        if len(parts) > 1:
            last.setdefault(parts[-1], []).append(name)
    for surname, names in last.items():
        if len(names) == 1 and len(surname) >= 4 and surname not in config.COMMON_SURNAMES:
            out[names[0]]["keys"].add(surname)
    for c in out.values():
        c["keys"] = {k for k in c["keys"] if len(k) >= 3}
    return out


LABELS = {"back": "Recuperado", "susp": "Baja por sanción", "out": "Baja", "doubt": "Duda", "ok": "Disponible"}
PRIORITY = ["back", "susp", "out", "doubt", "ok"]


def _phrases(words_by_cat):
    out = []
    for cat, words in words_by_cat.items():
        out += [(w.split(), cat) for w in words]
    return sorted(out, key=lambda p: -len(p[0]))


def _spans(tokens, phrases):
    """Todas las apariciones (inicio, fin, dato) de cada frase (lista de palabras) en la lista de palabras."""
    found = []
    for ptoks, data in phrases:
        n = len(ptoks)
        for i in range(len(tokens) - n + 1):
            if tokens[i:i + n] == ptoks:
                found.append((i, i + n, data))
    return found


def _negated(toks, s, e):
    rules = config.FANTASY_RULES
    if s >= 1 and toks[s - 1] in rules["neg_adjacent"]:
        return True
    if s >= 2 and toks[s - 2] in rules["neg_adjacent"] and toks[s - 1] in rules["neg_fillers"]:
        return True
    if any(t in rules["avoid"] for t in toks[max(0, s - 3):s]):
        return True
    return any(t in rules["neg_after"] for t in toks[e:e + 1])


def _victim(toks, s, e, ps, pe):
    """El estado (s, e) no es del jugador (ps, pe): este recibe la acción que lo causa ("sanción por ... a X")
    o se le cita como remedio de las bajas de otros ("Rodri ante las tres bajas")."""
    rules = config.FANTASY_RULES
    if e < ps and toks[ps - 1] in rules["victim"] and any(t in rules["cause"] for t in toks[e:ps - 1]):
        return True
    return pe <= s and any(t in rules["apart"] for t in toks[pe:s])


_NO_NAME_BEFORE ={"sin", "con", "tras", "por", "para", "ante", "contra", "sobre", "segun", "como", "que", "y", "e"}
_REPLACES = ["sustituto de", "sustituta de", "plan b de", "relevo de", "recambio de", "suplente de", "reemplazo de",
             "alternativa a", "heredero de", "sucesor de", "ausencia de", "hueco de", "puesto de", "lugar de"]


def _is_that_player(span, toks, cap, players):
    """Descarta un acierto dudoso: un apellido suelto precedido de otro nombre propio ("Borja Iglesias" no es
    "Juan Iglesias") o un jugador citado como a quien sustituye otro ("Kroupi, el plan B de Álvarez")."""
    s, e, name = span
    own = set(_n(name).split())
    s0 = s
    while s0 > 0 and toks[s0 - 1] in own:                 # empieza antes si el nombre va completo
        s0 -= 1
    for phrase in _REPLACES:
        p = phrase.split()
        if s0 >= len(p) and toks[s0 - len(p):s0] == p:
            return False
    if e - s == 1 and len(own) > 1 and s >= 1 and cap[s - 1] and cap[s] \
            and toks[s - 1] not in own and toks[s - 1] not in _NO_NAME_BEFORE and len(toks[s - 1]) > 2:
        return False
    # Lo mismo con un nombre propio detrás: "David González" no es "Jonathan David"
    if e - s == 1 and len(own) > 1 and e < len(toks) and cap[s] and cap[e] \
            and toks[e] not in own and toks[e] not in _STATUS_TOKENS and len(toks[e]) > 2:
        return False
    return True


_STATUS_TOKENS = {t for words in config.FANTASY_WORDS.values() for w in words for t in w.split()}


def analyze(title, players):
    """Estado de cada jugador que aparece en un titular. players = {nombre: {"keys": {...}}}.
    Devuelve {nombre: "back" | "susp" | "out" | "doubt" | "ok"}."""
    rules = config.FANTASY_RULES
    toks, cap = [], []                                  # palabras y si empezaban en mayúscula
    for w in str(title).split():
        parts = _n(w).split()
        toks += parts
        cap += [w[:1].isupper()] * len(parts)
    for idiom in rules["idioms"]:                       # "sin duda", "altas y bajas"... no cuentan
        for s, e, _ in _spans(toks, [(idiom.split(), None)]):
            toks[s:e] = ["_"] * (e - s)
    spans = _spans(toks, [(k.split(), name) for name, c in players.items() for k in c["keys"]])
    spans = [sp for sp in spans if _is_that_player(sp, toks, cap, players)]
    if not spans:
        return {}
    # Jugadores enumerados ("Lamine Yamal, Pedri y Raphinha") forman un grupo: comparten el mismo sujeto
    spans.sort()
    group, gid = [], 0
    for i, (ps, pe, name) in enumerate(spans):
        if i and ps - spans[i - 1][1] > 0 and toks[spans[i - 1][1]:ps] not in (["y"], ["e"], ["and"]):
            gid += 1
        group.append(gid)
    found = {}
    for s, e, cat in _spans(toks, _phrases(config.FANTASY_WORDS)):
        if cat == "susp" and any(t in rules["fine"] for t in toks):
            continue
        # Jugador (o grupo) más cercano a la palabra de estado
        # (la víctima de "sanción por los cabezazos a X" queda fuera de alcance)
        gaps = [(99 if _victim(toks, s, e, ps, pe) else max(ps - e, s - pe, 0), grp, name)
                for (ps, pe, name), grp in zip(spans, group)]
        best = min(g for g, _, _ in gaps)
        if best > rules["window"]:
            continue
        neg = _negated(toks, s, e)
        eff = cat if not neg else ("doubt" if cat in ("back", "ok") else "ok")
        winners = {grp for g, grp, _ in gaps if g == best}
        group_end = {grp: max(pe for (ps, pe, _), gg in zip(spans, group) if gg == grp) for grp in winners}
        for g, grp, name in gaps:
            # El estado se comparte con todo el grupo solo si va detrás de la lista ("X y Y, sancionados");
            # si va antes ("sanción a X y Y") se atribuye únicamente al jugador más cercano.
            if (grp in winners and s >= group_end[grp]) or g == best:
                found.setdefault(name, set()).add(eff)
    return {name: next(c for c in PRIORITY if c in cats) for name, cats in found.items()}


def report(news, cands, days=None, ignore=()):
    """Lista de {player, team, st, label, title, url, source, date, age}: primero bajas, luego dudas y recuperados.
    Para cada jugador manda el titular más reciente que hable de su estado y que siga vigente."""
    rules = config.FANTASY_RULES
    days = days or config.FANTASY_DAYS
    now = datetime.now(timezone.utc)
    cutoff = (now - timedelta(days=days)).isoformat()
    ign = [" ".join(_n(i).split()) for i in ignore if i.strip()]
    items = [n for n in news if n["date"] >= cutoff and not any(i in _n(n["title"]) for i in ign)]
    items.sort(key=lambda n: n["date"], reverse=True)
    done = {}
    for n in items:
        age = (now - datetime.fromisoformat(n["date"])).total_seconds() / 86400
        for name, st in analyze(n["title"], cands).items():
            if name in done:
                continue
            label = LABELS[st]
            if age > rules["stale"][st]:
                if st != "susp" or not _has(f" {_n(n['title'])} ",
                                            [w for w in config.FANTASY_WORDS["susp"] if w not in rules["red_only"]]):
                    continue                     # un aviso caducado se ignora y se mira el siguiente más antiguo
                                                 # (también una simple expulsión: sin sanción explícita no hay nada que comprobar)
                st, label = "doubt", f"Sanción de hace {int(age)} días: comprueba si sigue"
            done[name] = {"player": name, "team": cands[name].get("team"), "st": {"susp": "out"}.get(st, st),
                          "label": label, "title": n["title"], "url": n["url"], "source": n["source"],
                          "date": n["date"], "age": round(age, 1)}
    out = [r for r in done.values() if r["st"] != "ok"]      # "Disponible" no hace falta listarlo en el parte
    order = {"out": 0, "doubt": 1, "back": 2}
    out.sort(key=lambda r: r["date"], reverse=True)
    out.sort(key=lambda r: order[r["st"]])
    return out
