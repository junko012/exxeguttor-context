# Splash Screen — spec

Estado: **implementado en código** (`src/Exxeguttor.UI/Views/SplashWindow.axaml` +
`.axaml.cs`, `src/Exxeguttor.UI/ViewModels/SplashStageItem.cs`). Esta spec se escribió
retroactivamente — el mockup HTML se armó e iteró en una sesión de diseño, se pasó a
código en una sesión de código, y recién ahí se detectó que faltaba este `.md` (no se
había armado en el momento, a diferencia del resto de los hand-offs).

Mockup HTML de referencia: `splash_screen_boceto.html` (adjunto a la conversación de
diseño — no versionado en este repo, ver Nota de traza abajo).

---

## Por qué existe este rediseño

La primera implementación de este splash (antes de esta spec) usaba **una ilustración
directa de Exeggutor como fondo completo de la ventana** (`Assets/splash_bg.png`). Se
identificó como el asset de mayor riesgo de todo el proyecto — más que cualquier
discusión sobre el nombre "Exxeguttor" o la paleta de colores — porque es una
representación reconocible del personaje, no una alusión de estilo. Se eliminó el
archivo y se reemplazó por esta dirección, que no incluye ninguna ilustración, silueta
ni referencia visual directa a ningún Pokémon puntual.

---

## Concepto

"Pantalla LCD vieja, sobria" — CRT/handheld boot screen, pero pasado por el mismo
filtro de contención del resto de la app (paneles blancos, un único acento de color,
nada de efectos que rompan el orden). Nada de carcasa, D-pad ni botones tipo Game Boy
(se descartó explícitamente esa dirección por riesgo de trade dress) — solo el
**color** de pantalla LCD vieja, ya de por sí bastante genérico entre handhelds de
época.

## Ventana

- Sin decoraciones del sistema (`SystemDecorations="None"`), tamaño fijo, centrada en
  pantalla — igual que el splash de GIMP: vive en una `Window` separada de
  `MainWindow`, nunca las dos visibles a la vez.
- Tarjeta visible: **460×300**, esquinas redondeadas (**12px**, mismo radio que las
  tarjetas/paneles del resto de la app — se descartó la opción de esquinas rectas por
  desentonar con el resto del sistema visual, y también se descartó un "bisel CRT" de
  borde grueso, explorado como alternativa pero no elegido).
- La ventana real es más grande que la tarjeta (520×360) para dejarle aire transparente
  al `BoxShadow` — si el borde ocupara el 100% de la ventana, la sombra se cortaría en
  el borde en vez de "flotar".

## Paleta

Verde apagado, deliberadamente **no** el hex icónico de ninguna paleta de pantalla LCD
puntual (se evaluó y se descartó explícitamente usar los tonos exactos de cualquier
handheld conocido) — más cerca de "foto vieja destiñendo" que de una pantalla verde
saturada. Versión final, ya desaturada respecto de un primer intento más intenso:

| Token | Hex | Uso |
|---|---|---|
| Fondo | `#DBDFD0` | tarjeta, cover del wordmark, degradados de máscara del carrusel |
| Tinta | `#3C4235` | wordmark, mensaje de etapa activo |
| Tinta suave | `#5C6355` | subtítulo |
| Tinta tenue | `#7D8371` | etapas no activas, version tag |
| Acento | `#6B7A5A` | barra de escaneo únicamente |

Un solo acento de color en toda la pantalla (la barra de escaneo) — todo lo demás en
la familia tinta/fondo.

## Texturas de fondo

- **Scanlines**: líneas horizontales cada 3px, ≈5% de opacidad — textura, no efecto.
  Horneada como PNG estático (`Assets/textures/scanlines_overlay.png`) en vez de
  generarse por tiling en tiempo real, por simplicidad/confiabilidad.
- **Campo hex**: bytes aleatorios (`0F`, `A3`, `7C`, etc.) casi subliminales, referencia
  a "esto está leyendo un save file". También horneado como PNG estático
  (`Assets/textures/hexfield_overlay.png`) — no se randomiza en cada arranque real (sí
  se randomizaba en el mockup HTML; se simplificó a estático al pasar a código porque el
  valor agregado de la randomización era mínimo frente al riesgo de implementarla mal).
- Sin curvatura de pantalla ni aberración cromática — rompería la geometría recta del
  resto de la UI.

## Tipografía

- **Wordmark** ("EXXEGUTTOR"): Press Start 2P, la misma fuente ya usada en las cover
  cards de juegos. Se embebe como `.ttf` real (`Assets/fonts/PressStart2P-Regular.ttf`,
  convertido del paquete `@fontsource/press-start-2p` de npm, que redistribuye el
  archivo de Google Fonts — licencia SIL Open Font License 1.1, ver
  `Assets/fonts/PressStart2P-LICENSE.txt`), no depende de red en runtime.
- **Todo lo demás** (subtítulo, mensajes de etapa, version tag): tipografía del sistema,
  nunca pixel font — evita que la pantalla se sienta "toda disfrazada".

## Secuencia de arranque (un solo disparo, nunca en loop)

1. **Flicker de encendido** (~0.5s) — unos pocos saltos de opacidad sobre toda la
   tarjeta, simulando el encendido de una consola vieja.
2. **Reveal del wordmark** (~1.1s) — una barra de escaneo horizontal baja mientras una
   "tapa" del mismo color de fondo se encoge de arriba hacia abajo, revelando el texto
   progresivamente (no es un simple fade). Aparece recién después del flicker, nunca en
   paralelo.
3. **Subtítulo** ("EDITOR DE SAVE FILES") aparece con fade suave, junto con la
   habilitación del carrusel de etapas.
4. **Carrusel vertical de etapas** — ver sección propia abajo.
5. **Cierre** — cuando terminó de mostrarse el último mensaje del carrusel (el de
   cierre, ver abajo), la ventana se cierra y aparece `MainWindow`.

## Carrusel vertical de etapas

Mismo lenguaje visual que el cover flow horizontal del picker de especies
(`SpeciesPickerView`), aplicado en vertical y solo con texto (sin covers): el mensaje
activo queda al centro, grande y nítido; el anterior se ve más chico y tenue arriba;
todo lo demás queda fuera del viewport. Dos degradados (arriba/abajo) difuminan el
corte del recorte.

Mensajes, en orden:

1. **"Preparando entorno"** — mensaje "marco" (ver abajo), dispara apenas termina el
   reveal del wordmark.
2. "Cargando base de datos Pokémon..." — mensaje real, emitido por
   `MainWindowViewModel`.
3. "Cargando módulo identificador de savefiles Gen1-Gen9..." — ídem.
4. "Cargando editor Pokémon y Mochila/PC..." — ídem.
5. "Preparando ventana principal..." — emitido por `App.axaml.cs`, cubre el parseo del
   XAML de `MainWindow`.
6. **"Entorno completo y funcional"** — mensaje "marco" de cierre, confirma que todo
   terminó de cargar antes de que el splash desaparezca.

Los mensajes 2-5 son los pasos reales de arranque tal como ya estaban cableados en el
código (`onProgress` de `MainWindowViewModel` + el paso extra de `App.axaml.cs`) — no
son una lista inventada para el mockup, aunque su redacción exacta no se retocó al
pasar a código (podría eventualmente alinearse más con el tono breve del mockup
original, "Cargando base de datos" vs. el más descriptivo "Cargando base de datos
Pokémon..." actual — pendiente, no bloqueante).

### Mensajes "marco" (1 y 6)

Los dos extremos de la secuencia (arranque y cierre) llevan más peso que los de carga
de módulos intermedios: **negrita real** + una sombra de texto con presencia
(`text-shadow`/`DropShadowEffect`, no un `font-weight` apenas distinto — se probó esa
opción primero y no se notaba lo suficiente a este tamaño de texto). Los mensajes de
carga de módulos, en cambio, van en **peso normal**, no negrita — el contraste real lo
dan los dos extremos, no una diferencia sutil entre pesos intermedios.

### Timing

- El subtítulo se dibuja primero y se sostiene solo un momento — recién después se
  habilita el carrusel de etapas (antes pasaban las dos cosas juntas, y el primer
  mensaje competía visualmente con el propio subtítulo).
- Cada mensaje de carga real queda visible un **mínimo de 1.3s** — tiene que ser
  claramente más largo que la Transition de 0.75s del carrusel; con un valor apenas
  mayor a eso, el siguiente mensaje empieza a moverse antes de que el anterior termine
  de asentarse, y se ve todo pegoteado/artificial en vez de una sucesión de pasos
  prolijos (esto pasó en una primera pasada con valores de 700ms).
- El **último módulo real** ("Preparando ventana principal...") se sostiene un poco
  más que el resto (**1.9s**) — dan la sensación de que ahí hay algo más sustancial
  cargándose, en vez de que todos los pasos se sientan intercambiables. Esto se marca
  con un flag `extraHold` en `SetStage`, separado de `isMilestone` (que sigue siendo
  exclusivo de negrita + sombra) — un mensaje puede durar más sin llevar el peso visual
  de un mensaje "marco".
- Los dos mensajes "marco" se sostienen **1.6s**.
- Este mínimo por etapa vive **adentro del splash** (no en el orquestador de arranque)
  — ver Nota de arquitectura abajo. La carga real puede completarse a la velocidad que
  sea; la experiencia visual no depende de eso.

---

## Nota de arquitectura — sincronización (importante para no reintroducir el bug)

Esta parte tuvo dos vueltas de bug, no una — documento ambas porque las dos son formas
distintas de romper lo mismo si alguien vuelve a tocar el arranque.

**Vuelta 1 — bloquear el hilo de UI.** La primera versión de código sostenía cada etapa
con `Thread.Sleep` sobre el hilo de UI (heredado tal cual del splash viejo, que solo
hacía saltos instantáneos de texto/barra, sin animación). Eso bloquea por completo el
reloj de animación de Avalonia — con el splash rediseñado (que depende de `Transitions`
y de una secuencia `async`/`Task.Delay` interna), el resultado fue que nada se
animaba. **Corrección**: `SetStage`/`SetStatus` pasaron a solo *encolar* el mensaje en
un `Channel` (instantáneo, no bloqueante), con un consumidor `async` interno del propio
`SplashWindow` (`ConsumeStagesAsync`) decidiendo cuánto sostener cada uno vía
`await Task.Delay` — nunca `Thread.Sleep`.

**Vuelta 2 — competencia por el único hilo de UI, sin bloqueo explícito.** Sacar el
`Thread.Sleep` no alcanzó. La construcción de `MainWindowViewModel`/`MainWindow` es
código **totalmente síncrono, sin ningún `await` adentro** — mientras corre, monopoliza
el hilo de UI de punta a punta, sin importar qué prioridad de `Dispatcher` se le
asigne (esto no tiene nada que ver con prioridades: un método síncrono no se puede
"interrumpir" para dejar correr otra cosa mientras tanto, en un hilo único). Si esa
construcción arrancaba antes de que la animación de apertura del splash (flicker +
reveal del wordmark) llegara a completarse, quedaba congelada a mitad de camino hasta
que la construcción terminara — el síntoma observado fue: el splash aparece en blanco,
**la ventana principal aparece primero**, y recién después el splash "revive" y
muestra todos los mensajes de golpe, para cerrarse solo al toque. **Corrección**:
`SplashWindow` expone `IntroCompletedTask` (se resuelve cuando termina el reveal del
wordmark), y `App.axaml.cs` hace `await splash.IntroCompletedTask;` **antes** de
arrancar la construcción pesada — sincronización explícita, no prioridades del
dispatcher cruzando los dedos.

**Vuelta 3 — intentar solapar animación con trabajo real, en un solo hilo, no funciona.**
Con la vuelta 2 resuelta, apareció el mismo problema un escalón más abajo: `main.Show()`
se llamaba apenas terminaba la construcción (síncrona, rápida), sin esperar a que el
carrusel de etapas llegara a *reproducir* los mensajes ya encolados — la ventana
principal aparecía primero, y recién cuando el hilo de UI volvía a quedar libre el
splash mostraba todo de golpe. La lección de fondo: **no hay forma real de solapar una
animación con trabajo síncrono en un único hilo de UI** sin mover ese trabajo a otro
hilo (cambio de arquitectura bastante más riesgoso). **Corrección**: se abandonó el
intento de solapamiento — el splash ahora reproduce **toda** su secuencia de punta a
punta (intro + los 4 mensajes de carga real + el mensaje final) sin que nada más
compita por el hilo de UI en el medio, y recién cuando termina aparece
`MainWindow`. Esto es, de hecho, más fiel al patrón "splash primero, app después" tipo
GIMP pedido desde el arranque de esta función — los intentos de solapamiento fueron
una optimización propia, no algo pedido, y terminaron siendo la raíz de las vueltas 2
y 3.

Si en algún momento se vuelve a tocar el orquestador de arranque, tres reglas (no dos):
1. Cualquier mecanismo que bloquee el hilo de UI (Sleep, loops síncronos largos)
   rompe las animaciones del splash — encolar + esperar de forma async, nunca dormir
   el hilo.
2. Cualquier trabajo síncrono pesado (sin `await` adentro) que se dispare mientras el
   splash todavía está animando su apertura va a congelarla, sin importar la
   prioridad del `Dispatcher` — hay que esperar explícitamente (`await`) a que la
   animación de apertura termine antes de arrancarlo (`IntroCompletedTask`).
3. **No tratar de mostrar `MainWindow` mientras el carrusel de etapas todavía está
   reproduciendo mensajes** — esperar `StagesDrainedTask` antes de `main.Show()`. Si en
   el futuro se necesita de verdad que la carga real corra en paralelo con la
   animación (para que el arranque total sea más rápido, no solo prolijo), la única
   forma correcta de lograrlo es mover la construcción pesada a otro hilo real
   (`Task.Run`) — auditando antes que ningún servicio/sub-viewmodel toque tipos
   Visual/Control de Avalonia desde ese hilo, porque eso sí rompería con una
   excepción real de afinidad de hilo.

---

## Nota de traza — mockup HTML

El mockup interactivo (`.html`, con toggles para comparar redondeada/bisel CRT y
paleta sobria/LCD verde) se armó e iteró en una sesión de diseño previa, adjunto
directo a esa conversación — no quedó copiado a este repo de contexto en su momento.
Si hace falta retomarlo visualmente sin pasar por código, conviene recrearlo o pedirlo
de nuevo en la próxima sesión de diseño en vez de asumir que existe acá.
