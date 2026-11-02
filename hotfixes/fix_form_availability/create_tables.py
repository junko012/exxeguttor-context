#!/usr/bin/env python3
"""Crea (si no existe) FormGameAvailability en pokemon.db. Idempotente.
Uso: python3 create_tables.py /ruta/a/pokemon.db"""
import sqlite3, sys

DDL = """
CREATE TABLE IF NOT EXISTS FormGameAvailability(
 FormAvailabilityId INTEGER PRIMARY KEY AUTOINCREMENT,
 SpeciesId INTEGER NOT NULL,
 FormId INTEGER NOT NULL,
 GameId INTEGER NOT NULL,
 Status TEXT NOT NULL,
 Reason TEXT,
 UNIQUE(SpeciesId, FormId, GameId)
);
CREATE INDEX IF NOT EXISTS IX_FormGameAvailability_Game ON FormGameAvailability(GameId, Status);
"""

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    con = sqlite3.connect(sys.argv[1])
    con.executescript(DDL)
    con.commit()
    con.close()
    print("OK: FormGameAvailability lista")
