#!/usr/bin/env python3
"""Crea la tabla SpeciesGameAvailability en pokemon.db.

Misma convención que ItemGameCodes: (SpeciesId -> Species, GameId -> Games). Una fila por especie y
juego, SOLO para los juegos que recortan su Pokédex (Let's Go, Espada/Escudo, Legends: Arceus,
Escarlata/Púrpura, Legends: Z-A). Un juego sin filas no restringe nada (Gen 1-7, BD/SP).

Uso: python3 create_tables.py /ruta/a/pokemon.db
"""
import sqlite3, sys

DDL = """
CREATE TABLE IF NOT EXISTS SpeciesGameAvailability(
 AvailabilityId INTEGER PRIMARY KEY AUTOINCREMENT,
 SpeciesId INTEGER NOT NULL,
 GameId INTEGER NOT NULL,
 Status TEXT NOT NULL,
 Reason TEXT,
 UNIQUE(SpeciesId, GameId)
);
CREATE INDEX IF NOT EXISTS IX_SpeciesGameAvailability_Game ON SpeciesGameAvailability(GameId, Status);
"""

def main(path):
    con = sqlite3.connect(path)
    con.executescript(DDL)
    con.commit()
    print("OK: SpeciesGameAvailability lista en", path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
