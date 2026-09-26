# Diálogos de confirmación — Cerrar sin exportar / Descartar ediciones

> Diseñado en sesión de UI/UX separada (Claude, chat). Este documento + el boceto
> `rotom-confirmation-dialogs-boceto.html` adjunto son el hand-off para la sesión de
> implementación. Estos dos diálogos **ya están implementados funcionalmente**
> (capturas de pantalla reales aportadas desde la sesión de implementación) — este
> documento solo agrega el tratamiento visual temático, sin tocar el texto ni la
> lógica existente.
>
> Este documento reemplaza una versión anterior con el mismo nombre de archivo que
> quedó desactualizada: esa primera versión usaba partículas abstractas (cuadrados
> de colores volando, burbujas genéricas) para representar la pérdida de cambios.
> **La versión final y confirmada usa hojas de papel reales** interactuando con cada
> forma de Rotom, más directa y legible que la abstracción anterior — ver el
> detalle completo más abajo.

## Qué reemplaza

Los dos diálogos ya funcionan y tienen buena redacción (texto exacto abajo, no
cambiar) pero hoy son genéricos: título + texto + dos botones, sin ningún elemento
visual. Se les agrega un ícono animado de Rotom a la izquierda del texto,
interactuando con hojas de papel que representan los cambios de sesión sin
exportar.

## Por qué Rotom, y por qué dos formas distintas

Ambos diálogos ocurren cuando hay cambios de sesión sin exportar — el mismo
concepto que representa Rotom en el ícono de la barra de estado inferior (ver
documento de estados de la barra de estado). Se decidió no introducir un Pokémon
nuevo para este caso, y aprovechar que Rotom tiene múltiples formas de aparato para
diferenciar visualmente cada acción sin cambiar de personaje:

- **Rotom-Ventilador** (forma "Fan", `pokemon_id` 10011) para "cerrar sin
  exportar" — los cambios se los lleva el viento.
- **Rotom-Lavadora** (forma "Wash", `pokemon_id` 10009) para "descartar
  ediciones" — los cambios se lavan de vuelta al estado original.

## Diálogo 1 — "¿Cerrar sin exportar?" → Rotom-Ventilador vuela las hojas

- **Cuándo aparece**: el usuario intenta cerrar el save (o la app) habiendo cambios
  de sesión sin exportar.
- **Texto (ya implementado, no modificar)**:
  - Título: `"¿Cerrar sin exportar?"`
  - Cuerpo: `"Hay cambios de esta sesión que todavía no exportaste — se van a
    perder si cerrás ahora."`
  - Botones: `"Cancelar"` (secundario) / `"Cerrar de todos modos"` (destructivo,
    rojo — ya implementado así).
- **Escena**: Rotom-Ventilador con bob vertical sutil, y **tres hojas de papel
  pequeñas** (rectángulos blancos con líneas finas simulando texto, no cuadrados de
  color abstractos) que salen despedidas desde el ventilador hacia la derecha,
  rotando y desvaneciéndose progresivamente — cada hoja con un tamaño y ángulo de
  salida ligeramente distinto, y con un pequeño desfase de tiempo entre ellas para
  dar sensación de ráfaga continua en vez de una sola ocurrencia. La metáfora es
  directa: las hojas (los cambios de la sesión) se pierden volando si el usuario
  cierra ahora.

## Diálogo 2 — "¿Descartar ediciones?" → Rotom-Lavadora moja las hojas

- **Cuándo aparece**: el usuario hace clic en el botón de descartar/limpiar
  ediciones (ícono de "limpiar" en la fila de acciones).
- **Texto (ya implementado, no modificar)**:
  - Título: `"¿Descartar ediciones?"`
  - Cuerpo: `"El save vuelve a como estaba al cargarlo — se pierden todos los
    cambios de esta sesión que no exportaste."`
  - Botones: `"Cancelar"` (secundario) / `"Descartar cambios"` (destructivo, rojo —
    ya implementado así).
- **Escena**: Rotom-Lavadora con bob vertical sutil, junto a **una hoja de papel**
  (con las mismas líneas simulando texto) que recibe **gotas de agua** cayendo
  desde Rotom, se empapa progresivamente (un overlay de color se hace visible sobre
  la hoja, simulando la mancha de humedad) y se **combarce/dobla levemente**, como
  papel mojado perdiendo rigidez. Tres gotas caen con distinto desfase de tiempo. La
  metáfora: las ediciones "se lavan" de vuelta al estado original, coherente con
  "el save vuelve a como estaba".

## Patrón compartido entre ambos

- Layout: ícono de Rotom (64px) a la izquierda dentro de un contenedor de escena de
  ~90×70px (donde vive también la interacción con el papel), título + texto a la
  derecha — no centrado como los mensajes de error de carga de save, estos son
  diálogos más compactos con el ícono acompañando el texto en vez de protagonizar
  arriba de él.
- Footer: dos botones alineados a la derecha, el destructivo en rojo — sin cambios
  respecto a la implementación actual.
- Ambas animaciones son loops cortos (~1.6-2s) y sutiles — son diálogos que pueden
  aparecer con frecuencia, así que se evitó cualquier tratamiento pesado que se
  sienta repetitivo al verlo seguido.

## Datos / bindings esperados

- Ninguno nuevo — estos diálogos ya están implementados y funcionando; este
  documento solo agrega el ícono, la escena de papel y su animación sobre la
  estructura existente.

## Consideraciones técnicas para Avalonia

- Los sprites de las formas de Rotom se resuelven igual que el Rotom base, vía
  `SpriteService.Instance.GetPokemonSprite(...)` — confirmar que el proyecto ya
  tenga embebidas las formas alternativas (Ventilador `10011`, Lavadora `10009`) o
  si hace falta agregarlas como asset nuevo.
- Las hojas de papel son geometría simple (`Rectangle`/`Border` blanco con un par de
  líneas finas encima) — no requieren ningún asset de imagen.
- Animaciones: traslación + rotación + fade para las hojas voladas (Diálogo 1);
  traslación vertical + fade para las gotas, y una superposición de color con fade
  progresivo + una leve rotación/escala en Y para el combado de la hoja mojada
  (Diálogo 2) — todas son animaciones estándar de Avalonia (`TranslateTransform`,
  `RotateTransform`, `ScaleTransform`, `DoubleTransition` sobre `Opacity`).

## Pendiente de confirmar antes de implementar

1. ✅ **Resuelto — disponibilidad de los sprites de forma**: NO estaban embebidos (confirmado
   revisando `src/Exxeguttor.UI/Assets/sprites/pokemon/` — solo existía el Rotom base, especie
   479). Se agregaron `10009.png`/`10011.png` en `pokemon/normal/` y `pokemon/shiny/` (no
   existen variantes `female`/`shiny-female` para ninguna de las dos — Rotom no tiene género,
   confirmado con la fuente real, HTTP 404 en esas dos rutas). También se extendió
   `scripts/download-sprites.py` con una lista `EXTRA_FORM_IDS` para que una regeneración
   completa de sprites desde cero no las vuelva a perder — antes el script solo cubría el rango
   1-1025 por diseño (dex nacional), sin ningún mecanismo para IDs de forma sueltos por encima
   de eso.
2. **Reutilización en otros diálogos similares**: si en el futuro aparecen más
   confirmaciones relacionadas a cambios sin exportar, esta misma pareja de formas
   de Rotom (y la metáfora de hojas de papel) es candidata a reusarse. Ver también
   `rotom-open-other-save-dialog.md`, que ya reusa Rotom-Ventilador para un tercer
   disparador (abrir otro save con cambios sin exportar).

## Ver también

- `rotom-confirmation-dialogs-boceto.html` — boceto animado navegable (abrir en
  cualquier navegador).
- `rotom-open-other-save-dialog.md` / `.html` — tercer disparador del mismo patrón,
  ya en español estándar con texto es/en.
- Documento de estados de la barra de estado inferior — el ícono de Rotom base para
  "cambios sin exportar" que este documento extiende con dos variantes de forma.
