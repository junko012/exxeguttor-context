# Modal de exportación (extensión) — Mensajes de error al exportar

> Diseñada en sesión de UI/UX separada (Claude, chat). Este documento + el boceto
> `export-error-messages-boceto.html` adjunto son el hand-off para la sesión de
> implementación. Complementa `screen-03-export-modal.md` (el modal en sí) y
> `screen-07-export-success.md` (el camino feliz, Porygon/Rotom PC) — este
> documento cubre el "camino triste": qué pasa cuando la exportación falla.
> Sigue el mismo patrón visual que `screen-01-error-messages.md` (mensajes de error
> al cargar un save).

## Qué resuelve

`screen-07-export-success.md` dejaba pendiente el manejo de errores de exportación
("Ítem 9" de la casuística en `status-bar-states.md`) — no había ningún tratamiento
diseñado para cuando la escritura del archivo falla. Este documento cubre los 2
casos con mayor probabilidad de ocurrir.

## Casuística de errores de exportación

1. **Sin permisos de escritura** en la carpeta de destino.
2. **Error inesperado durante la escritura** (excepción no controlada, interrupción
   a mitad de camino — el archivo queda a medio escribir o corrupto).
3. **Sin espacio en disco** — quedó **fuera de alcance** de esta sesión de diseño
   por ser el caso menos frecuente de los tres; si se necesita, puede reusar el
   tratamiento visual del Caso 2 (Farfetch'd) o diseñarse aparte más adelante.

## Patrón común (igual al de `screen-01-error-messages.md`)

Mismo componente base: **modal centrado** con sprite animado en loop corto, título,
texto explicativo, y botón "Entendido".

```
┌─────────────────────────────────┐
│         [sprite animado]         │
│         Título corto             │
│    Texto explicativo (1-2 líneas)│
│            [Entendido]           │
└─────────────────────────────────┘
```

## Caso 1 — Sin permisos de escritura → Sudowoodo bloqueando el único paso

- **Trigger**: excepción de permisos al intentar escribir el archivo de destino
  (`UnauthorizedAccessException` o equivalente en el flujo de exportación).
- **Sprite**: Sudowoodo (Pokédex #185) — Pokémon que canónicamente se disfraza de
  árbol para **bloquear el único paso disponible** en una ruta del juego (necesitás
  la Botella de Riego para revelarlo y que se aparte). Es una referencia más precisa
  que la reutilización simple de Snorlax (ya usado para "sin permisos de *lectura*"
  en `screen-01-error-messages.md`) — acá se buscó variar el Pokémon mientras se
  mantiene la misma metáfora de "camino bloqueado".
- **Composición de la escena**: Sudowoodo centrado, flanqueado por **árboles
  tupidos a ambos lados** (4 árboles de cada lado, con degradé de tamaño y tono de
  verde — más chicos y claros en los extremos, más grandes y oscuros cerca de
  Sudowoodo) — el propósito de los árboles es dejar visualmente claro que la
  posición de Sudowoodo **es el único hueco por donde se podría pasar**, no un
  obstáculo cualquiera en un espacio abierto.
- **Animación**: temblor rígido y sutil (rotación mínima, no un movimiento
  orgánico) — refuerza que "no es lo que parece" (es una imitación de árbol, no un
  árbol real).
- **Título**: `"Sudowoodo bloquea el único paso"`.
- **Texto**: `"No tenés permiso para escribir en esta carpeta. Elegí otra ubicación
  o revisá los permisos."`
- **Footer**: solo "Entendido".

## Caso 2 — Falla durante la escritura → Farfetch'd no logra escribir

- **Trigger**: excepción no controlada durante la escritura del archivo (cae en el
  catch genérico del flujo de exportación).
- **Sprite**: Farfetch'd (Pokédex #83) — sostiene un puerro que usa como si fuera
  una lapicera, pero **no es una herramienta de escritura real**. El gag visual
  comunica "se intentó escribir y la herramienta no era la correcta / algo salió
  mal en el intento" sin necesitar texto técnico.
  - Se evaluó también **Sirfetch'd** (evolución de Galar, con un puerro más grueso
    usado como espada — el contraste "herramienta equivocada" sería aún más
    marcado) pero el asset de sprite de Sirfetch'd no está disponible en la fuente
    usada para los bocetos de esta sesión (Pokémon de Gen 8 en adelante,
    verificar disponibilidad real en los assets embebidos del proyecto antes de
    descartarlo definitivamente — si el proyecto sí cuenta con el sprite, Sirfetch'd
    es la opción preferida sobre Farfetch'd).
- **Tamaño**: el sprite de Farfetch'd debe verse **notablemente más grande que la
  hoja** sobre la que intenta escribir (proporción usada en el boceto: sprite de
  96px vs. hoja de ~36×46px) — el contraste de tamaño refuerza el chiste de "está
  totalmente sobrepasado/es la herramienta incorrecta para esta tarea en particular".
- **Animación**: movimiento de "garabatear" (rotación oscilante rápida, simulando
  el intento de escribir) que termina con el **puerro doblándose y desapareciendo**
  con un pequeño efecto de humo — nada queda escrito en la hoja, comunicando que el
  intento de escritura falló.
- **Título**: `"Farfetch'd no logró escribir el archivo"`.
- **Texto**: `"Algo interrumpió la exportación y el archivo no se guardó
  correctamente. Probá de nuevo."`
- **Footer**: solo "Entendido".

## Datos / bindings esperados

- Diferenciar en el flujo de exportación entre `UnauthorizedAccessException` (Caso
  1) y cualquier otra excepción no controlada (Caso 2), de forma similar a como ya
  se recomienda diferenciar excepciones en el flujo de apertura de save (ver
  `screen-01-error-messages.md`, sección de datos/bindings).

## Pendiente de confirmar antes de implementar

1. **Disponibilidad del sprite de Sirfetch'd** en los assets del proyecto — si
   existe, reemplaza a Farfetch'd en el Caso 2 (ver nota arriba).
2. **Redacción final de los textos** — ilustrativos, a llevar a
   `LocalizationService` con claves i18n nuevas.
3. **Caso de "sin espacio en disco"** — queda fuera de alcance, a definir si se
   necesita en una sesión futura.

## Ver también

- `export-error-messages-boceto.html` — boceto animado navegable (abrir en
  cualquier navegador).
- `screen-01-error-messages.md` / `.html` — el patrón equivalente para errores de
  carga (Ditto/MissingNo./Abra/Snorlax), mismo lenguaje visual.
- `screen-07-export-success.md` / `.html` — el camino feliz que este documento
  complementa.
- `status-bar-states.md` — casuística original donde se identificó este pendiente
  (ítem 9).
