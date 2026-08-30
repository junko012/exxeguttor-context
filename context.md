# context.md — Estado actual del proyecto Exxeguttor

_Última actualización: sesión larga de corrección del módulo Mochila (categorización real por
generación vía `ItemGameCodes.RawItemId`, ya no bloqueada), rediseño del panel central a grilla
de tiles tipo Caja de Pokémon con origen Mochila/PC navegable, descripciones de MT/HM por
generación, y gestión de sesión de save (Cerrar/Limpiar ediciones/confirmar antes de abrir otro
archivo). Sin repo git — no hay historial de commits._

---

## 📌 Estrategia de desarrollo — ya no aplica la secuenciación original

Durante gran parte del desarrollo, la estrategia fue "fase 1: pulir toda la UI en pendiente-
hasta-exportar, fase 2: recién ahí conectar la escritura real". **Esa fase 2 ya pasó** — el
pipeline de escritura real está implementado (ver GAP CRÍTICO abajo, ahora resuelto). El
desarrollo sigue, pero ya no bajo esa restricción de secuencia: se puede seguir sumando
funcionalidad de UI (Mochila, Pokédex) y a la vez seguir afinando el pipeline de escritura
(cintas/habilidad/objeto/shiny/dynamax/alpha ya están cableados pero sin test de round-trip
dedicado todavía — ver sección de Testing).

---

## ✅ GAP CRÍTICO — resuelto esta sesión (era la limitación histórica del proyecto)

Durante mucho tiempo, el editor fue una capa muy completa de "edición pendiente en memoria"
que nunca se aplicaba al `PKM`/`SaveFile` real — exportar escribía el save tal cual estaba en
memoria, sin las ediciones hechas en pantalla. **Esto ya no es así.**

### Cómo quedó armado el pipeline real

`EditSessionService` sigue siendo la única fuente de "qué cambió" (sin cambios en su rol ni en
el patrón de valor prístino). Lo nuevo es **`EditApplyService`** (Exxeguttor.UI/Services),
llamado desde `MainWindowViewModel.ConfirmExportAsync` **antes** de `PerformExportAsync`:

```csharp
private async Task ConfirmExportAsync()
{
    IsReviewModalVisible = false;
    _editApply.ApplyIncluded(ReviewSummary, TrainerSummary, BagReviewSummary);
    await PerformExportAsync();
}
```

`IsIncluded` en las tarjetas del modal de revisión **ahora filtra de verdad** — antes era
decorativo, y solo existía en la tarjeta de Pokémon. Se agregó también a
`EditedTrainerSummary`/`EditedBagPouchSummary` (antes esas dos no tenían checkbox porque "se
exportaban siempre que hubiera alguna edición" — ahora el usuario puede destildar cualquiera
de las tres superficies).

### Las cuatro superficies, cada una con su propio mecanismo (no es un diff genérico)

1. **Pokémon (Box/Party)** — releer el PKM real del slot (o tomar el ya construido si es una
   creación pendiente de `EditSessionService.GetPendingCreation`, aplicándole además cualquier
   edición posterior sobre ese mismo slot — creación y edición no son mutuamente excluyentes,
   el usuario puede crear un Pokémon y después tocarle algo más antes de exportar). Aplicar
   campos vía setters directos del PKM: mismo mapeo que ya usaba
   `EditSessionService.AnalyzeLegality` para el preview de legalidad (Nickname, Level, Nature,
   IVs, EVs, Moves+PPUps), extendido acá a Habilidad, HeldItem, Shiny (`SetShiny()`/
   `SetUnshiny()`), Dynamax/Gigantamax (PK8), Alpha/Noble (PA8) y Alpha (PA9, sin Noble — ver
   Legends Z-A abajo), que el preview de legalidad no cubre. Después `pkm.RefreshChecksum()` y
   `save.SetBoxSlotAtIndex(pkm, box, slot, default)` / `SetPartySlotAtIndex(pkm, slot, default)`
   — el `default` es un `EntityImportSettings` (struct, "lo conservador": no toca Pokédex ni
   records).
2. **Cintas** — nuevo `RibbonWriter` (simétrico a `RibbonReader`, generado a partir de su mismo
   mapeo interfaz-por-generación en vez de reinvestigado a mano). Dos caminos: formatos
   modernos usan `IRibbonIndex.SetRibbon(int, bool)` (un solo método para cualquier cinta);
   formatos viejos usan el setter de propiedad específico de cada cinta
   (`IRibbonSetCommonN.RibbonX = value`, resuelto por pattern-matching contra la interfaz
   correspondiente).
3. **Entrenador** — `TrainerService.ApplyEdits(...)` (Exxeguttor.App, simétrico a
   `GetTrainerInfo`), directo sobre `SaveFile`, sin clon. Mismo mecanismo de reflection que ya
   usaba la lectura para Money/Coin/BP (son `uint` en PKHeX.Core, `Convert.ChangeType` respeta
   el tipo real de la propiedad en vez de asumir `int`).
4. **Mochila** — el más particular: `InventoryPouch.Items` es un array de **tamaño fijo** por
   pouch (confirmado con test — cambiar el largo tira `ArgumentOutOfRangeException` en
   `SetPouch`). Aplicar una edición de cantidad busca el slot existente de ese ítem (para
   actualizar `Count` in-place) o, si es cantidad nueva, el primer slot con `Count==0` (para
   ocuparlo); nunca se agrega/saca una entrada del array. Al final se reasigna
   `save.Inventory` completo.

### SaveFileService — nombre sugerido y backup con la convención real de PKHeX

- El nombre sugerido del diálogo de "Exportar" ahora usa
  `save.Metadata.GetSuggestedExtension()` (la extensión real del formato de *ese* save
  concreto — `.sav`, sin extensión para Switch, etc.) en vez de reusar ciegamente el nombre del
  archivo original.
- El backup usa `save.Metadata.GetBackupFileName(directorio)` — la convención de nombre real de
  PKHeX.Core (`" [Entrenador (Versión) - fecha].bak"`). **Ojo**: el método espera el
  *directorio* donde va el backup, no la ruta completa del archivo — pasarle la ruta completa
  hace que trate el nombre del archivo como si fuera una carpeta más. Tiene fallback al
  timestamp manual de antes si `GetBackupFileName` falla (puede pasar con un save sintético sin
  fecha jugada válida — no debería darse con un save real de usuario).

### Qué está confirmado con test de round-trip, y qué no todavía

`tests/Exxeguttor.Tests/WritePipelineRoundTripTests.cs` — **mutación en memoria contra la
misma instancia de `SaveFile`**, no un ciclo binario completo `Write()` + releer bytes (ver
"Trampas conocidas" #20 para por qué). Confirmado con assertions reales: campos básicos de
Pokémon (Nickname/Level/Nature/IVs/EVs/Moves+PPUps) en 5 generaciones, Entrenador, Mochila,
Cintas (formato viejo en Gen3+Gen4, formato moderno en Gen9).

**Sin test de round-trip dedicado todavía** (compila, tipos verificados por reflection, pero
sin confirmar con datos reales): Habilidad, HeldItem, Shiny, Dynamax/Gigantamax, Alpha/Noble,
creación de Pokémon nuevo. Prioridad para una sesión futura antes de dar el pipeline por
100% cerrado.

**Deliberadamente afuera**: Tera (`PK9.TeraTypeOriginal`/`Override`) sigue solo lectura en la
UI — no se escribe todavía.

---

## 🎒 Módulo Mochila — categorización corregida, panel rediseñado (sesión larga)

### Arquitectura de lectura — `ItemInventoryService` (Exxeguttor.App)

**`pokemon.db.ItemGameCodes` es la ÚNICA fuente de qué categorías existen y qué ítems caen en
cada una, para toda generación por igual** — `SaveFile.Inventory` de PKHeX.Core solo se consulta
para leer/ubicar la CANTIDAD poseída real de cada ítem, nunca para decidir categorización. Esto
reemplaza por completo el diseño de `CategoryUpper` que se había acordado en la sesión anterior
y nunca llegó a implementarse (ver "Historial de diseño" abajo — la causa real resultó ser otra).

**`ItemGameCodes` tiene dos columnas de ID por fila, con roles distintos**:
- `ItemId` — el ID unificado de `pokemon.db` (para buscar `Name`/`Description`/`Category` en
  `Items`).
- `RawItemId` — el índice REAL que usa PKHeX.Core para ESE juego puntual. **Casi nunca coincide
  con `ItemId`** (confirmado contra un save real de Yellow: 125 de 130 filas difieren) — es el
  que hay que usar para matchear contra `InventoryPouch.Items[].Index`, tanto en lectura
  (`ItemInventoryService.GetPouches`/`GetItems`) como en escritura
  (`EditApplyService.ApplyBagPouch`).

`PokemonDatabase.GetItemPouchRows(gameId)` devuelve `List<ItemPouchRow>` (`ItemId`, `RawItemId`,
`UserPouchCategory`) para un `GameId` puntual — reemplaza al viejo
`GetItemUserPouchCategories(gameId)` (que devolvía solo `ItemId`→categoría, sin `RawItemId`, la
causa real del bug de MTs/MOs y de otros ítems que fallaban en silencio — ver más abajo).

**"Origen" (Mochila vs PC) es un eje ortogonal a la categoría** — ambos parámetros públicos de
`ItemInventoryService` (`GetPouches`/`GetItems`) llevan `useAlternateStorage: bool`:
- **Mochila**: cada categoría busca SU pouch real por `Type` en `save.Inventory`, con fallback
  al pouch genérico `Items` si esa generación no tiene uno dedicado (ej. "Bolas" en Gen1 — el
  juego solo tiene un pouch `Items` real donde vive todo mezclado). Mismo fallback en
  `EditApplyService.ApplyBagPouch` para la escritura.
- **PC**: un ÚNICO pouch físico real (`PCItems`/`FreeSpace`) sirve a TODAS las categorías —
  mismas tiles que Mochila, pero leyendo/escribiendo cantidades del pouch de PC. Si esta
  generación no tiene ningún pouch de PC real (Gen4+), `GetPouches(useAlternateStorage: true)`
  devuelve vacío — señal para `BagViewModel.ShowStoreNav`.

`InventoryPouch.CanContain` de PKHeX.Core **ya no se usa para nada** en este módulo (ver
Historial de diseño — se probó, resultó no confiable, y ni siquiera hacía falta una vez que se
encontró que `RawItemId` ya tenía el dato correcto desde el hotfix `fix_database`).

### Descripción de MT/HM por generación — `TmDescriptionResolver` (Exxeguttor.App, nuevo)

Para ítems `Category == "all-machines"` (TM/HM/TR), la `Description` cruda de `pokemon.db` es
prosa libre de veekun que menciona el movimiento de VARIAS generaciones a la vez en una sola
oración (ej. TM01: *"Teaches Hone Claws... (Gen IV & III: Focus Punch Gen II: DynamicPunch Gen
I: Mega Punch)"*) — confuso mostrado tal cual cuando el usuario mira el save de una generación
puntual. `TmDescriptionResolver.Resolve(rawDescription, generation)` parsea esa prosa (regex
sobre el patrón `"Gen <romano>[ & <romano>]: <movimiento>"`) y devuelve solo el movimiento que
corresponde a `save.Generation`. De Gen6 en adelante la Description ya viene sin paréntesis (un
solo movimiento, roster de MTs no reciclado entre generaciones) — se devuelve intacta.

**Gap de datos, no bloqueante**: TRs de Espada/Escudo (`Category` también `"all-machines"`) no
tienen `Description` cargada en absoluto desde el origen (`items.json` del hotfix
`fix_database`) — el resolver no tiene nada que parsear ahí, no es un bug del resolver.

### UI — panel central rediseñado a grilla de tiles tipo Caja (`BagPouchGridView`)

**Corrección de diseño explícita del usuario**: el diseño anterior (navegación `◀ nombre ▶` de a
una categoría, "mismo patrón que Caja pero solo cambia el texto") se descartó — el pedido fue
que el panel central se vea **exactamente como la grilla de Cajas de Pokémon**: arriba se navega
el **origen** (Mochila/PC, ◀▶, equivalente a Caja 1/Caja 2 — `BagViewModel.PreviousStoreCommand`/
`NextStoreCommand`, clamp sin wrap, mismo criterio que `BoxViewModel.PreviousBox`/`NextBox`), y
la **grilla de abajo muestra las categorías como tiles clickeables** (equivalente a los Pokémon
dentro de una caja), no una única categoría a la vez.

- **`Views/BagPouchTileView.axaml`** (nuevo, equivalente a `PokemonSlotView`) — la tile
  individual: ícono, nombre, contador "poseídos/legales". 204×108 (no 84×84 — ese tamaño se
  heredó sin querer de `PokemonSlotView` en un primer intento y hubo que agrandarlo para que
  entren 3 tiles por fila).
- **`BagPouchGridView.axaml`** — nav de origen arriba (`◀ Mochila/PC ▶` + texto "Almacenamiento
  X / 2") + `ItemsControl`/`WrapPanel` de tiles abajo, mismo esqueleto que `BoxView.axaml`.
  Code-behind maneja el click sobre una tile (`BagViewModel.SelectPouch`), igual que
  `BoxView.axaml.cs` con `PokemonSlotView`.
- **`BagItemListView.axaml`** (panel derecho) — sin cambios de estructura: buscador acotado a la
  categoría seleccionada, lista de todos los ítems legales (poseídos y no), cada fila con
  checkbox/sprite/descripción/stepper/MAX.

### Historial de diseño — por qué se descartó `CategoryUpper` (dejar como referencia, no repetir)

La sesión anterior había diseñado y dado por acordada una migración de `pokemon.db` agregando
una columna `CategoryUpper` a `Items`, bloqueada esperando un fix de modelado de TMs. **Esa
migración nunca se hizo** — en la sesión siguiente se aplicó en cambio el hotfix `fix_database`
(ver `exxeguttor-context/hotfixes/fix_database/`), que creó una tabla nueva **`ItemGameCodes`**
(no una columna en `Items`) con `PouchCategory`/`UserPouchCategory` **por juego** (no un valor
global por ítem como iba a ser `CategoryUpper`) — diseño más granular y correcto, que de paso ya
traía la columna `RawItemId` que terminó siendo la pieza que faltaba.

El camino hasta la causa real (documentado para no repetir la misma investigación):
1. Primera versión de esta sesión usó `InventoryPouch.CanContain` con un camino dual según si el
   save tenía una subclase dedicada de `InventoryPouch` — resultó poco confiable (Gen1 no se
   detectaba como esperado en runtime).
2. Se sacó `CanContain`, todo pasó a `ItemGameCodes.UserPouchCategory` — pero matcheando por
   `ItemId` (el unificado) contra `pouch.Items[].Index`. Funcionó para la mayoría de "Objetos"
   por coincidencia (muchos ítems comunes con ID bajo tienen `ItemId == RawItemId`), pero falló
   en silencio para el resto — visible sobre todo en MTs/MOs, donde SIEMPRE difieren.
3. Se armó un camino especial solo para MTs/MOs resolviendo índices y nombres en vivo contra
   PKHeX.Core (`InventoryPouch.GetAllItems()` + `GameStrings.GetItemStrings(save.Context,
   save.Version)`, confirmado por reflection real sobre el DLL vía tests `[Fact]` con
   `Assert.Fail` — sin acceso a NuGet en el sandbox de análisis, no se pudo verificar por
   reflection cruda esta vez, hizo falta que el usuario corriera los tests y pegara la salida).
   Funcionaba, pero dejaba el mismo bug sin resolver para el resto de categorías en Gen1/2 (Cebo
   Bueno, Piedras evolutivas, etc. — nunca reportado porque no se probó con esos ítems
   puntuales).
4. **Causa real**: `ItemGameCodes.RawItemId` ya tenía el índice correcto por juego desde el
   hotfix — nunca se había usado esa columna. Con eso, un solo camino uniforme alcanza para
   todas las categorías y generaciones — se sacó el camino especial de MTs/MOs por completo.

**Piedras evolutivas**: decisión de producto re-confirmada esta sesión — siguen dentro de la
tile genérica "Objetos", **no** tienen tile propia (la idea de una categoría virtual `"Stones"`
del diseño viejo no se implementó).

**Gap conocido, no bloqueante — Colosseum/XD**: `ItemGameCodes` solo tiene los 122 ítems
EXCLUSIVOS de esos dos juegos (llaves, discos, ADN Samples — rango sintético `ItemId >= 90000`,
sin ID unificado de PKHeX.Core). Los ítems COMPARTIDOS con el resto de la saga (Poké Ball,
Potion, etc., que también existen y se usan en Colosseum/XD) no están mapeados a esos dos
`GameCode` — un save real de Colosseum/XD hoy solo mostraría la tile "Clave" en Mochila. Ver
`hotfixes/colosseum_xd_shared_items_gap.md` para el detalle completo si se retoma.

### Gestión de sesión de save (Cerrar / Limpiar ediciones / confirmar antes de abrir otro)

Tres agregados a `MainWindowViewModel`, todos con el mismo lenguaje visual (overlay oscuro +
tarjeta blanca centrada, botón de acción destructiva en rojo):

- **Bug real corregido**: `EditSessionService` no se reseteaba al abrir un save nuevo — las
  claves de edición son estructurales (`PokemonSlotKey` de Box1/Slot1 es la misma para
  cualquier save), así que las ediciones pendientes de un save anterior quedaban pegadas y se
  mostraban/aplicaban sobre el save recién abierto. `EditSessionService.ResetSession()` (nuevo —
  limpia `_pendingEdits`/`_pristineValues`/`_displayNames`/`_nicknames`/`_pendingCreations`, las
  5 estructuras de estado) se llama ahora tras un `OpenAsync` exitoso (no antes — si el open
  falla, el save viejo si lo había sigue intacto).
- **Cerrar save** (`CloseSaveCommand`, ícono ✖ + menú File `Ctrl+W`) — vuelve a Pantalla 1
  (Recientes/drag&drop). Pregunta confirmación solo si `EditSessionService.HasAnyEdits` (ahora
  también cuenta `_pendingCreations`, no solo `_pendingEdits` — un Pokémon recién creado sin
  editar ninguna propiedad todavía antes no contaba como "hay cambios").
- **Limpiar ediciones** (`ClearEditsCommand`, ícono 🧹 al lado de la libreta) — descarta todo lo
  pendiente SIN cerrar el save, repoblando los paneles desde el `SaveFile` real (nunca se
  mutó — las ediciones son pendientes hasta exportar), mismo bloque de repoblado que
  `OpenSaveFromPathAsync`.
- **Confirmar antes de abrir otro save** (`RequestOpenSaveFromPath`, gatekeeper único para las
  tres formas de abrir — diálogo del sistema, Recientes, y a futuro drag&drop) — mismo gap que
  Cerrar pero en la otra puerta de entrada, agregado a pedido explícito del usuario.

**Caso pendiente sin resolver, revisar antes de sacar el ejecutable**: reportado que, tras
editar y luego usar "Limpiar", las alertas de Cerrar/Abrir-otro-save siguen apareciendo como si
hubiera ediciones pendientes, y "Limpiar" clickeado dos veces seguidas muestra el modal de
confirmación las dos veces en vez de "no había nada que descartar" la segunda. Análisis extenso
por lectura de código no encontró la causa (`ResetSession`, `HasAnyEdits`, `RecordEdit`/
`CapturePristine`, instancia única de `EditSessionService`, bindings XAML — todo revisado y
correcto en papel). Sospecha principal: build no limpio del lado del usuario (no confirmado). Si
persiste tras un `dotnet clean` + rebuild, retomar con diagnóstico real en vez de releer código.

---
## Stack técnico

| Componente | Versión |
|---|---|
| .NET | 9.0 |
| Avalonia UI | 11.3.8 |
| PKHeX.Core | 25.11.7 |
| SQLite (Microsoft.Data.Sqlite) | 9.0.5 |
| Target | linux-x64, self-contained, single file |

Sin repositorio git inicializado en el ZIP entregado. Sin dotnet SDK disponible en el entorno
de análisis de Claude tampoco (sin acceso de red a los dominios de Microsoft) — todo el
análisis de esta sesión sobre APIs de PKHeX.Core se hizo por **reflection cruda sobre el DLL
real** (`tests/Exxeguttor.Tests/bin/Debug/net9.0/PKHeX.Core.dll`, cuando estaba presente en el
ZIP subido) usando la librería Python `dnfile`, sin necesitar el runtime de .NET. El ciclo de
verificación real sigue siendo: Claude escribe → usuario compila localmente → pega el error/
output completo → Claude corrige. Para dudas de **comportamiento** (no solo firmas), reflection
no alcanza — hace falta un test real (`[Fact]` con `Assert.Fail` volcando resultados, o
assertions) que el usuario corra y comparta la salida.

---

## Estructura del repositorio

```
exxeguttor/
├── src/
│   ├── Exxeguttor.App/                  # Lógica de negocio (sin Avalonia)
│   │   ├── Capabilities/
│   │   │   ├── SaveCapability.cs        # Enum de capacidades por gen
│   │   │   └── SaveCapabilities.cs      # Detección automática — incluye Alpha (Legends
│   │   │                                  Z-A vía GameVersion.ZA) y el fix de GameVersion
│   │   │                                  genérico vs específico (Gen6, Gen9)
│   │   └── Services/
│   │       ├── LegalityMessageMapper.cs # Traducción CheckIdentifier→categoría/mensaje ES
│   │       ├── PokemonDatabase.cs       # Acceso SQLite + DTOs
│   │       ├── PokemonService.cs        # Lectura de party/box/legalidad (NO escritura)
│   │       ├── SaveFileService.cs       # Abrir/guardar saves — backup y nombre sugerido
│   │       │                              ahora usan la convención real de PKHeX.Core
│   │       ├── TrainerService.cs        # Lectura Y ESCRITURA de entrenador (ApplyEdits nuevo)
│   │       └── ItemInventoryService.cs  # NUEVO — lectura de mochila/inventario del save
│   └── Exxeguttor.UI/                   # UI Avalonia
│       ├── ViewModels/
│       │   ├── MainWindowViewModel.cs   # Orquestador — ahora con CurrentMode (Pokémon/
│       │   │                              Pokédex/Mochila) y wiring de EditApplyService
│       │   ├── PokemonEditorViewModel.cs # Editor de Pokémon — UsesLegacyIVs (Gen1/2),
│       │   │                              EvContribution() con fórmula sqrt para Stat Exp
│       │   ├── TrainerViewModel.cs      # Editable: Nombre/TID/SID/Género/Dinero/Monedas/BP
│       │   ├── MoveSelectorViewModel.cs
│       │   ├── RecommendedSetGroup.cs
│       │   ├── BoxViewModel.cs
│       │   ├── PartyViewModel.cs
│       │   ├── PokemonSlotViewModel.cs
│       │   ├── PokemonSlotKey.cs        # Clave de slot — ForBox/ForParty/ForTrainer/ForBag
│       │   ├── LearnsetGroup.cs
│       │   ├── TypeEffectivenessEntry.cs
│       │   ├── SpeciesPickerViewModel.cs / SpeciesPickerItemViewModel.cs
│       │   ├── RibbonItemViewModel.cs / RibbonGroupViewModel.cs / RibbonChipViewModel.cs
│       │   ├── TypeChipViewModel.cs
│       │   ├── BagViewModel.cs          # NUEVO — orquestador de Mochila
│       │   ├── BagItemRowViewModel.cs   # NUEVO — fila de ítem (checkbox/stepper/max)
│       │   └── BagPouchTileViewModel.cs # NUEVO — modelo de categoría
│       ├── Views/
│       │   ├── MainWindow.axaml(.cs)    # Selector de modo + panel central/derecho según modo
│       │   ├── PokemonEditorView.axaml(.cs)
│       │   ├── PokemonInfoView.axaml(.cs)
│       │   ├── PokemonStatsView.axaml(.cs) # EffectiveMax() ahora clampea Iv*/Ev* según
│       │   │                                  UsesLegacyIVs, no solo Iv* como antes
│       │   ├── BoxView.axaml(.cs)
│       │   ├── PartyView.axaml(.cs)
│       │   ├── TrainerView.axaml(.cs)
│       │   ├── PokemonSlotView.axaml(.cs)
│       │   ├── SpeciesPickerView.axaml(.cs)
│       │   ├── BagPouchGridView.axaml(.cs) # NUEVO — panel central Mochila, grilla de tiles
│       │   │                                tipo Caja (origen Mochila/PC navegable arriba)
│       │   ├── BagPouchTileView.axaml(.cs) # NUEVO — tile individual de categoría (204x108)
│       │   └── BagItemListView.axaml(.cs)  # NUEVO — panel derecho Mochila, lista de ítems
│       ├── Services/
│       │   ├── SpeciesDatabase.cs
│       │   ├── MoveDatabase.cs
│       │   ├── AbilityDatabase.cs
│       │   ├── ItemDatabase.cs
│       │   ├── NatureDatabase.cs
│       │   ├── MegaStoneDatabase.cs
│       │   ├── ZCrystalDatabase.cs
│       │   ├── RibbonDatabase.cs
│       │   ├── RibbonReader.cs
│       │   ├── RibbonWriter.cs          # NUEVO — simétrico a RibbonReader, escritura de cintas
│       │   ├── BagPouchDatabase.cs      # NUEVO — InventoryType → (nombre ES, ícono)
│       │   ├── TypeEffectivenessDatabase.cs
│       │   ├── MovesetDatabase.cs
│       │   ├── SpriteService.cs
│       │   ├── EditSessionService.cs    # Fuente de "qué cambió" — guards contra colisión de
│       │   │                              nombre Gender Pokémon/Trainer, ResetSession() nuevo
│       │   │                              (limpia las 5 estructuras al abrir/cerrar/limpiar
│       │   │                              un save), BagItemEditValue (nombre+cantidad
│       │   │                              capturado al momento de editar, ya no se
│       │   │                              reconstruye por ID en el modal de revisión)
│       │   ├── EditApplyService.cs      # NUEVO — el pipeline de escritura real
│       │   ├── BusyStateService.cs
│       │   └── FileDialogService.cs
│       ├── Converters/                  # (sin cambios esta sesión)
│       └── i18n/
├── lang/
├── tests/
│   └── Exxeguttor.Tests/
│       ├── SaveCapabilitiesTests.cs
│       ├── CreationApiDiagnosticTests.cs
│       ├── EntityBlankDiagnosticTests.cs
│       ├── LearnsetDiagnosticTests.cs
│       ├── InventoryApiDiagnosticTests.cs      # NUEVO — pouches/MaxCount por gen
│       ├── WritePipelineRoundTripTests.cs      # NUEVO — assertions reales del pipeline
│       ├── BagItemCategoryDiagnosticTests.cs   # NUEVO — investigación CanContain por ítem
│       ├── ItemStorageDiagnosticTests.cs       # NUEVO — descartó IsLegal como alternativa
│       └── MaxItemIdDiagnosticTests.cs         # NUEVO — MaxItemID real por generación
├── scripts/
│   ├── download-sprites.py
│   └── fetch-species-extra.py
├── pokemon-database/
│   ├── database/
│   │   └── pokemon.db                   # ItemGameCodes.RawItemId es la fuente real de
│   │                                       categorización de Mochila — ver sección Mochila
│   ├── resources/
│   ├── docs/
│   ├── ROADMAP.md, CHANGELOG.md, DATA_SOURCES.md, CONTRIBUTING.md
├── packaging/
└── .github/workflows/
```

---

## Base de datos SQLite (pokemon.db)

### Tablas principales
- **Species**, **SpeciesTypes**, **SpeciesAbilities**, **Moves**, **Abilities**,
  **TypeEffectiveness**, **Learnsets** — sin cambios esta sesión.
- **Items** — columnas confirmadas: `ItemId` (PK, coincide 1:1 con el índice de PKHeX.Core
  salvo para MTs/MOs, ver sección Mochila), `Name`, `Description`, `Category` (46-48 valores de
  PokeAPI, categorización por efecto/uso — NO es la agrupación por bolsillo de mochila), `Cost`,
  `FlingPower`, `FlingEffect`.
- **ItemGameCodes** (nueva, del hotfix `fix_database`) — `ItemId`, `GameId`, `RawItemId`
  (índice real de PKHeX.Core para ese juego — ver sección Mochila, la pieza que faltaba),
  `PouchCategory` (real, fiel al motor), `UserPouchCategory` (la tile de UI a mostrar — igual a
  `PouchCategory` en Gen4-9, subclasificada a mano en Gen1-3+Colosseum/XD).

**Nota**: naturalezas y categorías/nombres de cintas siguen sin estar en la DB — tablas
estáticas en `NatureDatabase.cs`/`RibbonDatabase.cs`. Mismo criterio ahora para
`BagPouchDatabase.cs` (16 valores de `InventoryType`, dominio fijo del motor).

### Resolución de ruta de la DB
Sin cambios: `/usr/share/exxeguttor/pokemon.db` → `{AppContext.BaseDirectory}/pokemon.db` →
`./pokemon-database/database/pokemon.db` → hasta 10 niveles arriba.

---

## Estado actual de la UI

### Selector de modo general (nuevo)
`MainWindowViewModel.CurrentMode` (`AppMode` enum: `Pokemon`/`Pokedex`/`Mochila`) controla qué
se muestra en el panel central y derecho — el panel Entrenador (columna izquierda) queda
**igual en cualquier modo**. Pokédex sigue deshabilitado como placeholder. Al abrir un save
nuevo, el modo vuelve siempre a Pokémon. Al cambiar a modo Mochila se llama `Bag.Initialize()`
de nuevo (recarga defensiva).

### Panel principal — modo Pokémon (sin cambios de fondo)
Izquierda: TrainerView + PartyView. Centro: BoxView + PokemonInfoView. Derecha:
PokemonStatsView (tabs). Selección de Pokémon dispara `LoadPokemon`.

### Panel principal — modo Mochila
- **Centro** (`BagPouchGridView`): nav de origen arriba (`◀ Mochila/PC ▶`, equivalente a
  Caja 1/Caja 2 — solo visible si el save tiene un segundo origen real, o sea Gen1-3) + grilla
  de tiles de categoría abajo (mismo lenguaje visual que la grilla de Cajas de Pokémon).
- **Derecha** (`BagItemListView`): buscador (acotado a la categoría actual), lista de **todos**
  los ítems legales de esa categoría (poseídos y no — para poder agregar, no solo editar
  cantidad), cada fila con checkbox, sprite, descripción, stepper `−/+` y botón MAX.
- Ver "Módulo Mochila" arriba para el detalle de categorización (`RawItemId`, ya no bloqueado).

### TrainerView (sin cambios esta sesión, ya editable de antes)
Nombre, TID/SID, Género, Dinero, Monedas, Battle Points — todo con el mismo mecanismo
pendiente-hasta-exportar de siempre, ahora efectivamente escrito al SaveFile real al confirmar
la exportación (ver GAP CRÍTICO arriba).

### PokemonInfoView — 3 columnas (sin cambios estructurales)

### PokemonStatsView — tabs
Orden sin cambios: **IVs/EVs → Moves → Learnsets → Sets → Ribbons → Special**.

#### Tab IVs/EVs — Gen1/2 con mecánica propia (nuevo esta sesión)
- **IVs en Gen1/2 son DVs (0-15, no 0-31)** — `PokemonEditorViewModel.UsesLegacyIVs` (true si
  `Capabilities.Generation is 1 or 2`) topea los steppers de `Iv*` a 15 en vez de 31. El
  stepper de PS se **deshabilita y atenúa** (`BoolToOpacityConverter`) para estas generaciones,
  con tooltip explicando que el DV de PS se deriva de Atq/Def/Vel/Especial, no es un valor
  propio (confirmado con round-trip test: asignarlo directo se ignora silenciosamente).
- **EVs en Gen1/2 son Stat Experience (0-65.535, no 0-252)** — mismo `UsesLegacyIVs` sube el
  tope de los steppers de `Ev*` a 65.535. La fórmula de cálculo de stats usa
  `EvContribution()`: `floor(sqrt(StatExp)/4)` en vez de `floor(EV/4)` para estas dos
  generaciones (en el techo de cada escala ambas fórmulas coinciden: `floor(sqrt(65535)/4) ==
  floor(252/4) == 63`, por eso Gen3+ pudo simplificar el sistema sin cambiar el rango efectivo
  de stats).
- El botón "Max" del stepper usa el mismo `EffectiveMax()` (`PokemonStatsView.axaml.cs`), así
  que ya sale bien diferenciado por generación sin código aparte.
- **Asunción sin confirmar**: que Stat Experience funciona idéntico en Gen1 y Gen2 (mismo
  rango, misma fórmula) — reusan el mismo flag `UsesLegacyIVs` sin distinguirse entre sí. Si en
  algún momento se confirma que difieren, hay que separar el flag en dos.
- Resto del tab sin cambios (barras segmentadas, radar, `GetNatureMultiplier` lee
  `_selectedNature`).

#### Tab Moves, Learnsets, Sets, Special — sin cambios estructurales esta sesión
(Ver sesiones anteriores para el detalle completo — Mega/Z-Move derivados de HeldItem/Moves sin
campo propio, Dynamax/Alpha/Tera con campos reales, exclusión de Mega Stones/Z-Crystals del
combo de Held Item del tab Info.)

#### Tab Ribbons — ahora escribe al PKM real (antes solo quedaba pendiente)
Mismo flujo de carga/edición de siempre (`RibbonReader`, prefijo `"Ribbon:"` en
`EditSessionService`), pero ahora al exportar con `IsIncluded=true`, `RibbonWriter` aplica el
cambio de verdad al PKM (ver GAP CRÍTICO arriba). Antes de esta sesión, las cintas quedaban
pendientes para siempre — nunca se aplicaban ni con la exportación confirmada.

### Modal de revisión / exportación
- Tres tipos de tarjeta: Pokémon (con legalidad previsualizada), Entrenador, Mochila (una por
  pouch tocado). **Las tres con checkbox `IsIncluded` real** — antes solo la de Pokémon tenía
  el checkbox, y era decorativo en las tres.
- `ConfirmExportCommand` ahora llama `EditApplyService.ApplyIncluded(...)` antes de
  `PerformExportAsync()` — el SaveFile que se termina escribiendo a disco ya refleja las
  ediciones tildadas.
- `CancelReviewCommand` sin cambios — cierra sin borrar nada.

### Libreta (checkpoint visual)
Sin cambios de mecanismo. `GetSimpleSummary()` ahora también distingue correctamente al
Entrenador (antes de este fix, tocar el género del entrenador podía mostrarse mal etiquetado
como "Pokémon: Género" — ver Trampas conocidas #23).

---

## Flujo de datos (actualizado con el pipeline de escritura real)

```
Usuario abre save
  → SaveFileService.OpenAsync(path)
  → SaveCapabilities(save)           # incluye Alpha para Legends Z-A, Terastal robusto a
  │                                     GameVersion genérico vs específico
  → TrainerService.GetTrainerInfo()
  → TrainerViewModel.LoadFrom(info)
  → BoxViewModel.Initialize(boxCount)
  → PartyViewModel.Load()
  → Bag.Initialize()                 # pouches de Mochila disponibles ni bien se abre el save
  → CurrentMode = AppMode.Pokemon    # un save nuevo siempre arranca en modo Pokémon

Usuario hace click en slot (modo Pokémon)
  → PokemonEditorViewModel.LoadPokemon(pkm, capabilities, slotKey)
      → (sin cambios de flujo — ver sesiones anteriores para el detalle completo)

Usuario navega Mochila (modo Mochila)
  → BagViewModel.PreviousPouch/NextPouch/SwitchToBag/SwitchToPc
  → LoadItemsForSelectedPouch() — CapturePristine + reaplica ediciones pendientes de la sesión
    (mismo patrón que RestorePendingRibbonEdits)

Usuario edita un campo en la UI (Pokémon, Entrenador o Mochila)
  → Set<T>/RecordEdit → EditSessionService.CapturePristine (primera vez) + RecordEdit
  → ⚠️ solo actualiza la propiedad del ViewModel y el diff en EditSessionService —
     NO se escribe en _currentPkm ni en el SaveFile TODAVÍA

Usuario exporta
  → ExportFileAsync → EditSessionService.BuildSummary()/BuildTrainerSummary()/BuildBagSummaries()
      (clon + campos seguros + LegalityAnalysis solo para Pokémon; Entrenador/Mochila sin legalidad)
  → si hay algo pendiente: modal de revisión (IsIncluded real en las 3 tarjetas) → ConfirmExportCommand
  → EditApplyService.ApplyIncluded(ReviewSummary, TrainerSummary, BagReviewSummary)
      # ★ ACÁ SE APLICAN DE VERDAD LAS EDICIONES TILDADAS AL SaveFile REAL ★
      # Pokémon+Cintas: releer PKM real, aplicar campos, RefreshChecksum, SetBoxSlotAtIndex
      # Entrenador: TrainerService.ApplyEdits directo sobre SaveFile
      # Mochila: reconstruir pouch (array de tamaño fijo), reasignar save.Inventory
  → PerformExportAsync() → SaveFileService.SaveAsAsync()
      # save.Metadata.GetSuggestedExtension() para el nombre sugerido
      # save.Metadata.GetBackupFileName(directorio) para el backup
      # escribe el SaveFile YA MUTADO — refleja las ediciones aplicadas arriba
  → EditSessionService.ClearAll()
```

---

## Mapeo GameVersion → GameId de la DB

Sin cambios en los pares base — agregado el mismo fix que en `SaveCapabilities.Detect()`:

```csharp
// En PokemonEditorViewModel.MapVersionToGameId()
// (todos los pares de sesiones anteriores sin cambios)
...
// Gen 9 — Scarlet/Violet → scarletviolet (18). Se agrega también GameVersion.Gen9 genérico
// (mismo motivo que XY/ORAS — SaveFile.Version puede devolver el agregado según el caso).
GameVersion.SL or GameVersion.VL or GameVersion.SV or GameVersion.Gen9 => 18,
```

---

## Sets competitivos (MovesetDatabase) — sin cambios esta sesión

## Legalidad (LegalityMessageMapper) — sin cambios de fondo esta sesión
`EditApplyService` reusa el mismo mapeo campo→PKM que `EditSessionService.AnalyzeLegality` ya
tenía para el preview, extendido a los campos que el preview no cubre (ver GAP CRÍTICO arriba)
— no hay una copia nueva de esta lógica, es la misma fuente.

## i18n — sin cambios esta sesión

---

## Testing

- `SaveCapabilitiesTests.cs`, `CreationApiDiagnosticTests.cs`, `EntityBlankDiagnosticTests.cs`,
  `LearnsetDiagnosticTests.cs` — de sesiones anteriores, sin cambios.
- **`WritePipelineRoundTripTests.cs`** (nuevo) — mutación en memoria contra la misma instancia
  de `SaveFile` (no round-trip binario completo, ver Trampas conocidas #20 para por qué).
  Assertions reales (`Assert.Equal`), no solo diagnóstico. Cubre Pokémon (5 gens), Entrenador,
  Mochila, Cintas (viejo y moderno). Dos tests informativos aparte (`Assert.Fail` deliberado):
  si `Write()` explota por generación desde un save sintético, y convenciones de nombre de
  archivo/backup.
- **`InventoryApiDiagnosticTests.cs`** (nuevo) — pouches/MaxCount/Items.Length reales por
  generación, confirmó la estructura completa de `SaveFile.Inventory`.
- **`BagItemCategoryDiagnosticTests.cs`** (nuevo) — investigación del bug de categorización,
  confirmó que Gen3 está bien y Gen1/2 no, con datos concretos ítem-por-ítem.
- **`ItemStorageDiagnosticTests.cs`** (nuevo) — descartó `IItemStorage.IsLegal` como
  alternativa a `CanContain` (siempre `true`).
- **`MaxItemIdDiagnosticTests.cs`** (nuevo) — pendiente de correr, iba a dar `MaxItemID` real
  por generación pero quedó superado por el hallazgo del bug de TMs en la DB (bloqueante
  distinto, ver sección Mochila).
- **Gap de testing que sigue abierto**: Habilidad/HeldItem/Shiny/Dynamax/Alpha/Noble y creación
  de Pokémon nuevo compilan y están cableados al pipeline de escritura, pero sin test de
  round-trip dedicado todavía — prioridad para la próxima sesión de testing.

---

## Pokédex (tab planeado, no implementado) — sin cambios esta sesión

## Empaquetado y distribución — sin cambios esta sesión

---

## Trampas conocidas / Lecciones aprendidas

_(1-19: ver sesiones anteriores — tipos Gen1/2 vs Gen3+, Silver vs Scarlet, MetTimeOfDay solo
PK2, ClearFields obligatorio, slots de relleno BoxViewModel, Hidden Power Gen2-7, SpriteService
y guiones, LearnsetGroups no observable, MovesetDatabase lazy-load, compiled bindings, gap de
escritura histórico — YA RESUELTO, ver GAP CRÍTICO arriba, este ítem queda obsoleto pero no se
renumera para no romper referencias de sesiones viejas —, radar de stats, naturalezas no vienen
de SQLite, HeldItem no sincronizado entre combos, nombres de ítems de pickers Mega/Z-Move desde
DB propia, Money/Coin/BP uint + Coin singular, patrón de valor prístino, cintas vía RibbonReader
sin interfaz única, IsIncluded — YA NO decorativo, ver GAP CRÍTICO, este ítem también queda
obsoleto en su redacción original.)_

20. **⚠️ `BlankSaveFile.Get` NO deja el save listo para un `Write()` completo desde cero en
    todas las generaciones.** Confirmado que SAV3 y SAV4 tiran `ArgumentOutOfRangeException`
    (`BlockInfo4.GetRevision`/`SAV3.WriteSectors`) al intentar escribir un save recién
    sintetizado, sin haber tocado ni un solo campo — el error ocurre incluso en el test más
    simple posible (solo tocar campos de entrenador, sin ningún PKM). **Confirmado con un save
    Gen3 REAL** (abrir sin editar + Exportar, en la app tal cual estaba antes de esta sesión)
    que esto **no** pasa en producción — es puramente un artefacto de sintetizar un save desde
    cero, no algo que afecte al pipeline de escritura real (que siempre parte de un save YA
    ABIERTO desde un archivo real, nunca de `BlankSaveFile.Get`). Por este motivo,
    `WritePipelineRoundTripTests` prueba mutación **en memoria** contra la misma instancia
    (`SetBoxSlotAtIndex` → `GetBoxSlotAtIndex` sin pasar por `Write()`/releer) en vez de un
    ciclo binario completo — es exactamente lo que hace el pipeline real de todos modos (mutar
    en memoria, escribir a disco una sola vez, nunca re-parsear los propios bytes recién
    escritos).

21. **`SaveFile.SetChecksums()` existe pero es `protected`** — no se puede llamar desde otro
    proyecto/ensamblado. `Write()` debería recalcular todo internamente vía `GetFinalData()`
    (que sí invoca la versión protegida puertas adentro). No intentar llamar `SetChecksums()`
    directo esperando que compile — ya costó una vuelta completa de error de compilación esta
    sesión antes de descubrirse.

22. **`GameVersion` tiene valores agregados/genéricos ADEMÁS de los específicos, y
    `SaveFile.Version` puede devolver cualquiera de los dos según el caso** — ya hay un
    comentario en el propio código (`SaveCapabilities.Detect()`) que documentaba haber
    encontrado este problema en una "sesión de diagnóstico Gen9", pero el fix en su momento
    solo se había aplicado al caso de Gen6 (X/Y/XY), dejando Gen9 con el mismo bug sin corregir
    hasta esta sesión (el tab Special no aparecía para ningún save de Gen9 con ese caso). **Dos
    bugs reales en producción por el mismo motivo, confirmado.** Regla: siempre agregar el
    valor genérico (`GameVersion.Gen6`, `GameVersion.Gen9`, etc.) junto a los específicos en
    cualquier `switch` sobre `GameVersion` que decida capacidades — tanto en
    `SaveCapabilities.Detect()` como en `PokemonEditorViewModel.MapVersionToGameId()` (mismo
    fix aplicado en los dos lugares esta sesión, aunque el segundo no tenía un bug reportado
    todavía).

23. **`"Gender"` es una clave de propiedad compartida entre Pokémon y Entrenador en
    `EditSessionService.CategoryMap`** — sin un guard explícito, editar el género del
    entrenador hacía que `BuildSummary()` (pensado solo para Pokémon) lo tratara como si fuera
    un Pokémon editado, disparando `fetchPristine(PokemonSlotKey.ForTrainer())` →
    `PokemonService.GetBox(-1)` → `ArgumentOutOfRangeException` real en producción (bug
    reportado y corregido esta sesión). `BuildSummary()` y `GetSimpleSummary()` ahora excluyen
    explícitamente las claves sentinel de Entrenador (`key == PokemonSlotKey.ForTrainer()`) y
    Mochila (`key.IsBag`) al principio de su loop sobre `_pendingEdits`, antes de llegar a
    cualquier lógica que asuma "esto es un Pokémon". Si se agrega una clave de propiedad nueva
    a cualquiera de los `CategoryMap` (Pokémon o Entrenador), revisar que no colisione con el
    otro mundo.

24. **Legends Z-A (`GameVersion.ZA`) usa `PA9`, no `PK9`** — mismo patrón que Legends Arceus
    (`PA8` ≠ `PK8`) pese a ser "misma generación" que Escarlata/Púrpura en el sentido de
    generación Pokédex. `SAV9ZA` es la clase de save correspondiente. `PA9.IsAlpha` existe
    (mismo mecanismo que `PA8`), pero **`PA9` NO tiene `IsNoble`** — no asumir simetría
    completa entre formatos "hermanos" (mismo prefijo de letra, distinta generación) sin
    confirmar cada propiedad. `SaveCapabilities.Detect()` suma `SaveCapability.Alpha` para
    `GameVersion.ZA` pero no `NobleLevel`. Sin este case, el tab Special no aparecía para
    ningún save de Legends Z-A (bug real reportado y corregido esta sesión, encontrado al
    mismo tiempo que el fix de Gen9/Terastal pero es una causa distinta — dos bugs separados
    con el mismo síntoma superficial).

25. **IVs/EVs en Gen1/2 no son "0-31 / 0-252" genérico — son DVs (0-15) y Stat Experience
    (0-65.535) respectivamente, con fórmula de stats distinta.** Bug real de UI corregido esta
    sesión (antes se permitía editar IVs hasta 31 y EVs hasta 252 en cualquier generación,
    incluida Gen1/2). El DV de PS específicamente **no es un valor propio** — PKHeX.Core lo
    deriva del bit menos significativo de Atq/Def/Vel/Especial (confirmado con round-trip
    test: asignar `IV_HP` directo en un PKM de Gen1 se ignora silenciosamente). Ver sección
    "Tab IVs/EVs" arriba para el detalle completo de la fórmula y qué se asumió sin confirmar
    (que Gen1 y Gen2 comparten exactamente el mismo comportamiento).

26. **`InventoryPouch.CanContain` no es confiable como filtro de categoría en los formatos
    "genéricos" de PKHeX.Core (Gen1/2/4/5/6, clase base `InventoryPouch` sin subclase propia)
    — SÍ es confiable en Gen3/7/8/9 (subclases dedicadas `InventoryPouch3`/`7`/`8`/`9`).** No
    es solo impreciso: devuelve resultados que ni siquiera respetan qué ítems existen en esa
    generación (confirmado con datos reales). `IItemStorage.IsLegal` (investigado como
    alternativa) resultó peor: siempre `true`. **Ya no se usa ninguno de los dos en el módulo
    Mochila** — la categorización sale entera de `pokemon.db.ItemGameCodes` (ver sección
    Mochila arriba para el detalle completo, incluida la causa real y por qué ya no hace falta
    la columna `CategoryUpper` que se había diseñado antes).

27. **`InventoryPouch.Items` es un array de tamaño FIJO por pouch, nunca se agranda ni se
    achica** — confirmado con round-trip test real (`InventoryPouch.SetPouch` tira
    `ArgumentOutOfRangeException` si el largo cambia). Un slot "vacío" tiene `Count==0`, no se
    elimina del array. Cualquier código que escriba en la mochila tiene que buscar el slot
    existente del ítem o el primer slot libre (`Count==0`) y mutarlo in-place — nunca construir
    un array de largo distinto y asignarlo.
