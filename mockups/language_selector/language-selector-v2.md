# Boceto v2: menú Preferencias e idioma (interfaz + datos)

Reemplaza al boceto original (`language-selector-boceto.html`, `language-selector.md`), que asumía un solo idioma y reinicio al cambiar. El boceto vigente es `language-selector-v2-boceto.html`; el plan, `docs/i18n_project/i18n-plan.md`. Decisiones acordadas con Juan el 2026-10-20.

## Decisiones
- **Menú propio «Preferencias»** entre `File` y `Help` (no dentro de `File`: cambiar de idioma no es una acción sobre un save, y habrá más preferencias). Contiene dos submenús: **Idioma de la interfaz** e **Idioma de los datos**.
- **Solo texto, sin banderas.** Una bandera es un país, no un idioma (español, inglés, portugués, chino simplificado/tradicional) y no existe para hindi, indonesio o árabe; además, las banderas emoji no se muestran en Windows. Cada idioma se escribe en su propio idioma ("Español", "English", "Français", "日本語") con un código corto (`ES`) como apoyo visual.
- **Marca de activo**: `✓` verde `#1D9E75` y fondo `#E6F6F0` (misma familia que el subrayado verde de los rails). Hover gris `#ECEEF2`; bordes `#DCDCE0`/`#D5D8DE`; tinta `#1F2937`.
- **Interfaz**: lista los idiomas con JSON; los que no tienen datos en PKHeX (ru, ar, hi, id, pt-BR) llevan debajo la leyenda «Datos del juego en inglés». Al pie, «Abrir carpeta de paquetes de idioma…».
- **Datos**: primera fila «Igual que la interfaz» (por defecto, borde punteado verde, muestra a qué idioma resuelve hoy) y debajo los idiomas de PKHeX (en, es, fr, de, ja, ko, zh-Hans, zh-Hant; it y es-419 si se agregan). Nota azul: las descripciones largas siempre en inglés.
- **Indicador en la barra de estado** (abajo a la derecha, junto al estado del save): píldora `UI ES · PK ES` (UI = interfaz, PK = datos del juego). Se vuelve **ámbar** solo cuando los datos caen a inglés por falta de idioma en PKHeX. Un clic abre un popover «Idiomas activos» con los dos valores, un aviso ámbar si aplica y botones «Cambiar interfaz…» / «Cambiar datos…» que abren los submenús.
- Cambio **en caliente**, sin diálogo de reinicio. Sin sección «Disponibles para instalar».
- Sin animación temática ni mascota: es una selección puntual.

## Escenas del boceto
1. Idioma de la interfaz (submenú abierto). 2. Idioma de los datos. 3. UI en ruso: datos en inglés (indicador ámbar y popover con aviso). 4. Indicador / popover.

## Pendiente de implementación
- Estilos Avalonia: `MenuItem`/`Popup` con las esquinas redondeadas y la paleta de arriba; `LocaleMenuEntry` con `Command` ya armado.
- Textos nuevos (`Menu_Preferences`, `Menu_Prefs_UiLanguage`, `Menu_Prefs_DataLanguage`, `Lang_Auto`, `Lang_DataFallbackEnglish`…) en `es.json`/`en.json`.
- Accesibilidad: el indicador es un botón con `AutomationProperties.Name`; el estado ámbar no depende solo del color (el popover lo explica con texto).
