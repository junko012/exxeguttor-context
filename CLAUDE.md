# CLAUDE.md — Instrucciones para Claude

## Lo primero que debes hacer en cada sesión

1. **Leer `context.md`** — contiene el estado actual del proyecto, arquitectura, decisiones
   técnicas clave y trampas conocidas de PKHeX.Core.
2. Si el usuario sube un ZIP del proyecto, extraer y leer los archivos fuente relevantes para
   refrescar tu contexto antes de opinar o modificar código. No confiar ciegamente en
   `context.md`/`CLAUDE.md`: el código real puede haber avanzado desde la última actualización
   de estos archivos (no hay repo git en el ZIP para verificar por commits, así que la única
   forma de confirmar es leer el código).
3. Antes de asumir el comportamiento de cualquier API de PKHeX.Core que no hayas verificado en
   ESTA sesión, **confirmala primero** (reflection sobre el DLL real, o un test que corra el
   usuario). Ya pasó varias veces esta sesión: asumir mal una firma/accesibilidad/comportamiento
   de PKHeX.Core sin verificar cuesta una vuelta completa de compile-error o, peor, un bug
   sutil que recién se nota con datos reales (ver "Trampas de PKHeX.Core" más abajo, es una
   lista larga por una razón).

---

## ⚠️ No hay dotnet SDK disponible en el sandbox de análisis

Claude no puede compilar ni correr el proyecto en su entorno de trabajo — no hay red hacia los
dominios de Microsoft para instalar el SDK. El ciclo de trabajo real es:

1. Claude escribe/edita código basándose en el análisis del código existente.
2. Antes de asumir cualquier firma/comportamiento de la API de **PKHeX.Core** que no esté ya
   confirmado en sesiones anteriores, Claude debe verificarlo por **reflection cruda sobre el
   DLL real** (`tests/Exxeguttor.Tests/bin/Debug/net9.0/PKHeX.Core.dll`, si está presente en el
   ZIP subido) usando la librería Python `dnfile` — permite leer nombres, firmas, flags de
   accesibilidad y tokens de tipo sin necesitar el runtime de .NET. Esto evitó varios errores
   de compilación esta sesión (`SetChecksums` resultó `protected`, `GetFileName` resultó
   `private`, hubo que decodificar bytes de firma a mano para confirmar tipos de parámetro).
3. El usuario compila localmente y pega el error/output completo.
4. Para preguntas de **comportamiento en runtime** (no solo firmas) — ej. "¿`CanContain`
   realmente filtra por categoría?" — reflection cruda no alcanza, hace falta un test real
   (`[Fact]`/`[Theory]` con `Assert.Fail` volcando resultados, o assertions reales) que el
   usuario corra y pegue la salida. No asumir comportamiento de datos reales sin este paso.
5. Si algo fallaba, Claude corrige y entrega solo los archivos tocados (no el ZIP entero) para
   minimizar qué tiene que pisar el usuario.

**Regla dura de esta sesión**: cuando la reflection de firmas y el comportamiento real
diverjan, ganó el comportamiento real. Ejemplo con dos capas de sorpresa: `CanContain` tiene
firma pública y confirmada (`bool CanContain(ushort)`), pero su comportamiento real es
category-inconsistente para pouches sin subclase propia (Gen1/2/4/5/6) — devuelve resultados
mezclados/incorrectos (ej. Great Ball clasificada en "Items" en vez de "Balls" para un save de
Gen2). Nunca dar por buena una API solo porque la firma compila.

---

## Sobre el proyecto

**Exxeguttor** es un editor de archivos de guardado de Pokémon para Linux, escrito en .NET 9.0 +
Avalonia UI, usando PKHeX.Core 25.11.7 como motor de lectura/escritura de saves. **La escritura
real ya está conectada** (ver sección siguiente) — dejó de ser el gap crítico que fue durante
gran parte del desarrollo.

El ZIP del proyecto siempre estará en `/mnt/user-data/uploads/`. Extraer en
`/home/claude/exxeguttor/`.

---

## ✅ Pipeline de escritura real — implementado esta sesión (antes era el GAP CRÍTICO)

Hasta hace poco, todo el editor era una capa de "edición pendiente en memoria" que nunca se
aplicaba al `SaveFile` real — exportar escribía el save tal cual estaba, sin las ediciones de
la UI. Eso ya no es así.

**Cómo quedó armado**, siguiendo el mismo patrón pendiente-hasta-confirmar de siempre pero con
un paso nuevo antes de exportar:

1. `EditSessionService` sigue siendo la única fuente de "qué cambió" (sin cambios en su rol).
2. **`EditApplyService`** (Exxeguttor.UI/Services) es la pieza nueva — se llama en
   `MainWindowViewModel.ConfirmExportAsync`, **antes** de `PerformExportAsync`. Muta el
   `SaveFile` en memoria; `PerformExportAsync`/`SaveFileService` no cambiaron su rol, solo que
   ahora sí escriben algo que refleja las ediciones.
3. `IsIncluded` en las tarjetas del modal de revisión **ahora filtra de verdad** — antes era
   decorativo. Esto aplica a las tres superficies: Pokémon, Entrenador y Mochila (`IsIncluded`
   se agregó también a `EditedTrainerSummary`/`EditedBagPouchSummary`, antes solo lo tenía la
   de Pokémon).
4. Cuatro superficies, cada una con su propio mecanismo de aplicación (no es un diff genérico):
   - **Pokémon (Box/Party)**: releer el PKM real (o tomar el ya construido si es una creación
     pendiente — y aplicarle también cualquier edición posterior sobre ese mismo slot, no
     asumir que "creación" y "edición" son mutuamente excluyentes), aplicar campos vía
     setters directos del PKM (mismo mapeo que ya usaba `EditSessionService.AnalyzeLegality`
     para el preview, extendido a Habilidad/HeldItem/Shiny/Dynamax/Alpha/Cintas, que el preview
     de legalidad no cubre), `pkm.RefreshChecksum()`,
     `save.SetBoxSlotAtIndex(pkm, box, slot, default)` / `SetPartySlotAtIndex` con
     `EntityImportSettings` default (struct, "lo conservador" — no toca Pokédex ni records).
   - **Cintas**: vía `RibbonWriter` (nuevo, simétrico a `RibbonReader` — generado a partir de
     su mismo mapeo interfaz-por-generación, no reinventado a mano). Dos caminos: formatos
     modernos usan `IRibbonIndex.SetRibbon(int, bool)` (un solo método para todas las cintas);
     formatos viejos usan el setter de propiedad específico por cinta
     (`IRibbonSetCommonN.RibbonX = value`).
   - **Entrenador**: `TrainerService.ApplyEdits(...)` (Exxeguttor.App, simétrico a
     `GetTrainerInfo`) — directo sobre `SaveFile`, sin clon, mismo mecanismo de reflection para
     Money/Coin/BP (son `uint`, `Convert.ChangeType` respeta el tipo real).
   - **Mochila**: reconstruir el pouch — **el array `InventoryPouch.Items` es de tamaño FIJO**,
     nunca se agranda/achica (confirmado con `WritePipelineRoundTripTests` — tirar
     `ArgumentOutOfRangeException` si el largo cambia). Buscar el slot existente del ítem
     (actualizar `Count` in-place) o el primer slot con `Count==0` (ocuparlo); reasignar
     `save.Inventory` completo al final.
5. `SaveFileService`: el nombre sugerido del diálogo de exportar ahora usa
   `save.Metadata.GetSuggestedExtension()` (extensión real del formato de *ese* save, no una
   tabla propia por generación) en vez de reusar ciegamente el nombre del archivo original. El
   backup usa `save.Metadata.GetBackupFileName(directorio)` (la convención real de PKHeX.Core —
   **ojo, espera el directorio, no la ruta completa del archivo**; pasarle la ruta completa lo
   trata como si fuera una carpeta), con fallback al timestamp manual viejo si falla (puede
   pasar con fechas jugadas no inicializadas en saves sintéticos, no debería pasar con un save
   real de usuario).

**Qué está confirmado con test de round-trip** (`WritePipelineRoundTripTests.cs`, mutación en
memoria contra la misma instancia — no round-trip binario completo, ver por qué en el propio
archivo): campos básicos de Pokémon (Nickname/Level/Nature/IVs/EVs/Moves+PPUps) en 5
generaciones, Entrenador, Mochila, Cintas (formato viejo Gen3+Gen4, formato moderno Gen9).

**Qué NO está confirmado con test todavía** (compila, tipos verificados por reflection, pero
sin round-trip dedicado): Habilidad, HeldItem, Shiny, Dynamax/Gigantamax, Alpha/Noble,
creación de Pokémon nuevo. Antes de dar por cerrado el pipeline al 100%, priorizar tests para
estos.

**Deliberadamente afuera**: Tera (`PK9.TeraTypeOriginal`/`Override`) sigue solo lectura en la
UI, no se escribe.

---

## 🎒 Módulo Mochila — implementado esta sesión

Editor de objetos del save, con el mismo patrón "edición pendiente hasta exportar" que Pokémon
y Entrenador.

### Arquitectura
- **`ItemInventoryService`** (Exxeguttor.App) — lee `SaveFile.Inventory` (PKHeX.Core), cruza
  con `PokemonDatabase` para nombre/descripción. `Items.ItemId` de `pokemon.db` coincide 1:1
  con el índice de PKHeX.Core (confirmado, mismo criterio que ya usaban Mega Stones/Z-Crystals)
  — **excepto para TMs/HMs, ver "Bug conocido, en curso" más abajo**.
- **`BagViewModel`** (Exxeguttor.UI) — orquestador: pouches disponibles, ítem seleccionado,
  búsqueda (acotada a la categoría actual, no global), toggle Mochila/PC.
- **`BagItemRowViewModel`** — una fila de ítem: checkbox poseído, stepper `−/+`, botón **MAX**
  (topea al `MaxCount` real del pouch, distinto por juego — nunca hardcodeado).
- **`RibbonWriter`**/`EditApplyService` — ver sección de pipeline arriba.
- **Navegación tipo caja**: el panel central de Mochila (`BagPouchGridView`) usa el mismo
  patrón visual que `BoxView` — `◀ [ícono + nombre de categoría] ▶` con texto de posición
  debajo ("Categoría 2/6"), **no** una grilla de tiles clickeables. Mismo clamp sin wrap que
  `BoxViewModel.PreviousBox/NextBox`. El toggle Mochila/PC sigue arriba, aparte.

### Confirmado por reflection/test esta sesión
- `InventoryPouch.CanContain(ushort)` — pública, pero **no confiable como filtro de
  categoría** en pouches sin subclase propia (ver bug conocido abajo).
- `InventoryPouch.Items` es array de tamaño **fijo** por pouch — nunca se agranda/achica.
- `IItemStorage.IsLegal(InventoryType, int, int)` — siempre devuelve `true` para todo, en
  cualquier pouch. Investigado como alternativa a `CanContain`, resultó inútil, descartado.
- Gen1 tiene 2 pouches (`Items`, `PCItems`) — TMs/HMs, bolas y objetos clave viven todos
  mezclados en el mismo pouch `Items`, no hay separación real en el juego.
- El toggle Mochila/PC solo tiene sentido en Gen1-3 (únicas generaciones con pouch `PCItems`
  real) — de Gen4 en adelante no existe ese storage aparte.

### ⚠️ Bug conocido, en curso — categorización de ítems para Gen1/2/4/5/6

**Síntoma reportado**: en la UI, ítems de distintas categorías (Bolas, MTs) aparecen mezclados
con Objetos para estas generaciones, y en Gen1 las MTs/HMs no aparecen agrupadas.

**Causa raíz confirmada** (no es solo "categorías mezcladas", es más profundo):
`InventoryPouch.CanContain` en los formatos **sin subclase propia** de PKHeX.Core (Gen1/2/4/5/6
usan la clase base genérica `InventoryPouch`, a diferencia de Gen3/7/8/9 que tienen
`InventoryPouch3`/`7`/`8`/`9` dedicadas) no hace un chequeo real de categoría — devuelve
resultados inconsistentes (ej. Great Ball clasificada como "Items" en vez de "Balls" para un
save de Gen2; un ítem de Sinnoh/Gen4 como "old-gateau" apareciendo como legal en un save de
Gen2). `IsLegal` (alternativa investigada) resultó aún peor: siempre `true`.

**Solución en curso, con un giro importante**: en vez de confiar en PKHeX.Core para la
categorización de estas generaciones, se va a agregar una columna **`CategoryUpper`** a la
tabla `Items` de `pokemon.db`, poblada a partir de la columna `Category` existente (46-48
categorías de PokeAPI) agrupada en los mismos 15 valores de `InventoryType` — guardando
literalmente el *nombre del enum* (`"Balls"`, `"TMHMs"`, etc.) para que el mapeo en C# sea un
`Enum.TryParse` directo, sin tabla intermedia. Mapeo completo ya acordado con el usuario
(PokeAPI category → CategoryUpper), incluye una categoría **virtual nueva `"Stones"`** (piedras
evolutivas) que no corresponde a ningún `InventoryType` real de PKHeX — las tiles de Mochila
van a pasar a depender de `CategoryUpper` (no del pouch real de PKHeX.Core), y el pouch real
solo decide *dónde* se escribe la cantidad (con fallback a `Items`/`PCItems` si esa generación
no tiene un pouch dedicado para esa categoría — ej. una MT en Gen1 se ve bajo la tile "MTs/MOs"
pero físicamente se escribe en el pouch `Items`, porque ese es el único que existe ahí).

**⚠️ BLOQUEADO ahora mismo**: el usuario detectó, durante esta misma investigación, que el
problema real de raíz está en **cómo `pokemon.db` modela las TMs/HMs** — ninguna MT de
generaciones tempranas trae su categoría `all-machines` esperada (aparecen 110 filas `tm01`...
en la DB, todas con `ItemId` en el rango 305+, pero el corte real de Gen1/Gen2 quedó
observado ~250 — sugiere que el `ItemId` único por "tm01" no contempla que en Gen1/2 esa MT
enseña un movimiento distinto al de Gen3+, y una sola fila no alcanza para representar eso
correctamente entre generaciones). El usuario está resolviendo esto en **otra sesión de
Claude aparte** y va a traer los pasos ya validados para que se ejecuten acá. **No tocar la
migración de `CategoryUpper` ni el código de categorización de Mochila hasta que eso llegue** —
armar la columna/mapeo sobre una tabla `Items` con las MTs mal modeladas solo agregaría un
problema encima del otro.

**Qué SÍ quedó cerrado y no hace falta revisar de nuevo cuando se retome**:
- El mapeo completo PokeAPI category → CategoryUpper (todas las categorías salvo TM/HM, que
  depende del fix pendiente).
- El diseño de tiles virtuales por `CategoryUpper` con fallback de pouch real.
- Conteos reales confirmados (antes del hallazgo del bug de TMs): Gen1/2 → 9 categorías
  (Objetos, Bolas, Batalla, Bayas, Clave, Correo, Medicina, Piedras, Tesoros), Gen3 → 10 (+
  MTs/MOs). Van a necesitar recalcularse una vez resuelto el modelado de TMs en la DB.

---

## Reglas de código que debes respetar siempre

### Arquitectura
- **`Exxeguttor.App`** — lógica de negocio, servicios, integración con PKHeX.Core
  (`PokemonDatabase`, `PokemonService`, `SaveFileService`, `TrainerService`,
  `ItemInventoryService`, `LegalityMessageMapper`). Sin referencias a Avalonia.
- **`Exxeguttor.UI`** — vistas AXAML, ViewModels, Converters, Services de UI (incluye
  `EditSessionService`, `EditApplyService`, `BusyStateService`, `RibbonReader`/`RibbonWriter`,
  `BagPouchDatabase`, `SpeciesPickerViewModel`). Referencia a `Exxeguttor.App`.
- Nunca mezclar lógica de PKHeX directamente en ViewModels; pasar siempre por los servicios de
  `Exxeguttor.App`. Excepciones conscientes, todas del mismo tipo (lectura/escritura directa de
  PKHeX.Core justificada porque la lógica es puramente de UI, no de negocio, y moverla a
  `Exxeguttor.App` no daría beneficio real): `RibbonReader`/`RibbonWriter` (Exxeguttor.UI) y
  `EditApplyService` (que necesita acceso directo tanto a `EditSessionService` como a tipos de
  PKHeX.Core para poder aplicar las ediciones — es la pieza que puentea ambos mundos a
  propósito).

### PKHeX.Core — reglas críticas confirmadas (por reflection y/o test real esta sesión)

**Tipos y estructuras:**
- **Tipos de Pokémon**: NUNCA usar `PersonalInfo.Type1/Type2` (índices divergen entre Gen1/2 y
  Gen3+). SIEMPRE usar `SpeciesDatabase.Instance.GetById(species).Types` que lee de la DB SQLite.
- **MetTimeOfDay**: solo existe en `PK2`. Usar pattern matching: `if (pkm is PK2 pk2) pk2.MetTimeOfDay`.
- **Pokérus**: usar `pkm.IsPokerusInfected` (abstracto en `PKM` base).
- **Legends Z-A usa `PA9`, no `PK9`** — mismo patrón que Legends Arceus (`PA8` ≠ `PK8`) pese a
  ser "misma generación" que Escarlata/Púrpura en otro sentido. `PA9.IsAlpha` existe (mismo
  mecanismo que `PA8`), pero **`PA9` NO tiene `IsNoble`** — no asumir simetría completa entre
  formatos "hermanos" sin confirmar. `SAV9ZA` es la clase de save correspondiente.

**GameVersion — el enum tiene valores específicos Y genéricos agregados, y `SaveFile.Version`
puede devolver cualquiera de los dos según el caso** (encontrado primero para X/Y/XY en una
sesión anterior, después confirmado que el mismo patrón rompía Gen9 también — **dos bugs reales
en producción por este motivo**, ambos ya corregidos): siempre agregar el valor genérico
(`GameVersion.Gen6`, `GameVersion.Gen9`, etc.) junto a los específicos en cualquier `switch`
sobre `GameVersion` que dependa de detectar la generación correctamente
(`SaveCapabilities.Detect()`, `PokemonEditorViewModel.MapVersionToGameId()`). Si se agrega
soporte a una generación nueva, sumar el genérico correspondiente desde el principio, no
esperar a que aparezca el bug.
  - Sword=SW=44, Shield=SH=45, Legends:Arceus=PLA=47, BD=48, SP=49, Scarlet=SL=50, Violet=VL=51,
    Legends Z-A=ZA
  - Silver=SI=40 (NO confundir con SL=50 que es Scarlet)
  - Ruby=R=2, Sapphire=S=1, Red=RD=35, Blue=BU=37, Yellow=YW=38
- **`.ToString()` en GameVersion** produce: Silver→"SI", Scarlet→"SL", Ruby→"R", Sapphire→"S", Red→"RD", Blue→"BU", Yellow→"YW"
- **`ExpandGameName()`** en `TrainerViewModel` mapea esos strings a nombres completos.

**Ribbons (`RibbonIndex`)**: dos caminos según formato — `IRibbonIndex.SetRibbon(int, bool)` /
`.GetRibbon(int)` para formatos modernos (un solo método para todas las cintas); interfaces
`IRibbonSetCommon3..9`/`IRibbonSetEvent3/4`/`IRibbonSetMemory6`/`IRibbonSetMark8/9` con setter
de propiedad específico por cinta para formatos viejos. Ver `RibbonReader.TryGet`/
`RibbonWriter.TrySet` para el mapeo completo ya resuelto — no rehacer este trabajo desde cero.

**Entrenador (`Money`/`Coin`/`BP`)**: son propiedades `uint` en PKHeX.Core, no `int` — nunca
castear directo `(int)raw` sobre un valor boxeado (tira `InvalidCastException`). Usar
`Convert.ToInt32`/`Convert.ChangeType` con try/catch de `OverflowException`. El nombre real de
la propiedad de monedas de casino es **`Coin`** (singular), no `Coins`.

**Escritura de Pokémon/save (confirmado esta sesión, todo por reflection + round-trip test)**:
- `SaveFile.SetBoxSlotAtIndex(PKM, int box, int slot, EntityImportSettings)` /
  `SetPartySlotAtIndex(PKM, int slot, EntityImportSettings)` — públicos. `EntityImportSettings`
  es **struct** (hereda de `System.ValueType`), `default` compila sin constructor explícito.
- `SaveFile.GetBoxSlotAtIndex(int box, int slot)` / `GetPartySlotAtIndex(int slot)` — públicos,
  devuelven `PKM`.
- `SaveFile.SetChecksums()` existe pero es **`protected`** — no se puede llamar desde afuera de
  la clase. `Write()` debería recalcular internamente vía `GetFinalData()` (que sí llama a la
  versión protegida internamente).
- `PKM.RefreshChecksum()` — pública, confirmada.
- `PKM.Move1` (y `Move2/3/4`) es **`ushort`**, no `int` — los PPUps correspondientes
  (`Move1_PPUps` etc.) sí son `int`.
- `PKM.CurrentLevel` es `byte`. `PKM.Ability`/`HeldItem` son `int`. `SaveFile.Gender` es `byte`.
- `PKM.SetShiny()` es un método de **instancia** público (void). `SetUnshiny()` es un método de
  **extensión** público en `PKHeX.Core.CommonEdits` (devuelve `bool`) — ambos resuelven bien
  con sintaxis `pkm.SetShiny()`/`pkm.SetUnshiny()` sin using extra (ya está `using PKHeX.Core;`).
- `BlankSaveFile.Get(...)` **no** deja el save listo para un `Write()` completo desde cero en
  todas las generaciones — confirmado que **SAV3 y SAV4** tiran `ArgumentOutOfRangeException`
  (`BlockInfo4.GetRevision`/`SAV3.WriteSectors`) al intentar `Write()` un save recién
  sintetizado, sin haber tocado nada. **Confirmado con un save Gen3 REAL (abrir + Exportar sin
  editar, en la app tal cual estaba) que esto NO pasa en producción** — es una limitación
  puntual de `BlankSaveFile.Get` para esas dos generaciones, no un bug real que afecte al
  pipeline de escritura. Por eso los tests de round-trip prueban mutación **en memoria** contra
  la misma instancia de `SaveFile` (que es exactamente lo que hace el pipeline real — mutar y
  escribir una sola vez, nunca re-parsear los propios bytes recién escritos) en vez de un ciclo
  completo `Write()` + `SaveUtil.GetSaveFile()`.
- `SaveFileMetadata.GetSuggestedExtension()` y `GetBackupFileName(directorio)` son públicos —
  usar para nombre sugerido/backup. `GetFileName(string, string)` es **privado**, no se puede
  usar desde afuera (existe pero es de uso interno de la clase).

**Mochila / Inventory**:
- `SaveFile.Inventory` — lista de `InventoryPouch`, un pouch por `InventoryType` presente en
  ese save (varía por generación, nunca hardcodear cuáles existen — leer dinámicamente).
- `InventoryPouch.Type` (`InventoryType`, campo público), `.MaxCount` (`int`, campo público,
  varía por pouch/juego — nunca hardcodear el tope del stepper "Max"), `.Items`
  (`InventoryItem[]`, campo público, **tamaño fijo por pouch, nunca se agranda/achica** — un
  slot "vacío" tiene `Count==0`, no se elimina del array).
- `InventoryItem.Index`/`.Count` son `int` (no `ushort`) — es un `record class` (referencia,
  tiene constructor parameterless, sintaxis `new InventoryItem { Index = x, Count = y }`
  compila).
- `InventoryPouch.CanContain(ushort itemIndex)` — **cast explícito** de `int` a `ushort`
  necesario. Fiable en Gen3/7/8/9 (subclases dedicadas), **no fiable como filtro de categoría**
  en Gen1/2/4/5/6 (clase base genérica) — ver "Bug conocido" arriba.
- `IItemStorage.IsLegal(InventoryType, int, int)` (vía `InventoryPouch.Info`) — investigado
  como alternativa a `CanContain`, descartado: siempre devuelve `true`.
- `InventoryType` — 16 valores confirmados: `None, Items, KeyItems, TMHMs, Medicine, Berries,
  Balls, BattleItems, MailItems, PCItems, FreeSpace, ZCrystals, Candy, Treasure, Ingredients,
  MegaStones`. `PCItems`/`FreeSpace` son el "almacén aparte de la mochila" de generaciones
  tempranas (Gen1-3 tienen `PCItems`; de Gen4 en adelante no existe ese pouch).

### IVs/EVs — Gen1/2 tienen mecánica propia, no son "0-31 / 0-252" genérico

Bug real encontrado y corregido esta sesión — antes el editor permitía IVs hasta 31 y EVs hasta
252 en **cualquier** generación, incluida Gen1/2:

- **IVs en Gen1/2 son en realidad DVs: 0-15, no 0-31.** El DV de PS **no es un valor propio**:
  PKHeX.Core lo deriva del bit menos significativo de Atq/Def/Vel/Especial — confirmado con
  round-trip test (asignar `IV_HP` directo en un PKM de Gen1 se ignora silenciosamente, sale
  siempre derivado). El stepper de PS se deshabilita/atenúa para estas generaciones
  (`PokemonEditorViewModel.UsesLegacyIVs`), y el resto de los steppers de IV topean a 15.
- **EVs en Gen1/2 son en realidad "Stat Experience": 0-65.535 por stat, no 0-252**, y **sin**
  tope de suma total (a diferencia de Gen3+, que sí tiene el límite de 510 combinado — ese
  límite hoy tampoco está forzado en el código, es un gap preexistente aparte). El aporte a la
  fórmula de stats es `floor(sqrt(StatExp)/4)`, no `floor(EV/4)` — en el techo de cada escala
  ambas fórmulas coinciden (`floor(sqrt(65535)/4) == floor(252/4) == 63`), por eso Gen3+ pudo
  simplificar el sistema sin cambiar el rango efectivo de stats. Ver
  `PokemonEditorViewModel.EvContribution()`.
- El botón "Max" del stepper de IV/EV usa el mismo clamp que el resto (`EffectiveMax` en
  `PokemonStatsView.axaml.cs`), así que ya sale bien diferenciado por generación sin código
  aparte al tocarlo.
- **Se asumió que Stat Experience funciona idéntico en Gen1 y Gen2** (mismo rango, misma
  fórmula) — si en algún momento se confirma que difieren entre sí, hay que separar el flag
  `UsesLegacyIVs` en dos.

### PokemonEditorViewModel y edición
- **Patrón `Set<T>` con valor prístino**: tanto `PokemonEditorViewModel.Set<T>` como
  `TrainerViewModel.Set<T>` y `BagItemRowViewModel` (vía callback a `RecordEdit`) capturan el
  valor "tal cual venía" la primera vez que se ve una propiedad en un slot
  (`EditSessionService.CapturePristine`), y `RecordEdit` compara cada cambio posterior contra
  ese prístino: si el usuario vuelve al valor original, la edición se borra en vez de quedar
  marcada para siempre. Replicar este mismo patrón en cualquier ViewModel nuevo con edición
  trackeada por `EditSessionService`.
- **⚠️ Cuidado con nombres de propiedad compartidos entre Pokémon y Entrenador en
  `CategoryMap`** — `"Gender"` es una clave que existe en ambos mundos. `BuildSummary()` (solo
  para Pokémon) y `GetSimpleSummary()` (la libreta) tienen que excluir explícitamente las
  claves sentinel de Entrenador/Mochila al principio del loop (`key.IsBag`,
  `key == PokemonSlotKey.ForTrainer()`) — sin este guard, editar el género del entrenador
  dispara `fetchPristine(ForTrainer())` → `PokemonService.GetBox(-1)` → crash real en
  producción (bug encontrado y corregido esta sesión). Si se agrega una clave de propiedad
  nueva a cualquiera de los dos `CategoryMap`, revisar que no colisione con el otro.
- El tab Moves usa `MoveSelectorViewModel` para el panel de selección por slot (1-4).
  `ApplyMoveSelection()` actualiza el ViewModel y ya está cableado al pipeline de escritura vía
  `EditApplyService.ApplyMove`.
- El tab IVs/EVs incluye barras segmentadas y un radar de stats.
  **`GetNatureMultiplier()` debe leer `_selectedNature`, NUNCA `_currentPkm.Nature`**.
- **Tab Ribbons** — editable, mismo mecanismo pendiente-hasta-exportar, prefijo `"Ribbon:"` en
  `EditSessionService`. Ya escribe al PKM real vía `RibbonWriter` (ver pipeline arriba).

### Panel de Entrenador (TrainerViewModel)
- Editable: **Nombre**, **TID/SID**, **Género**, **Dinero**, **Monedas de casino**, **Battle
  Points**. Cada uno pasa por `Set<T>` con la clave sentinel `PokemonSlotKey.ForTrainer()`.
- Ya escribe al `SaveFile` real vía `TrainerService.ApplyEdits(...)` (ver pipeline arriba).
- **`TID`/`SID` no están en `TrainerCategoryMap`** (gap conocido, no bloqueante) — se aplican
  bien al exportar porque `EditApplyService` lee `GetRawEdits` directo, pero no aparecen
  listados en la libreta ni en el modal de revisión. Si se quiere mostrar, agregar la entrada
  al mapa (una línea).

### Modal de revisión / exportación (EditSessionService + EditApplyService + MainWindowViewModel)
- Tres tipos de tarjeta (Pokémon, Entrenador, Mochila), **las tres con checkbox `IsIncluded`
  real** que filtra qué se aplica al exportar.
- `CancelReviewCommand` cierra el modal sin borrar nada — las ediciones siguen intactas.
- El botón "Guardar" del toolbar (`CheckpointCommand`) es un checkpoint visual (libreta,
  `GetSimpleSummary()`) — no escribe a disco ni aplica nada, solo refresca el resumen.

### Selector de modo general (Pokémon / Pokédex / Mochila)
- `MainWindowViewModel.CurrentMode` (`AppMode` enum) controla qué panel central/derecho se
  muestra — el panel Entrenador queda igual en cualquier modo.
- **Pokédex sigue siendo un placeholder deshabilitado** — no implementado todavía.
- Al cambiar a modo Mochila se llama `Bag.Initialize()` de nuevo (recarga defensiva, mismo
  criterio que `LoadPokemon` en el editor).

### Legalidad (LegalityMessageMapper)
- Única fuente compartida de traducción `CheckIdentifier → categoría/mensaje ES`. Dos
  consumidores: `PokemonService.GetLegalitySummary` y `EditSessionService.AnalyzeLegality`.
  Tocar solo este archivo si hace falta agregar/corregir una categoría.

### Capacidades por generación (`SaveCapabilities`)
- Detecta automáticamente qué campos mostrar según el save cargado — la UI usa las propiedades
  `Has*`, nunca hardcodear números de generación en la vista.
- **Siempre agregar el valor genérico de `GameVersion` junto al específico** en cualquier
  `case` nuevo (ver regla de PKHeX.Core arriba) — dos bugs reales de esto ya corregidos esta
  sesión (Gen9/Terastal, y el mismo patrón para Gen6 en una sesión anterior).
- Legends Z-A (`GameVersion.ZA`) suma `SaveCapability.Alpha` (mismo mecanismo que Legends
  Arceus) pero **no** `NobleLevel` — `PA9` no tiene `IsNoble`.

### Testing
- Proyecto `tests/Exxeguttor.Tests/` con xUnit + FluentAssertions.
- **`WritePipelineRoundTripTests.cs`** — mutación en memoria (no round-trip binario, ver por
  qué en las reglas de PKHeX.Core arriba) del pipeline de escritura real. Assertions reales,
  no diagnóstico.
- Tests de diagnóstico por reflection (`Assert.Fail` volcando resultados, no assertions de
  negocio) acumulados esta sesión, todos documentan cómo se resolvió una duda de API sin
  documentación confiable disponible — mismo patrón a reusar ante una API nueva desconocida:
  `InventoryApiDiagnosticTests.cs`, `BagItemCategoryDiagnosticTests.cs`,
  `ItemStorageDiagnosticTests.cs`, `MaxItemIdDiagnosticTests.cs` (más los ya existentes de
  sesiones anteriores: `CreationApiDiagnosticTests.cs`, `EntityBlankDiagnosticTests.cs`,
  `LearnsetDiagnosticTests.cs`).
- Antes de dar por buena una feature de capacidades por gen, agregar/extender un test en
  `SaveCapabilitiesTests.cs`.

### Empaquetado
- RPM spec: `packaging/rpm/exxeguttor.spec`
- DEB control + desktop entry: `packaging/debian/control`, `packaging/debian/exxeguttor.desktop`
- CI/CD: `.github/workflows/build.yml` y `release.yml`
- Target: `linux-x64`, self-contained, single file.

---

## Flujo de trabajo actual

```
Abrir save → SaveFileService.OpenAsync()
            → SaveCapabilities(save)
            → TrainerService.GetTrainerInfo() → TrainerViewModel.LoadFrom()
            → PokemonService.GetBox/GetParty()
            → BoxViewModel / PartyViewModel
            → Bag.Initialize() (pouches de Mochila, disponible ni bien se abre el save)

            → click en slot → PokemonEditorViewModel.LoadPokemon(pkm, caps, slotKey)
            → edición en UI (Pokémon, Entrenador o Mochila) → Set<T>/RecordEdit
              → EditSessionService (pendiente en memoria, PKM/SaveFile real sin tocar todavía)

            → Exportar → EditSessionService.BuildSummary()/BuildTrainerSummary()/BuildBagSummaries()
              (clon + LegalityAnalysis solo para Pokémon; Entrenador/Mochila sin legalidad)
            → modal de revisión (IsIncluded real por tarjeta) → confirmar
            → EditApplyService.ApplyIncluded(...)
              (AHORA SÍ aplica lo tildado al SaveFile real: Pokémon+Cintas, Entrenador, Mochila)
            → PerformExportAsync() → SaveFileService.SaveAsAsync()
              (escribe el SaveFile YA MUTADO — refleja las ediciones aplicadas)
            → EditSessionService.ClearAll()
```
