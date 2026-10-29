#!/usr/bin/env python3
"""Crea la tabla HiddenItems en pokemon.db (si no existe). Idempotente.
Uso: python3 create_tables.py /ruta/a/pokemon.db"""
import sqlite3, sys

DDL = """
CREATE TABLE IF NOT EXISTS HiddenItems (
    GameId  INTEGER NOT NULL,
    ItemId  INTEGER NOT NULL,
    Reason  TEXT    NOT NULL,                -- machine_without_move | manual
    PRIMARY KEY (GameId, ItemId),
    FOREIGN KEY (GameId) REFERENCES Games(GameId),
    FOREIGN KEY (ItemId) REFERENCES Items(ItemId)
);
"""

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    con = sqlite3.connect(sys.argv[1]); con.executescript(DDL); con.commit(); con.close()
    print("Tabla HiddenItems lista.")
