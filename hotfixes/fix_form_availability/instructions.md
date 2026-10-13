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
