# Boceto: modal "Buscar IVs legales" (solver por semilla — paso 2)

> `ivs-solver-modal-boceto.html` es el hand-off visual. Continúa el paso 1 (botón
> "Corregir automáticamente" con `Method1Solver`, Gen3/4). Aquí se diseña lo que el paso 1
> no cubre: encuentros cuyo PID/EC/IVs salen de una **semilla** del juego (Gen8/9) y los
> casos donde no hay solución.

## Cuándo aparece (y cuándo NO)

Regla general: **no hay alerta de legalidad → no aparece nada** (como el resto de la UI, que
reacciona sola). Todo lo nuevo se muestra únicamente mientras exista la alerta de IVs.

- **Aviso en el tab IVs / EVs** (nuevo): una franja de una línea que aparece junto con el "!" rojo
  que ya marca la pestaña y los campos, y desaparece sola cuando el Pokémon vuelve a ser legal.
  Dice "Con estos IVs el Pokémon deja de ser legal en este encuentro" y trae el botón
  **"Buscar IVs legales"**. Va en el pie del tab (encima de "Total EVs"): el encabezado fijo
  ya está al límite de alto (~580 de 600 px), y la lista tiene scroll propio, así que sumar
  ~26 px solo cuando hay alerta no rompe nada.
- **Fila del tab Diagnóstico** (ya existe): mismo botón, mismo modal.
- **Solo se muestra el aviso cuando hay algo que ejecutar.** Para los casos sin solución
  automática (Gen5–7 con "al menos N IVs en 31", regalos con IVs fijos) no se agrega nada
  nuevo: siguen como hoy, con los campos marcados y el mensaje explicativo en Diagnóstico. Por
  eso se eliminó el estado "regla" del boceto anterior.
- **Qué hace el botón según el juego:** Gen3/4 (Method 1) corrige al instante, sin modal (como
  ya hace el paso 1); Gen8/9 con semilla abre el **modal** de búsqueda, que bloquea la ventana
  mientras calcula y muestra progreso con opción de cancelar.

## Estados del modal (los tres están en el boceto)

1. **Buscando.** **Rotom PC procesando, con lluvia de código estilo Matrix**: la pantalla
   se oscurece y detrás de Rotom caen columnas de dígitos hexadecimales que cambian de valor
   sin parar (con estela y cabeza brillante), hasta que la búsqueda termina. Rotom queda al
   frente con un halo claro y **cambia de forma muy rápido, "hackeado" por la Matrix**
   (**increscendo**: arranca con un cambio cada 0.25–0.7 s y la velocidad sube de 1× a 3× a medida que avanza la búsqueda, como los agentes de la película): se disuelve de arriba hacia abajo en
   dígitos hexadecimales (con franjas desplazadas y separación de color rojo/cian) y se
   rematerializa como otra forma — Calor, Lavadora, Frío, Ventilador o Corte, al azar sin
   repetir la actual — y el Rotom original reaparece seguido (35 % de los cambios) para que se
   note que es él quien está siendo hackeado, mientras la lluvia se acelera durante el
   cambio. Entre cambios tiene micro-fallos ocasionales. Abajo a la izquierda una lectura
   "SEED 7F3A91C2" cambia a cada cuadro y las teclas del teclado se iluminan en secuencia.
   Debajo, los IVs objetivo, la barra de progreso REAL (semillas revisadas / 2³²), tiempo
   transcurrido, tiempo restante estimado y un contador de coincidencias en vivo (ver "Por qué
   hay coincidencias en vivo"). Botón **Cancelar**: no toca el Pokémon.
2. **Encontrada.** La PC se detiene: borde y teclas en verde, Rotom en reposo y un ✔. Muestra los IVs, una lista de
   **opciones** navegable (‹ ›) y la tabla "qué cambia" de cada una (Naturaleza, Habilidad,
   Género, Brillante, Tamaño). La opción 1 siempre es la que mantiene más atributos. Botones
   **Aplicar** / **Descartar**. Cada opción ya viene verificada con `LegalityAnalysis`.
3. **Sin solución.** La pantalla se vuelve ámbar con un "?" y Rotom queda en tono apagado. Se revisó todo el espacio y ninguna semilla produce esos IVs. Ofrece
   **"Usar la más cercana"** (la que difiere en menos IVs, trazada durante la misma pasada) o
   **"Volver a los IVs originales"**. También se usa en Gen3/4 cuando `Method1Solver` falla
   (hoy en ese caso el botón no hace nada y el usuario no recibe ninguna respuesta).

## Por qué hay varias opciones

Un par de IVs exacto casi nunca tiene una única semilla: en Gen9 (semilla de 32 bits) la
cantidad de semillas que producen esos IVs depende de cuántos son 31 forzados. Con 3 IVs
perfectos obligatorios habría del orden de miles de coincidencias, y con IVs al azar solo unas
pocas (**estimación teórica por conteo de probabilidades, todavía sin medir** con PKHeX). Cada coincidencia trae su propia Naturaleza, Habilidad, Género, Brillante y Tamaño
(todo sale de la misma semilla), así que no se puede garantizar que se conserven. Por eso el
modal ordena las opciones por **cuántos atributos mantiene** y deja elegir.

## Por qué hay coincidencias en vivo

Una búsqueda de 10–40 s sin señal intermedia se siente colgada (esa fue la crítica a la primera
versión: el flujo de fondo era muy tenue). Por eso hay tres señales de vida: la lluvia de
código, la lectura de semilla que cambia y el contador de coincidencias, que sube cuando se
encuentran semillas válidas.

## Comportamiento

- Modal centrado con dim de ventana completa, igual que los demás loaders/diálogos.
- Mientras busca, la ventana principal no se puede editar (el Pokémon está "congelado" en sus
  IVs objetivo). Esc = Cancelar.
- **Aplicar** registra las ediciones resultantes (PID/EC y lo que la opción cambie) en la
  sesión de edición, igual que el botón de Method 1 del paso 1; la legalidad en vivo se
  recalcula y el mensaje desaparece.
- Cancelar o Descartar no dejan ninguna edición registrada.

## Textos (neutros, claves i18n es/en para `LocalizationService`)

| Clave | Español |
|---|---|
| `IvSolver_Searching_Title` | Buscando una combinación legal… |
| `IvSolver_Searching_Hint` | Puedes cancelar cuando quieras: el Pokémon no cambia hasta que apliques un resultado. |
| `IvSolver_Found_Title` | Combinación legal encontrada |
| `IvSolver_Found_Verified` | Verificada con el analizador de legalidad: sin errores |
| `IvSolver_None_Title` | Esa combinación no existe en este encuentro |
| `IvSolver_Rule_Title` | Este encuentro limita los IVs |
| `IvSolver_Action_Apply` / `_Discard` / `_Cancel` / `_UseClosest` / `_BackToOriginal` / `_GotIt` | Aplicar / Descartar / Cancelar / Usar la más cercana / Volver a los IVs originales / Entendido |

## Equivalencias en Avalonia (para implementación)

- PC: `Border` (pantalla) + cuello + teclado de 12 `Border` pequeños, el mismo armado de la
  Rotom PC de `export_success` (conviene extraerlo a un control compartido en vez de copiarlo).
- Rotom: sprite base (`pokemon/normal/479.png`, el mismo que usa la Rotom PC de exportación)
  con bob vertical. Las otras cinco formas ya están en el repo (`pokemon/forms/479_1..5.png`:
  Calor, Lavadora, Frío, Ventilador, Corte), no hace falta ningún asset nuevo.
- Efecto de cambio de forma: va dentro del mismo control propio de la lluvia (o en uno
  hermano), dibujando el sprite por bloques de 6×6 px con `DrawingContext.DrawImage(origen,
  rectOrigen, rectDestino)` (256 bloques como máximo por cuadro). Los bloques "opacos" de cada
  forma y las dos copias teñidas (rojo/cian, para la separación de color) se precalculan una vez
  al cargar, con un `WriteableBitmap`. Los dígitos que reemplazan a los bloques disueltos salen
  de glifos hexadecimales prerrenderizados (no `FormattedText` nuevo en cada cuadro). Máquina
  de estados: *mantener* (0.25–0.7 s) → *disolver* (170 ms) → *rematerializar* (170 ms), a 1×;
  los tres tiempos se dividen por un factor `1 + 2 × progreso` (1× al inicio, 3× al final).
  El factor se ata al **progreso real de la búsqueda** (el mismo de la barra), no al reloj: así
  el clímax coincide con el final y, si la búsqueda es corta o larga, la rampa se adapta. A 3×
  cada tramo dura ~57 ms, por eso el efecto de Rotom necesita su propio temporizador a ~40
  cuadros/s (la lluvia sigue a ~18 cuadros/s): con 18 cuadros/s la disolución quedaría en un
  solo cuadro.
- En el estado "Encontrada" Rotom queda en su forma base y estable; el cambio de forma solo
  ocurre durante la búsqueda.
- Lluvia de código: un control propio (`Control` con `Render(DrawingContext)`) de ~172×100 px,
  sin hijos visuales, redibujado por un `DispatcherTimer` a ~18 cuadros/s. Cada columna es un
  gotero con posición y velocidad propias; la estela sale de pintar un rectángulo
  semitransparente encima en cada cuadro. Solo corre mientras el modal está en el estado
  "Buscando" (se detiene en los demás para no gastar CPU). Con `prefers-reduced-motion`/ajuste
  equivalente se queda en un cuadro fijo.
- Lectura "SEED": en la implementación real puede mostrar **semillas muestreadas de la
  búsqueda** (el servicio las reporta junto con el progreso), de modo que los números que
  cambian sean datos reales y no puro adorno.
- Teclas: cambio de `Background` con retardo escalonado por tecla (un `Style` con `Delay`).
- Un solo `RenderTransform` por elemento (regla del proyecto).
- Barra: mismo patrón de dos columnas Star + `StarWidthConverter`, bindeada a un progreso real.
- Aviso del tab IVs/EVs: un `Border` en el pie de `PokemonStatsView`, con `IsVisible` ligado a
  `HasIvsEvsIssue` Y a que exista una corrección disponible (así desaparece solo al quedar legal).
- Tabla "qué cambia": `ItemsControl` con una fila por atributo.
- Sin `blur` ni `conic-gradient` (no existen en Avalonia).

## Notas técnicas de la búsqueda (no visuales)

- Servicio nuevo en `Exxeguttor.App` (sin dependencias de UI): `SearchAsync(PKM editado,
  IProgress<…>, CancellationToken)`. Reparte el espacio de semillas entre
  `Environment.ProcessorCount - 1` hilos, comprueba la cancelación por bloque y reporta cada
  ~16 M de semillas.
- Filtro rápido por IVs primero; solo las coincidencias (miles como máximo) pasan por
  `LegalityAnalysis` y se puntúan por atributos conservados.
- Estimación de tiempo: microbenchmark de ~7 ns por semilla en un hilo → 2³² ≈ 30 s por
  hilo. **Es una estimación, no una prueba completa**: la búsqueda real contra PKHeX en Gen8/9
  todavía no se prototipó.
- Raids de Gen8 con semilla de 64 bits: no hay espacio exhaustivo; la búsqueda es por muestreo
  y no puede afirmar "no existe" — el estado 3 diría "no se encontró en N intentos".

## Por qué Rotom PC

Rotom ya es el asistente de la app (ícono de la barra de estado, diálogos de confirmación) y la
Rotom PC ya existe en la pantalla de exportación exitosa. Una PC "procesando una clave" es
lore coherente, y la Pokédex roja ya está reservada para los escaneos (abrir save, legalidad,
catálogo de especies). El sprite es el Rotom base, igual que en exportación (no existe sprite
oficial de "Rotom PC").

## Decisiones tomadas

1. **Opciones:** el modal muestra varias y el usuario elige (no se aplica sola la mejor).
2. **Dónde se corrige:** desde el aviso del tab IVs/EVs y desde la fila de Diagnóstico. No hay
   estado "regla": si no hay alerta no se muestra nada, y si no hay corrección automática se
   queda el comportamiento actual.
3. **"Usar la más cercana":** se ofrece siempre.

## Por revisar antes de implementar

- Confirmar visualmente el aviso en el pie del tab IVs/EVs (maqueta en el boceto, con la casilla
  "Simular IVs legales" para ver que desaparece solo).
- Prototipo de la búsqueda de semillas contra `LegalityAnalysis` en Gen8/9 (todavía sin probar).
