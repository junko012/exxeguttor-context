#!/usr/bin/env python3
"""Carga ItemDescriptions y MachineMoves en pokemon.db desde los CSV de data/. Idempotente.

Uso:
  python3 load_data.py /ruta/a/pokemon.db [--dry-run] [--research otro_items_text_research.csv] [--vacuum]
  (data/items_text_research.csv se carga solo si existe)

- Crea las tablas si faltan. No borra ni cambia Items, ItemGameCodes ni Games.
- ItemDescriptions y MachineMoves son tablas DERIVADAS: cada ejecución las reconstruye completas en una transacción.
- Prioridad cuando hay varios textos para (objeto, idioma):
    en:     research verificado > legacy (Items.Description) > pokeapi > template > research sin verificar
    resto:  research verificado > pokeapi > template > research sin verificar
- Las filas Verified=0 solo entran si no hay otra mejor (la app no debe mostrarlas hasta aprobarlas).
"""
import argparse, csv, os, sqlite3, sys, datetime, re
from create_tables import DDL

HERE = os.path.dirname(os.path.abspath(__file__))
LANGS = {"en", "es", "fr", "de", "it", "ja", "ko", "zh-Hans", "zh-Hant"}
MACHINE = re.compile(r"^(TM|TR|HM)\d+$")


def prio(lang, source, verified):
    if source == "research":
        return 5 if verified else 1
    if source == "legacy":
        return 4 if lang == "en" else 0  # solo se importa en inglés
    if source.startswith("pokeapi"):
        return 3
    if source == "template":
        return 2
    return 0


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("db")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--data-dir", default=os.path.join(HERE, "data"))
    ap.add_argument("--research", help="items_text_research.csv generado por validate_research.py")
    ap.add_argument("--vacuum", action="store_true")
    a = ap.parse_args()

    con = sqlite3.connect(a.db)
    con.execute("PRAGMA foreign_keys=ON")
    con.executescript(DDL)

    items = {r[0]: (r[1], r[2] or "") for r in con.execute("select ItemId,Name,Description from Items")}
    games = {r[0]: r[1] for r in con.execute("select GameId,GameCode from Games")}
    pouch = {(r[0], r[1]): r[2] for r in con.execute("select GameId,RawItemId,ItemId from ItemGameCodes")}
    warnings = []

    # ---------- candidatos de texto ----------
    cands = {}  # (item, lang) -> (prio, text, source, url, verified)

    def offer(item, lang, text, source, url, verified):
        if item not in items:
            warnings.append(f"texto para ItemId {item} inexistente ({source}/{lang})"); return
        if lang not in LANGS:
            warnings.append(f"idioma no soportado {lang} (ItemId {item})"); return
        text = text.strip()
        if not text:
            return
        p = prio(lang, source, verified)
        if p == 0:
            return
        k = (item, lang)
        if k not in cands or p > cands[k][0]:
            cands[k] = (p, text, source, url, verified)

    for item, (name, desc) in items.items():           # legacy en (no MT/MO/DT: su texto depende del juego)
        if desc.strip() and not MACHINE.match(name or ""):
            offer(item, "en", desc, "legacy", "", 1)
    for fn in ("items_text.csv", "items_text_template.csv"):
        p = os.path.join(a.data_dir, fn)
        if os.path.exists(p):
            for r in read_csv(p):
                offer(int(r["db_item_id"]), r["lang"], r["text"], r["source"], "", 1)
    research_files = [os.path.join(a.data_dir, "items_text_research.csv")] + ([a.research] if a.research else [])
    for rf in research_files:
        if not os.path.exists(rf):
            continue
        for r in read_csv(rf):
            offer(int(r["db_item_id"]), r["lang"], r["text"], "research", r.get("source_url", ""), int(r.get("verified", 0)))

    # ---------- movimientos de MT/MO/DT ----------
    mm, mm_skipped = {}, 0
    for r in read_csv(os.path.join(a.data_dir, "machine_moves.csv")):
        gid, item, raw = int(r["game_id"]), int(r["db_item_id"]), int(r["raw_item_id"])
        if games.get(gid) != r["game"]:
            warnings.append(f"GameId {gid} ya no es «{r['game']}» en esta base: fila omitida"); mm_skipped += 1; continue
        if pouch.get((gid, raw)) != item:
            warnings.append(f"{r['game']} {r['kind']}{r['number']}: (GameId,RawItemId)->ItemId no coincide con ItemGameCodes"); mm_skipped += 1; continue
        mm[(gid, r["kind"], int(r["number"]))] = (item, int(r["move_id"]))

    # ---------- MT/MO/DT de la base sin movimiento (candidatas a revisar, NO se borran) ----------
    no_move = []
    q = con.execute("select g.GameId,i.ItemId,i.Name from ItemGameCodes g join Items i using(ItemId)")
    for gid, item, name in q:
        m = MACHINE.match(name or "")
        if m and (gid, name[:2], int(name[2:])) not in mm:
            no_move.append(f"{games[gid]} {name}")

    by_src, by_lang = {}, {}
    for (item, lang), v in cands.items():
        by_src[v[2]] = by_src.get(v[2], 0) + 1
        by_lang[lang] = by_lang.get(lang, 0) + 1
    print(f"ItemDescriptions: {len(cands)} filas | por fuente {by_src} | por idioma {by_lang}")
    print(f"MachineMoves: {len(mm)} filas (omitidas {mm_skipped})")
    print(f"MT/MO/DT en ItemGameCodes sin movimiento: {len(no_move)} {no_move[:15]}")
    for w in warnings[:20]:
        print("AVISO:", w)
    if len(warnings) > 20:
        print(f"... y {len(warnings) - 20} avisos más")

    if a.dry_run:
        print("--dry-run: no se escribió nada.")
        con.close(); return

    with con:
        con.execute("DELETE FROM ItemDescriptions")
        con.execute("DELETE FROM MachineMoves")
        con.executemany("INSERT INTO ItemDescriptions(ItemId,Lang,Text,Source,SourceUrl,Verified) VALUES (?,?,?,?,?,?)",
                        [(i, l, v[1], v[2], v[3] or None, v[4]) for (i, l), v in sorted(cands.items())])
        con.executemany("INSERT INTO MachineMoves(GameId,Kind,Number,ItemId,MoveId) VALUES (?,?,?,?,?)",
                        [(g, k, n, v[0], v[1]) for (g, k, n), v in sorted(mm.items())])
        today = datetime.date.today().isoformat()
        for k, v in (("ItemDescriptionsVersion", today),
                     ("ItemDescriptionsSource", "PokeAPI (item_flavor_text/item_prose) + plantillas + investigación; ver Source por fila"),
                     ("MachineMovesVersion", today),
                     ("MachineMovesSource", "PokeAPI machines (ids de movimiento verificados contra PKHeX)")):
            con.execute("INSERT INTO Metadata(Key,Value) VALUES(?,?) ON CONFLICT(Key) DO UPDATE SET Value=excluded.Value", (k, v))

    bad = con.execute("PRAGMA foreign_key_check").fetchall()
    ok = con.execute("PRAGMA integrity_check").fetchone()[0]
    empty = con.execute("select count(*) from ItemDescriptions where trim(Text)=''").fetchone()[0]
    print(f"integrity_check={ok} · foreign_key_check={len(bad)} violaciones · textos vacíos={empty}")
    if a.vacuum:
        con.execute("VACUUM")
    con.close()
    if ok != "ok" or bad or empty:
        sys.exit(1)


if __name__ == "__main__":
    main()
