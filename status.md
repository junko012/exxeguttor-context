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

---

## Sesión muy larga (~50 commits, mensajes de commit genéricos — reconstruida leyendo código,
## no el historial de git): Pokédex, Diagnosticador de legalidad, construcción cross-versión
## Gen3, campos huérfanos del pipeline

**Resumen**: la sesión más grande documentada hasta ahora. Dos módulos nuevos completos
(Pokédex y Diagnosticador de legalidad), una extensión grande de la construcción "intercambio
entre versiones hermanas" a Gen3, y un lote de campos que se editaban en la UI pero se perdían
en silencio al exportar, ahora corregidos. Ver `context.md` para el detalle técnico completo de
cada punto — acá solo el resumen de producto y qué quedó pendiente.

**Pokédex — implementada de punta a punta (revierte una decisión de producto anterior)**
- Una sesión previa había sacado Pokédex del enum `AppMode` a propósito ("no implementar ni
  dejar placeholder", documentado en `context.md` y en `mockups/navigation_rail`). El usuario
  confirmó explícitamente esta sesión que es un cambio de rumbo intencional: Pokédex se
  reincorpora y se implementa completa (álbum de figuritas, no un placeholder).
- Álbum con una tarjeta por especie base, posesión real según Caja/Equipo del save cargado.
  Reverso de la tarjeta con género, hábitat, flavor text del juego, y cadena evolutiva con la
  condición traducida a español.
- Disponibilidad restringida por juego (Espada/Escudo, Escarlata/Púrpura, Legends Arceus,
  Legends Z-A) — esos juegos recortan qué especies tienen datos programados.
- Efecto de sonido nuevo (primera dependencia de audio del proyecto — vía `paplay`/`aplay` de
  línea de comandos, sin librería .NET, para no sumar peso por un solo sonido de UI).
- `pokemon.db` creció de ~46 MB a ~51 MB con los datos nuevos que alimentan este módulo.
- **Decisión de producto pendiente de registrar**: el mockup de `navigation_rail` queda sin
  actualizar todavía a propósito — falta crear/retomar un mockup dedicado de Pokédex
  (`screen-pokedex-album.md` en `exxeguttor-context/mockups/`, no existe todavía).

**Diagnosticador de legalidad — módulo nuevo (tab "Diagnóstico")**
- Reemplaza la idea original de un simple resumen de legalidad por un tab con, por cada
  problema, categoría + explicación + (cuando hay un valor concreto que sugerir) un botón
  "Corregir automáticamente".
- v1 (esta sesión): listar y resaltar el campo correspondiente en la UI. v2 (a futuro, no
  arrancada): aplicar el arreglo con un click — la arquitectura ya está pensada para eso sin
  rediseñar nada.
- Tres acciones de auto-arreglo disponibles: regenerar PID (resuelve Naturaleza/Género/
  Habilidad/Brillante), variante para el bug de "Método 1" de PID en Gen3/4, y recalcular
  CatchRate en PK1.
- Recálculo en vivo mientras el usuario edita (no solo al exportar), corriendo en paralelo sin
  bloquear la UI.
- **Gap conocido, no bloqueante**: la variante "Método 1" de regenerar PID puede cambiar
  también la Naturaleza asociada, pero todavía no hay ningún aviso de esto en la UI — el
  usuario podría no notar que cambió algo más además del PID.

**Construcción cross-versión (Crear Pokémon exclusivo de versión hermana) extendida a Gen3**
- Hasta esta sesión, esto solo cubría Gen1/Gen2 (intercambio por cable link entre versiones
  hermanas, para poder crear especies exclusivas de una versión que el save no es). Ahora
  también Gen3 — Rubí/Zafiro/Esmeralda/RojoFuego/VerdeHoja.
- Caso especial encontrado y resuelto: Feebas→Milotic (evolución por Belleza) necesitó un
  tratamiento distinto a todo lo demás — es la única evolución de las que maneja esta
  funcionalidad donde el juego vuelve a verificar una condición después del hecho, y hubo que
  descubrir además el mecanismo real de cómo se correlaciona con el "Brillo" (Sheen) en el
  juego real antes de que funcionara.

**Bug real corregido: campos "huérfanos" del pipeline de escritura**
- Brillante, Huevo, Amistad, Género del Pokémon, Nombre de Entrenador Original, TID propio del
  Pokémon, y las fechas de encuentro/huevo se podían editar desde hacía tiempo en la UI
  (aparecían bien en la libreta y en el modal de revisión) pero la edición se perdía en
  silencio al exportar — nunca se había conectado al pipeline de escritura real. Mismo síntoma
  que tuvo Met Level/Ball/Ubicación en una sesión anterior. Todos corregidos esta sesión.
- De paso se separó "apodo" de "flag de apodado" (antes se forzaba a apodado sin condición al
  editar el nombre, sin forma de destildarlo — causaba apodos ilegales con texto normal).

**Otros bugs reales encontrados y corregidos**
- **`Ball` (Poké Ball con la que se atrapó) solo tiene sentido editarla desde Gen3** — en
  Gen1/Gen2 ese dato no existe en el formato de guardado del juego real. Antes se podía editar
  en Gen2 y el cambio se perdía en silencio al exportar. Se agregó también una capacidad nueva,
  `Breeding` (Gen2+, puede existir el concepto de huevo sin eclosionar — Gen1 no tiene cría).

**Pendiente para una sesión futura** (ver también `context.md` para el detalle de cada uno):
- Tests de round-trip para el Diagnosticador de legalidad y para la extensión de Gen3 en la
  construcción cross-versión — ninguno de los dos tiene cobertura de test dedicada todavía, a
  diferencia del resto del proyecto.
- Aviso en la UI cuando "Corregir automáticamente" (variante Método 1) cambia también la
  Naturaleza, no solo el PID.
- Mockup de Pokédex (`screen-pokedex-album.md`) — no existe todavía en `exxeguttor-context/mockups/`.
- El caso pendiente de alertas post-"Limpiar ediciones" (documentado en la sesión anterior)
  sigue exactamente igual — no se tocó nada de `EditSessionService` relacionado esta sesión.
- Arrastrados de antes, sin tocar esta sesión: tests de round-trip para Habilidad/HeldItem/
  Dynamax/Alpha/creación de Pokémon nuevo; `TID`/`SID` de entrenador no listados en
  libreta/modal; límite de suma de EVs (510 en Gen3+) sin forzar.

---

## Sesión de loaders temáticos, diálogos de Rotom, pantalla de éxito de exportación, e
## idioma de la UI (selector + preferencias persistentes — primera vez que existe)

**Resumen**: sesión larga trabajada en mockups+implementación de a poco (no todo de una
vez), terminó cubriendo los 4 loaders que faltaban reemplazar de la pokebola genérica, los 3
diálogos de confirmación sin tratamiento visual, una pantalla de éxito de exportación que
antes no existía en absoluto, y el arranque real de idioma de la UI (existía la
infraestructura de `LocalizationService` hace tiempo, pero nunca se había expuesto en la UI
ni conectado a un selector). Ver `context.md`, secciones "🎬 Loaders temáticos..." y "🌐
Idioma de la UI", para el detalle técnico completo de cada punto — acá el resumen de
producto y pendientes.

**Loaders temáticos — los 4 que faltaban, ya ninguno usa la pokebola genérica para esto**
- Loader 1 (abrir save): 2 bugs reales de una sesión anterior corregidos (barra de progreso
  que nunca se movía — clase de animación huérfana; tarjeta que cortaba a Hitmonlee a la
  mitad — pasó por dos vueltas de ajuste de ancho + `ClipToBounds`). Se sacó además una
  espera artificial de ~2.9s que ya no se justificaba.
- Loader 3 (crear Pokémon): sin cambios esta sesión, ya estaba de una sesión previa.
- Loader 4 (verificar/analizar legalidad): Pokédex escaneando, nuevo de punta a punta. Dos
  bugs reales encontrados y corregidos en el camino — mostraba una silueta genérica en vez
  del Pokémon real, y al exportar con varios Pokémon solo se veía el último (ráfaga de
  cambios más rápida que un frame de UI).

**3 diálogos de confirmación con Rotom** ("¿Cerrar sin exportar?", "¿Descartar ediciones?",
"¿Abrir otro save?") — todos compartían antes el mismo texto plano sin ningún elemento
visual. Rotom-Ventilador/Rotom-Lavadora, con sprites que no estaban embebidos y se
agregaron a mano (más una extensión al script de descarga de sprites para que no se
vuelvan a perder en una regeneración completa).

**Pantalla de éxito de exportación — no existía ningún feedback visual de que exportar
funcionó, antes de esta sesión.** Porygon evolucionando a Porygon2 vía el objeto Mejora,
Rotom reaccionando. Corrección real tras feedback: la primera versión del objeto viajando
por la tubería resultaba invisible casi todo el recorrido (se leyó el boceto CSS original
demasiado literal) — corregido a un recorrido visible.

**Idioma de la UI — primera vez que existe un selector real**
- Decisión de producto confirmada: los nombres de especie/movimiento/ítem siempre se
  muestran en el idioma de la UI, nunca en el idioma original del cartucho del save.
- Pivot real durante la implementación: el plan original preveía pedir reiniciar la app para
  aplicar un cambio de idioma: al implementar se encontró que ya había binding directo al
  indexador de `LocalizationService` en el menú File, lo que permitió cambio EN CALIENTE sin
  reiniciar con mucho menos costo del asumido — se armó la regla de usar ese patrón de
  binding para toda UI nueva de acá en adelante.
- Primera vez que el proyecto tiene preferencias de usuario persistentes
  (`~/.config/exxeguttor/settings.json`, mismo patrón que ya usaba `recent.json`).
- 3 lugares que hardcodeaban nombres de especie/ítem en inglés fijo, sin importar el idioma
  de la UI, corregidos.
- Módulo de Tips conectado al selector (ya no fijo en español) — pero sin contenido
  traducido todavía (solo existe el archivo en español) y sin recarga en caliente si el
  modal ya está abierto al cambiar de idioma (sí recarga bien si está cerrado).
- Se armó un documento de plan dedicado y vivo, `docs/i18n_project/i18n-plan.md` — a
  diferencia de este changelog, ESE se sigue actualizando en vivo durante la sesión, no se
  reescribe por sesión. Ahí está el detalle de lo que falta (migrar ~135 strings
  hardcodeados a `_loc[...]`, documentar paquetes lang para usuarios reales).

**Pendiente para una sesión futura** (ver `docs/i18n_project/i18n-plan.md` para el plan
completo de todo lo de idiomas, y `context.md` para el resto):
- Migrar ~135 strings hardcodeados en `.axaml` a `{Binding Loc[Clave]}` — incluye TODO lo
  que esta misma sesión agregó para los loaders/diálogos (Rotom, Pokédex, Porygon), ninguno
  quedó conectado a `_loc` todavía.
- Contenido traducido de Tips (solo existe en español) y recarga en caliente del modal si ya
  está abierto al cambiar de idioma.
- `PokemonEditorViewModel.GetPKHeXLang` quedó duplicado con la nueva
  `LocalizationService.PKHeXLanguageCode` — no se unificó esta vuelta.
- Documentar el mecanismo de paquetes lang para usuarios reales (README del repo de código).

## 2026-10-04 — Formas Fase 1 + Fase 2

**Fase 1 (editar forma de un Pokémon existente):** combo "Forma" editable en PokemonInfoView, con
casos especiales Arceus/Giratina/Ogerpon/Meowstic/Keldeo; se aplica ANTES de Ability. Validado
contra PKHeX 25.11.07 real (14 casos, 8 idiomas, formas de solo batalla excluidas).

**Fase 2 (crear con forma regional):** `RegionalFormCatalog` (57 formas Alola/Galar/Hisui/Paldea),
una tarjeta por forma en el selector de especie, solo si el juego del save la tiene.
`BuildPokemon(species, form)`, `TryEvolveForward` elige la rama de la forma pedida,
`GetLearnsets(..., formId)` filtra por forma en todos sus usos (panel de movimientos del editor incluido), solo para formas regionales (TRAMPA #30 resuelta para ellas).
Sprites nuevos en `Assets/sprites/pokemon/forms/` (+ `shiny/`).
Validación: 405 creaciones con PKHeX real, 0 formas equivocadas, 399 legales.

**Limitaciones conocidas:**
- Stunfisk de Galar y Avalugg de Hisui salen ilegales en Z-A (limitación previa de Z-A, afecta también a forma 0).
- Etiquetas de región en inglés (nombres de forma de PKHeX), no localizadas.
- Género/habilidad del fallback salen de datos por especie (sin forma).
- UI Avalonia y tests nuevos no compilados con el SDK del proyecto en la sandbox (sin NuGet); la lógica sí corrió contra PKHeX con un shim.

**Pendiente para una sesión futura:** localizar etiquetas de región; Z-A.

### Corrección posterior (misma fecha) — feedback tras compilar
- Nuevo `SpeciesFormResolver` (App): (especie, forma) → fila de `Species` con id > 10000 (p. ej. 103/1 → 10114). El editor (`GetByForm`) lee tipos, stats base, habilidades y Effectiveness de la fila de la forma; antes leía la especie base.
- Sets recomendados por clave Showdown de la forma ("Exeggutor-Alola"); sin entrada, el tab se oculta (sin respaldo a la base).
- Combo "Forma": una forma regional es identidad, no un toggle. No se ofrece en un Pokémon regional ni se ofrecen las regionales en uno base.
- Nombre distinguible ("Exeggutor de Alola" / "Alolan Exeggutor") en selector, caja/equipo, editor y mensajes (`FormNameFormatter` + claves `Form_Name_*` en i18n es/en).
- Tipos de las tarjetas del selector ahora desde pokemon.db (ya no PersonalInfo). Test cruza DB vs PKHeX en las 57 formas.
- Pendiente: evolución (Pokédex) por forma; sets para las 29 formas sin datos; copiar genus/grupos huevo a las filas de forma.

### Ampliación: todas las formas guardables (no solo regionales)
- `SpeciesFormResolver` ahora cubre también Giratina Origen, Deoxys, Rotom, Wormadam, Kyurem, formas Therian, Basculin, Meowstic/Indeedee/Basculegion/Oinkologne hembra, Toxtricity Low Key, Ogerpon, Calyrex, Urshifu, etc. (64 formas más). Por contenido: se compara tipos, habilidades y stats de la entrada de PKHeX contra las filas de forma de pokemon.db; si la forma no cambia datos (Unown, Vivillon...) queda la especie base.
- Sprites de esas 64 formas (normal + shiny) en `Assets/sprites/pokemon/forms/`.
- Al cambiar la forma en el combo del editor se actualizan al instante sprite, tipos, debilidades, stats base/radar, habilidades y, vía una copia del PKM con `ApplyForm`, objeto (Orbe Griseo, placas) y género de Meowstic, Tipo Tera de Ogerpon y movimientos que agrega la forma, p. ej. Keldeo (valores derivados, sin registrarlos como ediciones propias).
- Pendiente: formas cosméticas sin fila en la DB siguen con el sprite de la especie base (Unown, Vivillon, Alcremie...).

### Corrección: Meowstic hembra (Z-A) y combo de género
- `ApplyForm` ahora reemplaza los movimientos que dejan de ser válidos al cambiar de forma (`FixMovesAfterFormChange`, con fuentes `MoveSourceType.Encounter`; con todas las fuentes PKHeX sugería TM/tutores inexistentes en Z-A). Barrido de 5 juegos: 835 cambios de forma sin movimientos inválidos; quedan Ursaluna Bloodmoon en Escarlata/Púrpura y Pikachu (formas con gorra) en Leyendas: Arceus.
- Combo de Género: al cambiar de forma se recalcula la lista de géneros disponibles (cada forma de Meowstic tiene proporción de género fija) y el valor mostrado.

## 2026-10-05 — Loader de abrir save (Pokédex escaneando) + IVs editables en Gen3/4 (paso 1)

**Loader 1 (abrir save):** reemplaza la coreografía Hitmonlee/Voltorb/Dugtrio por la Pokédex
roja (la de legalidad) escaneando en todas direcciones — tres anillos desde la lente, rayo
giratorio 360° y dos líneas que cruzan el cuerpo — con la barra de progreso REAL debajo, la
etapa actual a la izquierda y el porcentaje a la derecha. Boceto en
`mockups/open_save_pokedex/` (aprobado). Etapas y título en `i18n` (`OpenSave_*`, es/en).
- Piso de 1 s de visibilidad (antes 650 ms solo para la patada de Hitmonlee): con saves chicos
  casi no se veía. Es un `await`, no bloquea la animación.
- Cierre sin "modal pegado": primer frame pintado antes de trabajar y, al cerrar, un paso del
  dispatcher en Render + otro en Background (se mantiene el repintado forzado que ya existía en
  `MainWindow.axaml.cs`). Es una mitigación: el bug no se pudo reproducir en la sandbox.
- Eliminado lo exclusivo del Loader 1 viejo (estilos `l1-*`, sprites, `GetHitmonleeGhostSprite`).
  Los assets de `Assets/sprites/pokemon/ghost/` quedan huérfanos (borrado opcional).
- Nota: `Box.Initialize` solo carga la caja actual, no todas.

**Incidente:** el commit `0439bc5` ("adding hotfix forms") revirtió partes del loader en
`MainWindowViewModel.cs`, `SpriteService.cs` e `i18n` (la vista nueva quedó con el código viejo
detrás). Re-aplicado con merge de 3 vías sobre `bdb34fd`, sin conflictos.

**IVs editables — diagnóstico (medido contra PKHeX 25.11.07 real):** editar IVs deja ilegal al
Pokémon cuando el encuentro liga el PID/semilla a los IVs. No es solo "encuentros especiales":
- Gen3 (Esmeralda) 118/299 y Gen4 (Platino) 122/377 — todo lo que no es huevo, incluidos los
  salvajes (PID Method 1). Gen5: 7/520 (regalos con IVs fijos). Gen6/7: regla de mínimo de IVs
  en 31. Gen8 (Espada) 332/639 (estáticos, raids, dens: semilla Xoroshiro). Gen9 (Escarlata)
  145/667 (Tera raids 106/106 entre otros). Los huevos no se rompen: sus IVs son libres.
- Dos causas por las que "Corregir automáticamente" no resolvía: (1) `ApplyAutoFix` calculaba
  sobre el PKM original del save, no sobre el editado, así que armaba el PID para los IVs viejos;
  (2) ofrecía el fix de Method 1 en cualquier generación (en Gen8 resolvió 0 de 261 casos).

**Paso 1 implementado:**
- `ApplyAutoFix` calcula sobre el Pokémon con las ediciones pendientes aplicadas
  (`EditSessionService.TryBuildEditedPkm`); vale también para PID y tasa de captura.
- `Method1Solver` (nuevo, `Exxeguttor.App/Services`): mantiene los IVs, enumera los ~4 PIDs del
  LCRNG y verifica cada uno con `LegalityAnalysis` antes de aceptarlo. Prefiere tocar lo menos
  posible (Naturaleza/Género/Habilidad intactos → Naturaleza → Género → Habilidad); el Brillante
  nunca cambia. Clave de edición nueva `PIDAbilitySlot` (en Gen3 el bit de habilidad vive en el
  IV32, setear `Ability` por id no alcanza). El preview ahora aplica también la edición de Género.
- El botón solo se ofrece para PKM de formato 3/4; en el resto, `PIDTypeMismatch` muestra una
  explicación sin botón.
- Resultados medidos (IVs aleatorios): Gen3 salvajes 54/55, estáticos 9/9; Gen4 salvajes 84/95,
  estáticos 22/22; Gen3 regalos 0/52.

**Limitaciones conocidas:**
- Gen4 salvajes: ~11/95 combinaciones de IVs no tienen ningún frame válido (`EncConditionBadRNGFrame`):
  esos IVs no existen en ese slot.
- Gen3 regalos (BACD/CXD) y Pokéwalker: sin solver todavía. Gen8/9: sin botón ni solver.
- La UI no avisa cuando el solver cambia Naturaleza/Género/Habilidad como efecto secundario.
- UI Avalonia y `PokemonEditorViewModel`/`EditSessionService` no compilados con el SDK del proyecto
  en la sandbox (sin NuGet); el algoritmo sí se probó contra PKHeX real compilado (SDK .NET 10 por
  `apt`, PKHeX 25.11.07 retargeteado a net10.0).

**Pendiente para una sesión futura:**
- Paso 2: boceto del modal solver (progreso + cancelar) para Gen3 regalos y búsqueda de semilla en
  Gen8/9. Semillas de 32 bits; microbenchmark ~7 ns/semilla en 1 hilo (2^30 ≈ 7 s, 2^32 ≈ 30 s),
  sin validar todavía contra `LegalityAnalysis` en Gen8/9.
- Gen5–7 e IVs fijos: no hay semilla; el modal solo explicaría la regla (mínimo N IVs en 31 / IVs
  fijos del evento).
- Decidir si crear como huevo eclosionado es aceptable en especies con huevo (IVs libres).
- Avisar en la UI de los campos que cambia el solver.

### Ajuste de formas: filtro por juego y Ursaluna Bloodmoon (sobre commit 50d7c52)
- `GetSelectableForms` ya no ofrece formas que la tabla del juego del Pokémon no contempla (p. ej. gorras de Pikachu en Legends: Arceus, que quedaban sin movimientos).
- Ursaluna Bloodmoon se agregó a `RegionalFormCatalog` (etiqueta "Bloodmoon", i18n `Form_Name_Bloodmoon`): tarjeta propia en el selector (solo en juegos donde existe) y ya no sale en el combo de forma, porque convertir un Ursaluna base daba "encuentro de origen no coincide".

### Formas: tablas de evoluciones por forma y datos por forma (sobre commit 50d7c52)
- Nuevo hotfix `hotfixes/fix_form_data/` (create_tables.py + load_data.py + JSON): tablas `FormEvolutionChains` (54) y `FormEvolutionConditions` (340), misma estructura que `EvolutionChains`/`EvolutionConditions` pero con ids de forma de `Species` (>10000). `EvolutionChains` no se toca.
- `Species` (formas): `EggGroup1/2` completado en 132 formas; `GenderRate` corregido en 7 (Meowstic♀, Indeedee♀, Basculegion♀, Oinkologne♀, Ursaluna Bloodmoon, Greninja BB/Ash); Height/Weight de Ursaluna Bloodmoon. `Metadata.FormDataVersion = 2026.10`.
- Código: `PokemonDatabase.GetFormEvolutionsFrom/Into` (devuelven lista vacía si la DB no tiene el hotfix) y `PokedexService.GetEvolutionFamily(species, form)`. La UI del Pokédex sigue siendo por especie: aún no muestra ramas por forma.
- Docs: `pokemon-database/docs/SCHEMA_REFERENCE.md` y `CHANGELOG.md` actualizados.
- Pendiente: genus/hábitat/flavor text por forma (sin fuente por forma), sprites de formas cosméticas, ocultar Stunfisk Galar y Avalugg Hisui en Z-A, pruebas con FluentAssertions.

## 2026-10-09 — Tab Moves (PP, tarjetas), rediseño del tab Special y corrección de ids de Mega/Z

**Resumen**: sesión larga sobre los tabs Moves y Special. Dos bugs reales de datos/legalidad
(PP de movimientos y ids de Mega Stones/Z-Crystals), un tercero de UI (combo pegado) y el
rediseño visual de ambos tabs. **Todo el código se escribió sin compilar** (sin SDK en el
sandbox): pendiente `dotnet build` y prueba manual de cada punto de "Pendiente / sin verificar".
Base de trabajo: commit `d5fad73`.

**Nota de sincronización**: el commit `2023bc9` ("adding forms gen 8", 6 oct) no estaba
documentado: tocó `PokemonService.cs`, `RegionalFormCatalog.cs`, claves de i18n es/en y el
sprite `games/w.png`.

### Bugs reales corregidos

**1. PP actual del slot conservaba el del movimiento anterior** (`EditSessionService`, `EditApplyService`)
- Síntoma: al reemplazar un movimiento en un slot ya ocupado, el diagnóstico marcaba "PP por
  encima del máximo". En slots vacíos no pasaba (PP 0).
- Causa: `MoveN`/`MoveN_PPUps` se aplicaban al PKM pero `MoveN_PP` nunca. En
  `AnalyzeLegality` el parámetro `setPP` estaba declarado y no se usaba; en `ApplyFieldsToPkm`
  no existía. Afectaba el preview Y el export. El movimiento nuevo SÍ se grababa bien.
- Fix: si un slot tiene edición de movimiento o de PP Ups se llama `pkm.HealPPIndex(slot)`
  después de setear ambos. Slots sin edición conservan su PP.

**2. Ids de Mega Stones y Z-Crystals desalineados con la DB** (`MegaStoneDatabase`, `ZCrystalDatabase`)
- Causa raíz: las tablas se escribieron con la numeración PokeAPI original de `Items.ItemId`.
  El hotfix `fix_database` (26 ago) recargó la tabla con ids de PKHeX y las tablas nunca se
  actualizaron. Resultado: el id 845 (Snorlium Z en la numeración vieja) es hoy "Sparkling
  Stone"; el 695 (Gengarite) es "Power Plant Pass". Las opciones equipaban el objeto equivocado.
- Mega Stones: remapeadas por nombre (47 entradas); `RawItemId == ItemId` en XY, ORAS, SM,
  USUM y Z-A, así que la DB y PKHeX coinciden.
- Z-Crystals: **en SM/USUM el id del cristal EQUIPADO difiere del `ItemId` de la DB**
  (`RawItemId` 807-835 vs `ItemId` 776-806; PKHeX además trae cada cristal dos veces con el
  mismo nombre: mochila 776-806 y equipado 807+). La tabla ahora usa el id crudo de PKHeX.
  Se agregaron los 6 cristales exclusivos de USUM (ids crudos 927-932: Solganium, Lunalium,
  Ultranecrozium, Mimikium, Lycanium, Kommonium). Total: 18 de tipo + 17 exclusivos.
- Nuevo campo `HeldItemRawId` (VM): lo setean solo los selectores del tab Special; el export y
  el preview de legalidad lo usan con prioridad sobre el nombre. Cualquier cambio de objeto
  desde el combo del panel central lo vuelve a 0 (ahí se sigue resolviendo por nombre).
- El filtro que oculta Mega/Z del combo general ahora aplica solo en juegos con esas
  mecánicas (`capabilities.HasMega` / `HasZMoves`) y oculta por id Y por nombre.
- Los nombres de las opciones Z salen de la lista de objetos del juego (idioma de la UI), no
  de la DB en inglés.

**3. Combo de selección rápida pegado y reselección que no hacía nada** (Mega y Z)
- Causa (preexistente): el selector era un `SelectedItem` bindeado cuyo setter se reseteaba a
  vacío él mismo; Avalonia no re-empuja un valor cambiado dentro del propio binding.
- Fix: `SelectionChanged` en code-behind (`OnMegaOptionPicked`, `OnZCrystalOptionPicked`) →
  `EquipMegaOption` / `EquipZCrystalOption` en el VM, y el combo se vacía con `Post`.
  Se eliminaron las propiedades `SelectedMegaOption` / `SelectedZCrystalOption`.

**4. El diagnóstico no se actualizaba al deshacer todas las ediciones** (`RunLegalityRecalcAsync`)
- Causa: `if (edits == null || edits.Count == 0) return;` — al revertir al estado original
  quedaba el resultado de la edición anterior. Ahora se analiza también el Pokémon sin ediciones.
  Afectaba a cualquier edición deshecha, no solo a objetos.

**5. El preview de legalidad ignoraba ediciones del tab Special**
- `AnalyzeLegality` ahora aplica también `DynamaxLevel`, `CanGigantamax`, `IsAlpha`, `IsNoble`
  y el Tera override, con el mismo mapeo que `ApplyFieldsToPkm`.

### Tab Moves — tarjetas rediseñadas
- Franja vertical + pill con el color del tipo, nombre, chip de clase de daño (Physical /
  Special / Status), fila Power / Accuracy, PP Ups como 3 puntos entre −/+ y descripción
  (hasta 2 líneas). Fondo y borde por clase de daño (decisión explícita: la clase es un dato
  adicional, los colores de fondo anteriores se mantienen).
- Barra de PP: 1 segmento por PP, 64 en total (máximo posible: PP base 40 con 3 PP Ups), 2
  filas de 32, tamaño fijo. Lleno = PP actuales, tenue = hasta el máximo del movimiento, gris =
  fuera del alcance. Color `#7D848E` (gris pizarra de la paleta de la app).
- Tamaños de fuente alineados con la escala del resto de tabs (nombre 12, etiquetas 9, etc.);
  no hay `FontFamily` propio en ningún tab, todo hereda.
- Modal de selección: se eliminó la columna ⓘ; la descripción es ahora el tooltip del nombre.
- Nuevas propiedades `MoveNMaxPP` y `MoveNPpSegments`; `PpSegment` (nuevo) y
  `CapitalizeConverter` / `PpUpPipBrushConverter` (`MoveCardConverters.cs`, nuevo).

### Tab Special — rediseño y funcionalidad
- Convención de tarjetas con tipo (Mega, Z-Moves, Tera): franja izquierda del color del tipo +
  fondo/borde suaves + pill con letra legible. `TypeTextColorConverter` (nuevo) elige letra
  oscura sobre tipos claros (Electric, Ground, Ice, Steel, Fairy) y blanca sobre el resto; se
  aplicó también a las pills de tipo de las tarjetas de Moves.
- **Dynamax**: barra de 10 segmentos + botones 0 y 10. El checkbox de Gigantamax se deshabilita
  si la especie no lo admite (`Gigantamax.CanToggle`), salvo que el Pokémon ya traiga el flag
  (para poder destildarlo).
- **Alpha/Noble**: "Es Noble" solo aparece en Legends Arceus (PA8); en Z-A solo Alpha.
- **Tera Type (SV)**: el Override es editable (combo: sin override, 18 tipos, Stellar); el Original
  queda de solo lectura. Bloqueado en Ogerpon, Terapagos y huevos (PKHeX exige un override
  fijo en esos casos). Codificación en `TeraOverrideCodec` (nuevo): sin override = 19, Stellar = 99.
  Nueva categoría "Tera Type" en el resumen de ediciones.
- **Objeto equipado desde el tab**: las Mega Stones y Z-Crystals NO están en el combo de Held
  Item del panel central (es a propósito: este tab es su único punto de entrada). Las tarjetas
  Mega y Z muestran "Equipado: …" con botón **Quitar**, avisan "Reemplazó: X" al equipar sobre
  otro objeto y avisan que Mega y Z comparten el slot de objeto.
- **Z-Crystal exclusivo**: ahora se verifica que la especie coincida y que el Pokémon conozca el
  movimiento requerido (compara por id vía `MoveDatabase.GetByName`). Antes la tarjeta decía
  "✓" y "no verificado automáticamente". Si falta el movimiento: "✗ Equipado, pero no conoce X".
  La tarjeta toma el color del tipo del movimiento.
- **Aviso en el tab Diagnóstico** (`Severity.Fishy`, sin ficha roja): Z-Crystal exclusivo sin el
  movimiento o de otra especie, Z-Crystal por tipo sin movimiento dañino de ese tipo, Mega
  Stone que no corresponde a la especie. **PKHeX no valida nada de esto** (`ItemVerifier` solo
  comprueba que el objeto se pueda llevar equipado en ese juego): el badge sigue en "Legal".

### Archivos (todos bajo `src/Exxeguttor.UI/`)
Nuevos: `ViewModels/PpSegment.cs`, `Converters/MoveCardConverters.cs`,
`Converters/TypeTextColorConverter.cs`, `Services/TeraOverrideCodec.cs`.
Modificados: `App.axaml`, `Views/PokemonStatsView.axaml`, `Views/PokemonStatsView.axaml.cs`,
`ViewModels/PokemonEditorViewModel.cs`, `Services/EditApplyService.cs`,
`Services/EditSessionService.cs`, `Services/MegaStoneDatabase.cs`, `Services/ZCrystalDatabase.cs`.

### Pendiente / sin verificar
- **Compilar y probar** (nada de esto se compiló). En Moon/USUM: equipar el cristal de un
  Snorlax, exportar y abrir el save en PKHeX (debe llevar el id 832 equipado); Solganium Z con
  Solgaleo en USUM; un cristal de tipo debe aparecer una sola vez en el combo.
- En SV: cambiar el override de un Garchomp y revisar el diagnóstico (un Pokémon traído de HOME
  exige un override distinto de "sin override"); Ogerpon debe quedar bloqueado.
- **Riesgo conocido, no verificado — idioma y export de objetos normales**: `HeldItem` guarda el
  nombre de PKHeX en el idioma de la UI, pero el export resuelve con `ItemDatabase.GetByName`
  (`Items.Name` solo en inglés). Con la UI en otro idioma un objeto normal podría no resolverse
  y perderse en silencio. Mega/Z ya no dependen de esto (`HeldItemRawId`). Probar con UI en
  español: equipar un objeto cualquiera, exportar y revisar en PKHeX.
- Posible desajuste más general: `ItemId` vs `RawItemId` por juego (en Gen 1-5 casi nunca
  coinciden, ver sección de Mochila). El export de objetos normales equipados usa `ItemId`; no se revisó.
- **Combo de Held Item del panel central**: se dejó como está a pedido. Siguen abiertos: el
  combo probablemente queda en blanco con una Mega Stone/Z-Crystal equipada, y no se verificó si
  Avalonia le empuja `null` a `HeldItem` en ese caso. Ideas descartadas por ahora: placeholder
  con el objeto equipado, entrada fija "→ tab Special", botón Deshacer del aviso "Reemplazó".
- Z-Crystals exclusivos de USUM y Mega Stones de Z-A: las de Z-A no están en la tabla de Mega.
  Mega en Z-A no está habilitado en `SaveCapabilities` (solo Alpha).
- **Tamaño** (`HeightScalar`, `WeightScalar`, `Scale` en PK8/PK9/PA8): no implementado; falta
  confirmar qué propiedades tiene cada juego (y PA9).
- Mega con habilidad y deltas de stats: requiere verificar que la DB tenga la habilidad por forma.
- La categoría "Tera Type" podría no estar en el mapeo de colores del modal de exportación.
- Sin test de round-trip para el recálculo de PP ni para el export de Mega/Z/Tera.

### Formas: sprites cosméticos y Z-A (sobre commit 50d7c52)
- 146 sprites nuevos en `pokemon/forms/` (+146 shiny), copiados de PokeAPI/sprites: Unown, Arceus/Silvally por tipo, Vivillon, Alcremie (con la decoración fresa), Furfrou, Flabébé/Floette/Florges, Deerling/Sawsbuck, Burmy, Shellos/Gastrodon, Genesect, gorras de Pikachu, Keldeo, Magearna, Zarude, Tatsugiri, Squawkabilly, Dudunsparce, Maushold, Sinistea/Polteageist/Poltchageist/Sinistcha. Total en la carpeta: 267.
- Sin sprite propio (usan el de la especie): Scatterbug/Spewpa por patrón, Mothim por manto, Koraidon/Miraidon por modo (PokeAPI no los tiene). Las formas "Large" (tótem), "Lord/Lady" y Mega no se guardan.
- Maushold: el sprite base de PokeAPI es la Familia de Cuatro y en PKHeX la forma 0 es la de Tres → `925_0.png` existe y `SpriteService` busca el archivo de forma también para la forma 0 de esa especie.
- Z-A: `RegionalFormCatalog.AvailableIn` ya no ofrece Stunfisk de Galar ni Avalugg de Hisui (PKHeX no encuentra un origen legal para ellos en Z-A). Tests añadidos.
- Portada `games/za.png` generada con `scripts/gen-game-cover-za.py`.

### Selector de creación: especies inexistentes en el juego (sobre commit 171344b)
- Bug: en un save de Z-A, crear Unown o Arceus daba un Pokémon sin movimientos y con varias alertas de ilegalidad (no existen en el juego; el selector listaba todo hasta `MaxSpeciesID`).
- `CreatableSpecies` + `Assets/uncreatable_species.json` (recurso embebido): por juego, especies ausentes de la tabla de PKHeX y sin ninguna versión legal construible, menos las del `restricted_dex_availability.json`. `SpeciesPickerViewModel.SetHiddenSpecies` se llama desde `MainWindowViewModel` al cargar el save. Ocultas: ZA 211, PLA 663, SW/SH 234, SL/VL 292, LGPE 656; gens 1–7 y BD/SP, nada.
- Siguen visibles: especies de DLC y las legales por transferencia (Sandshrew en Z-A). Pendiente: ~81 especies presentes en Z-A que `BuildPokemon` no logra legales (siguen saliendo con alertas).
- Tests: `CreatableSpeciesTests`. Cómo regenerar el JSON: `scripts/README-uncreatable-species.md`.

### Disponibilidad de especies por juego: tabla `SpeciesGameAvailability` (hotfix fix_species_availability)
- Los datos de "especies ocultas" pasaron a la db: tabla `SpeciesGameAvailability` (SpeciesId, GameId, Status, Reason), 4507 filas, solo para los juegos que recortan su Pokédex (LGPE, SW/SH, PLA, SV, Z-A). Status: `native`, `present_illegal`, `transfer_only`, `dlc`, `uncreatable` (el selector oculta solo `uncreatable`). `Metadata.SpeciesAvailabilityVersion = 2026.10`.
- Código: `PokemonDatabase.GetUncreatableSpecies(gameId)`, `GameVersionMappings.TryGetGameId`, `CreatableSpecies.HiddenIn` lee de la DB y usa `uncreatable_species.json` como respaldo (db sin hotfix). Cuando se valide en la app el JSON se puede retirar.
- Pendiente: las 81 `present_illegal` de Z-A (37 en PLA) son especies que existen pero el constructor no deja legales.
