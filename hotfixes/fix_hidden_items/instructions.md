# fix_hidden_items — objetos que la Mochila no debe ofrecer

```bash
python3 create_tables.py /ruta/a/pokemon.db
python3 load_data.py /ruta/a/pokemon.db --dry-run
python3 load_data.py /ruta/a/pokemon.db [--vacuum]
```
Requiere `MachineMoves` (fix_item_descriptions). Copia de `pokemon.db` antes. Sin LFS.

`HiddenItems(GameId, ItemId, Reason)`: hoy 11 filas `machine_without_move` (MT sin movimiento en ningún juego fuente):
Rojo/Verde y Amarillo TM51–TM55, Escarlata/Púrpura TM00, Legends: Z-A TM161. Más las de `data/manual_hidden.csv` (opcional, columnas `game_id,item_id`).
`ItemGameCodes` no se toca. La app no las ofrece para agregar, pero si el save ya trae una, se sigue mostrando.
Para dejar de ocultar una: quitarla de la tabla (o completar su fila en MachineMoves y volver a correr load_data.py).
