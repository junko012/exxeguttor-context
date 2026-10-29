# fix_item_names — nombres de objetos de Z-A que PKHeX no trae, en `pokemon.db`

```bash
cd hotfixes/fix_item_names
python3 validate_names.py                       # research_raw/*.json -> data/item_names.csv (falla si hay errores)
python3 create_tables.py /ruta/a/pokemon.db     # crea ItemNames si no existe
python3 load_data.py /ruta/a/pokemon.db --dry-run
python3 load_data.py /ruta/a/pokemon.db [--vacuum]
```
Idempotente: `ItemNames` se reconstruye completa en una transacción. Copia de `pokemon.db` antes. Sin LFS.

## Qué agrega
`ItemNames(ItemId, Lang, Name, Source, SourceUrl, Confidence, Verified)`, PK (ItemId, Lang). Metadata `ItemNamesVersion/Source`.
Solo para los 65 objetos de Legends: Z-A sin nombre en PKHeX 25.11.07. No toca `Items`, `ItemGameCodes` ni `ItemDescriptions`.

## Flujo para agregar más nombres
1. Lista de objetos → CSV (`data/za_item_names_to_research.csv`) y `prompt_research_item_names.md` para la otra IA.
2. Guardar los JSON en `research_raw/` y correr `validate_names.py` (exige URL por nombre, sin espacios CJK, ids esperados).
3. `load_data.py`.
`confidence: low` entra con `Verified=0` (la app no lo muestra); `not_found` no entra.

## Conocido
- Fuente wiki (Bulbapedia, WikiDex, Poképédia), no capturas del juego. Los 65 objetos tienen los 9 idiomas.
- Cuando PKHeX incorpore estos nombres, la app ya los prefiere (ItemNames solo se usa si PKHeX no devuelve nombre).
