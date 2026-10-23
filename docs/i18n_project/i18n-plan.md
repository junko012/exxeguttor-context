# Plan de idiomas de MaxPotion / Exxeguttor — v2 (2026-10-20)

**Documento vivo.** A diferencia de `context.md` (se reescribe) y `status.md` (changelog append-only), este archivo se actualiza dentro de la misma sesión a medida que se completa cada tarea: **actualiza "Estado de avance" (al final) mientras avanzas**, no al terminar. Reemplaza al plan anterior (`mockups/language_selector/i18n-plan.md`, que asumía reinicio al cambiar de idioma y un solo idioma para todo).

## 0. Verificación obligatoria al empezar (hallazgo del 2026-10-20)

`context.md` (sección "🌐 Idioma de la UI") describe un trabajo de otra sesión: `AppSettingsService`, `LocalizationService` reactivo, selector `File → Idioma`, `LocaleMenuEntry`, recarga en caliente de Caja/Equipo. **Nada de eso existe en el `master` verificado el 2026-10-20** (`c92d486` + entregas 47/48): `LocalizationService` no implementa `INotifyPropertyChanged`, no hay `AppSettingsService`, `LocaleMenuEntry` ni `SwitchLocale`, y solo `MainWindow.axaml` (7) y `EmptyStateView.axaml` (3) usan `Loc[...]`. Esa sesión nunca se integró (o se perdió). **Tratar esa sección de `context.md` como diseño, no como código existente**, y antes de empezar clonar el repo y comprobar qué hay realmente (`git grep -n "AppSettingsService\|LocaleMenuEntry"`).

## 1. Los tres sistemas de idioma (no confundirlos)

1. **Idioma de la UI** — `LocalizationService` (`src/Exxeguttor.UI/i18n/`): menús, botones, diálogos, alertas, tips, etiquetas propias. JSON por idioma: `i18n/es.json`, `i18n/en.json` (embebidos) y `lang/*.json` (ar, de, fr, hi, id, ja, ko, pt-BR, ru, zh-CN; paquetes externos en `/usr/share/maxpotion/lang` o `./lang`). Fallback: idioma activo → inglés → la clave.
2. **Idioma de los datos del juego (NUEVO, separado)** — todo lo que se lee del save o se escribe en él: especies, movimientos, habilidades, objetos, tipos, naturalezas, balls, lugares, cintas, nombres de forma. Fuente única: `GameInfo.GetStrings(código PKHeX)` por **id**.
3. **Idioma original del save** (`TrainerViewModel.Language`, idioma con el que se jugó): dato informativo, no se toca.

## 2. Decisiones cerradas (confirmadas por Juan el 2026-10-20; no re-discutir)

- **Uniformidad**: todo lo que implica datos del savefile va en **un solo idioma**; los textos propios de la app (menús, alertas, tips…) van en el idioma de la UI. Nunca habilidades en un idioma y movimientos en otro.
- **Dos idiomas independientes**: idioma de la UI e idioma de los datos, cada uno con su selector, ambos con **cambio en caliente** (sin reiniciar).
- **Inicio sin preferencia guardada**:
  1. UI = idioma del sistema si hay JSON para él; si no, inglés.
  2. Datos = idioma del sistema si PKHeX lo tiene; si no, inglés.
  3. Si no existe ninguno, ambos en inglés.
- **Opción "Igual que la UI"** para los datos (valor por defecto, `dataLocale = "auto"`): los datos siguen a la UI; si la UI está en un idioma que PKHeX no tiene (ar, hi, id, pt-BR, ru), resuelve a inglés. Si el usuario elige un idioma de datos explícito, queda fijo y deja de seguir a la UI.
- **Descripciones largas en inglés** (efecto de movimientos, habilidades y objetos: solo existen en inglés en `pokemon.db`; PKHeX no trae descripciones). Es la **única** excepción a la regla de idioma único. Etiquetas cortas propias (clase de daño Physical/Special/Status, métodos de aprendizaje, encabezados) son textos de UI y van al JSON.
- **Preferencias**: dos claves persistentes (`uiLocale`, `dataLocale`), leídas **antes** de la detección del sistema; una preferencia guardada solo vale si el idioma sigue disponible (JSON presente / PKHeX lo tiene).
- Autoglotónimos en los selectores ("Español", "English", "Français", nunca "Spanish"). Sin sección "Disponibles para instalar" en v1.
- Los **ids** son lo que se guarda en ediciones y se escribe en el save; el nombre solo se calcula al mostrar. Por eso cambiar el idioma de los datos es seguro con ediciones pendientes (se recarga el Pokémon abierto; los ids se conservan). Apodos, nombre del entrenador e idioma original del Pokémon no se tocan.

## 3. Idiomas disponibles (verificado leyendo el código fuente de PKHeX, 2026-10-20)

- **PKHeX.Core** (`GameLanguage.LanguageCodes`): `ja, en, fr, it, de, es, es-419, ko, zh-Hans, zh-Hant`. Un código desconocido cae a inglés. No tiene ar, hi, id, pt-BR ni ru.
- **Tabla UI → PKHeX** (a centralizar en un único lugar, p. ej. `DataLanguageService`): `es→es, en→en, fr→fr, de→de, it→it, ja→ja, ko→ko, zh-CN→zh-Hans, zh-TW→zh-Hant`; (opcional) `es-419`; todo lo demás → `en`.
- **BUG a corregir (Fase 1)**: `PokemonEditorViewModel.GetPKHeXLang` (≈línea 3737) mapea `zh-CN`/`zh-TW` a `"zh"`, código que PKHeX no reconoce → con la UI en chino los nombres salen en inglés. Debe ser `zh-Hans`/`zh-Hant`.
- Para los datos, el selector ofrece los idiomas PKHeX (en, es, fr, de, ja, ko, zh-Hans, zh-Hant; it y es-419 si se decide agregarlos, sin costo de traducción de datos). Para la UI, los que tengan JSON (hoy 12; italiano y es-419 necesitarían su JSON).
- PKHeX WinForms usa **un solo** selector que cambia UI, nombres y reportes juntos; el diseño de MaxPotion (dos selectores, "Igual que la UI") es deliberadamente más flexible.
- Costo: `GameInfo.GetStrings(lang)` carga y cachea las listas **una vez por idioma** (carga perezosa, "costo no despreciable" según su propia documentación). No llamarla por fila/slot: guardar un diccionario id→nombre del idioma activo en un servicio y recargarlo solo al cambiar el idioma de los datos. **Medir** tiempo de carga y memoria al implementarlo (no hay medición todavía).

## 4. Estado verificado del código (2026-10-20, master `c92d486` + entregas 47/48)

- `LocalizationService`: `AvailableLocales = {es, en}` + `lang/*.json` detectados; `DetectSystemLocale` (fallback `en`); soporte RTL (`IsRtl`); sin notificación de cambio; nadie llama `Load()` tras el arranque.
- Por id desde PKHeX (en el idioma de la UI): objeto equipado, habilidad, ball (ediciones por id desde el 11 oct), naturaleza, especie y ubicaciones del panel Info, movimientos cargados del save, Tera Type, `PokedexNames.Display`, `EvolutionNameLocalizer`.
- **Aún en inglés fijo (DB)**: movimientos elegidos en el modal, Learnsets/Sets, pastillas de tipo, Effectiveness, Mega Stones/Z-Crystals y Z-Moves, nombres de objetos de la Mochila, cintas, nombres de especie en slots de Caja/Equipo y mensaje post-creación (`GameInfo.GetStrings("en")` en `PokemonSlotViewModel` y `MainWindowViewModel`).
- **Textos de UI**: casi todo son literales en `.axaml` (español o inglés mezclados), incluidos los de pantallas recientes (modal de recrear, tab Legal, tarjetas Special/Moves, loaders y diálogos de Rotom, Pokédex) y los mensajes de `LegalityMessageMapper` (español fijo). JSON actual: ~118+ claves (más las `Recreate_*`).

## 5. Plan de fases (cada fase deja la app compilando; una entrega por fase o tanda)

### Fase 0 — Preferencias
- `AppSettingsService` (capa App, mismo patrón que `RecentSavesService`: `Environment.SpecialFolder.ApplicationData`, ctor interno para tests). Archivo `~/.config/maxpotion/settings.json` (**maxpotion**, no exxeguttor: ver regla de nombres) con `{ "uiLocale": "...", "dataLocale": "auto" }`; deserialización tolerante a claves desconocidas. Métodos: `GetUiLocale/SetUiLocale`, `GetDataLocale/SetDataLocale`.

### Fase 1 — Infraestructura de idioma
- `LocalizationService`: implementar `INotifyPropertyChanged` (notificar `"Item[]"` y `CurrentLocale`); consultar `AppSettingsService` antes de `DetectSystemLocale`; propiedades computadas + handler central (`OnLocaleChanged`) para los textos "asignados una vez" (`Title`, textos de éxito de exportación…).
- **`DataLanguageService`** (nuevo): resuelve el código PKHeX activo (`auto` → sigue a la UI; explícito → fijo; sin soporte → `en`), expone diccionarios id→nombre cacheados (especies, movimientos, habilidades, objetos, tipos, naturalezas, balls, lugares), notifica el cambio de idioma de los datos. Corrige el bug `zh` → `zh-Hans/zh-Hant`. Reemplaza `GetPKHeXLang` y los `GetStrings("en")`.

### Fase 2 — Selectores
- **Menú propio «Preferencias»** entre `File` y `Help` (acordado 2026-10-20) con dos submenús: «Idioma de la interfaz» e «Idioma de los datos» (con «Igual que la interfaz» marcado por defecto). Solo texto con autoglotónimo y código corto, **sin banderas**; marca de activo `✓` verde. **Indicador en la barra de estado** (píldora `UI ES · PK ES`: interfaz · datos; ámbar si los datos caen a inglés; clic abre un popover con los dos idiomas). Diseño visual: `mockups/language_selector/language-selector-v2-boceto.html` y `language-selector-v2.md`. `LocaleMenuEntry` con `Command` ya armado (el `Style` del `MenuItem` solo bindea `Command`). Al cambiar: guardar preferencia, recargar Caja/Equipo (suscripción a `PropertyChanged`), recargar el Pokémon abierto (los diccionarios nombre→id de `PokemonEditorViewModel` se arman en `LoadPokemon`) conservando ediciones pendientes, y refrescar Pokédex y Mochila.
- Sin diálogo de reinicio. Si el modal de Tips está abierto al cambiar, recargarlo (requiere sacar la carga de categorías del constructor de `TipsViewModel`).

### Fase 3 — Datos del juego por id (tandas; una entrega cada una)
1. Slots de Caja/Equipo y mensaje post-creación (ya hay `LoadFrom(pkm, pkhexLang)`).
2. Movimientos: modal selector, Learnsets, Sets (las ediciones de movimiento deben pasar a ids; `MoveDatabase.GetByName` deja de ser llave).
3. Tipos (pastillas, Effectiveness, selector de Tera) — nombres de tipo desde PKHeX.
4. Mega Stones, Z-Crystals y Z-Moves (`MegaStoneDatabase`, `ZCrystalDatabase`; ojo `ItemId` vs `RawItemId`).
5. Mochila (`BagPouchDatabase`, nombres de ítems por id), cintas (PKHeX trae `text_Ribbons_*`).
6. Revisar `EditSessionService` (resumen de ediciones muestra nombres: construirlos con el idioma de los datos activo) y `LegalityMessageMapper`/formatters.
- Cada tanda: tests de "nombre → id → mismo índice" por idioma (patrón de `NameToIdIndexTests`) y sondeo de que el idioma de datos nunca se mezcla.

### Fase 4 — Textos de UI a `Loc[...]` (pantalla por pantalla; marcar abajo)
- [x] `MainWindow.axaml` (toolbar, menú, diálogos Rotom, éxito de exportación, loaders) — entrega 57 (sin compilar): 64 literales a claves `Rail_*`, `Toolbar_*`, `Notebook_*`, `Editor_*`, `Tab_*`, `Review_*`, `Dialog_*`, `Tips_*`, `Loader_Verify_*`; mensajes de estado/ocupado de `MainWindowViewModel` a `Status_*`/`Busy_*`
- [ ] `PokemonStatsView.axaml` (todos los tabs, incl. Legal y las tarjetas Special/Moves)
- [ ] `PokemonInfoView` (etiquetas IDENTITY/STATUS/ORIGIN y campos), `TrainerView`
- [ ] `BoxView`/`PartyView`, `BagPouchGridView`/`BagItemListView`, `PokedexView`, `SpeciesPickerView`
- [ ] Modales: exportación/revisión, `RecreateView` (`Recreate_*` ya tiene es/en), `AutoFixView`, IV solver
- [ ] Mensajes del diagnóstico (`LegalityMessageMapper`/`LegalityEncounterFormatter`…): hoy en español fijo; decidir si se parametrizan por clave o se usan los textos de PKHeX por idioma
- [ ] Tips (`tips_ES.json`: contenido por idioma, plan propio si se traduce)
- Estilo de claves existente: `Dialog_*`, `Status_*`, `Action_*`, `Menu_*`, `Recreate_*`, `Form_Name_*`. Usar `{Binding Loc[Clave]}` directo en XAML.

### Fase 5 — Cierre
- README del repo de código: formato y ruta de paquetes lang (`/usr/share/maxpotion/lang`, `./lang`), claves faltantes caen a inglés.
- Opcional: JSON de `it` y `es-419` para la UI.
- Probar con `LANG=es_ES.UTF-8 LC_ALL=es_ES.UTF-8 dotnet run --project src/Exxeguttor.UI`, cambio en caliente con Pokémon abierto y ediciones pendientes, y un idioma sin PKHeX (ru) con datos en inglés.

## 6. Reglas para código nuevo (mientras dure la migración)
- Nada de `GameInfo.GetStrings("en")` fijo: usar el idioma de los datos activo.
- Nada de llaves por nombre: ediciones y comparaciones por id.
- Textos nuevos de UI: clave en `es.json`/`en.json` y `{Binding Loc[...]}`; propiedades de C# que envuelvan `_loc[...]` deben notificarse en `OnLocaleChanged`.
- Descripciones largas de la DB: se muestran en inglés (decisión cerrada).

## 7. Riesgos y pendientes
- ar/hi/id/pt-BR/ru: datos en inglés (no hay fuente PKHeX); ar requiere RTL ya contemplado en `IsRtl`.
- Contadores y listas dependientes del idioma (ordenar alfabéticamente por nombre) pueden cambiar de orden al cambiar el idioma de datos.
- Rendimiento: medir carga de `GetStrings` por idioma y memoria (Fase 1).
- Movimientos en el modal: un mismo nombre puede no ser único entre generaciones; resolver por id.

## Estado de avance
- 2026-10-20: plan v2 acordado con Juan (diseño cerrado, sin código). Boceto visual v2 hecho (menú Preferencias + indicador). Verificado que la infraestructura descrita en `context.md` no está en `master`.
- 2026-10-21 (entrega 49, **sin compilar** — el sandbox no tiene dotnet): **Fases 0, 1 y 2 implementadas** + Fase 3 tanda 1 parcial.
  - Fase 0 ✔ `AppSettingsService` (App) — `~/.config/maxpotion/settings.json`, claves `uiLocale`/`dataLocale`, lectura tolerante, cada escritura relee el archivo (no pisa claves ajenas).
  - Fase 1 ✔ `LocalizationService` implementa `INotifyPropertyChanged` (notifica `"Item[]"`, `CurrentLocale`, `IsRtl`), arranca con preferencia guardada → sistema → **inglés** (antes caía a español), y tiene `SetLocale()` (en caliente + persiste). `DataLanguageService` (App, singleton `Instance`): `auto`/explícito, `PkhexCode`, `FallsBackToEnglish`, `Strings`, evento `Changed`, tabla UI→PKHeX única. **Bug `zh` corregido** (→ `zh-Hans`/`zh-Hant`) en `PokemonEditorViewModel.GetPKHeXLang`, `FormNameFormatter.PkhexLang`, `IvSolverViewModel.BuildRows` y `EvolutionNameLocalizer.PkhexLang`.
  - Fase 2 ✔ menú **Preferencias** (entre File y Help) con dos submenús (`LocaleMenuEntry`, ✓ en el Header), píldora `UI ES · PK ES` en la barra de estado (ámbar si los datos caen a inglés) con popover. Al cambiar: `OnLocaleChanged` (título, textos de éxito de exportación, listas del menú) y `OnDataLanguageChanged` (recarga Caja, Equipo, Pokémon abierto conservando ediciones pendientes, y Pokédex si está abierta).
  - Fase 3 tanda 1 (parcial) ✔ nombre de especie de las casillas de Caja/Equipo y mensaje/loader post-creación usan el idioma de los datos. **Sin tocar a propósito**: `GetStrings("en")` de `PokemonSlotViewModel` (llave del sprite del objeto) y `PokemonEditorViewModel` ≈3126 (índice nombre-en-inglés → sprite).
  - **No hecho de Fase 2**: botones «Cambiar interfaz…/Cambiar datos…» del popover, «Abrir carpeta de paquetes de idioma…», esquinas redondeadas del `MenuItem`, marca ✓ verde (hoy va en el texto del Header), leyenda «datos en inglés» en una segunda línea (hoy en la misma). Recarga del modal de Tips abierto.
  - **Limitaciones conocidas**: `StatusMessage` con un mensaje ya mostrado ("Guardado cargado…") queda en el idioma anterior hasta el próximo cambio de estado; el resto de textos de UI sigue hardcodeado hasta la Fase 4; `PokedexViewModel`/`PokedexService`/`EvolutionNameLocalizer` siguen usando el idioma de la UI para sus nombres (pasan a datos en la Fase 3).
  - Tests nuevos: `tests/Exxeguttor.Tests/DataLanguageServiceTests.cs` (settings + resolución + un test que carga `GameInfo.GetStrings` por cada código seleccionable). `Exxeguttor.App.csproj` suma `InternalsVisibleTo Exxeguttor.Tests` (sin él, los ctors internos "para tests" de `RecentSavesService`/nuevos no eran accesibles).
  - **Medición pendiente** (plan §3): tiempo de carga y memoria de `GetStrings` por idioma — correr en tu PC, no hay números todavía.
- 2026-10-21 (entrega 50, **sin compilar**): **Fase 3 tanda 2 — movimientos por id e idioma de los datos.**
  - `GetLearnsets` devuelve `MoveId` (`LearnsetDbEntry.MoveId`); `LearnsetEntry`/`MoveOption` lo llevan. El selector de movimientos agrupa y marca el movimiento actual **por id** (antes por nombre inglés).
  - Nombres de movimiento (learnsets, selector, slots del editor) salen de `DataLanguageService.Strings.Move`; el tooltip se resuelve por id.
  - Edición por id: el editor expone `Move1Id…Move4Id` (se cargan del PKM, se registran como edición y entran en `LegalityRelevantFields`); `EditApplyService` y `EditSessionService.AnalyzeLegality` aplican el id y solo caen al nombre si no hay id (mismo patrón que `AbilityId`/`HeldItemId`/`BallId`). Al restaurar ediciones pendientes los nombres se re-derivan de los ids (`ReapplyMoveNamesFromIds`). `IsSameMove` (Z-Moves) prueba primero el nombre localizado.
  - Tests: `LearnsetMoveIdTests` (ids >0 y coherentes con `GameInfo.GetStrings("en").Move`; nombre presente en es/fr/de/ja/ko/zh).
  - **Pendiente de la tanda 2**: Sets recomendados (`MovesetDatabase.ResolvedMoves` sigue por nombre inglés de la DB), tipos y clase de daño de los movimientos (siguen en inglés).
  - **Tanda 3 (tipos) NO hecha, a propósito**: `Type1/Move1Type/...` se usan como llave de iconos/colores/efectividad; localizar el texto exige separar «llave» de «texto mostrado» en los converters y vistas. Hay que mirar esos converters antes de tocarlos.
  - Caso borde conocido: si se cambia el idioma de los datos a mitad de sesión después de editar un movimiento, el nombre «prístino» guardado quedó en el idioma anterior; revertir a mano al movimiento original puede seguir contando como cambio en el resumen (el id sí revierte bien).
- 2026-10-21 (entrega 51, **sin compilar**): **Fase 3 tanda 3 — tipos.** Se separa la LLAVE (inglés, colores/efectividad) del TEXTO mostrado (idioma de los datos).
  - `TypeNames` (App): `IndexOf`/`ToKey`/`Localize` de los 18 tipos base; acepta el nombre inglés o el del idioma de los datos activo; "Todos", "Stellar" y cualquier otra cadena pasan sin tocar. `TypeNameConverter` (UI, registrado en `App.axaml`) lo usa **solo en el texto** de 21 bindings (`PokemonInfoView`, `PokemonStatsView`, `SpeciesPickerView`: Type1/2, Poder Oculto, tipo de cada movimiento, Mega, Z-Move, Tera, debilidades, chips de filtro).
  - `TypeColorConverter.GetBaseColor` normaliza con `TypeNames.ToKey` (los conversores «suave» y de texto ya pasaban por ahí): antes el color de Tera/Poder Oculto se perdía con datos en fr/de/ja/ko/zh porque la tabla solo tenía inglés y español. La tabla de debilidades del editor usa `ToKey` (antes pasaba `strings.Types[...]` localizado a `TypeEffectivenessDatabase`).
  - Tras cambiar el idioma de los datos, `ReloadForDataLanguage` dispara `OnPropertyChanged(string.Empty)` en el editor: la cadena del tipo no cambia, así que los converters no se reevaluaban solos.
  - Tests: `TypeNamesTests` (18 tipos × 7 idiomas, ida y vuelta; usa overloads internos con lista explícita para no tocar el singleton ni las preferencias reales).
  - **Fuera de alcance (Fase 4, son textos de UI, no datos de PKHeX)**: clase de daño (Physical/Special/Status), el chip «Todos». **Pendiente**: Sets recomendados por id; el modal de selección de especie y la Pokédex no se refrescan en vivo (se reevalúan al reabrirse); chips de filtro por tipo quedan con el texto del momento en que se abrió el modal.
- 2026-10-21 (entrega 52, **sin compilar**): **Fase 3 tanda 4 — Mega Stones, Z-Crystals y Z-Moves.**
  - `MoveNames` (App): resuelve un nombre de movimiento escrito en inglés en una tabla de dominio («Volt Tackle», «Breakneck Blitz») a su id de PKHeX (normalizado: sin mayúsculas/apóstrofos/guiones) y de ahí al nombre del idioma de los datos. El inglés queda solo como llave canónica de `ZCrystalDatabase`, nunca como texto mostrado.
  - Editor: opciones de Mega Stone con el nombre de objeto de PKHeX (idioma de los datos; pokemon.db solo de respaldo); nombre de la forma Mega con la especie de PKHeX + plantilla `Form_Name_Mega` («Mega {0}», es/en; otros idiomas caen a inglés) y sufijo X/Y; tipos del resumen Mega localizados; en Z-Moves se localizan el movimiento requerido del cristal exclusivo, el nombre del Z-Move resultante y el tipo citado en notas/avisos. `IsSameMove` resuelve el movimiento requerido por id vía `MoveNames` antes de caer a `MoveDatabase`.
  - `ZCrystalDatabase`/`MegaStoneDatabase` **no se tocaron**: sus ids ya eran los del objeto equipado (`ItemId`) y siguen siendo la llave; `RawItemId` (mochila) sigue igual.
  - Tests: `MoveNamesTests` (los 51 nombres ingleses de `ZCrystalDatabase` resuelven a id y tienen nombre en es/fr/de/ja/ko/zh; ids de Mega Stones y Z-Crystals equipados con nombre de objeto en 8 idiomas). La lista de nombres se repite en el test porque el proyecto de tests solo referencia App — si se agrega un cristal, agregarlo ahí también.
  - **Sigue en español fijo (Fase 4)**: «Tipo … · BST», «✗ Sin Z-Crystal equipado», «(requiere …)», «Reemplazó: …» y demás frases de las tarjetas Mega/Z-Moves.
- 2026-10-21 (entrega 53, **sin compilar**): **Fase 3 tanda 5 (parcial) — nombres de ítems de la Mochila.** Cintas NO hechas.
  - `ItemInventoryService.GetItems` calcula `BagItemInfo.DisplayName` con `GameStrings.GetItemStrings(save.Context, save.Version)` (lista de objetos de PKHeX **para ese juego**, instancia en el idioma de los datos; firma verificada contra el código fuente de PKHeX en GitHub) indexada por `RawItemId` — la misma forma que usa el editor de mochila de PKHeX. Sin nombre (o ítems sintéticos de Colosseum/XD, `ItemId >= 90000`) → se muestra el nombre de pokemon.db como antes. `Name` (inglés de pokemon.db) sigue siendo la llave del sprite; el orden alfabético usa el nombre mostrado.
  - `BagItemRowViewModel` muestra `DisplayName ?? name`; `BagViewModel.ReloadForDataLanguage()` descarta el cache de filas y reconstruye la categoría visible (MainWindowViewModel lo llama en `OnDataLanguageChanged`). Las ediciones pendientes se reaplican y su nombre capturado se refresca al idioma actual.
  - `BagItemEditValue`: la igualdad ahora **ignora el nombre** (solo cuenta `Quantity`): `RecordEdit` detecta «volvió al original» con `Equals`, y con el nombre dentro cambiar de idioma a mitad de sesión dejaba ediciones revertidas como cambios.
  - Tests: `BagItemNamesTests` (sondeo: `GetItemStrings` por idioma y juego, id 1 con nombre).
  - **Pendiente**: (1) **Cintas** — `RibbonDatabase` tiene nombres escritos a mano (es/en mezclados) por `RibbonIndex`; PKHeX trae `GameStrings.Ribbons` (`RibbonStrings`), pero no pude verificar su API en este sandbox: falta confirmar `GetName(...)` y la correspondencia `RibbonIndex` ↔ nombre de propiedad antes de tocarlo. (2) Nombres de las categorías de la Mochila (`BagPouchDatabase.DisplayName`: «Objetos», «Medicina»…) y «Mochila/PC» son textos de UI → Fase 4. (3) La descripción del ítem sigue en inglés (decisión cerrada).
- 2026-10-21 (entrega 54, **sin compilar**): **correcciones de pruebas reales (Platino, datos en ES).** Captura de Juan: naturalezas en inglés, combo de Naturaleza vacío al cargar un Pokémon (solo se veía con datos en EN), tipos de la pestaña Efectividad en inglés.
  - **Causa (naturalezas)**: `NatureDatabase` era inglés fijo, pero `Nature` se cargaba como `strings.Natures[...]` (idioma de los datos): el combo buscaba «Audaz» entre «Adamant…» y no encontraba nada; además `EditApplyService` hace `Enum.TryParse<Nature>`, así que una edición con nombre localizado se descartaba en silencio al exportar. Hardy (Nature 0) también quedaba vacío por `pkm.Nature > 0`.
  - **Arreglo**: `Nature` guarda la LLAVE inglesa (nombre del enum, mismo orden que el valor numérico); `NatureEntry` gana `Id` y `LocalizedName` (de `GameStrings.Natures`, idioma de los datos) y el combo muestra «Audaz (+Atq, -AtqE)» / «Fuerte (neutra)» con las abreviaturas de stat en el idioma de la UI (claves nuevas `Nature_Neutral`, `Stat_Short_*`, hook `NatureDatabase.Translate`). `NatureNameConverter` localiza la naturaleza de los Sets recomendados. La lista del combo se recrea en cada carga para que cambiar de idioma regenere el texto.
  - **Efectividad/Pokédex**: las chips de tipo de las listas de debilidades (`PokemonStatsView` ×4) y los badges de `PokedexView` (×3) usaban `{Binding}` sin propiedad, que mi barrido de la tanda 3 no cubría; ahora pasan por `TypeNameConverter`.
  - **Bonus detectado en la captura**: el sprite del objeto equipado no se veía con datos ≠ EN (el converter buscaba el sprite por el nombre localizado). `ItemNameToSpriteConverter` traduce primero a inglés por id.
  - Tests: `NatureNamesTests`. **Pendiente**: los Sets recomendados siguen por nombre inglés; sprites de la lista de Balls con datos ≠ EN sin revisar.
- 2026-10-21 (entrega 55, **sin compilar**): **Sets recomendados en el idioma de los datos.**
  - **Bug de fondo**: la pestaña Sets buscaba por `strings.Species[...]` (idioma de los datos) pero el JSON de Showdown/Smogon está indexado por nombre INGLÉS (`ShowdownName(englishSpeciesName, …)`): con datos ≠ EN la pestaña quedaba vacía. Ahora usa `GameInfo.GetStrings("en")` como llave canónica.
  - `GameNames` (App): habilidad/objeto en inglés → id de PKHeX → nombre del idioma de los datos; normalización sin acentos/mayúsculas/signos («Poké Ball» == «Poke Ball», «Will-O-Wisp» == «will o wisp»), compartida con `MoveNames`. Sin id (p. ej. «Hidden Power Fire») pasa sin cambios.
  - `RecommendedSet`: `AbilityDisplay`, `ItemDisplay` y `TeraTypeDisplay` (cada tipo localizado) calculados al leer; `SetMoveEntry.MoveName` ahora es de solo lectura sobre `EnglishName` (llave para tipo/poder en pokemon.db). **Nada se cachea localizado**: las instancias de `RecommendedSet` viven en `MovesetDatabase` y el idioma cambia en caliente. La vista usa `AbilityDisplay`/`ItemDisplay`; el sprite del objeto sigue por la llave inglesa. Los nombres de set («Offensive», «Calm Mind + Roost») y las etiquetas «Ability:/Item:/Lv.» (Fase 4) siguen como están.
  - Tests: `GameNamesTests`.
  - **Pendiente de Fase 3**: cintas (verificar `RibbonStrings`), tanda 6 (resumen de ediciones, formatters de legalidad).
- 2026-10-21 (entrega 56, **sin compilar**): **Fase 3 tanda 6 — idioma global de PKHeX, ubicaciones y formatters de legalidad.**
  - **Hallazgo (captura de Juan: «Route 217» en inglés con datos en ES)**: el proyecto nunca configuraba el idioma GLOBAL de PKHeX (`GameInfo.Strings`/`CurrentLanguage`, por defecto inglés). De ahí leen `GameInfo.GetLocationList` (ubicaciones de captura/huevo del panel Origen y de `EncounterRecreationService`), `ILocation.GetEncounterLocation` y `LegalityArgumentFormatter` (`GameInfo.Strings.Ability`). Comentarios viejos del código decían «GameInfo.Strings no está inicializado en este proyecto todavía».
  - `DataLanguageService.ApplyToPkhexGlobals()`: alinea `GameInfo.CurrentLanguage` y `GameInfo.Strings` (el setter reconstruye `GameInfo.Sources`) con el idioma de los datos. Se llama desde `MainWindowViewModel` al arrancar y como PRIMER paso de `OnDataLanguageChanged` (antes de recargar el editor, que vuelve a pedir las listas de lugares). No se llama desde el ctor ni `SetUiLocale` a propósito: es estado global del proceso y los tests que crean instancias propias no deben tocarlo. Firmas verificadas contra `GameInfo.cs` de PKHeX en GitHub.
  - Formatters de legalidad: nombres de movimiento (`LegalityMoveFormatter` ×2, `LegalityArgumentFormatter`) y de especie (×2) por id desde el idioma de los datos (`GameNames.MoveName`/`SpeciesName`), con pokemon.db y «movimiento #id» como respaldo. Los mensajes en sí (texto en español fijo) siguen siendo Fase 4.
  - `EditSessionService`: revisado — no hay nombres de datos fuera de la Mochila (ya resuelta en la entrega 53); sus etiquetas son texto de UI (Fase 4).
  - Tests: `DataLanguagePkhexGlobalsTests` (idioma global y listas de ubicaciones de Platino distintas en es vs en; restaura el estado global al terminar), `GameNamesByIdTests`.
  - **Pendiente de Fase 3**: solo cintas (`RibbonDatabase` a mano; verificar API de `RibbonStrings`) y los nombres de idiomas de juego de `LegalityArgumentFormatter.LanguageName` (texto fijo). Medición de tiempo de `ApplyToPkhexGlobals` (reconstruye `GameDataSource`): pendiente en la PC de Juan.
- 2026-10-21 (entrega 57, **sin compilar**): **Fase 4, pantalla 1: `MainWindow`.**
  - 64 textos fijos de `MainWindow.axaml` → `{Binding Loc[Clave]}` (barra lateral, libreta, barra de herramientas, vista previa del editor vacío, descripciones de las pestañas, modal de revisión, tres diálogos Rotom, tips, pasos del loader de legalidad). Dentro de `DataTemplate` (cuyo DataContext no tiene `Loc`) se usa `{ReflectionBinding $parent[Window].DataContext.Loc[Clave]}` (4 sitios: sufijo de la libreta y tres textos de las tarjetas de revisión).
  - Los contadores («1 de 3 seleccionados», «2 a revisar», «N cambios») siguen armados con `<Run>` + sufijo localizado (`Review_Of`, `Review_SelectedSuffix`, `Review_ToReviewSuffix`, `Notebook_ChangesSuffix`): sirve para es/en, pero no permite reordenar palabras en idiomas donde el número va al final. Si un idioma lo necesita, pasar a propiedades con `string.Format` en el ViewModel.
  - `MainWindowViewModel`: mensajes de estado y de ocupado (`No había cambios pendientes`, `Ediciones descartadas…`, `Generando a {0}…`, `{0} creado…`, `No se pudo crear…`, `Guardando…`, `Analizando legalidad…`, catálogo de especies) y el título del diálogo de exportar archivo a claves (`Status_*`, `Busy_*`). **No tocados**: los tres mensajes de arranque de `onProgress` (método estático sin `_loc`; pertenecen al splash, pantalla propia de la Fase 4).
  - Los nombres de pestaña (`Tab_*`) tienen el mismo texto en es y en («Moves», «Learnsets»…) como ya se veían; quedan como claves para poder traducirlos por idioma. La pantalla siguiente (`PokemonStatsView`) debe reutilizarlas.
  - Claves nuevas: 56 + 8 en `es.json`/`en.json` (los demás idiomas caen a inglés).
- Fase 0: ✔ · Fase 1: ✔ · Fase 2: ✔ (con los faltantes de arriba) · Fase 3: tandas 1 (parcial), 2, 3, 4 y 6 hechas; 5 parcial (ítems de Mochila sí, cintas no) · Fase 4: no arrancada · Fase 5: no arrancada.
