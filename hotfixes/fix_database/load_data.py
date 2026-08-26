"""
load_data.py
-------------
Carga items.json e item_game_codes.json en pokemon.db, sobre las tablas creadas
por create_tables.py.

IMPORTANTE - GameCode: item_game_codes.json identifica cada juego por un slug de
texto (GameCode), por ejemplo "redgreen", "crystal", "emerald", "scarletviolet".
Estos slugs son una propuesta razonada a partir de los ejemplos que aparecen en
SCHEMA_REFERENCE.md (redgreen, yellow, crystal, emerald, platinum, blackwhite,
scarletviolet) pero NO están verificados contra el contenido real de tu tabla
Games. Antes de correr esto:

  1. Correr `SELECT GameId, GameCode FROM Games;` sobre tu pokemon.db real.
  2. Completar GAME_CODE_OVERRIDES abajo con cualquier slug que no coincida
     (clave = GameCode usado en el JSON, valor = GameCode real en tu tabla Games).
  3. Los GameCodes del JSON que sigan sin existir en tu tabla Games se van a
     reportar como advertencia y se van a omitir (no rompen la carga).

Uso:
    python3 load_data.py /ruta/a/pokemon.db
"""
import json
import sqlite3
import sys
from pathlib import Path

# Ajustar acá si tus GameCode reales difieren de los usados en item_game_codes.json
#
# VERIFICADO directamente contra el pokemon.db real (github.com/junko012/pokemon-database):
#   - Tu tabla Games usa "galeofdarkness" para lo que este JSON llama "xd"
#     (Pokémon XD: Gale of Darkness -- mismo juego, slug distinto).
#   - Tu tabla Games NO TIENE ninguna fila para Colosseum. Hace falta:
#         INSERT INTO Games (GameCode) VALUES ('colosseum');
#     antes de correr load_data.py, o esas ~48 filas se van a reportar como
#     "GameCode sin correspondencia" y se van a omitir silenciosamente.
#   - El resto de los 23 GameCode coincide 1:1, no necesitan override.
GAME_CODE_OVERRIDES = {
    "xd": "galeofdarkness",
}

HERE = Path(__file__).parent


def main(db_path: str):
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # ---------- Items ----------
    items = json.loads((HERE / "items.json").read_text(encoding="utf-8"))
    cur.execute("DELETE FROM Items;")
    cur.executemany(
        """INSERT INTO Items (ItemId, Name, Description, Category, Cost, FlingPower, FlingEffect)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        [
            (it["ItemId"], it["Name"], it["Description"], it["Category"],
             it["Cost"], it["FlingPower"], it["FlingEffect"])
            for it in items
        ],
    )
    synthetic_count = sum(1 for it in items if it.get("IsSynthetic"))
    print(f"Items: {len(items)} filas insertadas ({synthetic_count} sintéticas, ItemId >= 90000, "
          f"exclusivas de Colosseum/XD sin ID unificado de PKHeX).")

    # ---------- Games lookup ----------
    game_id_by_code = {}
    for game_id, game_code in cur.execute("SELECT GameId, GameCode FROM Games;"):
        game_id_by_code[game_code] = game_id

    # ---------- ItemGameCodes ----------
    codes = json.loads((HERE / "item_game_codes.json").read_text(encoding="utf-8"))
    cur.execute("DELETE FROM ItemGameCodes;")

    rows = []
    missing_codes = {}
    for r in codes:
        json_code = r["GameCode"]
        real_code = GAME_CODE_OVERRIDES.get(json_code, json_code)
        game_id = game_id_by_code.get(real_code)
        if game_id is None:
            missing_codes[json_code] = missing_codes.get(json_code, 0) + 1
            continue
        rows.append((r["ItemId"], game_id, r["RawItemId"], r["PouchCategory"], r.get("UserPouchCategory")))

    cur.executemany(
        """INSERT OR IGNORE INTO ItemGameCodes (ItemId, GameId, RawItemId, PouchCategory, UserPouchCategory)
           VALUES (?, ?, ?, ?, ?)""",
        rows,
    )
    print(f"ItemGameCodes: {len(rows)} filas insertadas.")

    if missing_codes:
        print("\n⚠️  GameCodes del JSON sin correspondencia en tu tabla Games (filas omitidas):")
        for code, count in sorted(missing_codes.items()):
            print(f"   - {code}: {count} filas omitidas")
        print("   Agregalos a GAME_CODE_OVERRIDES o a tu tabla Games y volvé a correr.")

    con.commit()
    con.close()
    print("\nListo.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 load_data.py /ruta/a/pokemon.db")
        sys.exit(1)
    main(sys.argv[1])
