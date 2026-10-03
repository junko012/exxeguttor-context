# Plan: Idioma de la UI de Exxeguttor (selector + paquetes lang)

**Este documento es de uso activo, no un registro histórico** — a diferencia de `context.md`
(que se reescribe entero cada sesión) o `status.md` (changelog append-only), este archivo se
actualiza EN VIVO, dentro de la misma sesión, a medida que se completa cada tarea. Si estás
retomando esto en una sesión nueva: **actualizá la sección "Estado de avance" (al final) a
medida que avances**, no la dejes para el final de la sesión — mismo criterio de "escribir
antes de asumir" que el resto del proyecto.

## Cómo arrancar esta sesión

1. Cloná `junko012/exxeguttor` (repo privado, pedile el token a Juan) y revisá
   `git log --oneline -15` — si hay commits después de la última entrada de "Estado de
   avance" de este documento, alguien tocó código de idiomas sin actualizar este archivo:
   leé el diff real antes de asumir que el estado de abajo sigue vigente.
2. Este es un plan de trabajo acotado a UN tema (idioma de la UI) que corre en paralelo al
   resto del desarrollo de la app — no toques nada fuera de lo que este documento cubre. Si
   encontrás algo relacionado pero fuera de alcance (ej. un bug de legalidad), anotalo en
   `status.md` del repo de contexto, no lo arregles acá.
3. Cada fase de abajo debería dejar la app compilando y funcionando — no dejes una fase a
   medio terminar entre sesiones si podés evitarlo. Si tenés que cortar a mitad de una fase,
   dejalo anotado con precisión en "Estado de avance" (qué archivo, qué falta exactamente).

## Contexto — qué ya existe y qué no (confirmado leyendo código real, no asumido)

Hay **tres sistemas de idioma completamente separados** en el proyecto — no confundirlos:

1. **`LocalizationService`** (`src/Exxeguttor.UI/i18n/LocalizationService.cs`) — el idioma
   del CHROME de la UI propia de Exxeguttor (menús, botones, diálogos, mensajes de estado).
   Ya tiene: fallback chain (idioma activo → inglés → la clave misma), detección de idioma
   del SO, soporte para idiomas RTL (`IsRtl`), y un mecanismo de paquetes lang externos ya
   funcional (`/usr/share/exxeguttor/lang/*.json` o `./lang/*.json`, buscados en
   `TryLoadLocale`/`DetectAvailableLocales`). **Lo que NO tiene**: nada en la UI llama a
   `Load(locale)` después del arranque — el idioma se detecta una vez del SO y queda fijo
   para siempre, sin selector, sin persistencia de una elección manual.
   - `es.json`/`en.json`: 68 claves cada uno (al momento de escribir esto).
   - Solo **29 usos** de `_loc[...]` en 4 archivos (`MainWindowViewModel.cs`,
     `TrainerViewModel.cs`, `PokemonEditorViewModel.cs`, `EditApplyService.cs`).
   - El resto de la UI — **121+ `Text=` y 14+ `Content=` con texto en español hardcodeado
     directo en los `.axaml`** (conteo aproximado por regex, seguramente hay más en atributos
     multilínea o texto inline entre tags que el regex no agarra) — nunca pasa por acá.
2. **`GameInfo.GetStrings(lang)`** (de PKHeX.Core) — nombres de especie/movimiento/ítem TAL
   COMO LOS GUARDA EL PROPIO SAVE (ej. un cartucho francés internamente asocia el ID 1 a
   "Bulbizarre"). Sistema totalmente aparte, correcto que exista independiente del idioma de
   la UI — PKHeX.Core solo tiene tablas para los idiomas que los juegos reales tuvieron:
   `ja`, `en`, `fr`, `it`, `de`, `es`, `ko`, chino simplificado/tradicional. **Decisión de
   producto ya confirmada** (ver más abajo): los nombres se muestran en el idioma de la UI,
   NO en el idioma original del cartucho — el idioma del cartucho es solo un dato informativo
   (ver punto 3).
   - `PokemonEditorViewModel.cs` ya hace esto bien, vía un mapeo privado `GetPKHeXLang(string
     locale)` (switch con fallback a `"en"` si el idioma de UI no tiene tabla en PKHeX.Core —
     cubre el caso de instalar un paquete lang de un idioma que los juegos nunca tuvieron,
     ej. hindi o indonesio).
   - **Bug real, pendiente de arreglar** (Fase 1): tres lugares más llaman
     `GameInfo.GetStrings("en")` a mano, ignorando el idioma de UI activo:
     - `MainWindowViewModel.cs`, dentro de `OnSpeciesChosen` (mensaje del loader al crear un
       Pokémon) y en el `StatusMessage` post-creación.
     - `PokemonSlotViewModel.cs`, al armar `Name` (nombre mostrado en cada slot de
       Caja/Equipo) y al resolver el sprite del ítem sostenido.
3. **`TrainerViewModel.Language`** — el idioma CON EL QUE SE JUGÓ el cartucho (dato leído del
   save, mostrado como texto informativo en la ficha del entrenador). No tiene relación
   ninguna con el idioma de la UI ni con qué nombres se muestran — es solo un dato de
   lectura. No tocar en este plan, ya funciona bien y es un concepto distinto.

**Tampoco existe ningún mecanismo de preferencias/settings persistentes en todo el
proyecto** — cero archivos de configuración de usuario hoy. Hace falta crear uno desde cero
(Fase 0) — es una pieza de infraestructura compartida, no específica de idiomas, pero este
plan es lo que la necesita primero.

## Decisiones de producto ya tomadas (confirmadas por Juan, no re-discutir)

- **Selección de idioma al arrancar** (sin preferencia guardada todavía, o primera vez):
  si el idioma del SO tiene match exacto o por código base en `AvailableLocales`, usar ESE;
  si no hay match, **inglés por defecto** (¡no español! — cambiado explícitamente, ver
  `DetectSystemLocale` en `LocalizationService.cs`, YA APLICADO — ver "Estado de avance").
- Con una preferencia YA guardada (después de que el usuario elige algo distinto al detectado
  del SO), esa preferencia gana siempre sobre la detección del SO en arranques futuros — ver
  Fase 0.
- **Selector en la UI**: en algún lugar del menú (se diseñó como submenú de `File`, ver
  `mockups/language_selector/` — no es obligatorio implementarlo ahí si durante la
  implementación aparece una ubicación mejor, pero arrancar por esa propuesta).
- **Paquetes de idioma instalables**, mismo patrón que otras apps Linux (archivo `.json`
  suelto en una carpeta conocida, sin instalador ni descarga automática en v1) — el mecanismo
  YA EXISTE en código (`LocalizationService`), falta exponerlo en la UI (Fase 2) y
  documentarlo para usuarios reales (Fase 4).
- **Cambio de idioma requiere reiniciar la app** (Opción A del análisis, no cambio en
  caliente) — decisión tomada a propósito para evitar el refactor grande de convertir cada
  string "asignado una vez" en las ViewModels (ej. `Title = _loc["App_Title"];` en el
  constructor) a una propiedad computada + notificación de cambio de idioma. Si en algún
  momento el reinicio se siente limitante, se evalúa Opción B como mejora incremental
  posterior — NO agrandar el scope de este plan para cubrirlo ahora.
- **Nombres de especie/movimiento/ítem siempre en el idioma de la UI**, nunca en el idioma
  original del cartucho del save (confirmado explícitamente, ver Contexto punto 2 arriba).

## Plan de fases

### Fase 0 — Infraestructura de preferencias (prerrequisito, sin esto no hay nada que persista)

- Crear un servicio chico de settings (ej. `AppSettingsService` en `src/Exxeguttor.UI/Services/`
  o `src/Exxeguttor.App/Services/` — evaluar cuál capa es más apropiada al llegar a esto,
  probablemente `Exxeguttor.UI` porque es un concern de UI, no de dominio del save).
  - Archivo JSON simple en una ruta real de Linux — usar convención XDG:
    `$XDG_CONFIG_HOME/exxeguttor/settings.json`, con fallback a `~/.config/exxeguttor/settings.json`
    si `XDG_CONFIG_HOME` no está seteada (patrón estándar, no inventar una ruta propia).
  - Forma mínima para arrancar: `{ "locale": "es" }` — pensado para poder agregarle más
    claves después sin romper compatibilidad (deserializar tolerante a claves desconocidas,
    que es el comportamiento por defecto de `System.Text.Json` de todos modos).
  - Métodos mínimos: `string? GetLocale()` (null si nunca se guardó nada — primera vez) y
    `void SetLocale(string locale)`.
- `LocalizationService` debe consultar este servicio ANTES de `DetectSystemLocale()`: si hay
  una preferencia guardada Y sigue estando en `AvailableLocales`, usarla; si no, caer al
  flujo de detección del SO que ya existe (que a su vez ya tiene su propio fallback a inglés,
  ver arriba). Ojo con el orden de construcción — `LocalizationService` hoy se instancia sin
  dependencias (`new LocalizationService()` en `MainWindowViewModel`); si pasa a necesitar
  `AppSettingsService`, hay que revisar ese call site y cualquier otro lugar que construya
  `LocalizationService` directo.

### Fase 1 — Arreglar los 3 `GameInfo.GetStrings("en")` hardcodeados

- Mover `GetPKHeXLang(string locale)` de `PokemonEditorViewModel` (privado, ahí nomás) a un
  lugar compartido — recomendado: como propiedad/método público en `LocalizationService`
  mismo (ej. `public string PKHeXLanguageCode => GetPKHeXLang(CurrentLocale);` con el switch
  movido adentro), así cualquier ViewModel que ya tenga `_loc` inyectado lo puede usar sin
  pasar el locale a mano. Dejar el switch EXACTO que ya existe (es/fr/de/it/ja/ko/zh-CN/zh-TW
  → fallback en), no reinventarlo.
- `MainWindowViewModel.cs`: reemplazar los dos `GameInfo.GetStrings("en")` por
  `GameInfo.GetStrings(_loc.PKHeXLanguageCode)` (o el nombre final que se le dé).
- `PokemonSlotViewModel.cs`: **verificar primero si esta clase ya tiene una referencia a
  `LocalizationService` inyectada** — si no la tiene, hay que agregarla al constructor y
  revisar TODOS los call sites donde se instancia `PokemonSlotViewModel` (probablemente
  varios, uno por slot de Caja/Equipo) para pasarle la instancia compartida de `_loc`, no una
  nueva. Este es el cambio de mayor riesgo de la fase — no asumir que el constructor actual
  alcanza sin mirarlo primero.

### Fase 2 — Selector de idioma en la UI

- Ver `mockups/language_selector/` (boceto + decisiones ya tomadas) antes de tocar XAML.
- Comando `SwitchLocaleCommand(string locale)` en `MainWindowViewModel` (o donde termine
  viviendo el menú File):
  1. Si `locale == _loc.CurrentLocale`, no hacer nada (ya es el activo).
  2. Si hay ediciones sin exportar (`_editSession.HasAnyEdits`), reusar el flujo de
     confirmación que YA EXISTE para "Cerrar sin exportar" — no inventar un cuarto diálogo de
     confirmación de pérdida de datos, reusar el mecanismo (y el Rotom-Ventilador) que ya
     está implementado.
  3. Mostrar el diálogo de "reiniciar para aplicar" (ver mockup) — al confirmar: guardar el
     locale nuevo en `AppSettingsService`, y relanzar el proceso.
- **Relanzar el proceso — ojo con AppImage** (distribución target del proyecto, ver
  `context.md`): un `Process.Start(Environment.ProcessPath)` ingenuo relanza el binario
  extraído del AppImage, no el `.AppImage` original — hay que usar la variable de entorno
  `APPIMAGE` (seteada por el runtime de AppImage al binario original) si está presente,
  cayendo a `Environment.ProcessPath` si no (caso desarrollo, corriendo con `dotnet run`
  directo, sin empaquetar). Probar ambos casos antes de dar la fase por cerrada.
- Nombres de display por idioma (autoglotónimo — "Español", "English", "Français", no
  "Spanish"/"Inglés"/etc.) — tabla chica código→nombre para los idiomas conocidos
  (embebidos + `KnownLangPackLocales`), con fallback al código crudo si alguien instala un
  paquete de un idioma no contemplado en la tabla.

### Fase 3 — Migrar strings hardcodeados a `_loc[...]`

**No hacer de una sola vez** — son 121+ ocurrencias repartidas en muchas vistas. Ir pantalla
por pantalla (mismo criterio incremental que el resto del proyecto usa para mockups), y
actualizar esta sección con qué vistas ya están migradas:

- [ ] `MainWindow.axaml` — toolbar, menú File, diálogos de confirmación (Rotom x3), pantalla
      de éxito de exportación, loaders (mensajes ya via `_loc` en el C#, pero texto fijo del
      XAML como labels de botones no).
- [ ] `PokemonStatsView.axaml` (incluido el tab Diagnóstico)
- [ ] `BoxView.axaml` / `PartyView.axaml`
- [ ] `TrainerView.axaml`
- [ ] `BagPouchGridView.axaml` / `BagItemListView.axaml`
- [ ] `PokedexView.axaml`
- [ ] `SpeciesPickerView.axaml`
- [ ] Tips (`tips_ES.json` — sistema de contenido totalmente aparte, con su propio archivo
      por idioma; **evaluar si entra en este plan o si merece su propio plan** — tiene mucho
      más texto por entrada que una clave de UI simple, puede que no valga la pena
      traducirlo a todos los idiomas de golpe).

Al agregar claves nuevas a `es.json`/`en.json`, mantener el mismo estilo de nombres que ya
existe (`Dialog_*`, `Status_*`, `Action_*`) — no inventar una convención de nombres distinta
a mitad de camino.

### Fase 4 — Documentar paquetes lang para usuarios reales

- El mecanismo de carga (`/usr/share/exxeguttor/lang/`, `./lang/`) y el formato esperado del
  JSON (mismas claves que `en.json`, claves faltantes caen a inglés automáticamente — el
  fallback ya es tolerante, no hace falta que un paquete de idioma esté 100% completo) no
  están documentados en ningún lado fuera del código. Agregar una sección al README del
  repo de código (`junko012/exxeguttor`, no acá) explicando cómo armar/instalar un paquete.
- Evaluar si la lista "Disponibles para instalar" del selector (ver mockup, pendiente #3 de
  ese documento) tiene sentido en v1 sin una fuente real de descarga, o si conviene sacarla
  hasta que exista un repositorio de paquetes lang de verdad.

## Estado de avance

_Actualizar esta sección en cada sesión, con fecha aproximada y qué se tocó. No dejar tareas
"a medias" sin una nota específica de qué falta exactamente._

- **Ya aplicado, fuera de este plan formal** (hecho en la sesión donde se decidieron los
  criterios de producto de arriba, antes de que existiera este documento):
  - `LocalizationService.DetectSystemLocale()` ya cambiado: fallback sin match es `"en"`, no
    `"es"`.
- **Fase 0**: no arrancada.
- **Fase 1**: no arrancada.
- **Fase 2**: no arrancada (mockup ya existe, ver `mockups/language_selector/`).
- **Fase 3**: no arrancada.
- **Fase 4**: no arrancada.
