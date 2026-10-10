#!/usr/bin/env python3
"""Carga SpeciesGameAvailability en pokemon.db desde species_game_availability.json.
Idempotente: la tabla se repuebla entera. Correr antes create_tables.py.

Status:
  native           en la tabla del juego (PKHeX) y se construye legal
  present_illegal  en la tabla del juego, pero PokemonService.BuildPokemon no logra una versión legal
                   (limitación del constructor, no del juego): se sigue ofreciendo, sale con alertas
  transfer_only    ausente de la tabla del juego pero legal (llega por HOME, p. ej. Sandshrew en Z-A)
  dlc              ausente de la tabla de PKHeX.Core 25.11.07 pero en el Pokédex del juego
                   (restricted_dex_availability.json): se sigue ofreciendo
  uncreatable      no existe en el juego y no hay forma legal: el selector de creación la oculta

Uso: python3 load_data.py /ruta/a/pokemon.db [--dry-run]
"""
import json, sqlite3, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
VERSION = "2026.10"
SOURCE = "PKHeX.Core 25.11.07"
STATUSES = {"native", "present_illegal", "transfer_only", "dlc", "uncreatable"}

def main(path, dry):
    rows = json.loads((HERE / "species_game_availability.json").read_text(encoding="utf-8"))
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
            k = (r["SpeciesId"], r["GameId"])
            if k in seen:
                sys.exit(f"ERROR: fila duplicada {k}")
            seen.add(k)

        cur.execute("DELETE FROM SpeciesGameAvailability")
        cur.execute("DELETE FROM sqlite_sequence WHERE name='SpeciesGameAvailability'")
        cur.executemany(
            "INSERT INTO SpeciesGameAvailability(SpeciesId, GameId, Status, Reason) VALUES (?,?,?,?)",
            [(r["SpeciesId"], r["GameId"], r["Status"], r.get("Reason")) for r in rows])
        cur.execute("INSERT OR REPLACE INTO Metadata(Key, Value) VALUES ('SpeciesAvailabilityVersion', ?)", (VERSION,))
        cur.execute("INSERT OR REPLACE INTO Metadata(Key, Value) VALUES ('SpeciesAvailabilitySource', ?)", (SOURCE,))

        print(f"SpeciesGameAvailability: {len(rows)} filas")
        per = Counter((games[r["GameId"]], r["Status"]) for r in rows)
        for (g, s), n in sorted(per.items()):
            print(f"  {g:22s} {s:16s} {n}")
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
