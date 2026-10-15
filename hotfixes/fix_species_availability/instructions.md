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

## Revisión 2026.10.1
- Tras mejorar `BuildPokemon` (moveset sugerido por PKHeX como último recurso, FormArgument de Basculegion/Wyrdeer/Overqwil), 43 especies pasaron de `present_illegal` a `native`: 37 en Legends: Arceus, 5 en Espada/Escudo y 1 en Escarlata/Púrpura. Quedan `present_illegal`: Hoopa y Volcanion en Z-A (sin encuentro legal con PKHeX 25.11.07) y 6 en Escarlata/Púrpura. No cambia ninguna especie `uncreatable`, así que `Assets/uncreatable_species.json` sigue igual.

## Revisión 2026.10.2
- Yanmega y Dudunsparce (Escarlata/Púrpura) pasan de `present_illegal` a `native`: la sonda de nivel de `TryBuildFromLegitEncounter` ahora regenera el moveset en cada nivel probado (Gen9) y no acepta candidatos con slots vacíos/ilegales. Quedan `present_illegal` solo Hoopa y Volcanion en Z-A (sin encuentro legal con PKHeX 25.11.07). Ninguna especie `uncreatable` cambia.

## Revisión 2026.10.3
- Legends: Arceus: 17 especies cuya forma base no existe en el juego pasan a `uncreatable` (Growlithe, Arcanine, Voltorb, Electrode, Typhlosion, Qwilfish, Samurott, Lilligant, Basculin, Zorua, Zoroark, Braviary, Sliggoo, Goodra, Avalugg, Decidueye y Giratina). 16 estaban como `dlc` y Giratina como `native`. Antes el selector ofrecía la base y `BuildPokemon` la cambiaba en silencio a la forma que sí existe (Hisui; Giratina Origen; Basculin Rayas Blancas). Las formas de Hisui siguen ofreciéndose como tarjetas propias (catálogo regional); Giratina Origen (487:1) y Basculin Rayas Blancas (550:2) se agregan en `fix_form_availability` como `own_encounter`. `Assets/uncreatable_species.json` (PLA 663 → 680) y `Assets/creatable_forms.json` (GameId 11) se actualizan igual.

