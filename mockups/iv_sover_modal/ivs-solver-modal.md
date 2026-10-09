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

## Por qué hay varias opciones (y a veces pocas o ninguna)

Cada semilla fija a la vez los IVs, la Naturaleza, la Habilidad, el Género, el Brillante y el
Tamaño. Los IVs exactos que pide el usuario pueden salir de muchas semillas, de pocas o de
ninguna; cada una trae su propia Naturaleza/Género/Tamaño, así que no se puede garantizar
conservarlos. Por eso el modal ordena las opciones por **cuántos atributos mantiene** y deja
elegir, y **"Usar la más cercana" siempre está disponible**.

Medido con PKHeX 25.11.07 real sobre los 6 Tera raids de muestra de Escarlata/Púrpura (una
pasada completa sobre las 2³² semillas; las semillas exactas que se probaron salieron 100 %
legales):

| Encuentro (IVs perfectos forzados) | Semillas que pueden originar el raid | Exactas "todos 31" | Exactas "un IV cambiado" |
|---|---|---|---|
| Pachirisu 3★ (0) | 57,0 M | 0 (la más cercana: distancia 2, legal) | 0 (la más cercana: distancia 1, legal) |
| Ekans 1★ (1) | 249,9 M | 7 | 3 |
| Ekans 3★ (2) | 165,6 M | 149 | 11 |
| Wigglytuff 4★ (3) | 29,6 M | 916 | no medido |
| Raichu 5★ (4) | 12,5 M | 12 075 | 773 |
| Clefable 6★ (5) | 132,4 M | 4 137 342 | 690 919 |

Qué se conserva en las opciones (muestra de 40 semillas exactas **en orden de semilla**, no
ordenadas por conservación): la Habilidad suele coincidir en los raids de habilidad fija
(Clefable: 40/40) y muy poco en los demás; el Género coincide en ~50–75 %; la Naturaleza casi
nunca (0–2 de 40, o sea ~1/25 como se espera al azar); el Brillante coincide siempre. Con
millones de exactas (Clefable) hay de sobra para elegir una que conserve todo; con 3–11
exactas (Ekans) probablemente no, y las opciones mostrarán qué cambia.

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
  IProgress<…>, CancellationToken)`. Reparte el espacio de semillas en bloques de 2²⁴ entre
  `Environment.ProcessorCount - 1` hilos, comprueba la cancelación por bloque y reporta el
  progreso real por bloques completados.
- **Orden del filtro (medido):** primero `CanBeEncountered(seed)` (¿esta semilla puede originar
  este raid?: solo ~0,3–6 % de las semillas, y es barato) y recién después se calculan los IVs.
  En la misma pasada se acumulan las coincidencias exactas (con tope) y la **más cercana**
  (suma de diferencias de IVs), así que "Usar la más cercana" no cuesta una segunda pasada.
- Para armar cada candidato: `ConvertToPKM` + `GenerateSeed32`, y **asignar a mano**
  `TeraTypeOriginal = Tera9RNG.GetTeraType(...)`: `GenerateSeed32` no lo hace y sin eso todos
  los candidatos salen ilegales. Después se verifica con `LegalityAnalysis`.
- **Tiempo medido:** una pasada completa tarda ~37–77 s con **un solo núcleo** (~13–18 ns por
  semilla según el encuentro). La mejora con más hilos es la esperable pero **no la medí** (el
  sandbox tiene 1 núcleo): el ETA del modal debe calcularse con el ritmo real de los primeros
  bloques, no con una constante.
- En Tera raids (semilla de 32 bits) la pasada es exhaustiva, así que el estado "Sin solución"
  puede afirmar con certeza que no existe una semilla con esos IVs.
- **Gen8, estáticos de mundo abierto (semilla de 32 bits, medido con PKHeX 25.11.07 real):** la
  semilla fija EC, PID, IVs y tamaño, pero **no** la Naturaleza, el Género ni la Habilidad, así
  que *todas* las opciones conservan esos tres (40/40 en la muestra) y solo cambian EC/PID/Tamaño.
  No hay filtro de "¿puede ser este encuentro?": cualquier semilla vale (salvo la regla de
  brillante). Lapras (3 IVs perfectos forzados), "todos 31": 130 994 semillas exactas, 40/40
  legales, pasada de ~151 s en 1 núcleo (~35 ns/semilla con corte temprano por distancia).
  Pikachu (sin IVs forzados), "todos 31": 0 exactas; la más cercana (distancia 1) es legal; pasada
  de ~26 s. Mismo comportamiento que en Tera raids: "la más cercana" resuelve los casos sin solución.
## Cobertura medida con PKHeX 25.11.07 (todos los prototipos en `prototipos/`)

| Familia de encuentros | Mecanismo | Resultado medido (1 núcleo) |
|---|---|---|
| Gen9 Tera raids (6 encuentros) | semilla de 32 bits + filtro `CanBeEncountered`; pasada exhaustiva | 37–77 s; candidatos 100 % legales |
| Gen9 Might9 / Dist9 | igual que Tera raids (muestra de 1/256 del espacio) | candidatos exactos 100 % legales (tras asignar el Tera tipo) |
| Gen8 estáticos de mundo abierto | semilla de 32 bits; Nat/Gén/Hab no salen de la semilla | 26–151 s; 40/40 legales y conservan Nat+Hab+Gén |
| Gen8 raids/dens | semilla de 64 bits: **muestreo**, no pasada completa | con ≥3 IVs perfectos forzados, 20 exactas en ~1 s; con 2, 1–25 s; con 1, ~25–30 s para 2–13 exactas; 20/20 legales |
| Legends Arceus (estáticos) | semilla de entidad de 64 bits: muestreo | Spiritomb (3 forzados) <3 s; Phione (0 forzados) ~20 s para 2 exactas; legales |
| BDSP itinerantes (Mesprit, Cresselia) | semilla de 32 bits (EC = semilla) | ~182–186 s; 20/20 legales |
| Gen9 Fixed9 / Outbreak9 / Slot9 / Static9 (sin IVs fijos) | **solo regla** (mínimo de IVs en 31), sin semilla | 100 % legales si los 31 se mantienen (301/301, 29/29, 119/119, 35/35) |
| IVs fijos (Static9, Trade9, WC9 con IVs) | no editable | 1/12, 0/5, 28/55 legales: no hay solución |

Cuando no hay semilla exacta, la **más cercana** fue legal en todos los casos probados. Gen6/7
y Gen5 son de regla (mínimo de IVs en 31 o IVs fijos), sin semilla.

Detalles que el servicio real debe respetar (cada uno hizo fallar un candidato en pruebas):
1. **Tera tipo:** en Tera9/Might9/Dist9 hay que asignar `TeraTypeOriginal` con
   `Tera9RNG.GetTeraType(seed, TeraType, Species, Form)`; `GenerateSeed32` no lo hace.
2. **Guaridas estándar de Gen8** (`EncounterStatic8N`): la semilla también fija nivel y nivel
   Dinamax; solo valen semillas con `IsPossibleSeed(pk, seed, true)` frente al Pokémon actual.
3. **Partir del Pokémon del usuario** (`Clone()` + aplicar los campos de la semilla), no de uno
   nuevo, para no cambiar su nivel/Dinamax/ataques.
4. **Legends Arceus:** tras `TryApplyFromSeed` replicar la finalización del encuentro:
   `Scale = HeightScalar`, `ResetHeight()`, `ResetWeight()`.
5. **BDSP itinerantes:** si el encuentro tiene brillante aleatorio, llamar a
   `Roaming8bRNG.TryApplyFromSeed` con `Shiny.Never` (con `FixedValue` devuelve falso y deja
   el Pokémon sin tocar).
6. **Regla de brillante:** en encuentros no brillantes, descartar semillas cuyo PID resulte
   brillante con el ID del entrenador del save.
7. **Más núcleos:** no se midió el escalado (el sandbox tiene 1 núcleo); el ETA del modal debe
   salir del ritmo real de los primeros bloques.
8. **Si no hay semilla exacta** en un espacio exhaustivo (Gen9, Gen8 de 32 bits, BDSP), "Sin
   solución" es una afirmación segura; en los de 64 bits (muestreo) no, y el texto debe decir
   "no se encontró en N intentos".

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
- Nada pendiente de prototipar: la cobertura medida está en la tabla de arriba.
