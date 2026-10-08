# fix_form_data — evoluciones por forma y datos por forma en `pokemon.db`

## Resumen (leer primero)

```bash
python3 create_tables.py /ruta/a/pokemon.db      # crea FormEvolutionChains y FormEvolutionConditions
python3 load_data.py /ruta/a/pokemon.db --dry-run # opcional: muestra el resumen y revierte
python3 load_data.py /ruta/a/pokemon.db           # carga (idempotente: se puede repetir)
```

Probado contra una copia de la `pokemon.db` del repo (commit 50d7c52): `integrity_check` ok, mismas
filas en todas las tablas existentes, y solo cambian filas de forma de `Species` (`SpeciesId > 10000`).

## Qué hace

| Cambio | Detalle |
|---|---|
| Tabla nueva `FormEvolutionChains` | 54 aristas. Mismas columnas que `EvolutionChains`; `FromSpeciesId`/`ToSpeciesId` pueden ser filas de forma de `Species` (> 10000). |
| Tabla nueva `FormEvolutionConditions` | 340 filas. Mismo EAV y mismo vocabulario de `ConditionType` que `EvolutionConditions` (cada arista trae también los 5 valores por defecto: `trigger`, `time_of_day`, `needs_overworld_rain`, `needs_multiplayer`, `turn_upside_down`). |
| `Species.EggGroup1/EggGroup2` de formas | 132 formas tenían NULL; se completan con el dato por forma de PKHeX.Core (mismo formato: `plant`, `no-eggs`, `humanshape`...). Solo 3 difieren de la especie base (Greninja Battle Bond/Ash y Floette Eterna: `no-eggs`). |
| `Species.GenderRate` | 7 filas corregidas (PokeAPI da un dato por especie): Meowstic♀, Indeedee♀, Basculegion♀, Oinkologne♀ → 8 (siempre hembra); Ursaluna Bloodmoon, Greninja Battle Bond/Ash → 0 (siempre macho). |
| `Species.Height/Weight` | Solo Ursaluna Bloodmoon (2.4 m/290 kg → 2.7 m/333 kg, valores del juego). |
| `Metadata.FormDataVersion` | `2026.10`. `SchemaVersion` no se toca. |

No se tocan `EvolutionChains`, `EvolutionConditions`, `SpeciesTypes`, `SpeciesAbilities` ni `Learnsets`.

## Por qué tablas nuevas y no filas en `EvolutionChains`

`EvolutionChains` tiene una arista por especie y junta en un solo diccionario las condiciones de
todas las formas (p. ej. Meowth→Persian mezcla `min_level 28` de Kanto con `min_happiness 160` de
Alola), así que no distingue "Slowbro de Galar" de "Slowbro". Meter ahí filas con ids de forma haría
que Pikachu mostrara dos evoluciones en el código que ya lee esa tabla. Las tablas nuevas tienen la
misma forma, se leen y se unen igual, y no cambian nada de lo existente.

## Cómo leerlas

```sql
SELECT f.Name AS Desde, t.Name AS Hacia, c.ConditionType, c.ConditionValue
FROM   FormEvolutionChains e
JOIN   Species f ON f.SpeciesId = e.FromSpeciesId
JOIN   Species t ON t.SpeciesId = e.ToSpeciesId
JOIN   FormEvolutionConditions c ON c.EvolutionId = e.EvolutionId
WHERE  f.Name = 'slowpoke-galar';
```

## Matices

- Una arista puede repetirse si la condición cambia por juego (Qwilfish de Hisui → Overqwil: usar
  Barb Barrage 20 veces en Legends: Arceus; conocer Barb Barrage en Escarlata/Púrpura). Lo mismo con
  Sneasel de Hisui → Sneasler.
- Las aristas de base → forma (Pikachu → Raichu de Alola, Koffing → Weezing de Galar, Quilava →
  Typhlosion de Hisui...) llevan `region` (`alola`/`galar`/`hisui`/`paldea`): evolucionan a la forma
  regional solo en esa región.
- Genus (`GenusEs/GenusEn`), `Habitat` y `SpeciesFlavorText` de las formas siguen sin dato propio:
  no existe fuente por forma (PokeAPI los guarda por especie). El código debe usar los de la base.
- Los extractores (`tools/*.cs.txt`) son los programas de PKHeX.Core que generaron los dos JSON; se
  incluyen para trazabilidad, no hace falta correrlos.

## Archivos

| Archivo | Contenido |
|---|---|
| `form_evolutions.json` | 54 aristas con condiciones (y juegos de origen en `Sources`, informativo) |
| `species_form_data.json` | 132 filas de forma: grupos de huevo y `Corrections` |
| `create_tables.py` / `load_data.py` | creación y carga |
| `tools/ExtractFormEvolutions.cs.txt`, `tools/ExtractFormData.cs.txt` | extractores PKHeX.Core 25.11.07 |
