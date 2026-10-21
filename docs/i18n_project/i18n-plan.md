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
- [ ] `MainWindow.axaml` (toolbar, menú, diálogos Rotom, éxito de exportación, loaders)
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
- Fase 0: no arrancada · Fase 1: no arrancada · Fase 2: no arrancada · Fase 3: no arrancada · Fase 4: no arrancada · Fase 5: no arrancada.
