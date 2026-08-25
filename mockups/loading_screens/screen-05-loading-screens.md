# Pantalla 5 — Loaders contextuales (Pokémon-themed)

> Diseñada en sesión de UI/UX separada (Claude, chat). Este documento + el boceto
> `loaders-boceto.html` adjunto son el hand-off para la sesión de implementación.
> Ver también `CLAUDE.md` / `context.md` del proyecto para contexto general de arquitectura.

## Qué reemplaza

Hoy la app no tiene un indicador de carga unificado con identidad visual — este
diseño introduce **tres loaders distintos**, cada uno ligado a un tipo de operación
específica, en vez de un spinner genérico único para toda la app.

## Decisión de diseño: overlay modal bloqueante

Los tres loaders se muestran en un **modal centrado que bloquea toda la ventana**
(overlay oscuro de fondo) mientras dura la operación — no son toasts ni indicadores
inline dentro del área que carga. Se evaluaron alternativas no bloqueantes (toast en
una esquina, reemplazo inline del área específica) y se descartaron a favor del modal
centrado.

## ⚠️ Decisión de arquitectura importante: precarga de Pokémon + Mochila

Se evaluó explícitamente si hacía falta un loader propio para cambiar entre las
secciones **Pokémon** (cajas/equipo) y **Mochila** (objetos) del rail de navegación,
ya que ambas cargan datos de la DB propia + PKHeX y pueden tardar unos segundos.

**Se descartó agregar un loader para esa navegación.** En cambio, la recomendación es:
**precargar los datos de ambas secciones (Pokémon y Mochila) en el momento de abrir el
save** (durante el Loader 1), de modo que **cambiar entre pestañas del rail sea
instantáneo** una vez que el save terminó de cargar. La razón: cambiar de sección es
una acción que el usuario repite muchas veces por sesión, y una espera (incluso con un
loader liviano) ahí se sentiría como fricción repetida, mientras que abrir un save es
un evento puntual donde una espera breve es aceptable y donde ya tenemos un loader con
identidad (Loader 1) que puede absorber ese tiempo de carga combinado.

**Implicación técnica**: el flujo de `SaveFileService.OpenAsync` (o el punto
equivalente que dispara el Loader 1) debe resolver tanto los datos que hoy alimentan
`PokemonService.GetBox`/`GetParty` como los que alimentan la sección de Mochila, antes
de considerar la apertura del save "completa" y ocultar el loader — no debe haber una
segunda carga diferida al hacer click en la pestaña Mochila por primera vez.

## Mapeo evento → loader

| Evento disparador | Loader a mostrar | Mensaje de ejemplo |
|---|---|---|
| Abrir un archivo de save, incluyendo la precarga de Pokémon + Mochila (`SaveFileService.OpenAsync`) | **Loader 1 — Hitmonlee / Voltorb / Dugtrio** | `"Abriendo save..."` |
| Click en un Pokémon de la caja/equipo para editar (`PokemonEditorViewModel.LoadPokemon`) | **Loader 2 — Sprite + barra de EXP** | `"Cargando a {Nickname o especie}..."` |
| Confirmar una especie en el modal "Elegir Pokémon" / crear un objeto nuevo | **Loader 3 — Huevo que eclosiona** | `"Generando a {especie elegida}..."` |
| Cambiar entre las pestañas Pokémon / Mochila del rail | **Ninguno** — los datos ya están precargados desde el Loader 1, el cambio de pestaña debe ser instantáneo | — |

Son pocos puntos de carga en total, así que los mensajes personalizados por evento son
viables sin sobrecargar el código — cada uno de los flujos de arriba necesita pasar
explícitamente su propio texto de estado al mostrar el loader correspondiente.

## Loader 1 — Hitmonlee patea a Voltorb, que rueda y choca contra Dugtrio (abrir save)

Es una escena de tres Pokémon con una secuencia de causa-efecto clara, en loop
continuo mientras dura la carga real. Línea de tiempo de un ciclo completo (duración
de referencia: 2.8s, ajustable):

1. **0%–13% — Cargue de fuerza**: Hitmonlee (Pokédex #106), espejado horizontalmente
   para patear hacia la derecha, muestra 3 imágenes "fantasma" de sí mismo (mismo
   sprite con un filtro de tono azulado/oscuro) que avanzan progresivamente hacia
   adelante con opacidad decreciente hacia atrás, dando sensación de estar acumulando
   fuerza antes del golpe real — efecto inspirado en las imágenes de after-image de
   golpes especiales en juegos de pelea.
2. **14%–22% — Patada de contacto**: la pierna de Hitmonlee (el sprite real, no las
   sombras) rota hacia adelante y vuelve, marcando el golpe.
3. **22%–85% — Voltorb rueda**: justo después del contacto (no antes — es un error a
   evitar que Voltorb ya esté en movimiento durante el cargue de fuerza), Voltorb
   (Pokédex #100) se traslada linealmente desde la posición de Hitmonlee hasta la de
   Dugtrio, con un giro constante sobre sí mismo. El giro se simula con **3 copias
   superpuestas del mismo sprite** con pequeño desfase de tiempo en la rotación y
   opacidad decreciente (65%, 35%, capa base) — esto evita el problema visual de rotar
   una sola imagen plana con `RotateTransform` puro, que se ve "raro" para un sprite
   asimétrico visto de costado (a diferencia de un objeto redondo, un giro de imagen
   plana sobre su eje Z distorsiona la lectura de la silueta). Debajo del recorrido,
   una fila de puntitos con fade progresivo marca el "camino recorrido".
4. **85%–100% — Impacto y hundimiento**: al llegar, Voltorb desaparece y se dispara una
   explosión (destello radial + un ícono de estrella) en el punto de contacto, con una
   nube de polvo en el suelo. Dugtrio (Pokédex #51) reacciona rotando **180° hacia la
   derecha** mientras desciende y se desvanece — la lectura es que el impacto lo tira y
   queda hundido, coherente con su lore (vive bajo tierra).
5. El ciclo se reinicia y vuelve a empezar desde el paso 1, en loop, mientras dure la
   carga real.
- Debajo de toda la escena, la **barra de progreso real** (lineal, delgada) refleja el
  porcentaje de avance real de la apertura del save (y de la precarga de Pokémon +
  Mochila, ver sección de arquitectura arriba) si es calculable; si no, modo
  indeterminado.
- **Toda la coreografía descrita (pasos 1-4) es decorativa y corre en su propio loop
  independiente del porcentaje real** — no hay que sincronizar el momento del impacto
  con que el progreso real llegue a 100%. Esto simplifica bastante la implementación:
  la barra de abajo es la única fuente de verdad del progreso.

## Loader 2 — Sprite + barra de EXP (cargar Pokémon para editar)

- Sprite del **Pokémon específico que se está cargando** (no genérico — debe resolver
  dinámicamente la especie/forma/shiny del PKM seleccionado), con un idle sutil de
  bob vertical en loop.
- Debajo, una recreación de la **barra de experiencia clásica del juego**: fila con
  `"Nv. {N}"` a la izquierda y `"EXP"` a la derecha, y la barra en sí (fondo con
  borde, relleno de color de acento).
- El relleno de esta barra de EXP es **decorativo** (anima en loop de 0 a un valor
  fijo y vuelve, no representa el progreso de carga real) — es la ambientación
  temática, no el indicador funcional.
- Mensaje de estado arriba: `"Cargando a {Nickname si existe, si no el nombre de
  especie}..."`.

## Loader 3 — Huevo que eclosiona (crear Pokémon / objeto)

- Un huevo de Pokémon (ilustración simple: óvalo con manchas + grietas) tiembla
  levemente en loop.
- Aparecen **grietas progresivas** en el cascarón en distintos momentos del ciclo de
  animación (efecto puramente decorativo en loop, no atado a un porcentaje real de
  carga).
- Al final del ciclo, el huevo se desvanece y aparece (revela) el **sprite de la
  especie recién elegida/creada** en su lugar, con una pequeña animación de escala
  (entra "creciendo" levemente antes de asentarse).
- Mensaje de estado: `"Generando a {especie elegida}..."`.
- Debajo, la barra de progreso real de la operación de creación (si aplica).

## Consideraciones técnicas para Avalonia

- Todas las animaciones descritas (bob, rotación continua, fade de puntos, aparición
  de grietas, transición de escala, `filter` de color sobre un sprite, traslación
  lineal, rotación de 180°) son implementables con las animaciones nativas de Avalonia
  (`Animation`, `KeyFrame`, `RotateTransform`, `ScaleTransform`, `TranslateTransform`,
  `DoubleTransition` sobre `Opacity`). El efecto de tono azulado en las sombras de
  Hitmonlee puede lograrse con un `ColorMatrixEffect` o superponiendo un `Rectangle`
  semitransparente con `OpacityMask` del sprite, según lo que soporte mejor la versión
  de Avalonia usada en el proyecto.
- El sprite específico del Loader 2 y la especie del Loader 3 deben resolverse en
  tiempo real contra `SpriteService.Instance.GetPokemonSprite(...)` (mismo servicio ya
  usado en el resto de la app), no como asset fijo.
- El efecto de "3 copias superpuestas con desfase" (usado tanto en el giro de Voltorb
  como en las sombras de Hitmonlee) implica renderizar 3-4 instancias del mismo control
  de imagen simultáneamente — costo de renderizado bajo dado que son solo 1-2 loaders
  visibles a la vez y por poco tiempo, pero vale la pena tenerlo en cuenta si se
  observa jank en hardware más limitado.
- Cada loader corre su animación decorativa en loop **independientemente** de la
  barra de progreso real — no hay que sincronizar el ciclo de la animación temática
  con el porcentaje real de avance en ninguno de los tres loaders.

## Pendiente de confirmar antes de implementar

1. **Progreso real vs. indeterminado**: para cada uno de los tres flujos (abrir save +
   precarga combinada, cargar Pokémon, crear Pokémon/objeto), definir si existe un
   porcentaje real calculable (ej. bytes leídos del archivo, pasos de un pipeline de
   precarga) o si conviene mostrar directamente un modo indeterminado sin barra
   numérica.
2. **Duración mínima de aparición**: si alguna de estas operaciones es casi
   instantánea (ej. cargar un Pokémon ya en memoria), evaluar si vale la pena mostrar
   el modal igual (por consistencia) o si se omite para operaciones por debajo de
   cierto umbral de tiempo, para no generar parpadeo.
3. **Texto exacto de cada mensaje**: los mensajes de ejemplo de la tabla de arriba son
   ilustrativos — confirmar la redacción final y si se traduce vía
   `LocalizationService` con claves i18n nuevas, como correspondería dado que el resto
   de la app ya funciona así.
4. **Medición real del tiempo de precarga combinada** (Pokémon + Mochila juntos): si en
   la práctica esa precarga resulta demasiado lenta y hace que el Loader 1 se sienta
   excesivamente largo, puede ser necesario reconsiderar la decisión de precarga total
   y volver a evaluar un loader liviano para Mochila — se deja como riesgo conocido, no
   como bloqueante del diseño actual.

## Ver también

- `loaders-boceto.html` — boceto animado navegable (abrir en cualquier navegador; las
  animaciones son CSS puro, corren automáticamente al abrir el archivo).
- `screen-01-empty-state.md` / `.html` a `screen-04-pokemon-picker.md` / `.html`, y
  `screen-06-tips-carousel.md` / `.html` — pantallas previas del mismo flujo de
  hand-off.
