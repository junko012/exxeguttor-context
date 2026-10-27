#!/usr/bin/env python3
"""Crea las tablas ItemDescriptions y MachineMoves en pokemon.db (si no existen). Idempotente.
Uso: python3 create_tables.py /ruta/a/pokemon.db"""
import sqlite3, sys

DDL = """
CREATE TABLE IF NOT EXISTS ItemDescriptions (
    ItemId    INTEGER NOT NULL,
    Lang      TEXT    NOT NULL,              -- código PKHeX: en, es, fr, de, it, ja, ko, zh-Hans, zh-Hant
    Text      TEXT    NOT NULL,
    Source    TEXT    NOT NULL,              -- legacy | pokeapi-flavor | pokeapi-prose | template | research
    SourceUrl TEXT,
    Verified  INTEGER NOT NULL DEFAULT 1,    -- 0 = pendiente de aprobar (la app no debe mostrarlo)
    PRIMARY KEY (ItemId, Lang),
    FOREIGN KEY (ItemId) REFERENCES Items(ItemId)
);
CREATE INDEX IF NOT EXISTS IX_ItemDescriptions_Lang ON ItemDescriptions(Lang);

CREATE TABLE IF NOT EXISTS MachineMoves (
    GameId  INTEGER NOT NULL,
    Kind    TEXT    NOT NULL,                -- TM | TR | HM
    Number  INTEGER NOT NULL,                -- número dentro del juego
    ItemId  INTEGER NOT NULL,
    MoveId  INTEGER NOT NULL,                -- id de movimiento de PKHeX
    PRIMARY KEY (GameId, Kind, Number),
    FOREIGN KEY (GameId) REFERENCES Games(GameId),
    FOREIGN KEY (ItemId) REFERENCES Items(ItemId)
);
CREATE INDEX IF NOT EXISTS IX_MachineMoves_Item ON MachineMoves(GameId, ItemId);
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
    print("Tablas ItemDescriptions y MachineMoves listas.")
