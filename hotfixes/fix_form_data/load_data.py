#!/usr/bin/env python3
"""Carga los datos por forma en pokemon.db. Idempotente (se puede correr varias veces).

  1. FormEvolutionChains / FormEvolutionConditions  <- form_evolutions.json
  2. Species (solo filas de forma, SpeciesId > 10000) <- species_form_data.json
       · EggGroup1 / EggGroup2: se completan (estaban NULL en todas las formas).
       · GenderRate / Height / Weight: solo las correcciones listadas en "Corrections"
         (7 filas donde PokeAPI —dato por especie— difiere del dato real por forma de PKHeX.Core).
  3. Metadata: FormDataVersion.

Uso: python3 load_data.py /ruta/a/pokemon.db [--dry-run]
Correr antes create_tables.py. Con --dry-run hace todo y revierte (solo muestra el resumen).
"""
import json, sqlite3, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FORM_DATA_VERSION = "2026.10"

def main(path, dry):
    evos = json.loads((HERE / "form_evolutions.json").read_text(encoding="utf-8"))
    rows = json.loads((HERE / "species_form_data.json").read_text(encoding="utf-8"))
    con = sqlite3.connect(path)
    cur = con.cursor()
    try:
        ids = {r[0] for r in cur.execute("SELECT SpeciesId FROM Species")}
        for e in evos:
            for k in ("FromSpeciesId", "ToSpeciesId"):
                if e[k] not in ids:
                    sys.exit(f"ERROR: {k}={e[k]} no existe en Species ({e['From']} -> {e['To']})")

        # 1) Evoluciones por forma — se repuebla entera.
        cur.execute("DELETE FROM FormEvolutionConditions")
        cur.execute("DELETE FROM FormEvolutionChains")
        cur.execute("DELETE FROM sqlite_sequence WHERE name IN ('FormEvolutionChains','FormEvolutionConditions')")
        n_cond = 0
        for e in evos:
            cur.execute("INSERT INTO FormEvolutionChains(FromSpeciesId, ToSpeciesId) VALUES (?,?)",
                        (e["FromSpeciesId"], e["ToSpeciesId"]))
            eid = cur.lastrowid
            for k, v in e["Conditions"].items():
                cur.execute("INSERT INTO FormEvolutionConditions(EvolutionId, ConditionType, ConditionValue) VALUES (?,?,?)",
                            (eid, k, v))
                n_cond += 1

        # 2) Species (formas)
        n_egg = n_fix = 0
        for r in rows:
            if r["SpeciesId"] <= 10000 or r["SpeciesId"] not in ids:
                sys.exit(f"ERROR: SpeciesId {r['SpeciesId']} ({r['Name']}) no es una fila de forma válida")
            cur.execute("UPDATE Species SET EggGroup1=?, EggGroup2=? WHERE SpeciesId=?",
                        (r["EggGroup1"], r["EggGroup2"], r["SpeciesId"]))
            n_egg += cur.rowcount
            for col, val in r["Corrections"].items():
                if col not in ("GenderRate", "Height", "Weight"):
                    sys.exit(f"ERROR: columna no permitida en Corrections: {col}")
                cur.execute(f"UPDATE Species SET {col}=? WHERE SpeciesId=?", (val, r["SpeciesId"]))
                n_fix += 1

        # 3) Metadata
        cur.execute("INSERT OR REPLACE INTO Metadata(Key, Value) VALUES ('FormDataVersion', ?)", (FORM_DATA_VERSION,))

        print(f"FormEvolutionChains:     {len(evos)} filas")
        print(f"FormEvolutionConditions: {n_cond} filas")
        print(f"Species (formas) con EggGroup completado: {n_egg}")
        print(f"Species (formas) correcciones GenderRate/Height/Weight: {n_fix}")
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
