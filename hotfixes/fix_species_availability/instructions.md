# fix_species_availability — tabla `SpeciesGameAvailability` en `pokemon.db`

```bash
python3 create_tables.py /ruta/a/pokemon.db
python3 load_data.py /ruta/a/pokemon.db --dry-run   # opcional: resumen y revierte
python3 load_data.py /ruta/a/pokemon.db             # idempotente: repuebla la tabla entera
```

Probado sobre la `pokemon.db` del repo (commit 171344b): `integrity_check` ok, `foreign_key_check` vacío,
mismas filas en todas las tablas existentes; solo cambia `Metadata` (+2 claves).

- 4507 filas, solo para los 5 juegos que recortan su Pokédex: letsgopikachueevee (13), swordshield (20),
  legendsarceus (11), scarletviolet (18), legendsza (12). Sin filas = el juego no restringe nada.
- `Status`: `native`, `present_illegal`, `transfer_only`, `dlc`, `uncreatable` (definiciones en
  `docs/SCHEMA_REFERENCE.md` y en la cabecera de `load_data.py`). El selector de creación oculta solo `uncreatable`.
- Por par de versiones (SW/SH, SL/VL, GP/GE) una especie es `native` si lo es en cualquiera de las dos.
- Los conteos `uncreatable` coinciden exactamente con `Assets/uncreatable_species.json` (respaldo en el código).
- `species_game_availability.json` es el dato; `tools/ExtractSpeciesAvailability.cs.txt` es el programa de
  PKHeX.Core que lo generó (trazabilidad; no hace falta correrlo). Regenerar al actualizar PKHeX.Core.
