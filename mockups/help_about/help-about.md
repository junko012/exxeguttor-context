# Boceto: menú Ayuda y «Acerca de»

Boceto: `help-about-boceto.html` (5 escenas). Decisiones acordadas con Juan el 2026-10-30.

## Decisiones acordadas
- **Nombre del producto:** *Max Potion* (el de la UI) en menú y Acerca de. El repo y los paquetes siguen siendo `exxeguttor`.
- **Reportes:** en GitHub. El repo de código **se hará público** (ver «Antes de hacer público el repo»).
- **Alcance de la v1:** completo.

## Estado de partida
Menú `Help` con una sola entrada (`ShowAbout` es un `TODO`). Licencia GPL-3.0-or-later (README y `LICENSE`), versión 1.0.0. Preferencias en `~/.config/maxpotion/`. No hay registro de errores (solo la caja de debug del editor).

## Menú Ayuda (orden)
1. Guía rápida y consejos — `F1`. Reabre el modal de Tips (mockup `tips_stack`).
2. Atajos de teclado
3. —
4. Reportar un error… · Sugerir una función…
5. —
6. Buscar actualizaciones… · Carpeta de configuración · Carpeta de registros
7. —
8. Acerca de Max Potion

Sin atajo propio para Atajos (Ctrl+F1 choca con los espacios de trabajo de XFCE y `Ctrl+?` varía según el teclado).

## Acerca de (modal con pestañas)
- **General:** logo, nombre, versión, descripción, creador (alias + GitHub), motor (PKHeX.Core · Avalonia · .NET), licencia, enlaces (código, reportar, versiones, licencia) y aviso legal.
- **Créditos:** creador, colaboradores, traductores, terceros (PKHeX.Core GPL-3.0, Avalonia MIT, Microsoft.Data.Sqlite MIT, PokeAPI/veekun, sprites). Alimentado por `credits.json` embebido, no escrito a mano en la vista.
- **Licencias:** lista expandible con el texto completo de cada una, embebido en la app.
- **Sistema:** bloque de diagnóstico con «Copiar» y «Abrir carpeta de registros».
- **Aviso:** «Pokémon y sus nombres son marcas de Nintendo, Creatures y Game Freak. Proyecto de fans, sin afiliación. Haz un respaldo de tu save antes de editarlo».

## Reportar un error
- Un solo botón abre el navegador (`xdg-open`) en `…/issues/new?template=bug_report.yml&…` con el formulario ya prellenado. **La app no envía nada.**
- El modal explica qué se incluye y qué no, con un campo opcional «¿Qué pasó?» (el título). Si el navegador no abre, se copia el enlace.
- **Diagnóstico** (mismo texto en «Sistema»): versión, commit y fecha de build, .NET, PKHeX.Core, Avalonia, distro (`/etc/os-release`), escritorio (`XDG_CURRENT_DESKTOP`), sesión X11/Wayland, idioma UI/datos, **juego y generación del save abierto**.
- **Nunca** se incluye: nombre de entrenador, ID, rutas con el nombre de usuario (se reemplazan por `~`) ni el save. Se sugiere adjuntarlo a mano, avisando que contiene datos de la partida.
- La URL de GitHub tiene un límite práctico (~8 KB): el diagnóstico se recorta antes que el título.
- Formularios en `.github/ISSUE_TEMPLATE/`: `bug_report.yml`, `feature_request.yml` y `config.yml`. Los campos prellenados usan los `id` del formulario (`version`, `os`, `game`, `description`).

## Registro de errores y «Error inesperado»
- Registro rotativo (3 archivos de 1 MB) en `$XDG_STATE_HOME/maxpotion/logs` (por defecto `~/.local/state/maxpotion/logs`). Sin datos personales.
- Captura de excepciones no controladas (`AppDomain`, tareas y el despachador de Avalonia) y las muestra en el modal «Algo salió mal»: detalle técnico, *Copiar detalles*, *Continuar*, *Reportar este error* y *Cerrar la app*.
- No se promete que el save esté intacto; el texto solo pide revisarlo si se iba a guardar o exportar.
- Ilustración del error: **por definir**, siguiendo la convención de Pokémon con coherencia narrativa (propuestas: Rotom Dex con pantalla de error, o Porygon2 con falla).

## Buscar actualizaciones
Abre la página de *Releases* del repo en el navegador. **Sin llamadas de red** desde la app, coherente con una app que trabaja sin conexión.

## Atajos (modal)
Solo los reales hoy: `Ctrl+O` abrir, `Ctrl+S` guardar, `Ctrl+Shift+S` exportar, `Ctrl+W` cerrar save; en la revisión de exportación `← →`; en Consejos `↑ ↓`; en Crear Pokémon `← →`, `Shift+← →`, `Inicio`, `Fin`, `Enter`; `F1` guía rápida.

## Antes de hacer público el repo (checklist)
- Revisar el historial de git por tokens, claves o rutas personales (tokens de GitHub incluidos).
- Quitar saves o datos personales: tests, `scripts/`, `pokemon-database/`, capturas con nombres de entrenador.
- Confirmar atribución y licencia de los datos (`pokemon.db` viene de PokeAPI y veekun) y de la fuente de sprites e iconos.
- Agregar `THIRD-PARTY-NOTICES.md`, `.github/ISSUE_TEMPLATE/*` y una sección de créditos en el README.
- La GPL exige ofrecer el código a quien reciba los binarios: publicar el repo cubre ese punto (no es asesoría legal).

## Claves i18n nuevas (13 idiomas, ~60)
Prefijos: `Menu_Help_*`, `About_*`, `Credits_*`, `Licenses_*`, `Sys_*`, `Report_*`, `Shortcuts_*`, `Crash_*`. Español neutro, preparadas para `LocalizationService`.

## Plan de implementación (tras aprobar el boceto)
1. **Infra:** `AppInfo` (versión y commit vía `InformationalVersion`), `DiagnosticsService`, `AppLog`, `ExternalLinkService` (`xdg-open`), `IssueUrlBuilder`. Con pruebas: URL codificada y recortada, diagnóstico sin datos personales, rotación del registro.
2. **Vistas:** `AboutView` con pestañas, `ReportIssueView`, `ShortcutsView`, `CrashView`, cableado del menú y `F1`.
3. **i18n** en los 13 idiomas.
4. **Repo:** plantillas de Issues, `THIRD-PARTY-NOTICES.md`, `credits.json`.

## Pendiente de confirmar
- Nombre a mostrar del creador (hoy solo el alias `junko012`).
- Ilustración del modal de error.
- Fuente y licencia de sprites e iconos; atribución de PokeAPI/veekun.
- Créditos de traducción (las 11 de `lang/` se hicieron con asistencia de IA).
