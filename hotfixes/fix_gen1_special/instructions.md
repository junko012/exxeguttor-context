# fix_gen1_special — stat Especial único de Gen 1 en `pokemon.db`

```bash
python3 create_tables.py /ruta/a/pokemon.db        # agrega Species.BaseSpecialGen1 (si no existe)
python3 load_data.py /ruta/a/pokemon.db --dry-run  # opcional
python3 load_data.py /ruta/a/pokemon.db            # idempotente
```

- En Gen 1 existía un solo stat Especial. Las columnas `BaseSpAttack` / `BaseSpDefense` de `Species` son las de
  Gen 2+ (46 de las 151 especies de Kanto tienen un Ataque Esp. distinto del Especial de Gen 1, 67 en Defensa Esp.:
  Charizard 109/85 vs Especial 85; Tauros 40/70 vs 70).
- Columna nueva: `Species.BaseSpecialGen1` (INTEGER, NULL salvo las 151 de Kanto). Dato: `gen1_special.json`,
  verificado contra la tabla de Gen 1 de PKHeX.Core (`PersonalTable.RB`): 151/151 coinciden.
- La app (`PokemonDatabase.GetSpecies` → `SpeciesEntry.BaseStats.Gen1Special` → `PokemonEditorViewModel.ApplyGen1Special`)
  usa la columna SOLO cuando el save es Gen 1 (barras, radar y total base de Gen 1). Una DB sin la columna
  conserva el comportamiento anterior (Def. Esp. = Atq. Esp.).
- Metadata: `Gen1SpecialVersion`, `Gen1SpecialSource`.
