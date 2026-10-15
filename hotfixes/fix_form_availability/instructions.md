# fix_form_availability — tabla `FormGameAvailability` en `pokemon.db`

```bash
python3 create_tables.py /ruta/a/pokemon.db
python3 load_data.py /ruta/a/pokemon.db --dry-run   # opcional
python3 load_data.py /ruta/a/pokemon.db             # idempotente
```

- Formas (`SpeciesId`, `FormId`) que `PokemonService.BuildPokemon` no deja legales en un juego:
  legendsza (12), legendsarceus (11), scarletviolet (18), swordshield (20). Status `uncreatable`.
- El combo Forma las oculta solo si además `FormBreaksOrigin` confirma que el cambio rompe el origen
  (Z-A: Zygarde 10%/50%, Ash-Greninja).
- Respaldo si la tabla no existe: `Assets/uncreatable_forms.json` (mismos datos, embebido).
- Regenerar al actualizar PKHeX.Core.

## Status
- `uncreatable`: BuildPokemon no logra esa forma legal (el combo Forma la oculta si cambiarla rompe el origen).
- `own_encounter`: la forma se oculta del combo (cambiarla desde otro encuentro rompe el origen) pero tiene
  encuentro legal propio; el selector de creación la ofrece como tarjeta aparte (p. ej. Zygarde 10%,
  Ash-Greninja Battle Bond, Lycanroc Midnight en Gen 7). Respaldo: `Assets/creatable_forms.json` (clave = GameId).

## Revisión 2026.10.1
- Legends: Arceus (GameId 11): `own_encounter` para Giratina Origen (487:1) y Basculin Rayas Blancas (550:2), las únicas formas de esas especies que existen en el juego (su forma base se oculta desde `fix_species_availability` 2026.10.3).

