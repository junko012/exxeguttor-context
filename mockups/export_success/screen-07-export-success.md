# Pantalla 7 — Confirmación de exportación exitosa

> Diseñada en sesión de UI/UX separada (Claude, chat). Este documento + el boceto
> `export-success-boceto.html` adjunto son el hand-off para la sesión de
> implementación. Ver también `screen-03-export-modal.md`, que este mensaje
> complementa, y `screen-05-loading-screens.md` para el criterio de overlays ya
> usado en la app.

## Qué resuelve

Al confirmar la exportación (botón "Exportar" del modal de `screen-03`), hoy no hay
ninguna confirmación de que el archivo se generó correctamente. Este diseño agrega
una pantalla de confirmación con identidad visual propia, en vez de un mensaje de
texto genérico o silencio total.

## Cuándo aparece y cómo se comporta

- Aparece **después de que el modal de exportación se cierra** — es un
  overlay/pantalla independiente, no reemplaza el contenido de ese modal.
- Es un **overlay que bloquea la ventana** (mismo criterio que los loaders de
  `screen-05` — fondo oscurecido, contenido centrado).
- La animación de la escena **se reproduce una sola vez** (no en loop como los
  loaders) y **queda congelada en su estado final** al terminar.
- **Permanece visible hasta que el usuario la cierra explícitamente** — no hay
  autocierre por tiempo. Necesita un control de cierre visible (botón o ícono de X).

## La escena

Ilustración de "los datos se transfirieron correctamente" usando una cadena de tres
Pokémon/elementos con lore real, no elegidos al azar:

1. **Porygon** (Pokédex #137) — el único Pokémon canónicamente hecho de datos.
2. **Objeto Mejora / Up-Grade** — el ítem que causa la evolución de Porygon a
   Porygon2, y que viaja desde Porygon hasta la PC.
3. **Rotom PC** — una PC estilizada con teclado, con el sprite de **Rotom**
   (Pokédex #479) asomando en la pantalla (no existe un sprite oficial de Pokédex
   para "Rotom PC" en sí — es una pieza de escenario del juego sin sprite propio —
   así que se aproxima con el Rotom base).

### Secuencia (una sola pasada, línea de tiempo de referencia ~3s)

1. **0%–15%**: estado inicial — Porygon con idle sutil, objeto Mejora quieto sobre
   su cabeza, Rotom en reposo en la pantalla de la PC.
2. **15%–57%**: el objeto Mejora viaja por una **tubería en forma de herradura (∩)**
   que conecta a Porygon con la Rotom PC — sube desde arriba de la cabeza de
   Porygon, dobla en ángulo recto hacia la derecha en la parte superior, y baja
   hasta el centro de la pantalla de la Rotom PC. Esto es una referencia directa a
   la animación clásica de transferencia/intercambio de Pokémon de las primeras
   generaciones (el "tubo" del Centro de Intercambios).
   - El objeto **se encoge y desvanece al entrar en cada tramo curvo del tubo**
     (simulando que viaja "adentro"), reapareciendo a la salida de cada curva — no
     viaja flotando por encima del tubo.
   - El tubo tiene un **pulso de color de acento** que recorre el trayecto en
     sincronía con el objeto.
3. **57%–65% (momento de conexión)**: el objeto llega a destino y desaparece justo
   al hacer contacto con la pantalla; se dispara un **destello de chispa** (círculo
   con degradado radial en color warning) en el punto exacto de contacto; **Rotom
   reacciona** con un rebote de escala (crece levemente y vuelve a su tamaño).
4. **61%–80% (evolución)**: en simultáneo con la reacción de Rotom, **Porygon
   evoluciona a Porygon2** (Pokédex #233) — Porygon se desvanece con un destello
   blanco de evolución (círculo radial blanco creciendo y desapareciendo) y
   Porygon2 aparece creciendo desde una escala chica hasta su tamaño final.
5. **Estado final (congelado)**: Porygon2 junto a la Rotom PC en reposo, objeto
   Mejora ya no visible (consumido en la evolución), tubo y destello ya
   desvanecidos.

### Coordenadas de referencia del trazado de la tubería (boceto a 300×150)

Path de referencia usado en el boceto (ajustar proporcionalmente al tamaño real del
contenedor en la implementación):

```
M52,58 L52,36 Q52,18 70,18 L260,18 Q278,18 278,36 L278,58
```

- Punto de inicio `(52,58)`: con separación clara respecto a la cabeza de Porygon
  (no pegado a ella — ajustado explícitamente en la sesión de diseño tras una
  primera versión que quedaba demasiado próxima).
- Punto de llegada `(278,58)`: a la **misma altura** que el punto de inicio (forma
  simétrica de herradura, ambas "patas" de igual longitud), y centrado sobre la
  Rotom PC — también ajustado explícitamente tras versiones previas que caían sobre
  el borde/esquina de la pantalla de la PC en vez de su centro.
- El trazo grueso semitransparente (`stroke-width` mayor, color de borde) da cuerpo
  de tubería; el trazo fino superpuesto (`stroke-width` menor, color de acento) es
  el que pulsa para dar sensación de flujo.

Debajo de la escena: ícono de check verde + texto **"Save exportado"** + nombre del
archivo exportado en una línea secundaria más chica y atenuada.

## Datos / bindings esperados

- Nombre del archivo recién exportado (mismo dato que ya se muestra en el header del
  modal de exportación como "Se exportará a {archivo}").
- Trigger de la animación: dispararse una sola vez al montar la vista/overlay — no
  bindeado a ningún porcentaje de progreso (el archivo ya terminó de escribirse
  antes de mostrar esta pantalla).

## Consideraciones técnicas para Avalonia

- **Animación de una sola pasada**: todas las animaciones usan `IterationCount="1"`
  y deben dejar los elementos en su `KeyFrame` final sin revertir (comportamiento
  equivalente a `fill: forwards` de CSS / `FillMode="Forward"` en la sintaxis de
  animaciones de Avalonia).
- **La tubería** es una `Path`/`Geometry` con segmentos curvos (equivalente a los
  `Q` cuadráticos del boceto — usar `PathGeometry` con `PolyQuadraticBezierSegment`
  o similar).
- **El recorrido del objeto Mejora por la tubería**: el boceto usa
  `<animateMotion>` de SVG (sigue el path real automáticamente). Avalonia no tiene
  un equivalente directo — hay que interpolar manualmente puntos sobre la curva
  (muestrear la geometría en pasos de tiempo) y animar `TranslateTransform`
  correspondientemente, o usar una librería de animación de terceros si el proyecto
  ya cuenta con alguna. Es la parte de mayor complejidad técnica de esta pantalla.
- **Evolución de Porygon → Porygon2**: cross-fade entre dos `Image` superpuestas
  (`Opacity` de una baja mientras la otra sube) + `ScaleTransform` en la que
  aparece, más un flash blanco radial superpuesto en el momento del cruce — mismo
  patrón ya usado en el Loader 3 (huevo → sprite revelado) de `screen-05`, no es
  una técnica nueva para el proyecto.
- Los sprites (Porygon, Porygon2, Rotom, objeto Mejora) se resuelven contra los
  assets **ya embebidos en el proyecto** vía `SpriteService.Instance` (Pokémon) y el
  servicio equivalente de sprites de ítems si existe uno — no hardcodeados ni
  traídos de una fuente externa (el boceto usa una CDN externa solo para la vista
  previa).

## Pendiente de confirmar antes de implementar

1. **Texto exacto y control de cierre**: confirmar la redacción final ("Save
   exportado" es ilustrativo) y qué control visual usa para cerrarse (botón con
   label, ícono de X, o ambos).
2. **Localización**: si el texto se traduce vía `LocalizationService` con claves
   i18n nuevas, como el resto de la app.
3. **Caso de error**: este diseño cubre solo el camino feliz (exportación exitosa).
   Si la escritura del archivo falla, se necesita un mensaje de error aparte — no
   definido en esta sesión de diseño. Ver `screen-01-error-messages.md` para el
   patrón ya usado en errores de carga de save, que podría servir de referencia de
   estilo para un futuro mensaje de error de exportación.
4. **Complejidad de la animación de la tubería**: dado el costo de implementación
   señalado arriba (interpolación manual sobre la curva), evaluar si se justifica
   la fidelidad completa al boceto o si conviene una versión simplificada (ej. el
   objeto salta directo de un extremo al otro con un fade, sin recorrer la curva
   visualmente) si el tiempo de desarrollo es limitado — queda a criterio de la
   sesión de implementación, no es un requisito bloqueante del diseño.

## Ver también

- `export-success-boceto.html` — boceto animado navegable (abrir en cualquier
  navegador; la animación corre una sola vez al cargar la página y queda congelada
  en el estado final — recargar para volver a verla desde el principio).
- `screen-03-export-modal.md` / `.html` — el modal de exportación que precede a
  esta pantalla.
- `screen-05-loading-screens.md` — mismo criterio de overlay bloqueante y técnicas
  de animación (cross-fade, flash de evolución) ya usadas ahí.
