# Boceto: Pokédex escaneando — identidad visual para "verificar/analizar legalidad"

Reemplaza el overlay genérico de pokebola girando (`BusyKind.Generic`) en los dos puntos
donde hoy se muestra ese mensaje:

- **"Verificando legalidad…"** — `PokemonEditorViewModel.LoadLegalityAsync`, corre cada vez
  que se carga un Pokémon en el editor (incluida la carga automática justo después de crear
  uno con el Loader 3).
- **"Analizando legalidad…"** — `MainWindowViewModel`, corre al apretar "Exportar", antes de
  mostrar el modal de revisión.

Ambos disparadores comparten la MISMA identidad visual (una sola Pokédex, no dos mascotas
distintas) — son conceptualmente la misma acción (correr `LegalityAnalysis` de PKHeX.Core
sobre uno o más Pokémon), solo cambia el disparador. Mismo criterio que ya se usó con
Rotom-Ventilador reutilizado en tres diálogos de confirmación distintos.

## Por qué la Pokédex

Es la opción más directa de todas las evaluadas en la sesión de diseño: su función canónica
en los juegos es literalmente escanear un Pokémon y devolver datos verificados sobre él. Se
descartaron:

- **Growlithe/Arcanine** (el "perro policía", por su asociación con Oficial Jenny) — válido,
  pero más metafórico que literal.
- **Porygon-Z** (lore real: "datos alterados por un programa no autorizado que le causó
  inestabilidad") — descartado por compartir familia con Porygon/Porygon2, que ya son los
  protagonistas de la pantalla de éxito de exportación; hubiera leído como repetido.
- **Probopass/Nosepass** (brújula) — descartado por ser una metáfora más genérica
  ("detectar" en general, no legalidad específicamente).

También se investigó si hay algo en el lore real de los juegos más directo todavía — el GTS/
Wonder Trade rechaza automáticamente Pokémon hackeados al depositarlos — pero es un mensaje
de sistema, no un objeto con el que arme una escena visual. Queda como dato de lore para el
texto del diálogo si hace falta ("como el chequeo del GTS"), no como mascota.

## Decisión de estilo: ícono a color sólido (excepción consciente)

La Pokédex se dibuja como **ícono de color sólido** (rojo + lente celeste), no como outline
monocromático. Es el **primer ícono de UI a color** del proyecto — todo lo demás es o bien
outline monocromático (los 7 íconos del rail de navegación, incluido el libro abierto que hoy
representa "Pokédex" en el rail) o sprites reales de Pokémon (Rotom, Porygon, Hitmonlee, etc.,
sacados de `pokemon.db`/assets embebidos). Decisión tomada a propósito en la sesión de diseño
tras comparar las dos opciones: se ve más reconocible de un vistazo que una versión outline
fina, y vale la excepción para esta pantalla puntual — no implica que el resto de los íconos
de la app deban migrar a color.

**No existe ningún sprite ni asset de Pokédex en el proyecto** — se confirmó revisando
`Assets/sprites/` completo. Tiene sentido: la Pokédex es un dispositivo de la interfaz del
juego, no una entidad con `species_id` propio, así que nunca iba a estar en ninguna base de
sprites (ni la del proyecto, ni PokeAPI). El ícono se dibuja a mano en SVG/`Path.Data`, no se
busca ni se descarga de ningún lado.

## Elementos de la escena

- **Pokédex** — vaivén sutil (rotación ±3°, mismo `pokedex-idle` en loop que otros elementos
  "vivos" del proyecto como `l1-ghost`/`dlg1-fan-bob`), lente con un parpadeo breve a mitad
  de ciclo (`lens-blink`, opacity 1→0.3→1).
- **Pokémon siendo escaneado** — quieto, silueta genérica simple (no depende de la especie
  real que se está analizando — a diferencia del `Loader3EggRevealSprite`, acá no hace falta
  mostrar la especie exacta, el foco es el acto de escanear en sí).
- **Haz de escaneo** — línea horizontal que recorre al Pokémon de arriba a abajo en loop,
  2.4s, sincronizado con el resto de la escena.
- **Checklist de 4 categorías** — PID y naturaleza / IVs y stats / Movimientos / Origen del
  encuentro. **Mismas categorías que ya agrupa `LegalityMessageMapper`** (ver `context.md`,
  sección Legalidad) — no es texto inventado para el mockup, hay que reusar esa fuente. Cada
  ítem se ilumina en su propio momento del ciclo (`animation-delay` escalonado, 0/0.3s/0.6s/
  0.9s) — puramente decorativo en loop, igual que las grietas del huevo del Loader 3, NO
  atado a en qué paso real está el análisis de PKHeX.Core (haría falta instrumentar
  `LegalityAnalysis` paso a paso para eso, fuera de alcance).
- **Barra de progreso** — mismo criterio a definir que el resto de los loaders: real si hay
  algo medible, decorativa si no (ver "Pendiente" abajo).

## Patrón nuevo para el proyecto

Ningún loader anterior (Loader 1: Hitmonlee/Voltorb/Dugtrio; Loader 3: huevo que eclosiona)
mostró una lista de sub-pasos — ambos fueron una sola escena decorativa continua. La
checklist acá es una decisión consciente, no un accidente de scope: para "verificar
legalidad" tiene sentido mostrar categorías porque el usuario ya está acostumbrado a verlas
agrupadas así en el tab Diagnóstico y en las fichas de legalidad del editor — refuerza la
misma taxonomía en vez de inventar una nueva.

## Pendiente de confirmar antes de implementar

1. **Progreso real vs. decorativo**: `LegalityAnalysis.GetLegalityDiagnosticSteps` (usado por
   el tab Diagnóstico) corre sobre UN Pokémon a la vez — para "Analizando legalidad" al
   exportar, que corre sobre TODOS los Pokémon incluidos en el export, sí habría una
   granularidad real posible (progreso = Pokémon ya analizados / total). Para "Verificando
   legalidad" al cargar uno solo en el editor, no hay granularidad real posible — un
   Pokémon es una operación atómica. Puede que la barra tenga que comportarse distinto según
   el disparador (real en un caso, decorativa en el otro) — a diferencia de Loader 1/3 donde
   la misma barra sirve para todo.
2. **Duración mínima**: mismo tipo de pregunta que se resolvió para Loader 1/3 — analizar un
   solo Pokémon probablemente sea casi instantáneo (sin passthrough de I/O como abrir un
   save), así que corre el mismo riesgo que tuvo Loader 3 al principio: la animación decorativa
   nunca llega a completar un ciclo visible. Definir si hace falta algún piso artificial chico
   (mismo criterio que el de la patada de Hitmonlee, ~600-700ms) o si no importa por ser una
   operación de fondo poco visible de por sí.
3. **Texto exacto**: se mantienen los textos ya implementados ("Verificando legalidad…",
   "Analizando legalidad…") — no se proponen nuevos, siguiendo el mismo criterio que
   `rotom-open-other-save-dialog.md` (texto real tiene prioridad sobre redacción de mockup).

## Ver también

- `mockups/loading_screens/` — Loader 1 y Loader 3, mismo lenguaje visual de tarjeta blanca +
  overlay oscuro + barra de progreso al pie.
- `context.md`, sección "🩺 Diagnosticador de legalidad" — arquitectura de
  `LegalityMessageMapper`/`LegalityDiagnosticBuilder`, fuente real de las 4 categorías de la
  checklist.
