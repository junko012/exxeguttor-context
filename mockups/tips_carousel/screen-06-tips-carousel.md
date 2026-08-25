# Pantalla 6 — Carrusel de tips de edición

> Diseñada en sesión de UI/UX separada (Claude, chat). Este documento + el boceto
> `tips-carousel-boceto.html` adjunto son el hand-off para la sesión de implementación.
> Ver también `CLAUDE.md` / `context.md` del proyecto para contexto general de arquitectura.

## Qué es

Un modal de ayuda **bajo demanda** (no aparece automáticamente ni es un onboarding de
primer uso) que muestra tips de uso de la app en formato de tarjeta única navegable,
uno a la vez, con estilo de "carta coleccionable" en vez de una lista plana.

## Activación

- Se activa desde un **botón "?"** que se suma a la fila de acciones existente en la
  pantalla del editor (junto a notebook / checkpoint / exportar — ver
  `screen-02-navigation-rail.md`), no reemplaza ningún control existente.
- Es explícitamente **contenido de referencia bajo demanda**: el usuario lo abre
  cuando quiere, no se le fuerza a verlo.

## Layout del modal

```
┌───────────────────────────────────────┐
│ Tips de edición                    ✕   │  ← header
├───────────────────────────────────────┤
│                                         │
│  ┌───────────────────────────────┐    │
│  │ Creación            Tip 3 de 8 │    │  ← franja de categoría + contador
│  │                                 │    │
│  │         [sprite grande]         │    │
│  │      Salto rápido por teclado   │    │  ← tarjeta del tip actual
│  │   Texto explicando el tip...    │    │
│  └───────────────────────────────┘    │
│                                         │
│         ‹   ● ● ⬤ ● ● ● ● ●   ›        │  ← flechas + paginación
│                                         │
│   [General] [Creación] [Edición] [Legalidad] │  ← chips de categoría
│                                         │
└───────────────────────────────────────┘
```

## Header

- Título "Tips de edición" a la izquierda, botón de cerrar (✕) a la derecha.

## Tarjeta del tip (carrusel de a una)

- Franja superior con fondo tenue del color de acento: nombre de la categoría a la
  izquierda, contador `"Tip {n} de {total}"` a la derecha — el contador es sobre el
  **total general** de tips (no solo los de la categoría activa).
- Cuerpo de la tarjeta, centrado:
  - Sprite ilustrativo del tip (un Pokémon relacionado temáticamente cuando tenga
    sentido, o un ícono si no aplica ninguno en particular — no forzar un sprite
    random sin conexión al contenido).
  - Título corto del tip (una línea).
  - Texto explicativo (1-3 líneas), puede incluir referencias a teclas con estilo de
    código inline (ej. `Shift`).
- Borde de acento de ~1.5px en toda la tarjeta (mismo lenguaje visual que la tarjeta
  focalizada del modal de exportación y del picker de Pokémon — consistencia entre
  pantallas).

## Navegación

- Flechas `‹` `›` a los costados de la paginación, debajo de la tarjeta.
- Puntos de paginación representando el total general de tips (no por categoría) —
  el punto activo se agranda.
- **Chips de categoría** debajo de todo: click en un chip salta directo al primer tip
  de esa categoría (no filtra la lista, solo reposiciona el carrusel).

## Categorías (definidas en esta sesión de diseño)

Se definieron **4 categorías**, cada una respondiendo una pregunta distinta sobre la
app, sin superposición de contenido entre ellas:

1. **General** — administración de archivos y navegación: cómo abrir un save
   (incluye drag & drop), qué hace el checkpoint de sesión, cómo funcionan los
   recientes, cómo navegar entre secciones (rail Pokémon/Mochila), y el modal de
   exportación **tanto como concepto (qué hace, por qué existe) como en su mecánica
   de uso** (checkbox por Pokémon, paginación por legalidad, destino del archivo
   mostrado). Se decidió explícitamente **no crear una categoría "Exportación"
   separada** — todo eso vive acá.
2. **Creación** — selección/creación de Pokémon y de objetos (los modales tipo
   picker, ej. "Elegir Pokémon" con su cover flow, buscador, filtro y scrubber).
3. **Edición** — los tabs del editor de un Pokémon ya cargado (Moves, IVs/EVs,
   Ribbons, Special, Sets, etc.).
4. **Legalidad** — contenido **conceptual/educativo**: qué hace que un Pokémon sea
   válido para jugarse en un emulador o consola Nintendo real, cómo interpretar los
   resultados de `LegalityAnalysis`, por qué un campo puede marcarse como
   observación. No se mezcla con "Edición" a pesar de que la legalidad se calcula
   sobre datos editados, porque el objetivo de esta categoría es explicar el
   "por qué importa", no el "cómo se usa un campo del editor".

**Nota importante para la sesión de implementación**: esta sesión de diseño definió
la **estructura y las categorías**, pero **no el contenido final de cada tip**. La
lista completa de tips (redacción, cuáles se incluyen, cuántos por categoría) queda a
cargo de la sesión de implementación, que tiene visión completa y actualizada del
código y puede escribir tips más precisos y exhaustivos que los que se esbozaron como
ejemplo en esta sesión. Los tips usados en el boceto (`tips-carousel-boceto.html`) son
solo ilustrativos del formato, no contenido a copiar tal cual.

## Datos / bindings esperados

- Colección de tips, cada uno con: categoría (una de las 4 definidas), sprite/ícono
  opcional, título, texto, y posición dentro del total general.
- Índice actual del carrusel (para el contador y la paginación).
- Mapeo categoría → índice del primer tip de esa categoría (para el salto de los
  chips).
- Si el proyecto usa `LocalizationService` para todo el texto de la UI (como ya hace
  para el resto de la app — ver `context.md`), el contenido de los tips también
  debería vivir en los JSON de i18n en vez de hardcodeado, para mantener consistencia.

## Pendiente de confirmar antes de implementar

1. **Contenido final de los tips**: como se explicó arriba, queda a cargo de la
   sesión de implementación.
2. **Persistencia de "último tip visto"**: ¿el carrusel siempre arranca en el primer
   tip general al abrir el modal, o recuerda en qué tip/categoría se quedó la última
   vez dentro de la misma sesión de la app?
3. **Sprites por tip**: definir qué Pokémon (si alguno) ilustra cada tip conforme se
   escriba el contenido real — los sprites usados en el boceto son solo de ejemplo
   de formato.

## Ver también

- `tips-carousel-boceto.html` — boceto visual navegable (abrir en cualquier
  navegador).
- `screen-01-empty-state.md` / `.html` a `screen-05-loading-screens.md` / `.html` —
  pantallas previas del mismo flujo de hand-off.
