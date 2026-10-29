#!/usr/bin/env python3
"""Carga ItemNames en pokemon.db desde data/item_names.csv. Idempotente (reconstruye la tabla completa).
Uso: python3 load_data.py /ruta/a/pokemon.db [--dry-run] [--vacuum]
No toca Items, ItemGameCodes ni ItemDescriptions. Escribe Metadata ItemNamesVersion/ItemNamesSource."""
import argparse, csv, datetime, os, sqlite3, sys
from create_tables import DDL

HERE = os.path.dirname(os.path.abspath(__file__))
LANGS = {"en", "es", "fr", "de", "it", "ja", "ko", "zh-Hans", "zh-Hant"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("db")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--csv", default=os.path.join(HERE, "data", "item_names.csv"))
    ap.add_argument("--vacuum", action="store_true")
    a = ap.parse_args()
    con = sqlite3.connect(a.db)
    con.execute("PRAGMA foreign_keys=ON")
    con.executescript(DDL)
    items = {r[0]: r[1] for r in con.execute("select ItemId,Name from Items")}
    rows, warns = [], []
    for r in csv.DictReader(open(a.csv, encoding="utf-8", newline="")):
        i = int(r["db_item_id"])
        if i not in items:
            warns.append(f"ItemId {i} inexistente"); continue
        if r["lang"] not in LANGS or not r["name"].strip():
            warns.append(f"fila inválida {i}/{r['lang']}"); continue
        if r["lang"] == "en" and r["name"] != items[i]:
            warns.append(f"{i}: en «{r['name']}» ≠ Items.Name «{items[i]}» (Items no se modifica)")
        rows.append((i, r["lang"], r["name"], r["source"], r["source_url"] or None, r["confidence"], int(r["verified"])))
    print(f"ItemNames: {len(rows)} filas, {len({r[0] for r in rows})} objetos")
    for w in warns: print("AVISO:", w)
    if a.dry_run:
        print("--dry-run: no se escribió nada."); con.close(); return
    with con:
        con.execute("DELETE FROM ItemNames")
        con.executemany("INSERT INTO ItemNames(ItemId,Lang,Name,Source,SourceUrl,Confidence,Verified) VALUES (?,?,?,?,?,?,?)", rows)
        today = datetime.date.today().isoformat()
        for k, v in (("ItemNamesVersion", today),
                     ("ItemNamesSource", "Nombres de objetos de Legends: Z-A ausentes en PKHeX; wikis (Bulbapedia/WikiDex), ver Source por fila")):
            con.execute("INSERT INTO Metadata(Key,Value) VALUES(?,?) ON CONFLICT(Key) DO UPDATE SET Value=excluded.Value", (k, v))
    bad = con.execute("PRAGMA foreign_key_check").fetchall()
    ok = con.execute("PRAGMA integrity_check").fetchone()[0]
    print(f"integrity_check={ok} · foreign_key_check={len(bad)} violaciones")
    if a.vacuum: con.execute("VACUUM")
    con.close()
    if ok != "ok" or bad: sys.exit(1)


if __name__ == "__main__":
    main()
