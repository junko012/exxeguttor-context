# status.md — Changelog cronológico de sesiones (Exxeguttor)

Este archivo es un **log que se agrega, no se reescribe**: cada sesión suma una entrada nueva al
final, nunca se edita una entrada vieja salvo para corregir un error de hecho. Para el estado
*actual* del proyecto (cómo funciona todo hoy, sin importar el historial de cómo se llegó ahí),
ver `context.md` — ese sí se reescribe cada vez. `CLAUDE.md` son las instrucciones de proceso
para trabajar en este repo.

Formato de cada entrada: fecha aproximada (no hay git, así que es la fecha de la sesión de
chat, no de commit) + resumen de qué se hizo + decisiones de producto relevantes + qué quedó
pendiente. No hace falta detalle técnico exhaustivo acá — eso vive en `context.md`.

---

## 2026-07 — Sesión grande: migración PKHeX.Core + Crear Pokémon + rediseños varios

Sesión larga, de punta a punta:

**Migración PKHeX.Core 25.2.23 → 25.11.7**
- Motivada por necesitar soporte de edición completo para Gen 9 (SV), que 25.2.23 tenía
  incompleto (carga de saves SV bloqueada, ver hipótesis del fix de rango de tamaño de save en
  changelog público de PKHeX — no se llegó a confirmar 100% si era exactamente esa la causa raíz
  original, pero el bump de versión se hizo igual).
- 5 rondas de errores de compilación resueltas una por una (`SaveUtil.GetVariantSAV` renombrado,
  `SaveFile.Write()` cambió de tipo de retorno, `CheckResult.Comment` removido,
  `SaveUtil.GetBlankSAV` movido de clase, `PKM.IVs` deprecado) — **todas documentadas en detalle
  en `context.md`, sección "PKHeX.Core 25.11.7 — cambios de API"**, no repetir la investigación.
- Se usó reflection vía tests xUnit descartables (`Assert.Fail` con el mensaje volcando los
  miembros encontrados) para confirmar cada API nueva sin depender de documentación pública, que
  resultó contradictoria/desactualizada más de una vez.

**Funcionalidad "Crear Pokémon" (especie elegible desde Caja/Equipo)**
- Primera implementación escribía directo al `SaveFile` real (`SetBoxSlotAtIndex`/
  `SetPartySlotAtIndex`) — el usuario pidió corregirlo explícitamente: **todo tiene que quedar
  pendiente hasta confirmarse en el modal de exportación**, mismo criterio que el resto del
  editor. Se corrigió partiendo la operación en "construir en memoria" (`PokemonService.BuildPokemon`,
  sin tocar el save) + "trackear como pendiente" (`EditSessionService._pendingCreations`).
- Decisiones de producto acordadas explícitamente (no hay default de PKHeX para ninguna):
  Nivel 5, IVs 31 perfectos, EVs 0, habilidad slot 0, moveset = últimos 4 de levelup hasta el
  nivel de creación, Naturaleza/Género/Habilidad derivados del PID en Gen 3-5 (no elegidos a
  mano) y random independiente en Gen 6+, sin sumar `PKHeX.Core.AutoMod` como dependencia.
- Se agregó un badge "✦ Creación" en el modal de revisión, sprite en las tarjetas del modal
  (antes solo texto), y filtro por tipo en el selector de especie (además del buscador de texto).

**Rediseños de UI**
- Tab IVs/EVs: reordenado completo (editor arriba, gráficos como resumen al final), steppers
  conectados, Poder Oculto y Naturaleza (solo lectura) conectados a la UI por primera vez —
  existían en el ViewModel hacía rato pero nunca se habían mostrado.
- Tab Ribbons: de lista suelta a tarjetas por categoría con color (4 categorías con color
  propio, 3 grises diferenciados), items alfabetizados, chips de filtro con estado propio.
- Tabla de efectividad de tipos (columna Hits): de un `WrapPanel` mezclado a subcolumnas fijas
  por tipo propio, con header de tipos una sola vez arriba de la tabla (no repetido por fila).
- Tab Moves: "+" en el primer slot de movimiento vacío (mismo lenguaje visual que crear
  Pokémon), en vez de una tarjeta a medio llenar.
- Tab Learnsets: columna de nivel ahora muestra código de MT/MO cuando corresponde (antes
  mostraba "0" para todo lo que no fuera level-up).
- Tab Sets: filtrado por generación del juego actual (antes mostraba todas las generaciones
  disponibles para la especie), sprite de objeto agregado.
- Caja/Equipo: nivel+género visibles debajo del sprite en ambos paneles (antes se superponían
  en Caja por falta de alto en la tarjeta), badge de objeto equipado con fallback a Poké Ball.

**Pendiente para una sesión futura** (ver también `context.md` para el detalle de cada uno):
- Pipeline de escritura real (GAP CRÍTICO) — sigue sin existir para nada del editor, incluida la
  creación de Pokémon, que ya tiene todo listo del lado de construcción pero no aplica nada.
- `AnalyzeLegality` no está ajustado para Pokémon recién creados (preview de legalidad puede no
  ser preciso en ese caso puntual).
- Columna de MT/MO en Learnsets es angosta y trunca el texto — cosmético.
- Conectar el checkbox `IsIncluded` del modal de revisión a un filtro real (sigue siendo
  decorativo, documentado desde antes de esta sesión).

---

## 2026-08 — Edición de entrenador, generalización del modal de exportación, legalidad y cintas editables

Sesión centrada en extender el mismo patrón de "edición pendiente hasta exportar" (ya usado por
el editor de Pokémon) a nuevas superficies, más un renombre de servicio y varios ajustes:

**Panel de entrenador ahora editable**
- `TrainerViewModel` pasó de ser 100% solo lectura a tener editables: Nombre, TID/SID (con
  formato `D5`), Género (ComboBox Macho/Hembra), Dinero, Monedas de casino, y **Battle Points**
  (campo nuevo, no existía ningún soporte previo para BP).
- Mismo mecanismo que el editor de Pokémon: `Set<T>` reporta a `EditSessionService` usando una
  clave sentinel nueva, `PokemonSlotKey.ForTrainer()` — reusa toda la infraestructura existente
  (captura de valor prístino, diff, restauración) en vez de construir un sistema paralelo.
- Botones "Max" para Dinero/Monedas (al tope real que reporta PKHeX.Core para ese save) y Battle
  Points (tope `9999` hardcodeado, PKHeX.Core no expone ningún "MaxBP").
- Dos bugs de datos encontrados y corregidos en `TrainerService`: (a) `Money`/`Coin`/`BP` son
  `uint` en PKHeX.Core, no `int` — un cast directo tiraba `InvalidCastException`, corregido con
  `Convert.ToInt32` + manejo de overflow; (b) la propiedad real de monedas de casino es `Coin`
  (singular), no `Coins` — con el nombre viejo el campo nunca se detectaba en ninguna generación.

**Modal de exportación generalizado**
- El modal de revisión ahora también arma una tarjeta de entrenador (`EditedTrainerSummary`,
  sprite de entrenador/entrenadora, cambios agrupados por categoría) aparte de las tarjetas de
  Pokémon existentes — sin legalidad ni checkbox de inclusión, porque los datos de entrenador se
  exportan siempre que haya alguna edición.
- Se agregó el patrón de "valor prístino" a `EditSessionService` (`CapturePristine` +
  comparación en `RecordEdit`): revertir una edición a su valor original ahora borra la entrada
  en vez de quedar marcada como cambio para siempre — antes tildar y destildar algo (o volver a
  una opción de combo anterior) quedaba "pegado" sin motivo real en la libreta y el modal.

**Cintas: de solo lectura a editables**
- El tab Ribbons pasó de mostrar únicamente el estado real del PKM a permitir tildar/destildar
  cada cinta libremente. Nuevo `RibbonReader` (Exxeguttor.UI) resuelve, cinta por cinta
  (`RibbonIndex`), a qué interfaz de PKHeX.Core (`IRibbonIndex` directo en formatos modernos, o
  `IRibbonSetCommon3..9`/`Event3/4`/`Memory6`/`Mark8/9` en formatos viejos) hay que preguntarle
  el valor — cobertura completa de los ~34 valores relevantes del enum.
  - Los cambios se trackean con el prefijo `"Ribbon:"` en `EditSessionService`, agrupados aparte
    en la categoría "Cintas" del modal de revisión y de la libreta.
  - **Sigue sin escribirse al PKM real** — mismo patrón pendiente-hasta-exportar que todo lo
    demás, esto es "más superficie editable en memoria", no un avance del pipeline de escritura.

**Renombre: `LegalityMessageTranslator` → `LegalityMessageMapper`**
- Mismo archivo/responsabilidad (traduce `LegalityAnalysis` de PKHeX.Core a categorías/mensajes
  amigables en español, fuente única compartida entre el badge del panel principal y el preview
  del modal de exportación), solo cambió el nombre de la clase. Cualquier referencia al nombre
  viejo en código o docs de sesiones anteriores es simplemente obsoleta.

**Otros cambios menores**
- Nuevos converters `RibbonCategoryColorConverter` y `TypeSoftConverters` para el rediseño visual
  de cintas y chips de filtro.
- `BusyStateService` ahora también cubre el análisis de legalidad al exportar (antes solo
  cubría creación de Pokémon y abrir/guardar save).

**Pendiente para una sesión futura** (ver también `context.md` para el detalle de cada uno):
- Pipeline de escritura real (GAP CRÍTICO) — sigue sin existir. Ahora que `EditSessionService`
  es la fuente única de "qué cambió" (Pokémon, cintas, entrenador, creaciones), implementarlo es
  más mecánico que antes: releer PKM/SaveFile real, aplicar el mismo mapeo que ya usa
  `AnalyzeLegality` como base (extendido a Habilidad/HeldItem/Ribbons/Special), `RefreshChecksum`,
  `SetBoxSlotAtIndex`/`SetPartySlot`/escritura directa de campos de entrenador.
- `IsIncluded` en el modal sigue sin filtrar nada real (mismo pendiente de antes).
- `AnalyzeLegality` sigue sin correlacionar Habilidad/HeldItem/Ribbons/Special con la legalidad
  previsualizada (se muestran en la lista de cambios pero nunca disparan ⚠).
- Pokédex: `fetch-species-extra.py` ya genera `species_extra.json` desde PokeAPI, pero sigue sin
  existir el script de carga a `pokemon.db` ni ninguna vista que lo consuma.
- Módulo de Items/Bag: sigue en etapa de mockup/análisis, sin código.

---

## 2026-08 — Módulo Mochila completo + pipeline de escritura real (GAP CRÍTICO cerrado) + fixes reales en producción

Sesión larga y densa, con dos entregas grandes (Mochila + pipeline de escritura) y varios bugs
reales encontrados sobre la marcha, cada uno con causa raíz confirmada por test o reflection —
no hay ningún fix a ciegas en esta lista.

**Pipeline de escritura real — el GAP CRÍTICO histórico queda cerrado**
- Nuevo `EditApplyService` (Exxeguttor.UI), llamado desde `ConfirmExportAsync` antes de
  exportar — aplica de verdad al `SaveFile` en memoria todo lo tildado (`IsIncluded`) en el
  modal de revisión. Hasta ahora, exportar escribía el save tal cual estaba, sin aplicar nada.
- `IsIncluded` **ahora filtra de verdad** en las tres tarjetas del modal (Pokémon, Entrenador,
  Mochila) — antes solo existía en la de Pokémon, y era decorativo en los tres casos.
- Cuatro superficies con mecanismo propio: Pokémon+Cintas (releer PKM real, aplicar campos vía
  setters directos incluyendo ahora Habilidad/HeldItem/Shiny/Dynamax/Alpha, `RefreshChecksum`,
  `SetBoxSlotAtIndex`/`SetPartySlotAtIndex`), Cintas vía `RibbonWriter` nuevo (simétrico a
  `RibbonReader`, generado a partir de su mismo mapeo), Entrenador vía `TrainerService.
  ApplyEdits` nuevo, Mochila reconstruyendo el pouch real (**el array de ítems es de tamaño
  fijo, confirmado con test** — hay que mutar in-place, nunca cambiar el largo).
- `SaveFileService`: nombre sugerido de exportación y backup ahora usan las convenciones reales
  de PKHeX.Core (`GetSuggestedExtension`/`GetBackupFileName`) en vez de lógica propia.
- Confirmado con test de round-trip real (`WritePipelineRoundTripTests.cs`, mutación en memoria
  contra la misma instancia — no round-trip binario completo, ver `context.md` para el porqué):
  Pokémon básico en 5 generaciones, Entrenador, Mochila, Cintas viejas y modernas. **Sin test
  todavía**: Habilidad, HeldItem, Shiny, Dynamax, Alpha/Noble, creación de Pokémon nuevo —
  compilan y están cableados, pero sin confirmar con datos reales.
- Deliberadamente afuera: Tera sigue sin escribirse (solo lectura en la UI, como ya estaba).

**Módulo Mochila — implementado de punta a punta**
- `ItemInventoryService` (lectura de `SaveFile.Inventory`), `BagViewModel`/
  `BagItemRowViewModel`/`BagPouchTileViewModel` (UI), navegación de categorías **tipo caja**
  (mismo lenguaje visual que `BoxView` — `◀ nombre ▶` con texto de posición debajo, no una
  grilla de tiles como el primer boceto) por pedido explícito del usuario ("solo cambia el
  texto" respecto a como ya funcionaba Caja).
- Botón MAX en el stepper de cantidad, topeado al `MaxCount` real de cada pouch (nunca
  hardcodeado — varía mucho por juego).
- Toggle Mochila/PC — confirmado con test que solo tiene sentido en Gen1-3 (únicas
  generaciones con pouch `PCItems` real).

**Bug real: categorización de ítems rota para Gen1/2/4/5/6 — investigación en curso, BLOQUEADA**
- Reportado por el usuario: ítems de categorías distintas apareciendo mezclados en "Objetos".
- Investigación con tests reales (no supuestos) descartó dos hipótesis de PKHeX.Core:
  `InventoryPouch.CanContain` no es confiable como filtro de categoría en los formatos sin
  subclase propia (Gen1/2/4/5/6) — da resultados que ni respetan qué ítems existen en esa
  generación. `IItemStorage.IsLegal` (alternativa investigada) resultó peor: siempre `true`.
- Solución diseñada y acordada: agregar columna `CategoryUpper` a `pokemon.db.Items`,
  agrupando las ~48 categorías de PokeAPI en los 15 valores de `InventoryType` + una categoría
  virtual nueva `"Stones"` (piedras evolutivas, decisión de producto: aparece como su propia
  tile navegable aunque no exista ese pouch en ningún juego real). Mapeo completo ya cerrado.
- **BLOQUEADO**: durante la misma investigación, el usuario detectó que el problema de fondo
  está en cómo `pokemon.db` modela las TMs/HMs (un solo `ItemId` por "tm01" no alcanza para
  representar que enseña movimientos distintos entre eras) — lo está resolviendo en otra sesión
  aparte y va a traer los pasos validados. **No tocar la migración de `CategoryUpper` hasta que
  llegue eso.**

**Otros bugs reales encontrados y corregidos**
- **Crash real en producción**: editar el género del entrenador junto con Pokémon disparaba
  `ArgumentOutOfRangeException` (`PokemonService.GetBox(-1)`) — `"Gender"` es una clave
  compartida entre el `CategoryMap` de Pokémon y el de Entrenador, y `BuildSummary()` no
  filtraba las claves sentinel de Entrenador/Mochila antes de asumir "esto es un Pokémon".
- **Tab Special no aparecía para ningún save de Gen9 (Escarlata/Púrpura)**: `SaveFile.Version`
  puede devolver el valor genérico `GameVersion.Gen9` en vez del específico según el caso — ya
  había un comentario en el código documentando el mismo problema encontrado antes para Gen6,
  pero el fix nunca se había aplicado a Gen9. Corregido en `SaveCapabilities.Detect()` y
  `MapVersionToGameId()`.
- **Tab Special tampoco aparecía para Legends Z-A**: resultó ser un bug distinto con el mismo
  síntoma — Z-A usa su propio formato `PA9`/`SAV9ZA` (no `PK9`, pese a ser "Gen9"), sin ningún
  `case` para `GameVersion.ZA` en `SaveCapabilities`. `PA9` tiene `IsAlpha` (mismo mecanismo
  que Legends Arceus) pero no `IsNoble`.
- **IVs/EVs permitían valores fuera de rango en Gen1/2**: los IVs ahí son en realidad DVs
  (0-15, no 0-31), y el DV de PS no es editable de verdad (se deriva de los otros cuatro,
  confirmado con test que asignarlo se ignora). Los EVs son "Stat Experience" (0-65.535, no
  0-252), con fórmula de stats propia (`floor(sqrt(StatExp)/4)` en vez de `floor(EV/4)`).

**Metodología — lección dura de esta sesión**
Varias veces se asumió mal una firma o comportamiento de PKHeX.Core sin verificar primero
(`SetChecksums` resultó `protected`, `GetFileName` resultó `private`, `CanContain` resultó no
confiable pese a compilar perfecto) — cada vez costó una vuelta completa de compile-error o un
bug sutil. Sin dotnet SDK disponible para Claude en el sandbox de análisis, se afinó un flujo de
verificación por **reflection cruda sobre el DLL real** (librería Python `dnfile`, sin necesitar
el runtime de .NET) que evitó varios de estos casos apenas se adoptó — pero no reemplaza
verificar **comportamiento** (no solo firmas) con tests reales que corre el usuario.

**Pendiente para una sesión futura** (ver también `context.md` para el detalle de cada uno):
- Categorización de Mochila para Gen1/2/4/5/6 — bloqueada, esperando el fix de TMs en la DB.
- Tests de round-trip para Habilidad/HeldItem/Shiny/Dynamax/Alpha/creación de Pokémon (cableados
  pero sin confirmar con datos reales).
- `TID`/`SID` de entrenador no están en `TrainerCategoryMap` — se aplican bien al exportar pero
  no se listan en la libreta/modal (gap chico, no bloqueante).
- Límite de suma total de EVs (510 en Gen3+) sigue sin forzarse en el código — gap preexistente,
  no tocado esta sesión.
- Pokédex y Módulo de Items/Bag (mockup previo, ahora superado por el módulo Mochila real):
  Pokédex sigue sin script de carga ni vista.

---

## Sesión: corrección real de categorización de Mochila + gestión de sesión de save

**Resumen**: la categorización de ítems de Mochila (Gen1/2/4/5/6, bloqueada en la sesión
anterior esperando un fix de modelado de TMs) quedó resuelta de raíz — la causa real no era el
modelado de TMs en `pokemon.db`, sino que `ItemInventoryService` nunca usó la columna
`RawItemId` que ya traía `ItemGameCodes` desde el hotfix `fix_database`. Además se rediseñó el
panel central de Mochila (ahora grilla de tiles tipo Caja de Pokémon, con origen Mochila/PC
navegable arriba — antes era navegación de a una categoría), se agregaron descripciones de
MT/HM por generación, y se sumó gestión de sesión de save (Cerrar/Limpiar ediciones/confirmar
antes de abrir otro archivo). Ver `context.md`, sección "🎒 Módulo Mochila", para el detalle
técnico completo (incluye el historial de las cuatro correcciones hasta llegar a la causa real).

**Resuelto y probado con saves reales**:
- Categorización de Mochila para TODAS las generaciones, vía `ItemGameCodes.RawItemId` (no
  `ItemId`) — corrige tanto MTs/MOs (antes vacías en Gen1/2) como otros ítems que fallaban en
  silencio (Piedras evolutivas, Llaves, Cebo Bueno, etc. en Gen1/2).
- `TmDescriptionResolver` — descripción de MT/HM resuelta a la generación del save cargado, en
  vez de mostrar la prosa cruda con movimientos de varias generaciones mezclados.
- Panel central de Mochila rediseñado: grilla de tiles de categoría (antes navegación de a una),
  origen Mochila/PC navegable con ◀▶ (antes toggle), tiles agrandadas a 204×108 (antes 84×84,
  heredado sin querer de `PokemonSlotView`).
- Origen PC ahora también desglosado por categoría (antes una sola tile "Objetos (PC)" con todo
  mezclado, incluyendo ítems que ni pertenecían a esa generación).
- Modal de revisión de Mochila: una tarjeta por origen (Mochila/PC) en vez de una por categoría,
  con nombres correctos en la línea de cada ítem (antes se reconstruían mal por ID para
  Gen1/2/3, mostrando nombres sin relación con el ítem editado).
- Bug real: `EditSessionService` no se reseteaba al abrir un save nuevo — ediciones pendientes
  de un save anterior quedaban pegadas y se aplicaban sobre el save recién abierto.
- Cerrar save (nuevo), Limpiar ediciones sin cerrar el save (nuevo), confirmación antes de abrir
  otro save con ediciones pendientes (nuevo) — los tres con modal de confirmación cuando
  corresponde.

**Gap de datos, no bloqueante**:
- Colosseum/XD: `ItemGameCodes` solo mapea los 122 ítems exclusivos de esos juegos, no los
  compartidos con el resto de la saga (Poké Ball, Potion, etc.) — ver
  `hotfixes/colosseum_xd_shared_items_gap.md`.
- TRs de Espada/Escudo sin `Description` cargada desde el origen (`items.json`) — nada que
  `TmDescriptionResolver` pueda resolver ahí.

**Caso pendiente, revisar antes de sacar el ejecutable**: tras editar y usar "Limpiar", las
alertas de Cerrar/Abrir-otro-save siguen disparando como si hubiera ediciones pendientes, y
"Limpiar" clickeado dos veces seguidas muestra el modal de confirmación las dos veces en vez de
avisar que no había nada que descartar. Análisis extenso por lectura de código no encontró la
causa — sospecha principal es build no limpio, sin confirmar. Recomendado: `dotnet clean` +
rebuild antes de retomar, y si persiste, ir directo a diagnóstico real (mismo método que se usó
para encontrar el bug de `RawItemId`) en vez de releer código de nuevo.

**Sin tocar esta sesión** (arrastrados de antes): tests de round-trip para Habilidad/HeldItem/
Shiny/Dynamax/Alpha/creación de Pokémon nuevo; `TID`/`SID` de entrenador no listados en
libreta/modal; límite de suma de EVs (510 en Gen3+) sin forzar; Pokédex sin script de carga ni
vista.
