# Diagnosticador de Legalidad — estado completo

_Documento de continuidad — pensado para retomar este módulo en otra sesión/chat sin
perder contexto. Última actualización: Etapa 3 completa y compilando, Etapa 4 (UI) sin
empezar._

---

## 1. El problema que resuelve

Los editores basados en PKHeX (el nuestro incluido, hasta este módulo) dicen *que* un
Pokémon es ilegal y en qué categoría general, pero nunca *qué* cambiar para arreglarlo —
el usuario queda con un mensaje tipo "Ubicación" o "IVs/EVs" sin ninguna pista de qué
valor poner. No se encontró ningún editor basado en PKHeX que resuelva esto — es una
funcionalidad diferenciadora real, no una réplica de algo que ya existe en otro lado.

Casos concretos que dispararon esto (mencionados por el usuario):
- La ubicación de captura, muy seguido la causa real, sin forma de saber cuál sería la
  correcta.
- "Datos internos" (IVs/EVs) sin indicación de qué valor esperado.
- Bug aparte pero relacionado: el apodo no se completaba al crear un Pokémon (nacía
  ilegal desde el vamos).
- Bug aparte pero relacionado: el combobox de ubicación mostraba todas las ubicaciones
  del juego, no las válidas para esa especie puntual.

## 2. Visión completa (v1 + v2 futura)

- **v1 (este módulo)**: mostrar los pasos para volver legal un Pokémon — categorías con
  sugerencias accionables cuando el dato existe, resaltado de campos en la UI de
  edición, recálculo en vivo mientras el usuario edita.
- **v2 (futura, fuera de alcance de esta etapa)**: un botón "Hacer legal" que aplique
  automáticamente los `FieldFix` de severidad Invalid, reusando el pipeline de
  escritura ya existente (`EditApplyService`). **Deliberadamente NO** es un motor de
  regeneración tipo `PKHeX.Core.AutoMod` (se evaluó ese repo — 8.400 líneas dedicadas a
  reconstruir el Pokémon desde una plantilla con timeout — y se descartó copiar ese
  enfoque: nuestra v2 aplica campo por campo lo que el propio diagnosticador v1 ya
  calculó, no regenera nada desde cero).

## 3. Modelo de datos (`Exxeguttor.App/Services/DiagnosticStep.cs`)

```csharp
public sealed class DiagnosticStep
{
    public required int Order { get; init; }              // orden de resolución sugerido
    public required string Category { get; init; }        // "Ubicación", "IVs/EVs", etc.
    public required Severity Severity { get; init; }       // Invalid o Fishy (nunca Valid)
    public required string Summary { get; init; }          // texto amigable de categoría
    public required string TechnicalDetail { get; init; }  // CheckResult.ToString() concatenado
    public IReadOnlyList<FieldFix> Fixes { get; init; } = [];  // 0 a N — vacío si es Nivel C
}

public sealed class FieldFix
{
    public required string FieldId { get; init; }              // "Nickname", "MetLocation", "IV_HP"...
    public required string CurrentValueDisplay { get; init; }  // lo que tiene HOY
    public required string SuggestedValueDisplay { get; init; }// sugerido, YA resuelto a texto
    public required object? SuggestedValueRaw { get; init; }   // tipado, para v2 (auto-aplicar)
    public required FieldFixSource Source { get; init; }
}

public enum FieldFixSource
{
    DirectArgument,   // Nivel A — CheckResult.Value/Argument/Argument2
    EncounterMatch,   // Nivel B — LegalityAnalysis.EncounterMatch (ILocation, IFixedIVSet)
    MoveResultExpect, // LegalityAnalysis.Info.Moves/.Relearn (MoveResult.Expect)
    DerivedFromPkm,   // calculado por nosotros, PKHeX no da nada (suma de EVs)
}
```

**Por qué esta forma**: `SuggestedValueDisplay` (texto) y `SuggestedValueRaw` (tipado)
están separados a propósito — v1 solo necesita el primero, v2 va a necesitar el
segundo, y así no hay que rediseñar el modelo cuando llegue esa v2. `FieldId` sirve
para dos cosas con el mismo string: qué control resaltar en v1, qué propiedad del PKM
escribir en v2.

## 4. Los 3 niveles de accionabilidad (+ 1 fuente extra encontrada en el camino)

| Nivel | Fuente | Ejemplo |
|---|---|---|
| **A** — Directo | `CheckResult.Value`/`.Argument`/`.Argument2` | `HyperTrainLevelGEQ_0` → nivel mínimo exacto |
| **B** — Encuentro | `LegalityAnalysis.EncounterMatch` (`ILocation`, `IFixedIVSet`) | Ubicación correcta, IVs fijas de un regalo |
| **MoveResult** | `LegalityAnalysis.Info.Moves`/`.Relearn` (array `MoveResult`, no pasa por `CheckResult`) | Slot exacto + a veces el movimiento de reemplazo (`Expect`) |
| **Derivado** | Calculado por nosotros inspeccionando el PKM — PKHeX no da nada | Suma total de EVs (510) |

De los ~487 códigos de legalidad de PKHeX, ~81 traen argumento formateable
(`IsArgument()`/`IsMove()`/`IsLanguage()`/`IsMemory()`, métodos públicos de
`LegalityCheckResultCode` en PKHeX.Core — clasificación programática, no una tabla
hardcodeada por nosotros).

## 5. Lo ya codificado (Etapas 1 a 3, compilando)

### Etapa 1 — dos bugs de raíz
- **`PokemonService.cs`**: el apodo ahora se completa al crear un Pokémon
  (`SpeciesName.GetSpeciesNameGeneration` + `IsNicknamed = false`) — antes nacía
  ilegal por "Apodo" (campo vacío = `NickLengthShort`, confirmado en
  `NicknameVerifier.cs`).
- **`PokemonEditorViewModel.cs`**: el combobox de ubicación (`AvailableMetLocations`)
  ahora filtra usando `EncounterMovesetGenerator.GenerateEncounters` (mismo generador
  que ya usaba la creación de Pokémon) en vez de mostrar `GameInfo.GetLocationList`
  completo. Fallback a la lista completa si el filtro da vacío (regalos/trades sin
  ubicación). La ubicación actual del Pokémon se sigue mostrando aunque no sea válida.

### Etapa 2 — modelo de datos
`DiagnosticStep.cs` (ver sección 3).

### Etapa 3 — el diagnosticador en sí (backend completo)

| Archivo | Rol |
|---|---|
| `PokemonDatabase.cs` | Caché en memoria para `GetSpecies`/`GetMove` (antes sin cachear) |
| `MoveDatabase.cs` (UI) | Caché propia también acá, mismo criterio que `SpeciesDatabase` |
| `LegalityArgumentFormatter.cs` | Nivel A — `CheckResult` → `FieldFix` |
| `LegalityEncounterFormatter.cs` | Nivel B — ubicación e IVs fijas vía `EncounterMatch` |
| `LegalityMoveFormatter.cs` | Movimientos — lee `Info.Moves`/`.Relearn` |
| `LegalityEvFormatter.cs` | Suma de EVs — calculada por nosotros |
| `LegalityMessageMapper.cs` | Extendido: `OrderByCategory` + `GetOrder`/`GetCategory`/`GetFriendlyText` públicos (además de lo que ya tenía: `CategoryByIdentifier`, `Summarize`) |
| `LegalityDiagnosticBuilder.cs` | **Punto de entrada único**: `BuildDiagnosticSteps(analysis, pkm) → List<DiagnosticStep>` |

**Cobertura real de Nivel A** (verificado contra la fuente de PKHeX.Core 25.11.7, no
adivinado): Hyper Training, marcas (con rango), PP de movimientos (3 códigos), toda la
franja de movimientos de Legends (maestría), toda la franja de idioma, memoria
(OT/Handler), especie en evoluciones especiales (2 códigos), marcas de cinta, conteo
de cintas, Awakened/Ganbaru stats (Legends Arceus), Pokérus, filtro de números en
apodo/entrenador.

**Confirmado como ausencia definitiva, no pendiente** (sin campo de UI, verificado con
grep en `PokemonEditorViewModel.cs`, no asumido): Contest Sheen, Form Argument, stats
de LGPE (Fullness/Enjoyment/Social), CP, Egg Met Level. Estos caen a Nivel C
(descriptivo) porque el control de UI correspondiente no existe todavía — el día que se
agregue ese campo, ahí sí vale la pena volver a `LegalityArgumentFormatter.cs` a
mapearlos.

**Diferido a propósito** (no por falta de tiempo, por riesgo de romper algo sin poder
compilar): lista completa de nombres en `RibbonsInvalid_0`/`RibbonsMissing_0` (necesita
`RibbonStrings`, un recurso de PKHeX no inicializado en este proyecto — hoy usa el
conteo nomás, que sigue siendo mejor que el mensaje genérico). `WordFilterFlaggedPattern_01`
y el resto de la franja "Compleja" sin verificar quedan en Nivel C.

### 3 bugs reales encontrados y corregidos en el camino (documentados para no repetirlos)

1. **`LegalityAnalysis.Entity` es `internal`** en PKHeX.Core — no accesible desde
   `Exxeguttor.App` (ensamblado distinto). Todos los formateadores reciben el `PKM`
   como parámetro explícito en vez de leerlo de `analysis.Entity`.
2. **Orden de stats "Speed en el índice 3"**: `PKM.GetIVs`/`GetEVs` y
   `IndividualValueSet` NO usan el orden estándar HP/Atk/Def/SpA/SpD/Spe — usan
   0=HP,1=Atk,2=Def,**3=Speed**,4=SpA,5=SpD. Afectaba a `LegalityEvFormatter.cs`
   (ya corregido) y al caso `AwakenedStatGEQ_01`/`GanbaruStatLEQ_01` en
   `LegalityArgumentFormatter.cs` (ya corregido) — con el bug original, una EV de
   Velocidad pasada de 252 hubiera señalado Ataque Especial como el campo a corregir.
   **Ojo si se toca este código de nuevo**: `LegalityEncounterFormatter.cs` evita el
   problema del todo usando propiedades con nombre (`.HP`, `.ATK`, etc.) en vez de
   índices — ese es el patrón a seguir, no volver a indexar por posición.
3. **`CheckResult` es una unión, no 3 campos independientes** (`[StructLayout(LayoutKind.Explicit)]`,
   `Value` y `Argument`/`Argument2` comparten memoria). Para códigos de un argumento,
   `Value` y `Argument` dan lo mismo. Para códigos de dos argumentos empaquetados
   (sufijo `_01`), hay que leer `Argument`/`Argument2` por separado — leer `Value` ahí
   da un número empaquetado sin sentido.

---

## 6. Lo que falta codificar (Etapa 4 — UI, sin empezar)

### 6.1 — Extender la cobertura de campos de `EditSessionService.AnalyzeLegality`

**Esto es un prerequisito de arquitectura, no parte del diseño visual** — sin esto, el
recálculo en vivo no va a reflejar ediciones a Habilidad/Objeto/Ball/Ubicación/etc.

Hoy `AnalyzeLegality` (usado por el modal de revisión pre-exportación) solo aplica al
preview 6 campos: Nickname, Level, Nature, IVs, EVs, Moves+PPUps. Hay que extenderlo
para cubrir todos los campos que el diagnosticador toca: Ability, HeldItem, Ball,
MetLocation, y los demás `FieldId` que ya produce el backend (ver sección 5).

### 6.2 — Debounce + trigger en vivo

- `Set<T>` (el helper genérico de `PokemonEditorViewModel`, usado por las ~80
  propiedades editables) hoy solo actualiza el ViewModel y graba el diff en
  `_editSession` — no dispara ningún recálculo.
- Hace falta: un debounce corto (300-500ms sin más cambios) que dispare
  `LegalityDiagnosticBuilder.BuildDiagnosticSteps` contra un preview con los cambios
  pendientes aplicados (reusando/extendiendo la lógica de 6.1), **sin** el
  `Task.Delay(1500)` artificial que sí tiene sentido en `LoadLegalityAsync` (carga
  inicial) pero rompería la sensación de "instantáneo" en la edición en vivo.
- Decisión ya tomada: **automático con debounce, no un botón manual** — es justo el
  requisito explícito del usuario ("editás y esperás que se marque legal al
  instante"). Un botón de "verificar ahora" puede quedar como red de seguridad
  opcional para campos que en una primera pasada no queden cubiertos por 6.1, no como
  mecanismo principal.
- Performance ya evaluada: milisegundos, no un problema — `LegalityAnalysis` ya corre
  hoy en la carga inicial sin sentirse lento, `SpeciesDatabase`/`PokemonDatabase`
  cachean en memoria (Etapa 3.1), y el recálculo debe correr en background
  (`Task.Run`) nunca bloqueando el hilo de UI — misma lección aprendida con el bug del
  `Thread.Sleep` del splash screen.

### 6.2.1 — Nota especial: suma de EVs (y por qué IVs NO necesita esto)

**Las IVs no tienen tope de suma** en las reglas del juego — cada una es independiente,
0-31. El tope de 510 total / 252 por stat es **solo de EVs**.

El tab IVs/EVs no muestra hoy la suma total de EVs — hay que agregar un campo visible
(ej. "EVs: 462 / 510"). Diseño acordado:

- Cuando la suma supera 510, **ese mismo display de suma se pone en rojo** — no hace
  falta (ni conviene inventar) señalar una stat puntual, porque PKHeX no da esa
  información (`EffortAbove510` se dispara sin ningún argumento, confirmado en
  `EffortValueVerifier.cs`) y no hay un único "campo culpable" real. El número total ES
  el campo a mirar acá, vuelve a normal solo cuando el usuario baja alguna EV lo
  suficiente.
- Para el tope de 252 por stat individual, `LegalityEvFormatter.cs` **sí** da el
  `FieldId` puntual (`EV_HP`..`EV_SPE`) — ese caso sí resalta la stat específica en rojo,
  normal.
- El backend (`LegalityEvFormatter.BuildEvFixes`) ya está listo para ambos casos —
  falta únicamente la parte visual: agregar el campo de suma al tab, y conectar el
  resaltado rojo/normal de ese nuevo campo al mismo ciclo de recálculo en vivo de 6.2.

### 6.3 — El indicador compacto (debajo del sprite/badge)

Reemplaza el `LegalityIssueTags` actual (hoy: un string plano tipo "Movimientos,
Nivel") por **fichas individuales** — una por categoría con problema:

- **Solo categorías `Invalid`** — lo `Fishy` (ej. IVs "todas iguales", ya es legal
  aunque raro) NO va como ficha, solo vive en el tab Diagnóstico. Mostrarlo acá mandaría
  la señal equivocada de "esto también bloquea".
- Fichas en fila/wrap, texto rojo, tooltip con el resumen completo — mismo tinte que
  ya usa el modal de revisión (`#FBEAEA`/`#C62828`, confirmado en
  `DamageClassConverters.cs`/`LegalityColorConverter`).
- **Reaccionan al campo editado, nunca al revés** — el usuario edita el campo real
  (Ability, Location, el movimiento), y quand el recálculo en vivo (6.2) detecta que
  esa categoría ya no tiene ningún `FieldFix` de severidad Invalid, la ficha
  correspondiente desaparece sola.
- Al desaparecer: pulso de escala (reusa `Border.notebook-icon.pulse` de
  `MainWindow.axaml`, 1→1.3→1 en 0.45s) antes de esconderse — mismo "flasheo" que ya
  usa la libreta de cambios pendientes al guardar.
- Cuando no queda ninguna ficha, el badge de arriba (✗ Ilegal, rojo) pasa solo a
  (✓ Legal, verde) — sin ningún botón intermedio.

### 6.4 — Resaltado de campos en la UI de edición

- Cualquier control (TextBox/ComboBox/spinner) cuyo campo tenga un `FieldFix`
  pendiente se resalta: borde rojo + fondo `#FBEAEA` — mismo lenguaje que ya usa la
  app para "estado activo" (`Border.dynamax-active`/`alpha-active` en
  `PokemonStatsView.axaml`, no es un patrón nuevo).
- La sugerencia (`SuggestedValueDisplay`) va como texto chico **siempre visible**
  debajo del campo — no escondida en un tooltip, para no depender de que el usuario
  pase el mouse.
- El mismo `FieldId` que arma el backend es el que decide qué control resaltar — no
  hace falta (ni debería haber) una segunda tabla de mapeo en la UI.

### 6.5 — Campos que viven en un tab, no en la cabecera

- **Indicador a nivel tab**: un punto rojo chico en el header del tab (mismo patrón
  que el punto de la tab "Diagnóstico" en sí) cuando ese tab tiene algo pendiente
  adentro (Moves, Ribbons, Special, IVs/EVs).
- Adentro del tab, mismo resaltado de campo puntual que en 6.4 (borde rojo + hint).
- **Caso confirmado sin campo puntual todavía**: la franja de "maestría de
  movimientos" de Legends (`PlusMoveInvalid_0` y familia) no tiene ningún control en el
  tab Special hoy (confirmado con grep, no hay `Mastered`/`PlusMove`/`MoveShop`/
  `TechRecord` en ningún `.axaml`) — para esos, el `FieldId` genérico ("Moves") cae al
  punto del tab nomás, sin resaltar un control específico adentro. No es una falla,
  es la resolución correcta dado que ese control de UI todavía no existe.

### 6.6 — Tab "Diagnóstico" (Opción A confirmada, sobre Opción B "Popover")

- Nueva tab en `PokemonStatsView`, mismo patrón que Ribbons/Special (condicional,
  visible según si hay algo que mostrar).
- Lista los `DiagnosticStep` como checklist, ordenados por `Order` — cada uno con
  categoría, severidad (color/ícono), resumen, y sus `FieldFix` si tiene.
- Botón "Aplicar" por `FieldFix` — **deshabilitado a propósito en v1**, marcado como
  "v2 · próximamente" (mockup ya lo prueba así).
- Se decidió Tab por sobre Popover: más consistente con el resto de la app (mismo
  patrón que tabs condicionales ya existentes), aunque compite por espacio en la fila
  de tabs — trade-off aceptado.

### 6.7 — Mockup de referencia

Hay un mockup HTML interactivo (toggle Tab/Popover, simulación de edición en vivo con
fichas reaccionando, pulso incluido) — vive como adjunto de la sesión de diseño, **no
está guardado en ningún repo**. Si hace falta retomarlo visualmente en otra sesión, hay
que recrearlo o pedirlo de nuevo — no asumir que va a estar disponible.

---

## 7. Orden sugerido para la Etapa 4

1. **6.1 + 6.2** (extender `AnalyzeLegality` + debounce/trigger) — es la base sin la
   cual nada de lo visual funciona de verdad. Sin esto, todo lo demás se puede construir
   pero no se va a poder probar en vivo.
2. **6.3** (fichas) + **6.4** (resaltado de campo) — el corazón de la experiencia,
   ambos dependen del mismo dato (`List<DiagnosticStep>` actualizado en vivo).
3. **6.6** (tab Diagnóstico) — reusa el mismo dato, capa de detalle.
4. **6.5** (indicador a nivel tab para Moves/Ribbons/Special) — extensión del mismo
   patrón a más lugares.
5. **6.2.1** (campo de suma de EVs) — chico, independiente del resto, se puede hacer
   en cualquier momento del proceso.

## 8. Referencias técnicas rápidas (para no tener que re-consultar la fuente de PKHeX)

- `LegalityCheckResultCode.IsArgument()`/`.IsMove()`/`.IsItem()`/`.IsLanguage()`/`.IsMemory()`
  — métodos de extensión públicos en PKHeX.Core, clasificación por rango del enum.
- `IsItem()` prácticamente vacío para nuestro caso — un solo miembro
  (`BulkAssignedMegaStoneNotFound_0`), y ese pertenece al análisis de todo el save, no
  al de un Pokémon.
- `EncounterMovesetGenerator.GenerateEncounters(pkm, moves, versions)` — el generador ya
  usado para creación de Pokémon (Etapa 1) y para Nivel B (ubicación).
- `ILocation`/`IFixedIVSet` — interfaces chicas que algunas plantillas de encuentro
  implementan (con su propio `IsSpecified`/valor-0 para no asumir que el dato siempre
  está).
- `SpeciesName.GetSpeciesNameGeneration(species, language, generation)` — el helper
  correcto para nombres de especie por generación (mayúsculas Gen1-4, apóstrofo de
  Farfetch'd, etc.), no un lookup simple.
