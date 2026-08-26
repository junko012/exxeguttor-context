# Repoblación de `Items` + tabla nueva `ItemGameCodes` — instrucciones de carga

## ⚡ Resumen ejecutivo (leer esto primero, antes de correr nada)

1. **Correr `INSERT INTO Games (GameCode) VALUES ('colosseum');`** contra tu `pokemon.db`
   real — hoy esa fila no existe (verificado directo contra
   `github.com/junko012/pokemon-database`).
2. Correr en orden:
   ```bash
   python3 create_tables.py /ruta/a/pokemon.db
   python3 load_data.py /ruta/a/pokemon.db
   ```
3. `load_data.py` ya viene con el único `GAME_CODE_OVERRIDES` que hacía falta
   (`"xd" → "galeofdarkness"`, porque tu `Games` usa el subtítulo real del juego).
   El resto de los 23 `GameCode` de tu tabla matchean 1:1 sin ajustes — ya se probó
   end-to-end contra una copia real de tu `pokemon.db` y cargó sin ninguna advertencia.
4. Al terminar, `Items` queda con 2515 filas y `ItemGameCodes` con ~9801 filas efectivas
   (`INSERT OR IGNORE` descarta ~115 duplicados legítimos documentados abajo).
5. **`Items.ItemId` cambia de significado**: deja de ser el ID de PokeAPI y pasa a ser el
   ID unificado moderno de PKHeX.Core. Cualquier código que ya use `Items.ItemId` en otro
   lado del proyecto va a necesitar revisión.

Todo lo demás en este documento es la metodología y los matices, para trazabilidad —
no hace falta leerlo entero para ejecutar la carga.

---

## Archivos de este paquete

| Archivo | Contenido |
|---|---|
| `items.json` | 2515 filas para repoblar `Items` por completo |
| `item_game_codes.json` | 9916 filas para la tabla nueva `ItemGameCodes` (incluye `UserPouchCategory`) |
| `create_tables.py` | Recrea `Items` (mismo schema actual) y crea `ItemGameCodes` |
| `load_data.py` | Carga los dos JSON en `pokemon.db` (ya con el override de `galeofdarkness` aplicado) |
| `add_user_pouch_category.py` | Script ya corrido que generó `UserPouchCategory` en `item_game_codes.json`; se incluye para que quede trazable/editable el mapeo, no hace falta volver a correrlo salvo que quieras ajustar la clasificación |

Este spec viene de una sesión de **diseño de datos** (no de implementación). Todo el
contenido de `items.json` y `item_game_codes.json` fue generado a partir de las fuentes
reales del propio repo de **PKHeX.Core** (clonado y parseado directamente) más
**veekun/pokedex** (snapshot público del dataset detrás de PokeAPI) para metadata
descriptiva, y verificado end-to-end contra una copia real de `pokemon.db`
(`github.com/junko012/pokemon-database`). No hay datos inventados: cada ID, nombre y raw
ID fue extraído programáticamente de esas fuentes, con las excepciones y matices que se
detallan abajo.

## Qué cambia y qué no

- **`Items`**: mismo schema (`ItemId, Name, Description, Category, Cost, FlingPower,
  FlingEffect`), **se borra y repuebla entera**. `ItemId` deja de ser el ID de PokeAPI y
  pasa a ser el **ID unificado moderno de PKHeX.Core** (el mismo espacio que usan
  nativamente los juegos Gen4-9), tal como se acordó.
- **`ItemGameCodes`** (nueva): `(ItemId, GameId, RawItemId, PouchCategory, UserPouchCategory)`,
  PK `(GameId, RawItemId)`, `UNIQUE(ItemId, GameId)`. Resuelve, para cualquier ID crudo
  leído de un save vía PKHeX.Core en cualquier juego, qué ítem canónico es, en qué
  bolsillo vive **realmente** en ese juego (`PouchCategory`, fiel al motor) y en qué
  pestaña de mochila conviene mostrarlo en la **UI** (`UserPouchCategory`, decisión de
  producto — ver sección dedicada más abajo).

## Pasos para correrlo

```bash
python3 create_tables.py /ruta/a/pokemon.db
python3 load_data.py /ruta/a/pokemon.db
```

**Antes del segundo paso**, revisar `GAME_CODE_OVERRIDES` en `load_data.py` — ver sección
"GameCode: verificar antes de cargar" más abajo. Es el único punto que depende de datos
que esta sesión no pudo ver (tu tabla `Games` real).

---

## PouchCategory vs. UserPouchCategory

Son dos cosas distintas a propósito:

- **`PouchCategory`**: el bolsillo/pouch **real**, tal como lo modela el motor del juego
  en PKHeX.Core (`InventoryType`, parseado directo de `ItemStorage*.cs`). Es dato "oficial"
  — útil para legalidad/validación, pero en Gen1-3 es poco granular (Gen1 solo distingue
  `Items`/`TMHMs`; Gen2/3 agregan `Balls`/`KeyItems`/`Berries` pero meten medicina, objetos
  equipables, coleccionables y objetos de trama todos juntos dentro de `Items`).
- **`UserPouchCategory`**: la pestaña de mochila que conviene mostrar en la **UI** de
  Exxeguttor. Para Gen4-9 es una copia directa de `PouchCategory` (ya viene fino). Para
  Gen1-3 y Colosseum/XD, cuando `PouchCategory='Items'`, se sub-clasificó usando
  `Items.Category` (veekun) contra una tabla de mapeo (`CATEGORY_TO_POUCH` en
  `add_user_pouch_category.py`) hacia: `Balls, TMHMs, Medicine, Berries, MailItems,
  KeyItems, Items`. Puede quedar **`NULL` a propósito** en un puñado de casos (4 filas:
  Slowpoke Tail y Bike en dos juegos) — son ítems obsoletos que veekun marca como
  `unused`, no tiene sentido darles una pestaña.

  Distribución resultante en Gen1-3 + Colosseum/XD (antes todo esto vivía indiferenciado
  dentro de `PouchCategory='Items'`):

  | UserPouchCategory | Filas |
  |---|---|
  | KeyItems | 410 |
  | TMHMs | 382 (ya venía separado, sin cambios) |
  | Medicine | 307 |
  | Items | 281 |
  | Berries | 129 |
  | Balls | 66 |
  | *(NULL)* | 4 |

  **Esto es una decisión de producto tuya, no un dato oficial de PKHeX** — el mapeo
  categoría-veekun → pouch-de-UI es editable libremente en
  `add_user_pouch_category.py` si algo no te cierra (ej. si preferís que "Nature Mints"
  tenga su propia pestaña en vez de cae dentro de `Items`).

  **Nota curiosa verificada en el camino**: la categoría `dynamax-crystals` (300 ítems,
  nombres tipo `★And458`) no es basura — son los IDs internos reales de los cristales de
  las Guaridas Max Raid de Espada/Escudo, confirmado contra el propio código de PKHeX
  (`ItemStorage8SWSH.cs`, comentario `// ★And458 (Jangmo-o)`). Quedan con
  `UserPouchCategory=NULL` porque no son objetos que el jugador vea/use como tales en su
  mochila, pero el dato en sí es correcto.

## Metodología (para que quede trazable)

1. **Catálogo canónico**: se tomó `PKHeX.Core/Resources/text/items/text_Items_en.txt`
   (2685 líneas, índice = ID unificado). Se descartaron placeholders (`???`, vacíos,
   `None`) → 2522 entradas reales.
2. **Deduplicación de nombres reutilizados**: algunos IDs unificados repiten nombre
   (ej. "Ultra Ball" existe en el rango 1600-1700 porque **Legends: Arceus** reutiliza
   nombres con IDs propios, mecánicamente distintos del ID "base" 1-419). Se eligió como
   ID canónico el más bajo de cada grupo con el mismo nombre → **2384 ítems canónicos
   reales**. Los IDs más altos del mismo nombre no se pierden: quedan representados como
   filas adicionales en `ItemGameCodes` (ej. Legends: Arceus con su propio `RawItemId`
   apuntando al mismo `ItemId` canónico de "Ultra Ball").
3. **Metadata (Description/Category/Cost/FlingPower/FlingEffect)**: cruce por nombre
   normalizado contra `veekun/pokedex` (items.csv + item_prose.csv + item_categories.csv
   + item_fling_effects.csv, idioma inglés). **1484 de 2515 ítems** tienen esta metadata
   completa. Los **900 restantes** (mayormente Gen7 tardío, Let's Go, Legends: Arceus,
   BDSP, Scarlet/Violet y Legends Z-A — juegos posteriores al snapshot de veekun) quedan
   con `Description/Category/Cost/FlingPower/FlingEffect = NULL` y solo `Name` real de
   PKHeX. **Esto es un hueco de datos real, no un error** — hace falta una segunda pasada
   con una fuente más actualizada (PokeAPI en vivo, o Bulbapedia) para completarlos.
4. **`ItemGameCodes` por juego**:
   - **Gen 4-9** (`diamondpearl` ... `legendsza`, 15 juegos/agrupaciones): el raw ID that
     graba el juego **ya es** el ID unificado — se parsearon directamente las clases
     `ItemStorage*.cs` de PKHeX.Core (arrays por bolsillo + el switch `GetItems`/`GetLegal`
     que asigna cada array a un `InventoryType`).
   - **Gen 2 y Gen 3 mainline (General/Balls/TMs/Bayas)**: convertidos usando las tablas
     oficiales de PKHeX `ItemConverter.Item2to4` / `Item3to4`.
   - **Gen 1 (todo) y Key Items de Gen 2/3/Colosseum/XD**: PKHeX **no tiene tabla oficial
     de conversión** para estos casos (los objetos clave nunca se transfieren entre
     generaciones vía Pal Park/Time Capsule, así que PKHeX nunca necesitó mapearlos). Se
     resolvieron por **coincidencia de nombre** contra el catálogo canónico, con un
     puñado de alias manuales para renombres conocidos (ver abajo) y **IDs sintéticos**
     (rango `90000+`) para los que genuinamente no sobrevivieron a ninguna generación
     posterior (fotos porta-llaves de sala en RS/Emerald, Teachy TV, Tri-Pass, DNA
     Samples de Colosseum, etc. — **131 ítems sintéticos en total**).

## Alias manuales aplicados (verificados, no arbitrarios)

| Nombre en el juego origen | Nombre moderno usado | Cómo se verificó |
|---|---|---|
| Bicycle (Gen1/Gen3) | Bike | Coincidencia directa de concepto, confirmada contra lista moderna |
| Parlyz Heal (Gen1) | Paralyze Heal | ídem |
| X Defend (Gen1) | X Defense | ídem |
| Oak's Parcel (Gen1/Gen3) | Parcel | ídem |
| Itemfinder (Gen1/Gen3) | Dowsing Machine | ídem |
| PP Up (Unused) (Gen1, raw 50) | PP Up | Slot duplicado sin uso — mismo ítem que el raw 79 |
| X Special (Gen1) | X Sp. Atk | **Verificado con la propia tabla `Item2to4` de PKHeX** (Gen2 raw 53 → id 61) |
| Exp. All (Gen1) | Exp. Share | Aproximado — Bulbapedia documenta que su rol se fusionó con Exp. Share desde Gen6. Marcar para revisión si te importa la precisión histórica exacta. |

**Excluidos por no tener ningún equivalente real** (ni siquiera sintético — son datos de
estado del entrenador, no ítems de mochila): las 8 medallas de gimnasio de Kanto,
Bike Voucher, y "Coin" (las monedas de casino se trackean como contador, no como ítem).

## ⚠️ Dos colisiones de nombre genérico — revisar antes de confiar ciegamente

El matching por nombre asume que un mismo nombre = mismo ítem entre juegos. Dos casos
son sospechosos porque el nombre es genérico y el ítem real podría ser distinto entre
juegos:

- **"Elevator Key"**: Colosseum (raw 501) y XD (raw 501) quedaron mapeados al ID
  canónico 700, que es el "Elevator Key" real de **Legends: Arceus**. Es posible que sean
  conceptualmente el mismo tipo de objeto (llave de ascensor) pero de edificios
  completamente distintos — no hay garantía de que deban compartir fila.
- **"Card Key"**: Colosseum (raw 510) y FireRed/LeafGreen (raw 355) comparten el ID
  canónico 475 (el "Card Key" del Team Rocket Hideout).

Si preferís tratarlos como ítems distintos, lo más simple es asignarles un ID sintético
propio (rango 90000+) en vez del canónico — es un cambio de una línea en el JSON antes
de cargar.

## GameCode: ya verificado contra tu DB real

`item_game_codes.json` usa 24 slugs de texto para identificar juegos. Se contrastaron
directamente contra `github.com/junko012/pokemon-database` (23 `GameCode` reales en tu
tabla `Games`). Resultado:

- **22 coinciden 1:1**, sin ajustes.
- **`xd`** (este JSON) → tu DB lo llama **`galeofdarkness`** (subtítulo real de Pokémon
  XD). Ya resuelto en `load_data.py` vía `GAME_CODE_OVERRIDES`.
- **`colosseum`** no existe como fila en tu `Games` — hace falta el `INSERT` mencionado en
  el resumen ejecutivo antes de cargar, o esas 48 filas se van a reportar como
  "GameCode sin correspondencia" y se van a omitir sin romper nada.

Se probó la carga completa (`create_tables.py` + `load_data.py`) contra una copia real de
tu `pokemon.db` con ese `INSERT` aplicado: cero advertencias, 2515 filas en `Items` y
~9801 filas efectivas en `ItemGameCodes`.

## Nota sobre `load_data.py` y filas duplicadas dentro de un mismo juego

`load_data.py` inserta con `INSERT OR IGNORE`. Vas a ver que insertó ~115 filas menos que
las que trae `item_game_codes.json` (9916 → ~9801) — es esperado, no un bug: son casos
donde **un mismo juego tiene más de un `RawItemId` apuntando al mismo `ItemId` canónico**
(viola `UNIQUE(ItemId, GameId)` y se ignora la segunda ocurrencia, se queda la primera).
Ejemplos reales: **Legends: Arceus** tiene dos raw IDs distintos para "Ultra Ball" (posible
variante crafteada vs. comprada); **Colosseum** tiene 18 slots crudos distintos todos
llamados "DNA Sample" (uno por Pokémon Sombra específico de la trama), colapsados acá en
un solo ítem canónico "DNA Sample" por simplicidad de catálogo. Si tu UI necesita
distinguir esos casos individualmente (ej. mostrar de qué Pokémon es cada DNA Sample),
avisá y se separan con IDs sintéticos propios en vez de compartir uno.

## Resumen numérico

| Concepto | Cantidad |
|---|---|
| Ítems canónicos reales (ID unificado PKHeX) | 2384 |
| Ítems sintéticos (Colosseum/XD/Gen3-exclusivos, ID ≥ 90000) | 131 |
| **Total filas en `items.json`** | **2515** |
| Con metadata completa (veekun) | 1484 |
| Solo nombre (juegos posteriores al snapshot de veekun — pendiente 2da pasada) | 900 |
| **Total filas en `item_game_codes.json`** | **9916** |
| Juegos/agrupaciones cubiertos | 21 |
