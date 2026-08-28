# Barra de estado inferior — Íconos temáticos por estado

> Diseñada en sesión de UI/UX separada (Claude, chat). Este documento + el boceto
> `status-bar-boceto.html` adjunto son el hand-off para la sesión de implementación.
> Ver también `screen-05-loading-screens.md` (loaders) y `screen-07-export-success.md`
> (Porygon/Rotom PC), con los que esta pantalla comparte identidad visual.

## Qué reemplaza

Hoy la barra de estado inferior (`MainWindow`, franja fina debajo del contenido)
solo muestra texto plano vía `StatusMessage` (`"Ready"`, `"File loaded:
pokemon_yellow.sav"`, etc.), sin ningún ícono ni tratamiento visual. Este diseño le
suma un ícono pequeño a la izquierda del texto, cuya forma/color/animación comunica
el tipo de estado antes de leer el mensaje.

## Casuística completa de estados (análisis previo al diseño)

Se armó esta lista antes de diseñar, para no dejar estados sin cubrir:

**Carga de archivo (I/O de lectura)**
1. Reposo / sin save abierto.
2. Abriendo save (en proceso).
3. Save cargado con éxito.
4. Error al abrir — ya tiene su propio modal bloqueante (Ditto/MissingNo./Abra/Snorlax,
   ver `screen-01-error-messages.md`); la barra puede dejar un mensaje breve
   informativo después de que el usuario cierra ese modal, no es su responsabilidad
   principal comunicar el error en sí.

**Edición (estado del PKM en memoria vs. lo ya exportado)**
5. Save cargado, sin cambios pendientes ("limpio").
6. Hay cambios sin exportar (`IsDirty` — depende de que el pipeline de escritura
   descrito en `CLAUDE.md`/GAP CRÍTICO se implemente; este ícono solo tiene sentido
   una vez que exista ese flag).

**Exportación (I/O de escritura)**
7. Exportando (en proceso).
8. Exportado con éxito — ya existe la pantalla grande dedicada
   (`screen-07-export-success.md`, Porygon/Rotom PC); la barra refleja el estado
   "limpio" resultante después de cerrar esa pantalla.
9. Error al exportar — **no diseñado todavía**, pendiente de una sesión futura (ver
   nota en `screen-07-export-success.md`).

**Cierre de la app**
10. Cerrar con cambios sin exportar — se resuelve con un diálogo de confirmación
    aparte (no es responsabilidad de la barra), pero la barra debería mostrar el
    estado "sin exportar" (ítem 6) justo antes de que ese diálogo aparezca.

Este documento cubre el tratamiento visual de los ítems **1, 2, 3, 4 (mensaje
posterior), 5, 6, 7 y 8** con dos familias de íconos temáticos (ver abajo). El ítem 9
(error al exportar) queda fuera de alcance.

## Dos familias de íconos, una por tipo de operación

**Se decidió explícitamente no usar un solo ícono genérico para todo** — se separan
por el tipo de operación que representan, cada una con su propia lógica de Pokémon:

### Voltorb / Electrode — para I/O de archivo (abrir y exportar)

Ambos son, literalmente, Pokémon con forma de Pokébola — se representan con un
**ícono abstracto tipo pokébola** (no el sprite real) para poder controlar el color
según el estado, algo que un sprite de colores fijos no permite. La forma abstracta
ya evoca a estos dos Pokémon sin necesidad de mostrar el sprite en sí.

- **Tamaño uniforme: 20px** para todos los estados de esta familia (ajustado
  explícitamente en la sesión de diseño tras una primera versión con tamaños
  dispares entre Voltorb y Electrode).
- **Voltorb** (abrir save):
  1. *Reposo* (`"Ready"`): círculo con borde simple, sin relleno de color, línea
     divisoria central, "botón" central sin relleno — pokébola "apagada".
  2. *Abriendo* (`"Abriendo save..."`): mismo diseño con relleno de color de acento
     en la mitad superior, **girando** (rotación continua) mientras dura la carga.
  3. *Cargado con éxito* (`"File loaded: {archivo}"`): relleno verde, quieto.
  4. *Error al abrir* (mensaje breve posterior al cierre del modal de error, ej.
     `"No se pudo abrir el archivo"`): **parpadeo alternado rojo/blanco** (los
     colores de las dos mitades se invierten en cada paso, sin transición suave —
     `steps(1)`) — referencia directa al parpadeo real de Voltorb antes de
     autodestruirse en el juego. Es el estado con más intención de llamar la
     atención de los ocho.
- **Electrode** (exportar): mismo lenguaje visual de pokébola, con una variante que
  agrega **líneas horizontales adicionales** (el patrón de anillos que distingue a
  Electrode de Voltorb) para diferenciarlo sin cambiar el tamaño:
  5. *Exportando* (`"Exportando..."`): relleno de acento, girando **más rápido** que
     el estado "Abriendo" de Voltorb (operación de escritura completa, más pesada).
  6. *Exportado con éxito* (`"Save exportado: {archivo}"`): relleno verde, quieto.

### Rotom — para el estado de edición (dirty / limpio)

A diferencia de Voltorb/Electrode, acá **sí se usa el sprite real** de Rotom
(Pokédex #479) en vez de una forma abstracta, moduland sus filtros visuales (escala
de grises / color) para indicar el estado — Rotom ya tiene un color naranja
característico que funciona bien como señal de "atención" sin necesitar recolorearlo.

- **Sin cambios** (ítem 5 de la casuística): sprite en **escala de grises** + opacidad
  reducida (~60%) — "está ahí pero no hay nada que atender".
- **Cambios sin exportar** (ítem 6): sprite a **color completo** con un
  **resplandor ámbar pulsante** alrededor (`drop-shadow` animado, ciclo de ~1s) —
  llama la atención de forma orgánica sin badge ni ícono de alerta superpuesto.

#### ⚠️ Técnica obligatoria: recorte + zoom para no aumentar la altura de la barra

El sprite de Rotom tiene bastante margen transparente alrededor del personaje (como
la mayoría de los sprites de Pokémon). Si se escala el sprite completo a un tamaño
donde Rotom se distinga bien (~36px), **la barra de estado tendría que crecer en
altura** para contenerlo, lo cual se descartó explícitamente en la sesión de diseño.

**Solución adoptada**: un contenedor de tamaño fijo, igual a la altura actual de la
barra (~18-20px), con recorte (`ClipToBounds`/`overflow:hidden`) — el sprite se
escala más grande de lo que entra en ese contenedor (~1.3x) y se centra dentro,
recortando el margen transparente en los bordes. El resultado es que Rotom ocupa
visualmente mucho más del espacio disponible sin que la barra cambie de tamaño.

En Avalonia: un `Border`/`Panel` de tamaño fijo con `ClipToBounds="True"`,
conteniendo la `Image` con un `ScaleTransform` (~1.3) y centrada dentro — no requiere
ningún control nuevo, es una composición estándar.

## Datos / bindings esperados

- Un enum/estado que cubra los 8 casos de este documento (más el estado de error de
  exportación cuando se diseñe) para que la vista elija ícono + color + animación +
  texto correspondiente.
- El estado `IsDirty` (ítems 5/6 de Rotom) depende de que exista el flag mencionado
  en el GAP CRÍTICO de `CLAUDE.md` — **no se puede implementar el ícono de Rotom
  hasta que ese flag exista en el código**, ya que hoy no hay ningún mecanismo que
  detecte cambios sin exportar.

## Consideraciones técnicas para Avalonia

- Los íconos de Voltorb/Electrode son geometría simple (`Ellipse` + `Line` +
  `Ellipse` chico central) con `Fill`/`Stroke` bindeados al color de estado — no
  necesitan ningún asset de sprite.
- El giro continuo (`RotateTransform` animado) y el parpadeo alternado (`Animation`
  con `KeyFrame` en pasos discretos, sin interpolación) son animaciones estándar de
  Avalonia.
- El ícono de Rotom sí usa el sprite real vía `SpriteService.Instance.GetPokemonSprite(...)`,
  con `ClipToBounds` + `ScaleTransform` según la técnica descrita arriba, y filtros de
  escala de grises/opacidad para el estado "sin cambios" (Avalonia no tiene un
  filtro `grayscale` nativo tan directo como CSS — puede lograrse con un
  `ColorMatrixEffect` desaturado, o superponiendo un `Rectangle` semitransparente
  gris con `OpacityMask` del sprite si el proyecto no cuenta con el efecto de
  matriz de color).

## Pendiente de confirmar antes de implementar

1. **Texto exacto de cada mensaje** — los mensajes de este documento son ilustrativos,
   a confirmar y llevar a `LocalizationService` con claves i18n nuevas (algunas ya
   existen: `Status_Ready`, `Status_Loading`, `Status_Saving`, `Status_SaveLoaded`,
   `Status_SaveSaved` — revisar si alcanzan o hace falta agregar más específicas para
   "exportando"/"exportado" si son conceptualmente distintas de "guardando"/"guardado"
   en el código actual).
2. **Dependencia del flag `IsDirty`**: los estados de Rotom no se pueden implementar
   hasta que exista ese mecanismo — no es un bloqueante del diseño en sí, pero sí del
   orden de implementación.
3. **Mensaje breve tras error de apertura** (ítem 4): confirmar el texto exacto y si
   permanece en la barra indefinidamente o se limpia al iniciar la siguiente acción.
4. **Tamaño final de la caja de recorte de Rotom**: en el boceto se usó ~18px de caja
   con el sprite escalado a 1.3x — ajustar contra la altura real de la barra de
   estado en el AXAML actual.

## Ver también

- `status-bar-boceto.html` — boceto animado navegable con los 8 estados (abrir en
  cualquier navegador).
- `screen-01-error-messages.md` / `.html` — los mensajes modales de error de carga,
  que complementan el ítem 4 de este documento.
- `screen-07-export-success.md` / `.html` — la pantalla de éxito de exportación
  (Porygon/Rotom PC), que complementa el ítem 8.
