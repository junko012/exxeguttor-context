# Boceto: "Recrear con un encuentro válido" (errores de encuentro, Gen1–Gen4)

> `encounter-recreate-boceto.html` es el hand-off visual (cinco casos: Drapion de Platino, Corsola y Octillery de
> Crystal y Magmar de Yellow con datos **reales** de los saves del usuario; el caso de nivel bajo de Gen1 es una
> alteración sintética medida con PKHeX). Resuelve lo que hoy no tiene botón en el tab
> Diagnóstico: la fila **Origen del encuentro** (`EncInvalid`, `EncTypeMismatch`, `FatefulGiftMissing`).

## Cuándo aparece el botón (y cuándo no)

- **Con botón:** PKHeX encuentra al menos un encuentro candidato compatible con la especie y los movimientos
  actuales, y el Pokémon recreado con él **deja de tener errores de encuentro sin sumar errores nuevos**
  (criterio generate-and-verify, igual que `Method1Solver` y `IvSeedSolver`). La fila dice cuántas opciones hay.
- **Sin botón (caso C):** ningún encuentro coincide con sus movimientos → la fila lo explica y **lista los
  movimientos ilegales** (hoy solo dice "no coincide con el resto de sus datos"). Si el usuario los cambia, el
  botón aparece solo en cuanto exista un encuentro compatible. Botón secundario: "Ir a Moves".
- Sin alerta de encuentro no se muestra nada nuevo.

## Flujo

1. Fila del Diagnóstico → botón **"Recrear con un encuentro válido…"**.
2. **Modal de confirmación** (obligatorio: se reescribe el origen del Pokémon): lista de opciones elegibles, tabla
   **"qué cambia"** de la opción elegida y botones Cancelar / Aplicar. La primera opción viene preseleccionada.
3. Al aplicar, se reutiliza el **modal de feedback de "Corregir automáticamente"** (Rotom PC: Recreando… →
   Corrección aplicada), sin diseño nuevo.
4. El diagnóstico se recalcula: desaparece el error de encuentro y quedan los demás (EVs, habilidad…) con sus
   propias correcciones. El modal avisa de esto.

## Qué se conserva y qué cambia

| | Gen2 (Crystal) | Gen4 (Platino) |
|---|---|---|
| Se conserva | especie, nivel, movimientos (con PP), apodo, objeto, EVs, **DVs, brillante**, entrenador original/TID | especie, nivel, movimientos (con PP), apodo, objeto, EVs, **IVs**, **habilidad**, entrenador original/TID |
| Cambia | lugar y nivel de captura | lugar, nivel de captura, bola, y **Naturaleza y género** (salen del PID) |

En Gen4 el modal lo advierte y cada opción muestra el resultado exacto (por eso la tabla tiene Naturaleza y Género).

## Orden de las opciones

1. Opciones que **mantienen el lugar de captura** (etiqueta verde) — preseleccionada la primera.
2. Salvajes/estáticos por lugar.
3. **Huevo eclosionado** al final, con etiqueta naranja "origen de huevo" (es la que más inventa).
Se muestran 6 y el resto queda plegado ("Ver N opciones más": en el Corsola son 18).

## Gen1 (Red/Blue/Yellow): misma fila, otro arreglo

Gen1 **no guarda datos de captura** (ni lugar, ni nivel de captura, ni fecha): PKHeX decide el encuentro solo con
especie, nivel, movimientos y catch rate. No hay origen que recrear, así que la fila ofrece dos correcciones
distintas, ambas con modal de confirmación (casos D y E del boceto):

1. **Catch rate inválido (`G1CatchRate*`) — caso D, el Magmar real de Yellow.** El modal explica **por qué** el 45
   no vale y deja elegir el valor. Datos reales: Flamethrower (lo aprende por nivel 41 en Gen2) y Confuse Ray
   (nivel 49, Gen2) hacen que PKHeX lo trate como un Pokémon que pasó por Gen2, y entonces el catch rate debe ser
   un objeto de Gen2. Valor propuesto: **0 (sin objeto)**; con él el Magmar queda totalmente legal. Cubre cualquier
   otro Pokémon con el mismo problema, porque usa `CatchRateSolver` (prueba candidatos y verifica cada uno).
2. **Nivel demasiado bajo para la especie — caso E.** Se ofrece subir al **nivel mínimo con el que existe un
   encuentro válido** (se calcula probando niveles y verificando con `LegalityAnalysis`) y recalcular la
   experiencia. Medido con Pokémon alterados a nivel 2 en Yellow: Caterpie 3, Pidgeotto 12, Kadabra 18, Rhydon 10
   (por intercambio). **Cambia un dato visible** (nivel y EXP), por eso lleva confirmación y aviso.

Medido en Yellow con una especie por Pokémon legal generado (104 especies): con el nivel en 2, **99 de 99** quedan
legales al subir al nivel mínimo; con un movimiento ilegal solo 11 de 104 salen como error de encuentro (sin
candidatos; el resto se muestra como error de Moves). Un catch rate de 1 y el nivel 100 no rompen nada (1 es un
objeto válido de Gen2). **Limitación:** tu save de Yellow no tiene ningún caso real de nivel bajo; la alteración
"nivel 2" es sintética, así que no sé cuánto aparece en saves reales. `FatefulGiftMissing` apareció siempre junto
con `EncInvalid`: parece un efecto de "no se encontró encuentro" y desaparece al resolver el principal.

## Lo medido con los saves del usuario (PKHeX 25.11.07, un solo equipo)

| Save | Con error de encuentro | Con alguna opción válida | Sin candidatos (movimientos) | Con opción en el MISMO lugar |
|---|---|---|---|---|
| Crystal | 19 | **8** | 11 | — |
| Platino | 4 | **4** | 0 | 3 |

- **Crystal:** todos comparten entrenador original (Frogger/TID 4504 o Mattia{/8872) y casi todos son brillantes.
  14 de los 19 tienen además algún movimiento ilegal; los 11 sin candidatos son por eso (ej. el Octillery:
  Psychic y Thunderbolt ilegales, 0 candidatos).
- **Platino, Gen4, IVs conservados:** en los 4 Pokémon, todos los candidatos probados (24, 2, 13 y 2) quedaron
  válidos **con los IVs originales**; la **Naturaleza no se conservó en ninguno** (0 de 4): con unos IVs fijos
  hay solo ~4 PID posibles y casi nunca coinciden con la Naturaleza original.
- **Drapion (Platino):** original = Gran Pantano, nivel de captura 35, Poké Ball, Firme ♀, Armadura Batalla,
  IVs 31/31/31/0/31/31. Opciones reales: Gran Pantano (hierba) niveles 27–30 con Safari Ball (Grosera o Huraña, ♂)
  y huevo eclosionado en Pueblo Sosiego (Osada ♂). Detalle revelador: en el Gran Pantano la bola es Safari Ball,
  el original traía Poké Ball.
- **Corsola (Crystal):** original = Cueva Plateada, nivel de captura 42. 18 opciones: 16 de caña (buena nivel 20 /
  superior nivel 40 en 8 lugares) y 2 de huevo. El brillante se conserva en todas.

## ¿Es general? (medido con todas las especies, no solo los saves del usuario)

Se generó un Pokémon **legal por especie**, se le inventaron el nivel o el lugar de captura (como lo haría una
herramienta externa) y se probó recrearlo con este método:

| Juego | Pokémon con error de encuentro | Recreación encontró una opción válida |
|---|---|---|
| Crystal (Gen2) | 104 | 104 (100 %) |
| Platino (Gen4) | 196 | 193 (98,5 %) |
| Esmeralda (Gen3) | 63 | 60 (95,2 %) |

Fallos: Seadra y Gastrodon en Platino (la forma de Gastrodon es sospechosa; no se investigó) y Pikachu y Celebi de
regalos de Colosseum en Esmeralda (condiciones propias de entrenador original). **Limite de la prueba:** los
Pokémon tenían movimientos legales; en los saves reales el obstáculo dominante son los movimientos ilegales
(11 de 19 en Crystal), que dejan sin candidatos y sin botón. No se midieron Gold/Silver, Rubí/Zafiro,
Rojo Fuego/Hoja Verde, Diamante/Perla ni HGSS (mismo código).

## Lo que NO cubre / lo que no verifiqué

- No corrige EVs sobre 510 ni la habilidad del PID: siguen en el Diagnóstico.
- **No verifiqué** qué fecha, hora del día ni otros datos finos conserva el Pokémon recreado (en la prueba salieron
  los del encuentro generado). El diseño asume conservar la fecha original; hay que comprobar que siga legal.
- **Gen3** se midió solo con la prueba general (60 de 63); en el save de Esmeralda del usuario el único Pokémon
  ilegal era de PID, que ya resuelve el botón de Method 1.
- El criterio "sin errores nuevos" permite que sigan los errores ajenos que el Pokémon ya tenía.
- Observación sin explicar: PKHeX marca en el Drapion también `EffortAbove510` y `AbilityMismatchPID`, pero el
  Diagnóstico real solo mostraba el error de encuentro. El boceto los muestra como tarjetas aparte tras recrear.

## Textos (neutros, claves i18n es/en para `LocalizationService`)

| Clave | Español |
|---|---|
| `Recreate_Row_Available` | Se puede recrear con un encuentro válido |
| `Recreate_Row_Text` | Hay {0} opciones. Se conservan especie, nivel, movimientos, apodo, objeto, entrenador original y {1}; cambian los datos de captura. |
| `Recreate_Row_Button` | Recrear con un encuentro válido… |
| `Recreate_NoFix_Title` | Sin corrección automática |
| `Recreate_NoFix_Text` | Ningún encuentro de Pokémon {0} coincide con los movimientos de este Pokémon, así que no hay un origen válido al que recrearlo. Estos movimientos no son legales: |
| `Recreate_NoFix_Hint` | Cámbialos por movimientos legales y vuelve a revisar el diagnóstico: si después aparece un encuentro compatible, esta corrección se ofrece sola. |
| `Recreate_Modal_Title` / `_Subtitle` | Recrear con un encuentro válido / Elige el origen que quieres darle al Pokémon |
| `Recreate_Tag_SamePlace` / `_Tag_Egg` | mantiene el lugar / origen de huevo |
| `Recreate_Gen4_Note` | En Gen4 la Naturaleza y el género salen del PID, y el PID depende de los IVs: por eso pueden cambiar… |
| `Recreate_Done` | Origen recreado: el error de encuentro ya no aparece. |

## Equivalencias para implementar (sin código todavía)

- Servicio nuevo en `Exxeguttor.App` (sin UI): `FindOptions(PKM actual, SaveFile)` → opciones con lo que cambia.
  Usa `EncounterMovesetGenerator.GenerateEncounters` + `ConvertToPKM` y **trasplanta** al Pokémon generado:
  especie/forma, nivel y EXP, movimientos con PP y PP Ups, objeto, apodo, EVs, entrenador original/TID/SID/género
  (Gen2: también DVs). En Gen4: IVs y luego PID con `Method1Solver` (el mismo del botón de PID).
  **El trasplante de PP y PP Ups es obligatorio**: sin él casi todos los candidatos fallaban por errores de PP.
- Dedupe por (encuentro, lugar, nivel de captura, bola, naturaleza, género).
- El resultado se guarda como **edición compuesta** de la sesión (`EncounterRecreation`, aplicada al final en el
  preview y al exportar), igual que `IvSeedSolution`, y se descarta si el usuario edita a mano campos que ella fija.
- Acción nueva `FieldFixAction.RecreateEncounter` en la fila; vista/VM del modal de confirmación (reusa
  `RotomMatrixControl` no hace falta: lleva el Rotom estático del modal de confirmaciones); el feedback usa
  `AutoFixViewModel`.

## Por decidir antes de implementar

1. ¿Las opciones de **huevo** se muestran siempre (al final) o solo bajo "Ver más"? Son las que más inventan.
2. ¿Preseleccionar siempre la primera que mantiene el lugar, o ninguna hasta que el usuario elija?
3. ¿Incluir Gen3 en el primer lanzamiento (la prueba general dio 95 %) o esperar un caso real?
4. Conservar la **fecha de captura original** (hay que comprobar que siga legal).
5. Gen1: ¿el modal del catch rate ofrece solo el valor propuesto (0) o también otros valores válidos?
