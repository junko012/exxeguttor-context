#!/usr/bin/env python3
"""Carga FormGameAvailability en pokemon.db desde form_game_availability.json.
Idempotente: la tabla se repuebla entera. Correr antes create_tables.py.

Status: 'uncreatable' = BuildPokemon no logra esa forma legal en ese juego (el combo la oculta si cambiarla rompe el origen);
        'own_encounter' = la forma se oculta del combo pero tiene encuentro legal propio: el selector de creación la ofrece.

Uso: python3 load_data.py /ruta/a/pokemon.db [--dry-run]
"""
import json, sqlite3, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
VERSION = "2026.10.1"
SOURCE = "PKHeX.Core 25.11.07"
STATUSES = {"uncreatable", "own_encounter"}

def main(path, dry):
    rows = json.loads((HERE / "form_game_availability.json").read_text(encoding="utf-8"))
    con = sqlite3.connect(path)
    cur = con.cursor()
    try:
        species = {r[0] for r in cur.execute("SELECT SpeciesId FROM Species")}
        games = {r[0]: r[1] for r in cur.execute("SELECT GameId, GameCode FROM Games")}
        seen = set()
        for r in rows:
            if r["SpeciesId"] not in species:
                sys.exit(f"ERROR: SpeciesId {r['SpeciesId']} no existe en Species")
            if r["GameId"] not in games:
                sys.exit(f"ERROR: GameId {r['GameId']} no existe en Games")
            if r["Status"] not in STATUSES:
                sys.exit(f"ERROR: Status desconocido {r['Status']}")
            k = (r["SpeciesId"], r["FormId"], r["GameId"])
            if k in seen:
                sys.exit(f"ERROR: fila duplicada {k}")
            seen.add(k)

        cur.execute("DELETE FROM FormGameAvailability")
        cur.execute("DELETE FROM sqlite_sequence WHERE name='FormGameAvailability'")
        cur.executemany(
            "INSERT INTO FormGameAvailability(SpeciesId, FormId, GameId, Status, Reason) VALUES (?,?,?,?,?)",
            [(r["SpeciesId"], r["FormId"], r["GameId"], r["Status"], r.get("Reason")) for r in rows])
        cur.execute("INSERT OR REPLACE INTO Metadata(Key, Value) VALUES ('FormAvailabilityVersion', ?)", (VERSION,))
        cur.execute("INSERT OR REPLACE INTO Metadata(Key, Value) VALUES ('FormAvailabilitySource', ?)", (SOURCE,))

        print(f"FormGameAvailability: {len(rows)} filas")
        for (g, s), n in sorted(Counter((games[r["GameId"]], r["Status"]) for r in rows).items()):
            print(f"  {g:22s} {s:14s} {n}")
        if dry:
            con.rollback(); print("--dry-run: cambios revertidos")
        else:
            con.commit(); print("OK: commit")
    finally:
        con.close()

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        sys.exit(__doc__)
    main(args[0], "--dry-run" in sys.argv)
