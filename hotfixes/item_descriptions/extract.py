#!/usr/bin/env python3
"""Fase 1 del plan de descripciones de objetos: EXTRAE datos de PokeAPI y los cruza con pokemon.db.

NO modifica pokemon.db (solo la lee). Genera en --out:
  items_text.csv      db_item_id,lang,text,source,version_group_id
  machine_moves.csv   game,game_id,kind,number,db_item_id,raw_item_id,move_id,move_en,version_group_id
  unmatched_items.csv objetos de la base sin pareja en PokeAPI (con sugerencias de alias)
  report.md           cobertura y avisos

Uso:  python3 extract.py --db ../../database/pokemon.db --out ./out [--pkhex-moves text_Moves_en.txt]
Fuente: https://github.com/PokeAPI/pokeapi (data/v2/csv). Requiere solo la librería estándar.
"""
import argparse, csv, difflib, os, re, sqlite3, urllib.request, collections

BASE = "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/"
FILES = ["item_flavor_text", "item_names", "item_prose", "machines", "move_names"]

# language_id de PokeAPI -> código PKHeX usado por la app (DataLanguageService.SelectableCodes)
LANG = {9: "en", 7: "es", 5: "fr", 6: "de", 8: "it", 11: "ja", 1: "ja", 3: "ko", 12: "zh-Hans", 4: "zh-Hant"}
CJK = {"ja", "ko", "zh-Hans", "zh-Hant"}

# GameCode de pokemon.db -> version_group_id de PokeAPI (los últimos pisan a los primeros)
GAME_VG = {
    "redgreen": [28, 1], "yellow": [2], "goldsilver": [3], "crystal": [4],
    "rubysapphire": [5], "emerald": [6], "fireredleafgreen": [7],
    "diamondpearl": [8], "platinum": [9], "heartgoldsoulsilver": [10],
    "blackwhite": [11], "black2white2": [14], "xy": [15], "omegarubyalphasapphire": [16],
    "sunmoon": [17], "ultrasunultramoon": [18], "letsgopikachueevee": [19],
    "swordshield": [20, 21, 22], "brilliantdiamondshiningpearl": [8, 23],  # BDSP: PokeAPI no trae MT propias, se usa la lista de Gen 4
    "scarletviolet": [25, 26, 27], "legendsza": [30, 31],
    # sin MT/MO/DT en PokeAPI: legendsarceus, colosseum, galeofdarkness
}


def norm(s):  # mismo criterio que usaba la app: sin tildes, mayúsculas ni signos
    return re.sub(r"[^a-z0-9]", "", s.lower().replace("é", "e"))


def fetch(cache):
    os.makedirs(cache, exist_ok=True)
    for f in FILES:
        p = os.path.join(cache, f + ".csv")
        if not os.path.exists(p):
            print("descargando", f)
            urllib.request.urlretrieve(BASE + f + ".csv", p)


def rows(cache, name):
    with open(os.path.join(cache, name + ".csv"), encoding="utf-8", newline="") as fh:
        yield from csv.DictReader(fh)


def clean(text, code):
    t = text.replace("­", "").replace("\f", " ")
    t = re.sub(r"\s*\n\s*", "" if code in CJK else " ", t).strip()
    t = re.sub(r" {2,}", " ", t)
    return t.replace("　", "") if code == "ja" else t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--out", default="out")
    ap.add_argument("--cache", default=".cache")
    ap.add_argument("--pkhex-moves", help="text_Moves_en.txt de PKHeX (verifica ids de movimiento)")
    ap.add_argument("--aliases", default="aliases.csv", help="nombre_db,nombre_pokeapi (opcional)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fetch(a.cache)

    db = sqlite3.connect("file:" + a.db + "?mode=ro", uri=True)
    items = {r[0]: (r[1], r[2] or "", r[3]) for r in db.execute("select ItemId,Name,Description,Category from Items")}
    games = {r[0]: r[1] for r in db.execute("select GameId,GameCode from Games")}

    en_name = {}
    for r in rows(a.cache, "item_names"):
        if r["local_language_id"] == "9":
            en_name[int(r["item_id"])] = r["name"]
    by_name = {}
    for iid, n in en_name.items():
        by_name.setdefault(norm(n), iid)
    aliases = {}
    if os.path.exists(a.aliases):
        with open(a.aliases, encoding="utf-8", newline="") as fh:
            for r in csv.reader(fh):
                if len(r) >= 2 and not r[0].startswith("#"):
                    aliases[norm(r[0])] = norm(r[1])

    # --- pareja db_item_id -> pokeapi item id ---
    pair, unmatched = {}, []
    for dbid, (name, _d, cat) in items.items():
        k = aliases.get(norm(name), norm(name))
        pid = by_name.get(k)
        if pid:
            pair[dbid] = pid
        else:
            unmatched.append((dbid, name, cat))

    # --- textos de objetos (último grupo de versiones con texto por idioma) ---
    best = {}
    for r in rows(a.cache, "item_flavor_text"):
        code = LANG.get(int(r["language_id"]))
        if not code:
            continue
        key = (int(r["item_id"]), code)
        rank = (int(r["version_group_id"]), r["language_id"] == "11")  # kanji sobre kana
        if key not in best or rank > best[key][0]:
            best[key] = (rank, r["flavor_text"])
    prose = {}
    for r in rows(a.cache, "item_prose"):
        if r["local_language_id"] == "9" and r["short_effect"].strip():
            prose[int(r["item_id"])] = r["short_effect"].strip()

    machine_names = re.compile(r"^(TM|TR|HM)\d+$")
    text_rows, have_text = [], set()
    for dbid, pid in pair.items():
        if machine_names.match(items[dbid][0]):
            continue  # MT/MO/DT: se describen con machine_moves.csv
        found = False
        for code in LANG.values():
            v = best.get((pid, code))
            if v:
                text_rows.append((dbid, code, clean(v[1], code), "pokeapi-flavor", v[0][0]))
                found = True
        if not found and pid in prose:
            text_rows.append((dbid, "en", prose[pid], "pokeapi-prose", ""))
            found = True
        if found:
            have_text.add(dbid)
    text_rows = sorted(set(text_rows), key=lambda x: (x[0], x[1]))
    with open(os.path.join(a.out, "items_text.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh); w.writerow(["db_item_id", "lang", "text", "source", "version_group_id"]); w.writerows(text_rows)

    # --- movimientos de MT/MO/DT por juego ---
    move_en = {}
    for r in rows(a.cache, "move_names"):
        if r["local_language_id"] == "9":
            move_en[int(r["move_id"])] = r["name"]
    mach = {}  # (vg, kind, number) -> move_id
    for r in rows(a.cache, "machines"):
        n = en_name.get(int(r["item_id"]), "")
        m = machine_names.match(n)
        if m:
            mach[(int(r["version_group_id"]), n[:2], int(n[2:]))] = int(r["move_id"])

    mrows, missing_machines = [], []
    q = db.execute("""select g.GameId,i.ItemId,i.Name,g.RawItemId from ItemGameCodes g
                      join Items i using(ItemId) where i.Name glob 'T[MR][0-9]*' or i.Name glob 'HM[0-9]*'""")
    for gid, dbid, name, raw in q:
        game = games[gid]
        m = machine_names.match(name)
        kind, num = name[:2], int(name[2:])
        vgs = GAME_VG.get(game)
        mv = vg_used = None
        for vg in (vgs or []):
            if (vg, kind, num) in mach:
                mv, vg_used = mach[(vg, kind, num)], vg
        if mv is None:
            missing_machines.append((game, name))
            continue
        mrows.append((game, gid, kind, num, dbid, raw, mv, move_en.get(mv, ""), vg_used))
    mrows.sort()
    with open(os.path.join(a.out, "machine_moves.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["game", "game_id", "kind", "number", "db_item_id", "raw_item_id", "move_id", "move_en", "version_group_id"])
        w.writerows(mrows)

    # --- ids de movimiento vs PKHeX ---
    mismatch = []
    if a.pkhex_moves:
        with open(a.pkhex_moves, encoding="utf-8") as fh:
            pk = [l.rstrip("\n") for l in fh]
        for mid in sorted({r[6] for r in mrows}):
            if mid >= len(pk) or norm(pk[mid]) != norm(move_en.get(mid, "")):
                mismatch.append((mid, move_en.get(mid, ""), pk[mid] if mid < len(pk) else "(fuera de rango)"))

    # --- sin pareja + sugerencias de alias ---
    used = {r[0] for r in db.execute("select distinct ItemId from ItemGameCodes")}
    cand = list(by_name)
    with open(os.path.join(a.out, "unmatched_items.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh); w.writerow(["db_item_id", "name", "category", "in_a_pouch", "suggestion_pokeapi_name"])
        for dbid, name, cat in sorted(unmatched, key=lambda x: (x[2] or "", x[1])):
            s = difflib.get_close_matches(norm(name), cand, n=1, cutoff=0.85)
            w.writerow([dbid, name, cat or "", int(dbid in used), en_name[by_name[s[0]]] if s else ""])

    # --- informe ---
    empty_now = [d for d, v in items.items() if not v[1].strip() and d in used and not machine_names.match(v[0])]
    still = [d for d in empty_now if d not in have_text]
    langs = collections.Counter(r[1] for r in text_rows)
    by_game = collections.Counter(r[0] for r in mrows)
    with open(os.path.join(a.out, "report.md"), "w", encoding="utf-8") as fh:
        fh.write("# Informe de extracción\n\n")
        fh.write(f"- Objetos en la base: {len(items)} · con pareja en PokeAPI: {len(pair)} · sin pareja: {len(unmatched)}\n")
        fh.write(f"- Textos extraídos: {len(text_rows)} filas, {len(have_text)} objetos. Por idioma: {dict(langs)}\n")
        fh.write(f"- Objetos usados en mochilas, sin descripción en la base y no machine: {len(empty_now)}; "
                 f"de ellos **sin texto tras la extracción: {len(still)}**\n")
        fh.write(f"- MT/MO/DT resueltas: {len(mrows)} (por juego: {dict(by_game)})\n")
        fh.write(f"- MT/MO/DT sin movimiento: {len(missing_machines)}\n")
        for g, n in missing_machines[:60]:
            fh.write(f"  - {g}: {n}\n")
        if args_mismatch := mismatch:
            fh.write(f"\n## Movimientos cuyo id no coincide con PKHeX ({len(args_mismatch)})\n")
            for mid, a1, b1 in args_mismatch:
                fh.write(f"- id {mid}: PokeAPI «{a1}» vs PKHeX «{b1}»\n")
        elif a.pkhex_moves:
            fh.write("\n- Ids de movimiento: todos coinciden con PKHeX.\n")
    print(open(os.path.join(a.out, "report.md"), encoding="utf-8").read())


if __name__ == "__main__":
    main()
