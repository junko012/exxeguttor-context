# Pantalla 6 — Tips de edición (stack 3D)

> Diseñada en sesión de UI/UX separada (Claude, chat). Este documento + el boceto
> `screen-06-tips-stack.html` adjunto son el hand-off para la sesión de
> implementación. Ver también `CLAUDE.md` / `context.md` del proyecto para contexto
> general de arquitectura.
>
> **Esta versión reemplaza el diseño anterior** (carrusel de una sola tarjeta con
> paginación por puntos). La estructura de datos, categorías y contenido pendiente
> siguen siendo las mismas — lo que cambió es exclusivamente la representación
> visual y la interacción de navegación, a pedido explícito de Juan tras ver el
> resultado del diseño anterior en la práctica.

## Qué es

Un modal de ayuda **bajo demanda** (no aparece automáticamente ni es un onboarding de
primer uso) que muestra tips de uso de la app en formato de **stack de tarjetas en
3D**: la tarjeta activa se ve completa arriba de todo, y las siguientes en la cola
asoman detrás/debajo, en abanico, dando sensación de profundidad — inspirado en un
mockup de referencia de una app de wallet/tarjetas que pasó Juan.

## Activación

- **Ya implementado en código** (no es solo boceto): botón nuevo llamado "Tips" en la
  fila de acciones del editor, ícono de bombilla — ver `MainWindow.axaml`
  (`ShowTipsCommand`) y `MainWindowViewModel.cs` (`IsTipsVisible`). Es el primero de
  la fila: Tips → Libreta → Guardar → Exportar → Limpiar → Cerrar (orden decidido en
  la misma sesión que agregó el botón, con el criterio de mantener la única acción
  irreversible de la fila —Limpiar— lejos de un botón recién agregado, para minimizar
  clics accidentales mientras se aprende la nueva posición).
- **Discrepancia con la versión anterior de este documento**: la primera pasada de
  este diseño hablaba de un botón "?" — quedó reemplazado en la práctica por el ícono
  de bombilla "Tips" ya mencionado. Este documento ya refleja el estado real
  implementado, no el original.
- El modal en sí (contenido de tips) **todavía no está implementado** — hoy
  `ShowTipsCommand` abre un modal placeholder con 3 tips genéricos de ejemplo. Este
  documento + el boceto son el hand-off para reemplazar ese placeholder por la
  versión real en stack 3D.
- Es explícitamente **contenido de referencia bajo demanda**: el usuario lo abre
  cuando quiere, no se le fuerza a verlo.

## Layout del modal

```
┌───────────────────────────────────────┐
│ Tips de edición                    ✕   │  ← header
├───────────────────────────────────────┤
│  ┌───────────────────────────────┐    │
│  │ Creación            Tip 3 de 8 │    │  ← tarjeta ACTIVA (adelante, borde
│  │         [sprite grande]         │    │    de acento, contenido completo)
│  │      Salto rápido por teclado   │    │
│  │   Texto explicando el tip...    │    │
│  └───────────────────────────────┘    │
│  ╱───────────────────────────────╲     │  ← 3 tarjetas siguientes, en cola,
│ ╱─────────────────────────────────╲    │    asomando en abanico detrás (sin
│╱───────────────────────────────────╲   │    contenido visible, solo silueta)
│         ‹   ● ● ⬤ ● ● ● ● ●   ›        │  ← flechas + paginación (igual que antes)
│   [General] [Creación] [Edición] [Legalidad] │  ← chips de categoría (igual que antes)
└───────────────────────────────────────┘
```

## Header

- Sin cambios respecto al diseño anterior: título "Tips de edición" a la izquierda,
  botón de cerrar (✕) a la derecha.

## Stack de tarjetas

- **Tarjeta activa** (la de adelante): igual que en el diseño anterior — franja
  superior con categoría + contador `"Tip {n} de {total}"` (sobre el total general,
  no por categoría), sprite/ícono centrado, título corto, texto explicativo (puede
  incluir `código inline` para teclas), borde de acento ~1.5-2px (mismo lenguaje
  visual que la tarjeta focalizada del modal de exportación).
- **Tarjetas detrás** (hasta 3 visibles en cola): **sin contenido legible** a
  propósito — son silueta nomás (fondo gris, sin texto), para no competir
  visualmente con la tarjeta activa. Cada una progresivamente:
  - más angosta (por eso se ve el "abanico" a los costados),
  - más alta (por eso asoma una franja abajo — todas quedan ancladas arriba, lo que
    cambia es cuánto miden, no dónde empiezan),
  - más opaca/desaturada (para reforzar la sensación de profundidad/orden).
- El contenedor del stack recorta (`overflow: hidden`) lo que excede su alto fijo —
  las tarjetas de atrás nunca se ven completas, solo la franja que corresponde a su
  posición en la cola.

## Animación de navegación

Esto es lo que motivó el cambio de diseño respecto a la primera versión: la
navegación tiene que **verse** (la tarjeta de adelante yéndose hacia atrás, la de
atrás subiendo), no ser un cambio de contenido instantáneo con la geometría
recalculada de golpe.

- Las 4 tarjetas visibles son elementos **persistentes**: cada una mantiene consigo
  qué tip representa mientras se mueve entre posiciones. Navegar = cambiarle la
  posición (0=activa … 3=más atrás) a cada una — la transición anima ese movimiento
  específico, no un swap de contenido.
- El texto de la tarjeta que se va se oculta rápido (transición corta, independiente
  de la del movimiento) para no verse deformado mientras la tarjeta cambia de
  tamaño; el texto de la que llega se revela recién cuando ya está casi asentada en
  su nueva posición.
- Recién cuando una tarjeta termina su recorrido hacia el fondo de la cola (ya
  invisible) se le asigna el próximo tip que todavía no había entrado al stack — el
  reciclado de esa tarjeta física nunca se nota.
- **Saltos largos** (chip de una categoría lejana, o click directo en una tarjeta de
  atrás) encadenan varios pasos de esa misma animación en secuencia, más rápido que
  un solo click de flecha, para no hacer esperar una eternidad cruzando varios tips
  de una — pero sigue viéndose como una sucesión de movimientos, no un teleport.

## Navegación

- Flechas `‹` `›` + puntos de paginación (sobre el total general) — **sin cambios**
  respecto al diseño anterior.
- Chips de categoría debajo de todo, salto directo al primer tip de esa categoría —
  **sin cambios**.
- **Agregado respecto al diseño anterior**: las tarjetas que asoman en la cola
  también son clickeables — tocar la franja visible de una salta directo a ese tip
  (con la misma animación encadenada que los saltos de categoría). No estaba en la
  primera versión de este documento; surgió naturalmente al hacerlas visibles/
  interactuables en el stack. **A confirmar si se quiere mantener** (ver pendientes).

## Categorías

Sin cambios respecto al diseño anterior — se mantienen las 4 categorías ya definidas:

1. **General** — archivos/navegación + el modal de exportación completo (concepto y
   mecánica). Sin categoría "Exportación" separada.
2. **Creación** — pickers de Pokémon/objetos (cover flow, buscador, scrubber).
3. **Edición** — tabs del editor de un Pokémon cargado (Moves, IVs/EVs, Ribbons,
   Special, Sets...).
4. **Legalidad** — conceptual: qué hace válido a un Pokémon, cómo leer
   `LegalityAnalysis` — deliberadamente separada de "Edición".

## Datos / bindings esperados

- Colección de tips, cada uno con: categoría (una de las 4), sprite/ícono opcional,
  título, texto, posición dentro del total general.
- Índice actual del carrusel (para contador, paginación, y para saber qué 4 tips
  corresponden a las posiciones visibles del stack en un momento dado).
- Mapeo categoría → índice del primer tip de esa categoría (para el salto de chips).
- Si el proyecto usa `LocalizationService` para todo el texto de la UI (como ya hace
  para el resto de la app), el contenido de los tips también debería vivir en los
  JSON de i18n en vez de hardcodeado.

## Pendiente de confirmar antes de implementar

1. **Contenido final de los tips**: sigue a cargo de la sesión de implementación, con
   visión completa y actualizada del código — los tips del boceto son solo
   ilustrativos del formato, no copy final.
2. **Persistencia de "último tip visto"**: ¿el stack siempre arranca en el primer tip
   general al abrir el modal, o recuerda dónde quedó dentro de la misma sesión?
3. **Sprites por tip**: se definen conforme se escriba el contenido real.
4. **Click en tarjetas de la cola** (nuevo en esta versión): confirmar si se quiere
   mantener esta interacción o si el stack de atrás debería ser solo decorativo/no
   clickeable.

## Ver también

- `screen-06-tips-stack.html` — boceto visual interactivo (abrir en cualquier
  navegador; probar flechas, chips, y click en las tarjetas de atrás).
- `screen-01-empty-state.md` / `.html` a `screen-05-loading-screens.md` / `.html` —
  pantallas previas del mismo flujo de hand-off.
