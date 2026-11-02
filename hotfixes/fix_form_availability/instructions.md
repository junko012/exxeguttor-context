# fix_form_availability — tabla `FormGameAvailability` en `pokemon.db`

```bash
python3 create_tables.py /ruta/a/pokemon.db
python3 load_data.py /ruta/a/pokemon.db --dry-run   # opcional: resumen y revierte
python3 load_data.py /ruta/a/pokemon.db             # idempotente: repuebla la tabla entera
```

- Revisión 2026.11.1: 731 filas = 498 `own_encounter` + 233 `uncreatable`. Reemplaza la carga anterior (276 filas).
- `own_encounter`: forma que el combo Forma del editor no puede alcanzar sin romper el origen, pero que
  `BuildPokemon(especie, forma)` deja legal. El selector de creación las ofrece como tarjeta propia. Se sumaron
  letras de Unown (Gen 3/4/5, BDSP, Legends: Arceus, Sol/Luna, Ultrasol/Ultraluna), colores de Flabébé/Florges,
  tamaños de Gourgeist, cortes de Furfrou y patrones de Vivillon/Scatterbug/Spewpa (Gen 6/7), gorras de Pikachu,
  Totem de Gen 7, Sinistea/Polteageist, Toxtricity, formas hembra (Indeedee, Basculegion, Oinkologne, Meowstic),
  Maushold, Dudunsparce, Poltchageist/Sinistcha, Mothim/Shellos/Gastrodon (Legends: Arceus), Magearna Original
  (Espada/Escudo) y Gimmighoul Errante (Escarlata/Púrpura).
- `uncreatable`: se conservan las filas anteriores como registro (233; una pasó a `own_encounter`). El código ya no
  las usa: el combo oculta cualquier forma que deje ilegal al Pokémon (`PokemonService.GetSelectableFormsCore`).
- `Assets/creatable_forms.json` vuelve a ser solo respaldo (sin tabla o sin filas `own_encounter` en la DB) y trae
  las mismas formas `own_encounter` que esta carga: regenerarlo a partir de `form_game_availability.json` si cambia.
- Fuente: barrido con PKHeX.Core 25.11.07 (forma oculta del combo + `BuildPokemon` legal), 21 juegos.
