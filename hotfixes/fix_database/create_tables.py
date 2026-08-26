"""
create_tables.py
-----------------
(Re)crea las tablas Items e ItemGameCodes en pokemon.db.

- Items: mismo schema que ya existe en el proyecto (SCHEMA_REFERENCE.md), sin
  cambios de columnas. Se DROPEA y se vuelve a crear porque todos sus datos van
  a ser reemplazados por completo (ver instructions.md).
- ItemGameCodes: tabla nueva.

Uso:
    python3 create_tables.py /ruta/a/pokemon.db
"""
import sqlite3
import sys

DDL_ITEMS = """
CREATE TABLE Items (
    ItemId      INTEGER PRIMARY KEY,
    Name        TEXT,
    Description TEXT,
    Category    TEXT,
    Cost        INTEGER,
    FlingPower  INTEGER,
    FlingEffect TEXT
);
"""
# Mismo schema que SCHEMA_REFERENCE.md, sin columnas nuevas (según lo acordado).
# items.json trae un campo extra "IsSynthetic" (true solo para los ~113 ítems
# exclusivos de Colosseum/XD, ItemId >= 90000, sin ID unificado real de PKHeX).
# load_data.py lo usa solo para loguear un resumen al cargar, pero NO lo inserta
# como columna: la distinción queda dada por el rango de ItemId (>= 90000),
# tal como se definió en el diseño.

DDL_ITEM_GAME_CODES = """
CREATE TABLE ItemGameCodes (
    ItemId            INTEGER NOT NULL,
    GameId            INTEGER NOT NULL,
    RawItemId         INTEGER NOT NULL,
    PouchCategory     TEXT NOT NULL,
    UserPouchCategory TEXT,
    PRIMARY KEY (GameId, RawItemId),
    UNIQUE (ItemId, GameId),
    FOREIGN KEY (ItemId) REFERENCES Items(ItemId),
    FOREIGN KEY (GameId) REFERENCES Games(GameId)
);
"""
# PouchCategory: el pouch/bolsillo REAL tal como lo modela el motor del juego en
# ESE juego puntual (fiel a PKHeX.Core -- útil para legalidad/validación).
# UserPouchCategory: la pestaña de mochila que conviene mostrar en la UI de
# Exxeguttor. Para Gen4-9 es igual a PouchCategory (el motor real ya viene fino).
# Para Gen1-3 y Colosseum/XD, donde el motor real mete casi todo en un pouch
# "Items" único, se sub-clasificó usando Items.Category (ver
# add_user_pouch_category.py para la tabla de mapeo completa y su razonamiento).
# Puede ser NULL a propósito para un puñado de ítems obsoletos/no jugables
# (ej. Slowpoke Tail, Bike) que no tiene sentido mostrar en ninguna pestaña.

DDL_INDEX = "CREATE INDEX IX_ItemGameCodes_Item ON ItemGameCodes(ItemId);"


def main(db_path: str):
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    cur.execute("DROP TABLE IF EXISTS Items;")
    cur.execute(DDL_ITEMS)
    print("Tabla Items recreada.")

    cur.execute("DROP TABLE IF EXISTS ItemGameCodes;")
    cur.execute(DDL_ITEM_GAME_CODES)
    cur.execute(DDL_INDEX)
    print("Tabla ItemGameCodes creada.")

    con.commit()
    con.close()
    print("Listo. Ahora correr load_data.py.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 create_tables.py /ruta/a/pokemon.db")
        sys.exit(1)
    main(sys.argv[1])
