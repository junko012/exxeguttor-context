# Pantalla 1 — Estado vacío / Carga de save

> Diseñada en sesión de UI/UX separada (Claude, chat). Este documento + el boceto
> `screen-01-empty-state.html` adjunto son el hand-off para la sesión de implementación.
> Ver también `CLAUDE.md` / `context.md` del proyecto para contexto general de arquitectura.

## Qué reemplaza

La pantalla vacía actual (`MainWindow` cuando no hay save cargado) hoy solo muestra un
texto centrado ("Open a save file to get started") y un botón "Open save...". Este diseño
la reemplaza por dos zonas: **recientes** (izquierda) y **acción principal** (derecha).

## Layout

```
┌───────────────────────────────┬──────────────────────────────────────┐
│  RECIENTES (panel izquierdo)  │   ZONA DE ACCIÓN (drag & drop)        │
│  ancho = ancho del panel       │   centrada vertical y horizontalmente │
│  derecho de PokemonEditorView  │                                       │
│  (ver "Pendiente de confirmar")│                                       │
└───────────────────────────────┴──────────────────────────────────────┘
```

- Panel izquierdo y zona derecha viven dentro del mismo contenedor raíz que hoy
  centra el texto/botón — se reemplaza ese contenido, no la ventana completa.
- Separador vertical de 1px (`var`/color de borde estándar de la app) entre ambas zonas.
- Sin scroll en ninguna de las dos zonas para la cantidad de ítems esperada (ver abajo).

## Zona "Recientes" (panel izquierdo)

- Título de sección: "Recientes" (clave i18n nueva, ej. `Recent_Title`).
- Lista vertical de hasta 5 entradas (más reciente arriba). Sin recientes → la zona
  simplemente no se muestra (el drag&drop ocupa todo el ancho) — ver
  "Pendiente de confirmar" sobre persistencia.
- Cada fila (de arriba hacia abajo):
  1. **Sprite de portada del juego**: rectángulo 26×34px, `CornerRadius=4`, con
     degradado + ícono representativo por generación/juego (ver tabla de colores abajo).
     Este es un placeholder de diseño — la implementación real debería usar un asset
     por versión de juego (`GameVersion`), similar a como `SpriteService` ya maneja
     sprites de Pokémon/ítems. Si no existe asset por juego, se puede sustituir por un
     color sólido derivado de `GameVersion` + ícono genérico de consola/cartucho.
  2. **Nombre de archivo** (ej. `pokemon_yellow.sav`), una línea, elipsis si excede ancho.
  3. **Subtítulo**: `{NombreJuego} · Gen {N}` (usar `ExpandGameName()` ya existente en
     `TrainerViewModel` para el nombre completo del juego).
  4. **Fecha relativa**, alineada a la derecha de la fila: "Hoy · HH:mm", "Ayer",
     o fecha corta ("12 ago") si es más antigua.
- Fila superior (más reciente) con fondo levemente distinto (`surface` un tono más claro
  que el resto de la lista) para destacarla como "la última usada".
- Click en cualquier fila → abre ese save directamente (mismo flujo que
  `SaveFileService.OpenAsync(path)` con el path guardado).

## Zona de acción (drag & drop)

De arriba hacia abajo, todo centrado horizontal y verticalmente dentro de su mitad:

1. Ícono de upload/archivo (outline, ~24px).
2. Texto: "Arrastra tu save aquí".
3. Texto secundario, más chico y atenuado: "o".
4. Botón primario: "Abrir save..." (mismo comando que existe hoy, `OpenSaveCommand`).
5. Fila de badges chips (pill, borde 0.5px, fondo `surface`, texto chico ~10-11px):
   `Gen 1-9` · `.sav` · `.dsv` · `.dat` — lista de generaciones/extensiones soportadas.
   Ajustar el contenido real de los badges a lo que el proyecto efectivamente soporta.

### Comportamiento drag & drop

- Toda la zona derecha es un drop target. Al arrastrar un archivo sobre la ventana con
  extensión válida, dar feedback visual (ej. borde discontinuo se resalta, fondo cambia
  levemente) — no especificado en el mockup visual, usar criterio estándar de Avalonia
  (`DragDrop.AllowDrop`, eventos `DragEnter`/`DragLeave`/`Drop`).
- Extensión inválida → feedback de error breve (no bloqueante) y no intenta abrir.
- Reutilizar la misma lógica de apertura que el botón "Abrir save..." una vez que se
  suelta un archivo válido.

## Paleta de colores de portada por juego (placeholder, ajustar a gusto)

| Juego (ejemplo) | Gradiente | Ícono sugerido |
|---|---|---|
| Yellow (Gen 1) | `#F4D03F → #F7DC6F` | rayo (bolt) |
| Crystal (Gen 2) | `#5DADE2 → #85C1E9` | diamante |
| Emerald (Gen 3) | `#58D68D → #82E0AA` | hoja |
| Platinum (Gen 4) | `#A569BD → #BB8FCE` | montaña |

Esto es solo el criterio usado en el mockup para diferenciar visualmente las entradas;
no es una paleta oficial. La sesión de implementación puede definir una paleta fija por
generación (1–9) o por juego individual, lo que sea más simple de mantener.

## Datos / bindings esperados

- `RecentSavesViewModel` (o similar) con una colección de hasta 5 items:
  `FilePath`, `FileName`, `GameVersion` (enum existente), `LastOpenedAt` (DateTime).
- Cada item necesita poder resolver `ExpandGameName()` y el número de generación
  (ya existe mapeo similar en `MapVersionToGameId()` / `TrainerViewModel`).

## Pendiente de confirmar antes de implementar

1. **Ancho del panel de recientes**: debe igualar el ancho del panel derecho
   (`PokemonEditorView`) del editor cargado, para que la transición entre pantallas se
   sienta natural. En el mockup se usó 380px como estimación — **confirmar el valor real
   en el AXAML de `PokemonEditorView`** y ajustar.
2. **Persistencia de recientes**: ¿se guardan en disco (ej.
   `~/.config/exxeguttor/recent.json`) para sobrevivir entre sesiones, o viven solo en
   memoria mientras la app está abierta? — no se definió en la sesión de diseño.
3. **Sprites de portada por juego**: el mockup usa placeholders con gradiente + ícono.
   Definir si se usan assets reales embebidos por juego o se mantiene el criterio
   procedural (color derivado de `GameVersion` + ícono por generación).

## Ver también

- `screen-01-empty-state.html` — boceto visual navegable (abrir en cualquier navegador).
