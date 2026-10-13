#!/usr/bin/env python3
"""Crea la tabla FormGameAvailability en pokemon.db.

(SpeciesId -> Species, GameId -> Games). Una fila por especie, forma y juego, SOLO para las formas
que el constructor no consigue dejar legales en ese juego (Status = 'uncreatable'). El combo Forma
de la app las oculta cuando, además, el cambio de forma rompe el origen del Pokémon.

Uso: python3 create_tables.py /ruta/a/pokemon.db
"""
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

def main(path):
    con = sqlite3.connect(path)
    con.executescript(DDL)
    con.commit()
    print("OK: FormGameAvailability lista en", path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
