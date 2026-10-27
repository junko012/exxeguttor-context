# hotfixes/item_descriptions — Fase 1: extracción

Plan completo: `plan_item_descriptions_db.md`. Esta carpeta **no modifica `pokemon.db`**: solo la lee.

```
python3 extract.py --db ../../database/pokemon.db --out out \
    --pkhex-moves <PKHeX>/PKHeX.Core/Resources/text/other/en/text_Moves_en.txt
```
(descarga los CSV de PokeAPI a `.cache/`, que no se versiona).

Salidas en `out/`: `items_text.csv`, `machine_moves.csv`, `unmatched_items.csv`, `report.md`.

Notas:
- `aliases.csv`: solo alias verificados a mano. Las sugerencias de `unmatched_items.csv` son orientativas y varias son incorrectas (p. ej. "Snow Balm" ≠ "Snowball").
- MT sin movimiento en PokeAPI (probables filas inválidas de la base): Z-A `TM161`, SV `TM00`, Rojo/Verde y Amarillo `TM51`–`TM55`. Revisar en la Fase 3 si se eliminan de `ItemGameCodes`.
- Los ids de movimiento de PokeAPI coinciden con los de PKHeX (verificado).

## Fase 2
- `gen_templates.py`: descripciones de **plantilla** (no oficiales, `source=template`) para las 45 mega piedras de Z-A en 9 idiomas → `out/items_text_template.csv`.
  Las bayas Hyper NO llevan plantilla: no se conoce con certeza su efecto.
- `validate_research.py`: valida el JSON que devuelvan otras IAs (formato de `prompt_research_items.md`) →
  `out/items_text_research.csv` (aceptadas, con `verified`), `out/review_queue.csv`, `out/validation_report.md`.
  `tests/sample_research.json` es un ejemplo con casos buenos y malos.
- `missing_item_descriptions.csv`: lista de objetos a investigar (entrada del prompt y del validador).
