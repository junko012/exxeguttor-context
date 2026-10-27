# fix_item_descriptions — descripciones de objetos por idioma y movimientos de MT/MO/DT en `pokemon.db`

```bash
python3 create_tables.py /ruta/a/pokemon.db                      # crea ItemDescriptions y MachineMoves (si no existen)
python3 load_data.py /ruta/a/pokemon.db --dry-run                # opcional: muestra conteos y avisos sin escribir
python3 load_data.py /ruta/a/pokemon.db [--research items_text_research.csv] [--vacuum]
```
Idempotente: las dos tablas son DERIVADAS y se reconstruyen completas en una transacción.
Hacer una copia de `pokemon.db` antes. Subir como blob normal (sin LFS).

## Qué agrega
- `ItemDescriptions(ItemId, Lang, Text, Source, SourceUrl, Verified)` — PK (ItemId, Lang). `Lang` = código PKHeX
  (en, es, fr, de, it, ja, ko, zh-Hans, zh-Hant). `Source`: legacy | pokeapi-flavor | pokeapi-prose | template | research.
  `Verified=0` = pendiente de aprobar (la app no debe mostrarlo).
- `MachineMoves(GameId, Kind, Number, ItemId, MoveId)` — PK (GameId, Kind, Number). `MoveId` = id de PKHeX.
  La misma MT enseña cosas distintas según el juego (TM101 de SV ≠ TM101 de Z-A), por eso la clave incluye el juego.
- Metadata: `ItemDescriptionsVersion/Source`, `MachineMovesVersion/Source`.

## Qué NO toca
`Items`, `ItemGameCodes`, `Games` y `Items.Description` quedan intactos (la descripción en inglés sigue como respaldo).

## Prioridad de textos por (objeto, idioma)
- en: research verificado > legacy (`Items.Description`) > pokeapi > template > research sin verificar
- resto: research verificado > pokeapi > template > research sin verificar
- Las MT/MO/DT NO llevan texto en `ItemDescriptions`: su descripción se arma con `MachineMoves` + plantilla de la UI.

## Datos (`data/`)
Generados por `hotfixes/item_descriptions/` (extract.py, gen_templates.py): `items_text.csv`, `items_text_template.csv`,
`machine_moves.csv`. Los datos de investigación pasan antes por `validate_research.py` y se cargan con `--research`.

## Avisos conocidos
12 filas de MT en `ItemGameCodes` sin movimiento en ninguna fuente (no se borran; decidir aparte):
Rojo/Verde y Amarillo `TM51`–`TM55`, Escarlata/Púrpura `TM00`, Z-A `TM161`.

## Verificación hecha (copia de la base)
`integrity_check=ok`, `foreign_key_check=0`, sin textos vacíos, segunda ejecución idéntica (idempotente).
