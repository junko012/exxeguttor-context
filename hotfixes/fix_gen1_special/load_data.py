#!/usr/bin/env python3
"""Carga Species.BaseSpecialGen1 en pokemon.db desde gen1_special.json (151 especies de Kanto).
Idempotente: pone NULL en todas las filas y vuelve a cargar las 151. Correr antes create_tables.py.

Uso: python3 load_data.py /ruta/a/pokemon.db [--dry-run]
"""
import json, sqlite3, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VERSION = "2026.10"
SOURCE = "Tabla de personal de Gen 1 (PKHeX.Core PersonalTable.RB), verificada contra el JSON provisto: 151/151 coinciden"

def main(path, dry):
    rows = json.loads((HERE / "gen1_special.json").read_text(encoding="utf-8"))
    con = sqlite3.connect(path)
    cur = con.cursor()
    try:
        cols = [r[1] for r in cur.execute("PRAGMA table_info(Species)")]
        if "BaseSpecialGen1" not in cols:
            sys.exit("ERROR: falta la columna BaseSpecialGen1: correr create_tables.py primero")
        names = {r[0]: r[1] for r in cur.execute("SELECT SpeciesId, Name FROM Species")}
        ids = set()
        for r in rows:
            sid = r["SpeciesId"]
            if sid not in names:
                sys.exit(f"ERROR: SpeciesId {sid} no existe en Species")
            if names[sid] != r["Name"]:
                sys.exit(f"ERROR: SpeciesId {sid}: la DB dice '{names[sid]}', el JSON '{r['Name']}'")
            if not 1 <= r["BaseSpecialGen1"] <= 255:
                sys.exit(f"ERROR: BaseSpecialGen1 fuera de rango en {sid}")
            ids.add(sid)
        if ids != set(range(1, 152)):
            sys.exit("ERROR: el JSON debe traer exactamente las especies 1..151")

        cur.execute("UPDATE Species SET BaseSpecialGen1 = NULL")
        cur.executemany("UPDATE Species SET BaseSpecialGen1 = ? WHERE SpeciesId = ?",
                        [(r["BaseSpecialGen1"], r["SpeciesId"]) for r in rows])
        n = cur.execute("SELECT COUNT(*) FROM Species WHERE BaseSpecialGen1 IS NOT NULL").fetchone()[0]
        if n != 151:
            sys.exit(f"ERROR: se esperaban 151 filas con dato y hay {n}")
        cur.execute("INSERT OR REPLACE INTO Metadata(Key, Value) VALUES ('Gen1SpecialVersion', ?)", (VERSION,))
        cur.execute("INSERT OR REPLACE INTO Metadata(Key, Value) VALUES ('Gen1SpecialSource', ?)", (SOURCE,))
        print(f"{n} especies con BaseSpecialGen1 (rango {min(r['BaseSpecialGen1'] for r in rows)}-{max(r['BaseSpecialGen1'] for r in rows)})")
        if dry:
            con.rollback(); print("--dry-run: sin cambios")
        else:
            con.commit(); print("OK: commit")
    finally:
        con.close()

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    if len(args) != 1:
        sys.exit(__doc__)
    main(args[0], "--dry-run" in sys.argv)
