# Pantalla 1 (extensión) — Mensajes de error temáticos al cargar un save

> Diseñada en sesión de UI/UX separada (Claude, chat). Este documento + el boceto
> `error-messages-boceto.html` adjunto son el hand-off para la sesión de
> implementación. Extiende `screen-01-empty-state.md` — mismo `EmptyStateView`, agrega
> el tratamiento visual de 4 casos de error que hoy solo muestran texto plano en
> `StatusMessage` (barra de estado inferior).

## ⚠️ Nota importante — conflicto con `screen-01-empty-state.md`

El `.md` de contexto recibido para esta tarea (`casos-mensajes-empty-state.md`,
aportado por el usuario desde la sesión de implementación) aclara que **Avalonia
11.x no soporta destino XDND en el backend de X11**, por lo tanto **el drag & drop no
es viable** en la versión de Avalonia que usa el proyecto (se implementa recién en
Avalonia 12.1). El diseño original de `screen-01-empty-state.md` (pantalla 1 del
hand-off) sí incluye drag & drop como interacción central de la zona de acción.

**Esto no se resolvió en la sesión de diseño actual** — queda como una
inconsistencia conocida entre el hand-off de la pantalla 1 y esta actualización.
Recomendación: la sesión de implementación debería tratar `screen-01-empty-state.md`
como desactualizado en la parte de drag & drop specíficamente (texto "Arrastra tu
save aquí", el estado de zona de drop, y el feedback visual al arrastrar) y usar solo
el botón "Abrir save..." + el panel de Recientes como interacciones reales. El resto
del diseño de esa pantalla (recientes con portada por juego, ancho del panel, etc.)
no se ve afectado por esta limitación y sigue vigente.

## Alcance de este documento

Cubre **4 de los 5 casos** listados en `casos-mensajes-empty-state.md`. El caso 5
(panel de Recientes vacío) es un estado persistente, no un error puntual, y se
decidió tratarlo por separado en otra sesión de diseño — no está incluido acá.

## Patrón común a los 4 casos

Los 4 casos comparten la misma estructura de componente — un **modal centrado**
(mismo lenguaje visual que el resto de los modales ya diseñados: borde, radio de
esquina, header/body/footer), no un simple texto en la barra de estado:

```
┌─────────────────────────────────┐
│                                   │
│         [sprite animado]         │
│                                   │
│         Título corto             │
│    Texto explicativo (1-2        │
│    líneas, en lenguaje simple)   │
│                                   │
│   [Acción secundaria]  [Entendido]│  ← footer, acción secundaria opcional
└─────────────────────────────────┘
```

- **Sprite animado** en loop corto y sutil (no una escena coreografiada como los
  loaders de `screen-05`) — el gesto comunica el tipo de error por sí mismo antes de
  leer el texto.
- **Título corto** (una línea) + **texto explicativo** en 1-2 líneas, sin jerga
  técnica (nunca mostrar el mensaje crudo de una excepción de PKHeX.Core).
  Directamente **reemplaza** el uso actual de `StatusMessage` para estos 4 casos
  específicos — el texto ya no va (solo) a la barra de estado inferior.
  específicos.
- **Botón "Entendido"** siempre presente, cierra el modal y devuelve el foco a la
  pantalla de carga sin más efecto — excepto en el Caso 3, que suma una acción
  secundaria (ver abajo).
- Todos los sprites deben resolverse contra los assets **ya embebidos en el proyecto**
  (`SpriteService.Instance.GetPokemonSprite(...)`), no hardcodeados ni traídos de una
  fuente externa — ver nota sobre el Caso 2 más abajo, que es la única excepción
  posible.

## Caso 1 — Archivo no es un save válido → Ditto

- **Trigger**: `SaveUtil.GetSaveFile()` devuelve `null`.
- **Reemplaza**: clave i18n `Error_InvalidSave`.
- **Sprite**: Ditto (Pokédex #132).
- **Animación**: "wobble" de intento de transformación fallida — se deforma
  levemente (escala X/Y alternada + rotación leve) en loop, sin llegar a asentarse en
  una forma estable. Comunica "estoy tratando de copiar/reconocer esto, y no puedo".
- **Título**: `"Ditto no reconoce esta forma"` (ilustrativo, ajustar redacción final).
- **Texto**: `"Ese archivo no es un save de Pokémon válido. Probá con otro archivo."`
- **Footer**: solo "Entendido".

## Caso 2 — Save corrupto / el parser rompe a mitad de camino → MissingNo.

- **Trigger**: excepción no controlada de PKHeX.Core al parsear (cae en el `catch`
  genérico).
- **Reemplaza**: uso genérico de `Error_Unknown` para este caso específico — se
  recomienda una clave i18n nueva y dedicada (ej. `Error_CorruptedSave`) en vez de
  seguir usando la genérica, ya que ahora tiene tratamiento visual propio.
- **Sprite**: MissingNo. — el Pokémon-glitch nacido de un error de memoria en los
  juegos originales de Gen 1, la referencia más directa posible a "datos corruptos".
  **MissingNo. no es una especie con sprite en juegos modernos** ni en la mayoría de
  datasets de sprites estándar (no tiene entrada "oficial" post-Gen 1) — verificar si
  ya existe un asset para el Pokédex #000 en `Exxeguttor.UI.Assets.sprites`; si no
  existe, el usuario adjuntó una referencia (`missingnro.png`, el sprite glitch
  clásico) que puede embeberse como asset nuevo bajo esa misma convención de
  `SpriteService`.
- **Animación**: efecto "glitch" sobre el sprite — pequeños saltos de posición
  (unos pocos px, en pasos discretos, no interpolación suave) combinados con
  corrimiento de tono/contraste de color, en loop rápido y errático. El efecto
  funciona incluso aplicado sobre cualquier sprite si el asset de MissingNo. no
  estuviera disponible, aunque el sprite real es preferible por fidelidad.
- **Título**: `"Datos corruptos"`.
- **Texto**: `"Este archivo está dañado y no se pudo leer por completo. Probá con
  una copia de respaldo."`
- **Footer**: solo "Entendido".

## Caso 3 — Archivo no encontrado → Abra

- **Trigger**: `FileNotFoundException` al intentar leer la ruta — principalmente al
  hacer click en una fila de "Recientes" cuyo archivo original ya no existe.
- **Reemplaza**: clave i18n `Error_FileNotFound`.
- **Sprite**: Abra (Pokédex #63) — conocido por teletransportarse fuera de escena
  antes de que se pueda hacer algo con él ("¡Abra huyó con Teletransportación!").
- **Animación**: parpadeo intermitente combinado con una leve reducción de escala,
  simulando que está a punto de desvanecerse/teletransportarse.
- **Título**: `"Abra se teletransportó"`.
- **Texto**: `"Ese archivo ya no está donde lo dejaste. Puede que se haya movido o
  borrado."`
- **Footer**: **dos botones** — "Entendido" (cierra sin más acción) y **"Quitar de
  recientes"** (cierra el modal y además elimina esa entrada de la lista de
  recientes, ya que el archivo referenciado ya no existe). Este es el único de los 4
  casos con acción secundaria, justamente porque el problema no es el archivo que se
  intentó abrir ahora, sino una entrada obsoleta de una lista persistente.

## Caso 4 — Sin permisos de lectura → Snorlax

- **Trigger**: `UnauthorizedAccessException`.
- **Reemplaza**: clave i18n `Error_PermissionDenied`.
- **Sprite**: Snorlax (Pokédex #143) — bloquea rutas enteras durmiendo atravesado
  hasta que se resuelve la situación, metáfora directa de "no podés pasar por acá".
- **Animación**: respiración sutil (escala leve, ciclo lento) — postura pasiva, no
  amenazante, transmite "bloqueo" sin urgencia agresiva.
- **Título**: `"Snorlax bloquea el paso"`.
- **Texto**: `"No tenés permiso para leer este archivo. Revisá los permisos de la
  carpeta donde está guardado."`
- **Footer**: solo "Entendido".

## Datos / bindings esperados

- Un tipo de resultado/enum que distinga estos 4 casos (más el genérico existente
  para cualquier otro error no cubierto) para que la vista pueda elegir sprite +
  textos + footer correspondiente — hoy el catch genérico probablemente colapsa
  varios de estos casos en un solo camino de código; puede que haga falta
  diferenciar el manejo de excepciones en `SaveFileService.OpenAsync` (o donde
  corresponda) para poder distinguir `FileNotFoundException`,
  `UnauthorizedAccessException`, "parseo devolvió null" y "excepción de parseo no
  controlada" como casos separados, en vez de un catch-all único.
- Para el Caso 3, el comando de "Quitar de recientes" necesita acceso a la colección
  de recientes (la misma que alimenta el panel de `screen-01-empty-state.md`) para
  eliminar la entrada correspondiente.

## Pendiente de confirmar antes de implementar

1. **Resolver el conflicto de drag & drop** con `screen-01-empty-state.md` (ver nota
   al principio de este documento) — no es parte de esta entrega, pero bloquea que
   el hand-off de la pantalla 1 esté completo y correcto.
2. **Disponibilidad del sprite de MissingNo.** en los assets del proyecto — si no
   existe, decidir si se agrega como asset nuevo (usando la referencia adjunta) o se
   sustituye por el efecto glitch aplicado sobre otro sprite placeholder.
3. **Redacción final de los textos** — los títulos y descripciones de este documento
   son ilustrativos, a revisar/ajustar por la sesión de implementación, e
   idealmente llevados a `LocalizationService` con claves i18n nuevas como el resto
   de la app.
4. **Manejo de excepciones diferenciado**: confirmar si el código actual ya puede
   distinguir los 4 casos o si hace falta refactor en el catch de
   `SaveFileService.OpenAsync` para separarlos (ver sección de datos/bindings
   arriba).

## Ver también

- `error-messages-boceto.html` — boceto animado navegable con los 4 casos (abrir en
  cualquier navegador).
- `screen-01-empty-state.md` / `.html` — pantalla base que este documento extiende
  (ver la nota de conflicto de drag & drop arriba).
