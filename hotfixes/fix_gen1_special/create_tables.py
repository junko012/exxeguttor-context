#!/usr/bin/env python3
"""Agrega la columna Species.BaseSpecialGen1 en pokemon.db (si no existe).

BaseSpecialGen1 = stat Especial ÚNICO de Gen 1 (INTEGER, NULL para todo lo que no es Kanto).
En Gen 1 no existían Ataque Esp. / Defensa Esp. por separado; las columnas BaseSpAttack /
BaseSpDefense de la tabla son las de Gen 2+ (p. ej. Charizard 109/85, Gen 1: 85).
La app (PokemonDatabase.GetSpecies) lee esta columna si existe y la usa solo en saves de Gen 1.

Uso: python3 create_tables.py /ruta/a/pokemon.db
"""
import sqlite3, sys

def main(path):
    con = sqlite3.connect(path)
    cols = [r[1] for r in con.execute("PRAGMA table_info(Species)")]
    if not cols:
        sys.exit("ERROR: la tabla Species no existe en " + path)
    if "BaseSpecialGen1" not in cols:
        con.execute("ALTER TABLE Species ADD COLUMN BaseSpecialGen1 INTEGER")
        con.commit()
        print("OK: columna Species.BaseSpecialGen1 agregada en", path)
    else:
        print("OK: Species.BaseSpecialGen1 ya existía en", path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
