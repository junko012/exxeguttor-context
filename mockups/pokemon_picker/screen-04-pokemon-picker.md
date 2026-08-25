# Pantalla 4 — Modal "Elegir Pokémon" (selector con cover flow)

> Diseñada en sesión de UI/UX separada (Claude, chat). Este documento + el boceto
> `screen-04-pokemon-picker.html` adjunto son el hand-off para la sesión de implementación.
> Ver también `CLAUDE.md` / `context.md` del proyecto para contexto general de arquitectura.

## Qué reemplaza

El modal "Elegir Pokémon" ya existente (buscador + contador de resultados + chips de
filtro por tipo en 3 filas + grilla de 5 columnas con scroll vertical) se rediseña
manteniendo la lógica de datos y filtrado, mostrando los resultados en un
**cover flow 3D** en vez de grilla, y comprimiendo la zona de filtros a una sola fila.

**Nota de alcance**: el módulo que alimenta este modal ya limita la lista a especies
disponibles/obtenibles en la generación del save cargado — por lo tanto **no** se
necesita ningún indicador de "no disponible en esta generación", todo lo que aparece
en el cover flow es siempre válido para el contexto actual.

## Layout general del modal

```
┌──────────────────────────────────────────────────────────────────┐
│ Elegir Pokémon                                    386 resultados   │  ← header
│ [Buscar por nombre o N.°...                                    ]   │
│ [Todos] [Fire] [Water] [Grass] [Electric] [Psychic] ›               │  ← filtro (1 fila, scroll horiz.)
├──────────────────────────────────────────────────────────────────┤
│  ‹  [Venonat] [Venomoth]  [DIGLETT — focalizado]  [Dugtrio] [Meowth] › │  ← cover flow
│                                                                      │
│  ┈┈┈┈┈┈┈┈┈┈┈●┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈    │  ← scrubber con densidad
│  #001                    50 / 386 · Diglett                  #386  │
├──────────────────────────────────────────────────────────────────┤
│ ← → mover · Shift+← → saltar de a 10 · Home/End extremos  [Cancelar]│  ← footer
└──────────────────────────────────────────────────────────────────┘
```

## Header

- Título "Elegir Pokémon" a la izquierda, contador de resultados a la derecha
  (`"{n} resultados"`) — **el contador refleja el total ya filtrado** por búsqueda +
  tipo, no el total absoluto de especies disponibles en la generación.
- Buscador de texto (mismo comportamiento que hoy: busca por nombre o número de
  Pokédex).
- **Selector de tipo en una sola fila** con scroll horizontal (chips tipo pastilla,
  `border-radius` grande): "Todos" + los tipos existentes. **Selección única** (no se
  combinan tipos entre sí — click en un tipo desactiva el anterior). El chip activo se
  pinta con el color de acento de la app; los inactivos quedan en `surface`/borde sutil.

### Combinación buscador + tipo

- Buscador y filtro de tipo se combinan con **AND**: si hay texto de búsqueda y un tipo
  activo, solo se muestran los resultados que matchean ambos simultáneamente.
- Son independientes entre sí: activar/cambiar el tipo **no** limpia el texto del
  buscador, y viceversa. "Todos" solo limpia el filtro de tipo.
- El set resultante de esta combinación es el que alimenta tanto el cover flow como el
  contador del header y el rango del scrubber.

## Cuerpo — Cover flow 3D

**Decisión de diseño explícita**: a diferencia del modal de exportación (pantalla 3,
carrusel plano sin rotación), acá **sí se usa cover flow con perspectiva/rotación real**
(`rotateY` + escala decreciente hacia los bordes) — el usuario lo pidió explícitamente
inspirado en referencias de cover flow clásico (iTunes / Android CoverFlow Demo). No
homologar con el estilo plano de la pantalla 3.

- **Tarjeta focalizada** (centro): la más grande, sin rotación, borde de acento.
  Contenido:
  - Badges de tipo arriba (solo una vez — **no duplicar el mismo dato dos veces en la
    tarjeta**, error presente en el diseño anterior).
  - Sprite grande, centrado.
  - Número de Pokédex (`#050`) y nombre debajo.
- **Tarjetas laterales**: escala decreciente y rotación creciente cuanto más lejos del
  centro (dos niveles, igual que se usó en el cover flow del modal de exportación antes
  de simplificarlo — acá si aplica el efecto de profundidad progresivo). Contenido
  reducido: sprite, número, nombre, y como máximo un chip de tipo (no ambos si el
  Pokémon es de doble tipo, para no sobrecargar la tarjeta chica).
- Click en cualquier tarjeta lateral → pasa a ser la focalizada. Click/confirmación
  sobre la tarjeta focalizada → selecciona ese Pokémon y cierra el modal (mismo
  resultado que hoy al hacer click sobre una card de la grilla).
- Flechas `‹` `›` en los bordes del cover flow para moverse de a un resultado.

## Navegación — teclado, mouse y scrubber

Tres formas de moverse por el set filtrado, todas deben funcionar simultáneamente:

1. **Teclado** (foco en el cover flow):
   - `←` / `→`: mover de a un resultado.
   - `Shift + ←` / `Shift + →`: saltar de a 10 resultados.
   - `Home` / `End`: saltar al primer / último resultado del set filtrado.
2. **Scroll del mouse/trackpad** sobre el cover flow: desplazamiento horizontal
   continuo, velocidad proporcional al gesto (no es "un scroll = un resultado").
3. **Scrubber horizontal** (slider) debajo del cover flow:
   - Rango dinámico `1..N` donde `N` = total del set filtrado actual (se recalcula
     cada vez que cambia buscador o tipo).
   - Slider simple, sin marcas de densidad ni preview flotante al arrastrar — esas dos
     mejoras se evaluaron en la sesión de diseño pero **no** quedaron incluidas en la
     versión final.
   - Debajo del slider: `#001` (extremo izq.) — `"{posición} / {total} · {nombre
     actual}"` (centro) — `#{N}` o número de Pokédex del extremo derecho.
- Footer: línea chica con los atajos de teclado documentados (`← → mover · Shift+← →
  saltar de a 10 · Home/End extremos`) — evaluar si hace falta mostrarla siempre o solo
  la primera vez que se abre el modal, para no repetir texto en cada apertura.

## Footer

- Línea de atajos de teclado (ver arriba) a la izquierda.
- Botón "Cancelar" a la derecha (cierra el modal sin seleccionar nada — mismo
  comportamiento que hoy).

## Datos / bindings esperados

- Reutiliza la fuente de datos y lógica de filtrado ya existente del modal actual
  (búsqueda por nombre/número, filtro por tipo, restricción a especies disponibles en
  la generación del save). Este diseño no cambia esa lógica, solo cómo se presenta y
  cómo se navega el resultado.
- Necesita, además de lo que ya usa el modal actual:
  - Índice/posición actual dentro del set filtrado (para el cover flow y el scrubber).
  - Manejo de foco de teclado sobre el contenedor del cover flow para los atajos.

## Pendiente de confirmar antes de implementar

1. **Paso del salto rápido por teclado**: se definió `Shift + flecha` = 10 resultados
   como valor inicial razonable — confirmar si ese número tiene sentido dado el volumen
   típico de resultados filtrados (con un tipo activo, el set filtrado puede ser
   bastante más chico que 386, y saltar de a 10 podría ser demasiado).
2. **Persistencia de la línea de atajos de teclado en el footer**: si conviene mostrarla
   siempre o solo la primera vez (evitar ruido visual repetido en cada apertura del
   modal).
3. **Niveles de profundidad del cover flow con muy pocos resultados** (ej. un filtro que
   deja solo 2-3 Pokémon): el diseño asume que siempre hay suficientes elementos a los
   costados; definir el comportamiento cuando el set filtrado es más chico que la
   cantidad de tarjetas visibles simultáneamente (ej. centrar y dejar espacio vacío a
   los lados, o reducir el nivel de profundidad mostrado).

## Ver también

- `screen-04-pokemon-picker.html` — boceto visual navegable (abrir en cualquier
  navegador).
- `screen-01-empty-state.md` / `.html`, `screen-02-navigation-rail.md` / `.html`,
  `screen-03-export-modal.md` / `.html` — pantallas previas del mismo flujo de hand-off.
