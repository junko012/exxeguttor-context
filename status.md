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
