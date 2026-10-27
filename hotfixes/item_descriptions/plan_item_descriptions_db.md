# Plan: extracción, creación de datos y migración de descripciones de objetos a pokemon.db

Estado actual: las descripciones salen de `Items.Description` (solo inglés, 1677 filas vacías) y de un JSON embebido (`Assets/item_descriptions.json`, 1299 objetos × 9 idiomas, entrega 71). El movimiento de cada MT/DT se deduce de texto en inglés con `TmDescriptionResolver`.

Objetivo: **una sola fuente en `pokemon.db`** (tablas), con origen y estado de cada texto, regenerable con un script, y la app leyendo solo de ahí.

## Fase 0 — Congelar el punto de partida
- Copia de `pokemon.db` actual (tag/commit en el repo de contexto antes de tocarla).
- Anotar en `Metadata` una `schema_version` (si no existe) para poder detectar bases viejas desde el código.

## Fase 1 — Extracción (script reproducible, sin tocar la base)
Script `hotfixes/item_descriptions/extract.py` (mismo patrón que `fix_database/`):
1. Descargar de PokeAPI (GitHub, CSV): `item_flavor_text`, `item_names`, `machines`, `move_names`, `version_groups`.
2. **Textos de objetos:** por (objeto, idioma) tomar el texto del grupo de versiones más reciente; limpiar saltos de línea (sin espacio en ja/ko/zh) y `\f`.
3. **Emparejar con la base:** hoy se hace por nombre inglés normalizado (2111 de 2515 calzan). Mejora: tabla de **alias manuales** (`aliases.csv`: nombre_db → nombre_pokeapi) para los que difieren por tipografía (’ vs ', acentos, "TM01" vs "TM001").
4. **MT/DT/MO:** `machines.csv` → (grupo de versiones, número, movimiento). Mapa grupo→GameId de la base (SwSh=20, SV=25, Z-A=30 y 31 DLC, etc.). Verificar que `move_id` de PokeAPI coincide con el id de PKHeX (comparar nombres en inglés de los 920+ movimientos; los que difieran se listan).
5. **Plantillas** (sin inventar texto del juego, marcadas como tales): mega piedras nuevas de Z-A y bayas Hyper.
6. **Salida intermedia** en CSV/JSON versionable (diff legible en git): `items_text.csv`, `machine_moves.csv`, `report.md` (cobertura por categoría y por idioma, objetos sin match, conflictos).

## Fase 2 — Creación de datos faltantes (fuentes externas / otras IAs)
Para los ~800 objetos sin fuente abierta (Legends: Arceus/Z-A, Colosseum/XD):
1. Entregar `missing_item_descriptions.csv` + `prompt_research_items.md` a la otra IA/persona.
2. Recibir el JSON y **validarlo con script** (no confiar a ojo):
   - esquema (campos, tipos, `text_kind`, `confidence`);
   - `db_item_id` existente y nombre coincide con el CSV;
   - al menos una URL por entrada con texto; sin URLs de portada;
   - largo razonable (≤ ~200 caracteres), sin saltos, sin comillas envolventes;
   - idioma plausible (ja/ko/zh con caracteres CJK; es/fr/de/it sin kana ni hangul);
   - duplicados y contradicciones entre lotes → cola de revisión manual.
3. Estados: `confidence != high` o `text_kind = wiki_summary` entran como **no verificado** y no se muestran hasta que los apruebes (campo `verified`).
4. Guardar la fuente (URL) por texto: sirve para auditoría y para retirar un texto si hubiera objeción de derechos.

## Fase 3 — Esquema nuevo en la base
```sql
CREATE TABLE ItemDescriptions (
  ItemId   INTEGER NOT NULL REFERENCES Items(ItemId),
  Lang     TEXT    NOT NULL,         -- código PKHeX: en, es, fr, de, it, ja, ko, zh-Hans, zh-Hant
  Text     TEXT    NOT NULL,
  Source   TEXT    NOT NULL,         -- pokeapi | template | research | manual
  SourceUrl TEXT,
  Verified INTEGER NOT NULL DEFAULT 1,
  PRIMARY KEY (ItemId, Lang)
);
CREATE TABLE MachineMoves (
  GameId   INTEGER NOT NULL REFERENCES Games(GameId),
  Number   INTEGER NOT NULL,         -- TM/TR/HM número dentro del juego
  Kind     TEXT    NOT NULL,         -- TM | TR | HM
  ItemId   INTEGER NOT NULL REFERENCES Items(ItemId),
  MoveId   INTEGER NOT NULL,         -- id de PKHeX
  PRIMARY KEY (GameId, Kind, Number)
);
CREATE INDEX IX_ItemDescriptions_Lang ON ItemDescriptions(Lang);
```
- `Items.Description` (inglés) se **conserva** como respaldo hasta el final de la Fase 5; luego se decide si se vacía.
- Sin LFS: la base sigue como blob normal. Cada cambio = un commit de ~51 MB; por eso se agrupan los cambios en **un solo script** idempotente.

## Fase 4 — Migración (script `apply.py`)
1. Abre una copia de `pokemon.db`, crea las tablas si no existen.
2. Carga `items_text.csv` y `machine_moves.csv` (+ resultados validados de la Fase 2) con `INSERT OR REPLACE` en una transacción.
3. Sube `schema_version` y escribe en `Metadata` la fecha y el hash de las fuentes.
4. `VACUUM` y comprobaciones de integridad: `PRAGMA integrity_check`, conteos por idioma, ningún `Text` vacío, ninguna FK huérfana.
5. Resultado: `pokemon.db` nuevo + `report.md`. Tú haces el push manual.
6. **Reversible:** el script no borra nada; volver atrás = restaurar el commit anterior de la base.

## Fase 5 — Cambios en la app
1. `PokemonDatabase`: `GetItemDescription(itemId, lang)` (con respaldo `lang → en → Items.Description`, cargando por lotes como ya se hace con `GetItems`) y `GetMachineMove(gameId, kind, number)`.
2. `ItemDescriptionLocalizer` lee de la base; las MT usan `MachineMoves` (adiós `TmDescriptionResolver` y la deducción por regex sobre inglés).
3. Eliminar `Assets/item_descriptions.json` y su línea en el `.csproj`.
4. Tooltip del editor y Mochila usan la misma consulta.
5. Si el esquema no existe (base vieja): comportamiento actual, sin crashear.

## Fase 6 — Pruebas (proyecto `Exxeguttor.Tests`)
- Esquema presente y con `schema_version` esperada.
- Cobertura: 0 descripciones vacías para MT/DT/MO usadas en algún juego; lista blanca explícita para los objetos que se acepten vacíos.
- Cada `MachineMoves.MoveId` existe en PKHeX y su nombre inglés coincide con el de PokeAPI.
- Cada idioma de `SelectableCodes` tiene un respaldo definido.
- Paridad con la entrega 71: para los objetos ya cubiertos el texto no cambia.

## Orden y estimación de entregas
1. Extracción + informe de cobertura (solo scripts y CSV; sin tocar la base).
2. Validador y primera carga de datos de investigación (si ya los tienes).
3. Base nueva + script de migración.
4. Código de lectura desde la base + pruebas + retiro del JSON.
Cada paso se puede revisar y revertir por separado.

## Riesgos
- **Emparejar por nombre** deja objetos sin match → alias manuales y reporte explícito.
- **Numeración de MT por juego:** no asumir que TM101 es igual en SV y Z-A; por eso la clave es (juego, número).
- **Derechos de los textos:** guardar fuente por texto y poder retirarlos por lote; no republicar el JSON ni la base con textos de terceros sin revisarlo.
- **Tamaño de la base:** commits de ~51 MB; agrupar cambios.
- **Calidad de datos de otras IAs:** nada entra sin validación y estado `verified`.
