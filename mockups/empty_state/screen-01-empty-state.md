# Pantalla 1 — Estado vacío / Carga de save

> Diseñada en sesión de UI/UX separada (Claude, chat). Este documento + el boceto
> `screen-01-empty-state.html` adjunto son el hand-off para la sesión de implementación.
> Ver también `CLAUDE.md` / `context.md` del proyecto para contexto general de arquitectura.
>
> **Estado: implementado.** Este `.md` refleja la versión final tal como quedó en código
> (`EmptyStateView.axaml`, `MainWindowViewModel.cs`, `RecentSavesViewModel.cs` y afines en
> `exxeguttor`), no el hand-off original — ver "Historial de cambios respecto al hand-off
> original" al final para el detalle de qué cambió y por qué.

## Qué reemplaza

La pantalla vacía actual (`MainWindow` cuando no hay save cargado) hoy solo muestra un
texto centrado ("Open a save file to get started") y un botón "Open save...". Este diseño
la reemplaza por dos zonas: **recientes** (izquierda) y **acción principal** (derecha).

## Layout

```
┌───────────────────────────────┬──────────────────────────────────────┐
│  RECIENTES (panel izquierdo)  │   ZONA DE ACCIÓN                      │
│  ancho = 400px                 │   centrada vertical y horizontalmente │
│  (igual a la columna derecha   │                                       │
│  de MainWindow.axaml)          │                                       │
└───────────────────────────────┴──────────────────────────────────────┘
```

- Panel izquierdo y zona derecha viven dentro del mismo contenedor raíz que hoy
  centra el texto/botón — se reemplaza ese contenido, no la ventana completa.
- Separador vertical de 1px (`var`/color de borde estándar de la app) entre ambas zonas.
- Sin scroll en la zona de acción; el panel de Recientes sí tiene `ScrollViewer` propio
  (por si en el futuro se sube el máximo de 5 entradas).

## Zona "Recientes" (panel izquierdo)

- Título de sección: "Recientes" (texto fijo por ahora, no i18n — pendiente si se
  agrega clave `Recent_Title` más adelante).
- Lista vertical de hasta 5 entradas (más reciente arriba). Sin recientes → la zona
  completa no se muestra — la columna colapsa a 0 (`Auto` sin contenido visible) y la
  zona de acción ocupa todo el ancho, sola.
- Cada fila (de arriba hacia abajo):
  1. **Sprite de portada del juego**: rectángulo 26×34px, `CornerRadius=4`. Sprite real si
     existe en `Assets/sprites/games/{codigo}.png` (código crudo de `GameVersion.ToString()`
     en minúscula, ej. `sv.png`, `za.png` — ver `ExpandGameName()` en `TrainerViewModel` para
     la lista completa de códigos). **Hoy esa carpeta está vacía** — todas las portadas caen
     en el fallback procedural: degradado + glyph por generación (ver tabla más abajo,
     resuelto por `GameCoverService`).
  2. **Nombre de archivo** (ej. `pokemon_yellow.sav`), una línea, elipsis si excede ancho.
  3. **Subtítulo**: `{NombreJuego} · Gen {N}` (usa `ExpandGameName()` de `TrainerViewModel`,
     subido de `private` a `internal` para poder reusarlo desde el ViewModel de esta pantalla
     sin duplicar el mapeo).
  4. **Fecha relativa**, alineada a la derecha de la fila: "Hoy · HH:mm", "Ayer",
     o fecha corta ("12 ago") si es más antigua.
- Fila superior (más reciente) con fondo levemente distinto (`surface` un tono más claro
  que el resto de la lista) para destacarla como "la última usada".
- Click en cualquier fila → abre ese save directamente (mismo flujo interno que el botón
  "Abrir save...", vía `MainWindowViewModel.OpenSaveFromPathAsync`).

## Zona de acción

De arriba hacia abajo, todo centrado horizontal y verticalmente dentro de su mitad:

1. Texto: "No hay ninguna partida cargada".
2. Botón primario: "Abrir save..." (mismo comando de siempre, `OpenSaveFileCommand`).
3. Etiqueta pequeña: "Formatos soportados".
4. Fila de badges chips (pill, borde 1px, fondo blanco, texto chico ~10px):
   `Gen 1-9` · `.sav` · `.dsv` · `.gci / .bin / .bak` · `main (Switch)`.

**No hay drag & drop.** El hand-off original lo incluía (badges + ícono de upload + texto
"Arrastra tu save aquí / o"); se sacó por completo en implementación — ver el historial de
cambios al final para el motivo (no es negociable con más tiempo de desarrollo, es un límite
real de la versión de Avalonia que usa el proyecto).

## Modal de error al abrir un save

Los 4 casos con boceto propio en `mockups/error_empty_state/` (`screen-01-error-messages.md`)
están implementados: un modal centrado, overlay semitransparente sobre toda la pantalla,
sprite Pokémon temático con animación en loop + título + mensaje, según el tipo de error
(`SaveOpenErrorKind` en código): Ditto (save inválido), MissingNo. (corrupto), Abra (archivo no
encontrado — único con botón secundario "Quitar de recientes"), Snorlax (sin permisos). Ver ese
mockup para el detalle visual completo; no se repite acá.

## Paleta de colores de portada por juego (fallback procedural)

| Generación | Gradiente | Glyph | Origen |
|---|---|---|---|
| 1 | `#F4D03F → #F7DC6F` | ⚡ | mockup original (Yellow) |
| 2 | `#5DADE2 → #85C1E9` | ◆ | mockup original (Crystal) |
| 3 | `#58D68D → #82E0AA` | 🍃 | mockup original (Emerald) |
| 4 | `#A569BD → #BB8FCE` | ▲ | mockup original (Platinum) |
| 5 | `#85929E → #AEB6BF` | ❄ | definido en implementación |
| 6 | `#F06292 → #F48FB1` | ✧ | definido en implementación |
| 7 | `#F5B041 → #F8C471` | ☀ | definido en implementación |
| 8 | `#16A085 → #48C9B0` | ⚔ | definido en implementación |
| 9 | `#EC7063 → #F1948A` | ✦ | mockup original (Violet) |

Resuelto por generación, no por juego individual — más simple de mantener. Fuente de verdad
en código: `GameCoverService.PaletteByGeneration`.

## Datos / bindings (tal como quedó implementado)

- `RecentSavesViewModel` (Exxeguttor.UI) orquesta la colección de hasta 5
  `RecentSaveRowViewModel`, cada uno envolviendo un `RecentSaveEntry` (Exxeguttor.App):
  `FilePath`, `FileName`, `GameVersion` (código crudo string, no el enum), `LastOpenedAt`.
- Persistencia real en `~/.config/exxeguttor/recent.json` vía `RecentSavesService`
  (`Environment.SpecialFolder.ApplicationData`, que en .NET/Linux ya resuelve a
  `$XDG_CONFIG_HOME` o `~/.config`).

## Historial de cambios respecto al hand-off original

1. **Ancho del panel: 400px, no 380px.** Confirmado contra `MainWindow.axaml`
   (`<Grid ColumnDefinitions="200,*,400">` — la columna derecha, `PokemonStatsView`, mide
   400px real).
2. **Persistencia: en disco**, no solo en memoria — ver sección de arriba.
3. **Portadas por juego: carpeta `Assets/sprites/games/` creada, pero vacía.** El fallback
   procedural (tabla de arriba) cubre el caso mientras no haya assets reales — agregar el
   `.png` correspondiente alcanza, no requiere tocar código.
4. **Badges de formato corregidos**: el mockup original tenía `.dat` como placeholder — no
   existe en ningún lado del proyecto real. El set real es `.sav / .dsv / .gci / .bin / .bak`
   + archivos sin extensión, con `main (Switch)` como badge explícito (saves de Switch —
   Espada/Escudo, BD/SP, Legends: Arceus, Escarlata/Púrpura, Legends: Z-A — se llaman
   literalmente `main`, sin extensión).
5. **Drag & drop sacado por completo.** Se implementó primero tal como especificaba este
   hand-off (`DragDrop.AllowDrop`, handlers de `DragEnter`/`DragLeave`/`Drop`), pero no
   funcionaba: **Avalonia 11.x (la versión que usa el proyecto) no tiene ningún target XDND
   en el backend de X11** — un archivo soltado desde un gestor de archivos externo
   (confirmado con Nautilus/GNOME/X11) nunca le llega a la app. Se implementa recién en
   Avalonia 12.1, no portado hacia atrás a la serie 11.x. No es un bug de la implementación
   de Exxeguttor, es un límite de la plataforma — por eso se sacó del todo en vez de dejarlo
   "roto" o a medias. Sigue quedando el botón "Abrir save..." como único punto de entrada
   además de clickear una fila de "Recientes".
6. **Modal de error agregado** (no estaba en el hand-off original) — ver sección propia
   arriba y `mockups/error_empty_state/` para el spec completo.

## Ver también

- `screen-01-empty-state.html` — boceto visual navegable (abrir en cualquier navegador),
  actualizado para reflejar el estado final de esta lista.
- `mockups/error_empty_state/` — spec completo del modal de error (4 casos).

