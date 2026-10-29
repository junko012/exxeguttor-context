#!/usr/bin/env python3
"""Rellena HiddenItems: MT/MO/DT de ItemGameCodes sin movimiento en MachineMoves (+ data/manual_hidden.csv, opcional).
Uso: python3 load_data.py /ruta/a/pokemon.db [--dry-run] [--vacuum]
Requiere MachineMoves (hotfix fix_item_descriptions). Tabla derivada: se reconstruye completa. No borra nada de ItemGameCodes.
manual_hidden.csv: columnas game_id,item_id (Reason = manual)."""
import argparse, csv, os, re, sqlite3, sys, datetime
from create_tables import DDL

HERE = os.path.dirname(os.path.abspath(__file__))
MACHINE = re.compile(r"^(TM|TR|HM)(\d+)$")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("db"); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--vacuum", action="store_true")
    a = ap.parse_args()
    con = sqlite3.connect(a.db); con.execute("PRAGMA foreign_keys=ON"); con.executescript(DDL)
    mm = {(g, k, n) for g, k, n in con.execute("select GameId,Kind,Number from MachineMoves")}
    if not mm:
        raise SystemExit("MachineMoves vacía o inexistente: aplicar antes fix_item_descriptions.")
    games = {r[0]: r[1] for r in con.execute("select GameId,GameCode from Games")}
    rows = {}
    for gid, iid, name in con.execute("select g.GameId,i.ItemId,i.Name from ItemGameCodes g join Items i using(ItemId)"):
        m = MACHINE.match(name or "")
        if m and (gid, m.group(1), int(m.group(2))) not in mm:
            rows[(gid, iid)] = "machine_without_move"
    manual = os.path.join(HERE, "data", "manual_hidden.csv")
    if os.path.exists(manual):
        for r in csv.DictReader(open(manual, encoding="utf-8")):
            rows[(int(r["game_id"]), int(r["item_id"]))] = "manual"
    print(f"HiddenItems: {len(rows)} filas")
    for (g, i), why in sorted(rows.items()):
        print("  ", games.get(g), i, why)
    if a.dry_run:
        print("--dry-run: no se escribió nada."); con.close(); return
    with con:
        con.execute("DELETE FROM HiddenItems")
        con.executemany("INSERT INTO HiddenItems(GameId,ItemId,Reason) VALUES (?,?,?)", [(g, i, w) for (g, i), w in sorted(rows.items())])
        con.execute("INSERT INTO Metadata(Key,Value) VALUES('HiddenItemsVersion',?) ON CONFLICT(Key) DO UPDATE SET Value=excluded.Value", (datetime.date.today().isoformat(),))
    bad = con.execute("PRAGMA foreign_key_check").fetchall(); ok = con.execute("PRAGMA integrity_check").fetchone()[0]
    print(f"integrity_check={ok} · foreign_key_check={len(bad)} violaciones")
    if a.vacuum: con.execute("VACUUM")
    con.close()
    if ok != "ok" or bad: sys.exit(1)


if __name__ == "__main__":
    main()
