#!/usr/bin/env python3
"""Crea la tabla ItemNames en pokemon.db (si no existe). Idempotente.
Uso: python3 create_tables.py /ruta/a/pokemon.db"""
import sqlite3, sys

DDL = """
CREATE TABLE IF NOT EXISTS ItemNames (
    ItemId    INTEGER NOT NULL,
    Lang      TEXT    NOT NULL,              -- código PKHeX: en, es, fr, de, it, ja, ko, zh-Hans, zh-Hant
    Name      TEXT    NOT NULL,
    Source    TEXT    NOT NULL,              -- research-wiki | in-game
    SourceUrl TEXT,
    Confidence TEXT   NOT NULL DEFAULT 'medium',  -- high | medium | low
    Verified  INTEGER NOT NULL DEFAULT 1,    -- 0 = pendiente de aprobar (la app no debe mostrarlo)
    PRIMARY KEY (ItemId, Lang),
    FOREIGN KEY (ItemId) REFERENCES Items(ItemId)
);
CREATE INDEX IF NOT EXISTS IX_ItemNames_Lang ON ItemNames(Lang);
"""


def create(path):
    con = sqlite3.connect(path)
    con.executescript(DDL)
    con.commit()
    con.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    create(sys.argv[1])
    print("Tabla ItemNames lista.")
