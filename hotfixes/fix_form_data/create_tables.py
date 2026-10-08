#!/usr/bin/env python3
"""Crea FormEvolutionChains y FormEvolutionConditions en pokemon.db.

Misma estructura que EvolutionChains / EvolutionConditions (mismos nombres de columna, mismo EAV
de condiciones) — la única diferencia es que SpeciesId puede ser una fila de forma de Species
(SpeciesId > 10000, p. ej. 10114 = exeggutor-alola) en cualquiera de los dos lados.

Uso: python3 create_tables.py /ruta/a/pokemon.db
"""
import sqlite3, sys

DDL = """
CREATE TABLE IF NOT EXISTS FormEvolutionChains(
 EvolutionId INTEGER PRIMARY KEY AUTOINCREMENT,
 FromSpeciesId INTEGER NOT NULL,
 ToSpeciesId INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS FormEvolutionConditions(
 ConditionId INTEGER PRIMARY KEY AUTOINCREMENT,
 EvolutionId INTEGER NOT NULL,
 ConditionType TEXT NOT NULL,
 ConditionValue TEXT
);
CREATE INDEX IF NOT EXISTS IX_FormEvolutionChains_From ON FormEvolutionChains(FromSpeciesId);
CREATE INDEX IF NOT EXISTS IX_FormEvolutionChains_To ON FormEvolutionChains(ToSpeciesId);
CREATE INDEX IF NOT EXISTS IX_FormEvolutionConditions_Evolution ON FormEvolutionConditions(EvolutionId);
"""

def main(path):
    con = sqlite3.connect(path)
    con.executescript(DDL)
    con.commit()
    print("OK: FormEvolutionChains / FormEvolutionConditions listas en", path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
