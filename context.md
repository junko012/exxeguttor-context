# context.md — Estado actual del proyecto Exxeguttor

_Última actualización: sesión muy larga y densa, la más grande documentada hasta ahora (~50
commits sobre `master`, mensajes de commit genéricos tipo "updating files" — no sirven como
changelog, por eso esta reescritura salió de leer el código real, no del historial de git).
Dos módulos nuevos completos — **Pokédex** (álbum de figuritas, revierte la decisión de scope-
out documentada en la versión anterior de este archivo) y **Diagnosticador de legalidad**
(tab "Diagnóstico" con arreglos automáticos accionables) — más una extensión grande de
`PokemonService` (el "intercambio entre versiones hermanas" para construir especies exclusivas
ahora cubre Gen3, no solo Gen1/2, con el caso especial de Feebas→Milotic por Belleza) y un lote
de campos que quedaban "editables en la UI pero se perdían en silencio al exportar" (Shiny,
Huevo, Amistad, Género del Pokémon, OT, TID propio, fechas) ahora sí cableados al pipeline de
escritura real. `pokemon.db` creció de ~46 MB a ~51 MB (datos de Pokédex). Repo git ya
inicializado del lado del usuario — 50 commits en `master`, sin ninguna rama aparte._

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
sin confirmar con datos reales): Habilidad, HeldItem, Dynamax/Gigantamax, Alpha/Noble, creación
de Pokémon nuevo. Prioridad para una sesión futura antes de dar el pipeline por 100% cerrado.

### ⚠️→✅ Bug real corregido esta sesión — "campos huérfanos" que se perdían en silencio al exportar

Varios campos editables desde hacía tiempo en el panel principal (**Brillante, Huevo, Amistad,
Género del Pokémon, OT (nombre del entrenador original), TID propio del Pokémon, Fecha de
encuentro, Fecha/Ubicación de huevo**) sí pasaban por `Set<T>`/`RecordEdit` — aparecían bien en
la libreta y en el modal de revisión — pero `EditApplyService.ApplyFieldsToPkm` nunca tenía un
`case` para ellos: la edición se perdía en silencio al exportar, sin ningún error. Mismo síntoma
que tuvo Met Level/Ball/Ubicación en una sesión anterior. Todos quedaron agregados esta sesión:

- La mayoría son setters directos y abstractos en `PKM` (`Gender`, `CurrentFriendship`, `IsEgg`,
  `TID16`, `OriginalTrainerName` — confirmado en el código real de PKHeX.Core, no asumido).
  `MetDate`/`EggMetDate` son `DateOnly?` con setter propio.
- **`IsShiny` es la excepción** — `virtual bool IsShiny => TSV == PSV`, get-only, **sin
  setter**. Tildar/destildar Brillante desde la UI reusa el mismo sorteo de PID que ya usaba el
  botón "Corregir automáticamente" del tab Diagnóstico (`PokemonService.TryRegeneratePid`), pero
  apuntando al estado que el usuario pidió, no al que el PKM ya tenía. Si el sorteo no encuentra
  combinación válida en el tope de intentos (caso raro — ej. Brillante + Naturaleza puntual en
  Gen3-5), se ignora en silencio.
- `IsNicknamed` se separó de la edición de `Nickname` — antes se forzaba a `true` sin condición
  ni forma de destildarlo desde la UI (causa real de "apodo ilegal con texto normal": el flag no
  coincidía con el contenido). Ahora tiene su propio checkbox (`IsNicknamedFlag`).

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
**Sigue sin tocarse esta sesión** — nada en el diff de `EditSessionService.cs` toca
`HasAnyEdits`/`ResetSession`, así que sigue exactamente en el mismo estado.

---

## 🩺 Diagnosticador de legalidad — módulo nuevo esta sesión (tab "Diagnóstico")

Reemplaza la idea original de un simple resumen de legalidad por un tab dedicado que, por cada
problema detectado, muestra categoría + explicación + (cuando hay un valor concreto que
sugerir) un botón **"Corregir automáticamente"**. Diseñado desde el arranque para poder crecer
a v2 (aplicar arreglos con un click) sin rediseñar nada — v1 (esta sesión) solo lista y resalta.

### Arquitectura — `DiagnosticStep` + `FieldFix` (Exxeguttor.App)

- **`DiagnosticStep`** — un paso por categoría con problema (misma agrupación de siempre que ya
  arma `LegalityMessageMapper`), con `Order` (prioridad de resolución sugerida: Origen del
  encuentro → Especie/Forma/Habilidad/Género → PID/Naturaleza/IVs/Brillante →
  Nivel/EVs/Movimientos → Apodo/Idioma/Entrenador/Ball/Objeto/Cintas/Marcas/Recuerdos),
  `Severity` (solo `Invalid` o `Fishy` — nunca `Valid`, un step solo existe para un problema),
  `Summary`/`TechnicalDetail` (el texto amigable y el `CheckResult.ToString()` crudo de
  siempre) y `Fixes` (0 a N `FieldFix` — vacío cuando el problema es "Nivel C": puramente
  descriptivo, sin un valor correcto conocible, ej. "existen varios movimientos ilegales
  posibles, no un único reemplazo").
- **`LegalityDiagnosticBuilder.BuildDiagnosticSteps(analysis, pkm)`** — punto de entrada único,
  junta cuatro fuentes distintas de `FieldFix` por categoría (nunca un diff genérico):
  - **`LegalityArgumentFormatter`** ("Nivel A") — un `FieldFix` por `CheckResult` individual
    cuando `CheckResult.Value`/`.Argument`/`.Argument2` traen un valor accionable. **Ojo**:
    `CheckResult` es un struct con `[StructLayout(LayoutKind.Explicit)]` — `Value` y
    `Argument`/`Argument2` comparten la MISMA memoria (una unión, no tres campos
    independientes). Para códigos de un solo argumento, `Value` y `Argument` dan el mismo
    número; para códigos de dos argumentos empaquetados (sufijo `_01`), hay que leer
    `Argument`/`Argument2` por separado — leer `Value` ahí da un número empaquetado sin
    sentido. Confirmado leyendo `CheckResult.cs`/`Verifier.GetInvalid` de PKHeX.Core 25.11.7.
  - **`LegalityEncounterFormatter`** ("Nivel B") — cuando el `CheckResult` no trae el valor
    (ej. `IVNotCorrect`, sin argumento) pero `LegalityAnalysis.EncounterMatch` sí lo sabe (es la
    plantilla de encuentro real contra la que PKHeX comparó). Cubre ubicación (`ILocation`) e
    IVs fijas de un regalo/estático (`IFixedIVSet`).
  - **`LegalityMoveFormatter`** — sistema TOTALMENTE APARTE: los movimientos no generan
    `CheckResult` propio para "este movimiento no es legal" (solo para PP) — hay que leer
    `LegalityAnalysis.Info.Moves`/`.Relearn` (arrays de `MoveResult`, 1 por slot 1-4) en vez de
    `.Results`. Ventaja real: el índice del array da el slot exacto sin ambigüedad, y
    `MoveResult.Expect` a veces ya trae el ID del movimiento sugerido — la sugerencia más
    precisa de todo el diagnosticador.
  - **`LegalityEvFormatter`** — los dos códigos de suma de EVs (`EffortAbove510` y el asociado)
    no traen NINGÚN argumento en el `CheckResult` (confirmado en `EffortValueVerifier.cs`: el
    `AddLine` correspondiente no pasa valor) — se calcula a mano leyendo `pkm.EVs` directo. Única
    fuente de `FieldFix` del diagnosticador que no depende de ningún dato que exponga PKHeX
    (`FieldFixSource.DerivedFromPkm`). **Ojo con el orden de `pkm.GetEVs()`/`GetIVs()`**: no es
    el estándar HP/Atk/Def/SpA/SpD/Spe — usan la misma convención "Speed en el índice 3" que
    `IndividualValueSet` (confirmado leyendo `PKM.cs` línea por línea, no asumido).

### Botones "Corregir automáticamente" — `FieldFixAction` (v1: 3 acciones)

`PokemonEditorViewModel.ApplyAutoFix(FieldFix fix)` despacha por `FieldFixAction`:

- **`RegeneratePid`** — `PokemonService.TryRegeneratePid(pkm, generation, out newPid)`, sortea
  un PID nuevo que resuelva Naturaleza/Género/Habilidad/Brillante según corresponda a la
  generación. Si no encuentra combinación en el tope de intentos (raro), devuelve `false` y no
  se aplica nada — sin aviso, mismo criterio que el resto del sorteo de PID en el proyecto.
  Reusado también por el checkbox de Brillante en el editor normal (ver sección "campos
  huérfanos" arriba).
- **`RegeneratePidMethod1`** — variante para el bug de "Método 1" de generación de PID en
  Gen3/4 (RNG antiguo). A diferencia de `RegeneratePid`, puede necesitar avisar que también
  cambió la Naturaleza asociada (`changedNAG`) — todavía **sin canal de aviso real para esto en
  la UI**, queda como gap abierto.
- **`RecalculateCatchRate`** — solo PK1. `PokemonService.TryRecalculateCatchRate(pkm, out
  newCatchRate)`. Devuelve `false` si el PKM no es un `PK1` (no debería llegar a ofrecerse el
  botón en ese caso desde la UI, pero el método es defensivo igual).

### UI — tab "Diagnóstico" (`PokemonStatsView.axaml`, después de "Special")

- `DiagnosticSteps` (`ObservableCollection<DiagnosticStep>`) — la lista completa (Invalid +
  Fishy), con un `Expander "Detalle técnico"` colapsado por paso para el texto crudo.
- `LegalityChips` — subset (solo `Invalid`, nunca `Fishy`) usado para las fichas rojas de la
  cabecera del editor — Fishy solo aparece en el tab, nunca como ficha, para no mandar la señal
  de "esto también hay que arreglar" cuando el Pokémon ya es legal así como está.
- **Recálculo en vivo mientras se edita**: `EditSessionService.BuildLiveDiagnosticSteps(key,
  edits, getCurrentPkm)` — cada edición pendiente dispara un recálculo independiente del que
  corre en el modal de exportación (`PokemonService.GetLegalityDiagnosticSteps`, corrido en
  `Task.Run` en paralelo con las otras dos tareas del preview de exportación vía
  `Task.WhenAll`), para no bloquear la UI del editor.
- Resaltado de campo (`FieldHighlightConverter`, nuevo converter) — usa `FieldFix.FieldId` para
  iluminar visualmente el control de la UI que corresponde a cada arreglo sugerido.

Ver `exxeguttor-context/docs/legality_module/legality_diagnosticador.md` para el spec de diseño
original (Etapas 3.1 a 3.3) si hace falta retomar la v2 (aplicar con un click, no solo v1).

---

## 📖 Módulo Pokédex — implementado esta sesión (revierte la decisión de scope-out anterior)

La versión anterior de este archivo documentaba a Pokédex como sacada deliberadamente del enum
`AppMode` ("decisión de alcance de `mockups/navigation_rail` — no implementar ni dejar
placeholder"). **Esa decisión se revirtió esta sesión, a pedido explícito del usuario** — es un
cambio de rumbo intencional, no una corrección de un error. El mockup de `navigation_rail`
queda sin actualizar todavía a propósito (ver `screen-pokedex-album.md`, a crear/retomar en
`exxeguttor-context/mockups/` si no existe aún).

- `AppMode` vuelve a tener 3 valores: `Pokemon`, `Bag`, `Pokedex`. A diferencia de Mochila,
  **Pokédex no usa panel derecho separado** — ocupa todo el ancho (`IsPokedexMode` en
  `MainWindowViewModel`, nuevo `SwitchToPokedexModeCommand`).
- **`PokedexService`** (Exxeguttor.App) — orquestador sin estado de UI ni dependencia de
  Avalonia. Combina `PokemonService` (qué hay en Caja/Equipo → posesión de cada especie),
  `PokemonDatabase` (género/hábitat/cadena evolutiva/flavor text — 4 métodos nuevos:
  `GetSpeciesOrigin`, `GetFlavorText`, `GetEvolutionInto`, `GetEvolutionsFrom`) y una lista
  embebida de disponibilidad restringida por juego.
- **Álbum de figuritas** — una tarjeta por especie BASE (sin formas, decisión de diseño ya
  tomada), con posesión real (`Owned`) según lo que haya en el save cargado.
- **Reverso de la tarjeta** (`PokedexOriginInfo`) — Género (con fallback a inglés si no hay
  traducción), Hábitat (`HabitatDatabase`, nuevo — tabla fija de 9 valores es/en, mismo criterio
  que `NatureDatabase`: set cerrado que no vive en SQLite), y flavor text del juego cargado
  (`null` si no hay dato — la UI muestra "sin datos de origen", sin distinguir por qué faltó).
- **Cadena evolutiva con condición en español** (`PokedexEvolutionFamily`: 1 previa + 0..N
  siguientes) — `EvolutionConditionFormatter` traduce el diccionario EAV crudo de
  `DbEvolutionEdge.Conditions` (valores en inglés de PokeAPI vía EvolutionConditions) a una
  línea corta en español. Best-effort: un `ConditionType` nuevo desconocido cae al fallback
  humanizado (guiones→espacios, capitalizado) en vez de romper. **Caveat de fidelidad heredado
  de la fuente**: Sylveon (Encanto + amistad) solo trae `min_happiness` en PokeAPI, sin
  `known_move` — el texto sale incompleto para ese caso puntual.
- **Disponibilidad restringida por juego** — `restricted_dex_availability.json` (nuevo asset
  embebido, ~1860 líneas) cubre Espada/Escudo, Escarlata/Púrpura, Legends Arceus y Legends Z-A
  (juegos que recortan qué especies tienen datos programados, a diferencia de Gen1-7+BDSP donde
  alcanza con `SaveFile.MaxSpeciesID`). Lazy-load + double-check lock (mismo patrón que
  `MovesetDatabase`) — no se parsea si el usuario nunca abre la Pokédex.
- **`GameVersionMappings`** (Exxeguttor.App, nuevo) — deliberadamente separado de los otros DOS
  `MapVersionToGameId` que ya existían (`PokemonService.cs`, `PokemonEditorViewModel.cs`).
  Auditar el enum real de PKHeX.Core 25.11.7 confirmó que `SaveFile.Version` puede devolver
  tanto valores "específicos" (`GameVersion.R`) como "agregados" (`GameVersion.RS`), y **cuando
  llega el agregado no hay forma de saber cuál de los dos juegos del par es** (Rubí/Zafiro
  tienen flavor text distinto entre sí) — `TryGetFlavorTextSlug` devuelve `null` en ese caso en
  vez de adivinar. Más conservador de lo estrictamente necesario (algunos agregados podrían
  resolverse leyendo otra propiedad del `SaveFile` real, sin auditar todavía por falta de
  acceso a `PKHeX.Core.dll` esta sesión).
- **Efecto de sonido** (`SoundService`, Exxeguttor.UI, nuevo) — sin dependencia de audio previa
  en el proyecto; para UN sonido cortito de UI (`spark_chime.wav`, al completar/atrapar una
  entrada) no se justifica sumar una librería completa. Extrae el `.wav` embebido a un archivo
  temporal cacheado en disco y lo reproduce vía `paplay` (PulseAudio/PipeWire) con `aplay`
  (ALSA) como respaldo — falla en silencio (try/catch) si ninguno está instalado, un sonido
  decorativo nunca debería poder romper la app.
- `pokemon.db` creció de ~46 MB a ~51 MB por los datos nuevos de género/hábitat/flavor
  text/cadenas evolutivas que alimentan este módulo.

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
│   │   ├── Assets/
│   │   │   └── restricted_dex_availability.json  # NUEVO — ~1860 líneas, disponibilidad
│   │   │                                            restringida SW/SH, SV, PLA, Legends Z-A
│   │   └── Services/
│   │       ├── LegalityMessageMapper.cs # Traducción CheckIdentifier→categoría/mensaje ES
│   │       ├── PokemonDatabase.cs       # Acceso SQLite + DTOs — +GetSpeciesOrigin/
│   │       │                              GetFlavorText/GetEvolutionInto/GetEvolutionsFrom
│   │       ├── PokemonService.cs        # Lectura de party/box/legalidad + construcción
│   │       │                              cross-versión Gen1/2/3, TryRegeneratePid(Method1),
│   │       │                              TryRecalculateCatchRate, TrySetShiny (NO escritura
│   │       │                              al SaveFile real — eso sigue siendo EditApplyService)
│   │       ├── SaveFileService.cs       # Abrir/guardar saves — backup y nombre sugerido
│   │       │                              ahora usan la convención real de PKHeX.Core
│   │       ├── TrainerService.cs        # Lectura Y ESCRITURA de entrenador (ApplyEdits nuevo)
│   │       ├── ItemInventoryService.cs  # lectura de mochila/inventario del save
│   │       ├── PokedexService.cs        # NUEVO — orquestador del álbum Pokédex
│   │       ├── GameVersionMappings.cs   # NUEVO — GameVersion→slug de flavor text (Pokédex)
│   │       ├── DiagnosticStep.cs        # NUEVO — modelo DiagnosticStep/FieldFix
│   │       ├── LegalityDiagnosticBuilder.cs   # NUEVO — punto de entrada del diagnosticador
│   │       ├── LegalityArgumentFormatter.cs   # NUEVO — Nivel A (CheckResult.Value/Argument)
│   │       ├── LegalityEncounterFormatter.cs  # NUEVO — Nivel B (EncounterMatch)
│   │       ├── LegalityMoveFormatter.cs       # NUEVO — Moves/Relearn (sistema aparte)
│   │       └── LegalityEvFormatter.cs         # NUEVO — suma de EVs, derivado del PKM
│   └── Exxeguttor.UI/                   # UI Avalonia
│       ├── ViewModels/
│       │   ├── MainWindowViewModel.cs   # Orquestador — CurrentMode (Pokémon/Mochila/
│       │   │                              Pokédex, reincorporada esta sesión) y wiring de
│       │   │                              EditApplyService/PokedexService
│       │   ├── PokemonEditorViewModel.cs # Editor de Pokémon — UsesLegacyIVs (Gen1/2),
│       │   │                              EvContribution() con fórmula sqrt para Stat Exp,
│       │   │                              DiagnosticSteps/LegalityChips + ApplyAutoFix()
│       │   │                              (tab Diagnóstico, NUEVO esta sesión)
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
│       │   ├── BagViewModel.cs          # orquestador de Mochila
│       │   ├── BagItemRowViewModel.cs   # fila de ítem (checkbox/stepper/max)
│       │   ├── BagPouchTileViewModel.cs # modelo de categoría
│       │   └── PokedexViewModel.cs      # NUEVO — álbum de figuritas, paginado/cacheado
│       ├── Views/
│       │   ├── MainWindow.axaml(.cs)    # Selector de modo + panel central/derecho según modo
│       │   ├── PokemonEditorView.axaml(.cs)
│       │   ├── PokemonInfoView.axaml(.cs)
│       │   ├── PokemonStatsView.axaml(.cs) # EffectiveMax() clampea Iv*/Ev* según
│       │   │                                  UsesLegacyIVs; tab "Diagnóstico" NUEVO al final
│       │   │                                  (después de Special) con lista de DiagnosticStep
│       │   │                                  + Expander de detalle técnico
│       │   ├── BoxView.axaml(.cs)
│       │   ├── PartyView.axaml(.cs)
│       │   ├── TrainerView.axaml(.cs)
│       │   ├── PokemonSlotView.axaml(.cs)
│       │   ├── SpeciesPickerView.axaml(.cs)
│       │   ├── BagPouchGridView.axaml(.cs) # panel central Mochila, grilla de tiles tipo
│       │   │                                Caja (origen Mochila/PC navegable arriba)
│       │   ├── BagPouchTileView.axaml(.cs) # tile individual de categoría (204x108)
│       │   ├── BagItemListView.axaml(.cs)  # panel derecho Mochila, lista de ítems
│       │   └── PokedexView.axaml(.cs)      # NUEVO — álbum, ocupa todo el ancho (sin
│       │                                     panel derecho separado, a diferencia de Bag)
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
│       │   ├── EditApplyService.cs      # el pipeline de escritura real — ahora también
│       │   │                              PID/CatchRate (auto-fix) y campos huérfanos
│       │   │                              (Shiny/Huevo/Amistad/Género/OT/TID/fechas)
│       │   ├── HabitatDatabase.cs       # NUEVO — 9 hábitats es/en (Pokédex, tabla fija)
│       │   ├── SoundService.cs          # NUEVO — spark_chime.wav vía paplay/aplay (Pokédex)
│       │   ├── BusyStateService.cs
│       │   └── FileDialogService.cs
│       ├── Converters/                  # +FieldHighlightConverter (tab Diagnóstico),
│       │                                  +BoolToFontWeightConverter, +SeverityColorConverters
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
│   │   └── pokemon.db                   # ~51 MB (era ~46 MB) — creció con datos de género/
│   │                                       hábitat/flavor text/cadena evolutiva para Pokédex.
│   │                                       ItemGameCodes.RawItemId sigue siendo la fuente
│   │                                       real de categorización de Mochila — ver esa sección
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

### Selector de modo general
`MainWindowViewModel.CurrentMode` (`AppMode` enum: `Pokemon`/`Bag`/`Pokedex`) controla qué se
muestra en el panel central y derecho — el panel Entrenador (columna izquierda) queda **igual
en cualquier modo**. **Pokédex reincorporada esta sesión** (ver sección "📖 Módulo Pokédex"
arriba — ya no es un placeholder deshabilitado). Al abrir un save nuevo, el modo vuelve siempre
a Pokémon y se llama `Pokedex.Reload(save)` (recarga defensiva, mismo criterio que
`Bag.Initialize()`).

### Panel principal — modo Pokémon (sin cambios de fondo)
Izquierda: TrainerView + PartyView. Centro: BoxView + PokemonInfoView. Derecha:
PokemonStatsView (tabs, incluido el tab "Diagnóstico" nuevo — ver esa sección arriba).
Selección de Pokémon dispara `LoadPokemon`.

### Panel principal — modo Mochila
- **Centro** (`BagPouchGridView`): nav de origen arriba (`◀ Mochila/PC ▶`, equivalente a
  Caja 1/Caja 2 — solo visible si el save tiene un segundo origen real, o sea Gen1-3) + grilla
  de tiles de categoría abajo (mismo lenguaje visual que la grilla de Cajas de Pokémon).
- **Derecha** (`BagItemListView`): buscador (acotado a la categoría actual), lista de **todos**
  los ítems legales de esa categoría (poseídos y no — para poder agregar, no solo editar
  cantidad), cada fila con checkbox, sprite, descripción, stepper `−/+` y botón MAX.
- Ver "Módulo Mochila" arriba para el detalle de categorización (`RawItemId`, ya no bloqueado).

### Panel principal — modo Pokédex (NUEVO esta sesión)
- **A diferencia de Bag, ocupa todo el ancho** — sin panel derecho separado.
- `PokedexView` — grilla de tarjetas del álbum (una por especie base), estado de posesión real
  según el save cargado. Al voltear una tarjeta: género/hábitat/flavor text del juego +
  familia evolutiva con condición en texto (ver "📖 Módulo Pokédex" arriba para el detalle
  completo de arquitectura, `GameVersionMappings`, y el efecto de sonido `SoundService`).

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
  → Pokedex.Reload(save)             # NUEVO — posesión real de cada especie para este save
  → CurrentMode = AppMode.Pokemon    # un save nuevo siempre arranca en modo Pokémon

Usuario hace click en slot (modo Pokémon)
  → PokemonEditorViewModel.LoadPokemon(pkm, capabilities, slotKey)
      → PokemonService.GetLegalityDiagnosticSteps(pkm) corre en paralelo (Task.WhenAll) con
        el resto del análisis de legalidad de siempre — llena DiagnosticSteps/LegalityChips
        para el tab Diagnóstico (NUEVO esta sesión, ver esa sección arriba)

Usuario edita un campo con recálculo en vivo de diagnóstico (Pokémon)
  → EditSessionService.BuildLiveDiagnosticSteps(key, edits, getCurrentPkm) — independiente
    del análisis que corre en el modal de exportación, no bloquea la UI del editor

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

## Legalidad (LegalityMessageMapper) — base sin cambios, extendida por el diagnosticador nuevo
`EditApplyService` sigue reusando el mismo mapeo campo→PKM que `EditSessionService.AnalyzeLegality`
ya tenía para el preview (ver GAP CRÍTICO arriba) — no hay una copia nueva de esa lógica. Lo
nuevo esta sesión es un consumidor más de `LegalityMessageMapper.GetCategory` (la agrupación por
categoría, sin cambios): `LegalityDiagnosticBuilder`, que arma el tab Diagnóstico entero — ver
"🩺 Diagnosticador de legalidad" arriba para el detalle completo.

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
- **Gap de testing que sigue abierto**: Habilidad/HeldItem/Dynamax/Alpha/Noble y creación de
  Pokémon nuevo compilan y están cableados al pipeline de escritura, pero sin test de
  round-trip dedicado todavía — prioridad para la próxima sesión de testing. Shiny salió de esta
  lista (ver campos huérfanos arriba, reusa `TryRegeneratePid`, mismo mecanismo que el
  diagnosticador). **Sin ningún test nuevo** para el diagnosticador de legalidad ni para la
  extensión de Gen3 en `TryEvolveForward`/construcción cross-versión (`PokemonService.cs`) —
  todo lo de esta sesión en esas dos áreas está sin cobertura de test dedicada todavía, a
  diferencia del resto del proyecto que sí tiende a tener `[Fact]`s de por medio.
- `SaveCapabilitiesTests.cs` sí tuvo cambios esta sesión (+19 líneas) — cubre el fix de `Ball`
  (Gen3+, no Gen2+) y la capacidad `Breeding` nueva (ver sección de Capacidades más abajo).

---

## 🧬 `PokemonService` — construcción cross-versión extendida a Gen3, con evolución por Belleza

Extiende la funcionalidad de "crear Pokémon exclusivo de la versión hermana" (intercambio por
cable link, ya existente para Gen1/Gen2 desde la sesión de julio) a **Gen3**. Mismo espíritu:
elegir una especie exclusiva de otra versión de la misma generación debe funcionar igual que en
el juego real, donde el intercambio simple entre cartuchos hermanos era mecánica central.

- **Versiones que ahora se agregan como origen válido para Gen3**: Rubí/Zafiro/Esmeralda/
  RojoFuego/VerdeHoja — los cinco se intercambiaban libremente entre sí por cable link de GBA.
  Se excluye a propósito `GameVersion.CXD` (Colosseum/XD, GameCube) — mecánicamente muy
  distintos (Pokémon Sombra, cámara de purificación, sin intercambio directo simple con
  RSE/FRLG), no tiene sentido meterlo en este broadening.
- **`TryEvolveForward` ahora recibe también el encuentro (`IEncounterTemplate enc`)**, no solo
  la especie objetivo — hace falta para el caso nuevo de Belleza (ver abajo). Nuevos casos de
  Gen3 confirmados por lectura directa de PKHeX.Core, no asumidos:
  - **Nincada→Ninjask/Shedinja** — ramificación terminal, mismo mecanismo que Eevee en Gen1/2.
    El glitch de relación de PID "hermano" para Shedinja es exclusivo de **Gen4** (confirmado en
    `GenderVerifier.cs` de PKHeX.Core, acotado a `pk.Format == 4`) — no aplica acá.
  - **Clamperl→Huntail/Gorebyss, Seadra→Kingdra** (intercambio + objeto sostenido) — mismo
    patrón `UseItem`/`TradeHeldItem` que ya se usaba en Gen2, PKHeX no vuelve a verificar la
    evidencia después del hecho.
  - **Feebas→Milotic por Belleza — ÚNICA excepción real, a diferencia de todo lo anterior**:
    PKHeX SÍ vuelve a verificar esto después del hecho (`EvolutionMethod.cs`:
    `LevelUpBeauty when pk is IContestStatsReadOnly s && s.ContestBeauty < Argument =>
    LowContestStat`). El umbral (170) vive en `Argument`, no en `Level` — de ahí un acumulador
    aparte (`neededBeauty`/umbral de Belleza) en vez de reusar el de nivel.
    - **Segundo bug real encontrado recién al probar Milotic**: no alcanza con subir
      `ContestBeauty` a mano — en el juego real cada Pokébloque también sube el "Brillo"
      (Sheen) de forma correlacionada, y PKHeX vuelve a chequear esa correlación
      (`ContestSheenGEQ_0`, fórmula intrincada que depende de las 5 stats de concurso a la
      vez). En vez de reimplementarla a mano, se usa el helper real de PKHeX.Core —
      `PKM.SetSuggestedContestStats(enc, new EvolutionHistory())` — que además tiene un caso
      hardcodeado específico para Milotic (pone las 5 stats y el Brillo al máximo, 255, la
      combinación más simple que siempre cae en rango válido). `new EvolutionHistory()` vacío
      alcanza para Gen3 (su constructor sin parámetros deja todo en None/false, y
      `GetContestStatRestriction` ni siquiera lo consulta para `pk.Format < 6`).
- **CatchRate/Tipo1/Tipo2 al evolucionar** — confirmado que PK2/PK3 (a diferencia de PK1) no
  tienen ningún mecanismo tipo "CatchRate como marca de intercambio" que preservar: a partir de
  Gen2 el tipo se deriva de la tabla de especie, no se guarda por individuo. Asignar `Species`
  por la propiedad real + `ResetPartyStats()` alcanza para todos los formatos.
- **Alcance sin ampliar todavía**: Gen4+ (piedras con condición de género/hora/región,
  evolución en batalla, cadenas con ramas no terminales, formas regionales) sigue sin
  investigarse — probablemente necesite más que este mismo método genérico.

---

## Capacidades por generación (`SaveCapabilities`) — dos cambios reales esta sesión

- **Nueva capacidad `Breeding`** (Gen2+) — puede existir el concepto mismo de "huevo sin
  eclosionar". Gen1 no tiene mecánica de cría (Day Care) en absoluto: `PK1.IsEgg` está
  hardcodeado a `get => false; set { }` en PKHeX.Core — un no-op total, no un campo vacío.
  Distinta de `EggLocation`/`EggDate` (esas son "sabemos que `IsEgg=true` pero no dónde/cuándo",
  Gen3+/Gen4+ respectivamente) — `Breeding` es "puede existir el concepto mismo de huevo".
- **⚠️→✅ Bug real corregido: `Ball` vivía en el bloque `gen >= 2`, ahora en `gen >= 3`** — recién
  desde Gen3 los juegos registran con qué Poké Ball se atrapó al Pokémon; en Gen1/Gen2 el dato
  no existe en el formato de guardado (todo lo capturado ahí se muestra como Poké Ball estándar
  al pasar a generaciones posteriores — confirmado, no es límite de PKHeX ni nuestro). Antes de
  este fix, el combo de Ball quedaba editable y aparentaba funcionar en Gen2, pero cualquier
  cambio se perdía en silencio al exportar porque `pkm.Ball` no tiene dónde persistir en un
  `PK2`.

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

28. **`CheckResult` es una unión de memoria (`[StructLayout(LayoutKind.Explicit)]`), no tres
    campos independientes** — `Value` y `Argument`/`Argument2` comparten los mismos bytes. Para
    códigos de un solo argumento, leer cualquiera de los dos da el mismo número; para códigos
    de dos argumentos empaquetados (sufijo `_01`), HAY que leer `Argument`/`Argument2` por
    separado — leer `Value` ahí da un número empaquetado sin sentido para un humano. Confirmado
    leyendo `CheckResult.cs`/`Verifier.GetInvalid` de PKHeX.Core 25.11.7 (ver
    `LegalityArgumentFormatter`).

29. **Los movimientos no generan `CheckResult` propio para "este movimiento no es legal"** —
    solo lo generan para PP. La legalidad real de cada slot vive en
    `LegalityAnalysis.Info.Moves`/`.Relearn` (arrays de `MoveResult`, uno por slot 1-4), un
    sistema totalmente aparte de `.Results`. Cualquier código que quiera diagnosticar
    movimientos ilegales tiene que leer esos dos arrays, no intentar encontrarlos agrupando
    `Results` como el resto de las categorías (ver `LegalityMoveFormatter`).

30. **Los dos códigos de suma de EVs por encima de 510 (`EffortAbove510` y el asociado) no
    traen NINGÚN argumento en el `CheckResult`** — confirmado en `EffortValueVerifier.cs`: el
    `AddLine` correspondiente no pasa ningún valor. Si hace falta saber el total real o cuánto
    se pasó, hay que calcularlo a mano leyendo `pkm.EVs` directo — PKHeX no lo va a dar nunca
    para este código puntual (ver `LegalityEvFormatter`). Relacionado pero distinto: el orden
    de `pkm.GetEVs()`/`GetIVs()` no es el estándar HP/Atk/Def/SpA/SpD/Spe — usan la misma
    convención "Speed en el índice 3" que `IndividualValueSet` (confirmado leyendo `PKM.cs`
    línea por línea).

31. **`IsShiny` es `virtual bool IsShiny => TSV == PSV` — get-only, sin setter propio.** No se
    puede "tildar Brillante" con una asignación directa como el resto de los booleanos del
    editor; hay que sortear un PID que cumpla `TSV == PSV` (y de paso siga resolviendo
    Naturaleza/Género/Habilidad según la generación) — mismo mecanismo que ya usa el botón
    "Corregir automáticamente" del tab Diagnóstico para el código de legalidad "PID inválido"
    (`PokemonService.TryRegeneratePid`). Si el sorteo no encuentra combinación en el tope de
    intentos (raro — ej. Brillante + Naturaleza puntual en Gen3-5), se ignora en silencio.

32. **Feebas→Milotic (Gen3) es la ÚNICA evolución con condición que PKHeX vuelve a verificar
    DESPUÉS del hecho** — a diferencia de amistad, nivel, o intercambio+objeto (donde PKHeX
    solo le importa que la especie final sea alcanzable por alguna cadena válida, sin
    re-chequear "evidencia"), Belleza sí se re-verifica (`EvolutionMethod.cs`:
    `LevelUpBeauty when pk is IContestStatsReadOnly s && s.ContestBeauty < Argument`). Y ni
    siquiera alcanza con subir `ContestBeauty` sola: PKHeX también re-verifica la correlación
    con el "Brillo" (Sheen) que cada Pokébloque sube a la vez en el juego real
    (`ContestSheenGEQ_0`, fórmula intrincada sobre las 5 stats de concurso). La forma correcta
    de resolver esto es el helper real de PKHeX.Core, `PKM.SetSuggestedContestStats(enc,
    evolutionHistory)` — tiene un caso hardcodeado específico para Milotic (pone las 5 stats +
    Brillo al máximo, 255, la combinación más simple que siempre cae en rango válido). NO
    reimplementar la fórmula de Sheen a mano — alto riesgo de error, y PKHeX ya trae la
    solución correcta empaquetada.

33. **El glitch de relación de PID "hermano" de Nincada→Shedinja es EXCLUSIVO de Gen4** — no
    aplica al construir Ninjask/Shedinja para un save de Gen3 (confirmado en
    `GenderVerifier.cs` de PKHeX.Core, el chequeo está acotado a `pk.Format == 4`). No asumir
    que un glitch conocido de una generación aplica igual a la generación vecina solo porque
    la mecánica de evolución (Nincada partiéndose en dos) es la misma en ambas.

34. **`Ball` solo se puede editar de verdad desde Gen3 en adelante** — en Gen1/Gen2 el dato de
    "con qué Poké Ball se atrapó" NO EXISTE en el formato de guardado (todo lo capturado ahí se
    muestra como Poké Ball estándar al pasar a generaciones posteriores — confirmado,
    limitación real del juego, no de PKHeX ni nuestra). Antes de que `SaveCapabilities.Detect()`
    moviera esta capacidad del bloque `gen >= 2` al `gen >= 3` (bug real corregido esta sesión),
    el combo de Ball quedaba editable y aparentaba funcionar en Gen2, pero cualquier cambio se
    perdía en silencio al exportar porque `pkm.Ball` no tiene dónde persistir en un `PK2`.
