# Pantalla 2 — Rail de navegación + barra de acciones

> Diseñada en sesión de UI/UX separada (Claude, chat). Este documento + el boceto
> `screen-02-navigation-rail.html` adjunto son el hand-off para la sesión de implementación.
> Ver también `CLAUDE.md` / `context.md` del proyecto para contexto general de arquitectura.

## Qué reemplaza

Hoy, con un save cargado, la fila superior derecha de `MainWindow` mezcla en una sola
fila: tabs de navegación (Pokémon / Pokédex / Mochila), botones de acción (notebook,
checkpoint de sesión, exportar) y el badge de juego/generación (ej. "Yellow · Gen 1").
Este diseño separa navegación de acciones en dos zonas distintas.

## Decisión de alcance: se elimina la vista Pokédex

La navegación pasa de 3 secciones (Pokémon / Pokédex / Mochila) a **2**:
**Pokémon** y **Mochila**. No implementar ni dejar placeholder para Pokédex.

## Layout general

```
┌────┬──────────────────────────────────────────────────────────┐
│    │  Yellow · Gen 1                    🗒  💾  ⬆              │  ← fila superior (acciones + badge)
│ 🔵 │──────────────────────────────────────────────────────────│
│Poké│                                                            │
│món │                                                            │
│    │        (contenido: Trainer / Box / Party / Editor)         │
│ 🎒 │                                                            │
│Moch│                                                            │
│ila │                                                            │
└────┴──────────────────────────────────────────────────────────┘
```

- **Rail lateral** (columna izquierda, 54px de ancho fijo): navegación entre secciones.
- **Fila superior** (dentro del área a la derecha del rail, no del rail mismo): acciones
  + badge de estado del save.
- El resto del área (debajo de la fila superior, a la derecha del rail) es el contenido
  existente: `TrainerView` + `BoxView` + `PartyView` a la izquierda de esa área, y
  `PokemonEditorView` a la derecha cuando hay Pokémon seleccionado — **sin cambios**
  respecto a como funciona hoy, solo se le suma el rail y se reordena la fila superior.

## Rail lateral (columna izquierda, 54px)

- Fondo un tono distinto (más claro/oscuro, un nivel de "surface" por encima) del resto
  de la ventana, con borde derecho de 1px para separarlo del contenido.
- Dos ítems, apilados verticalmente, cada uno con ícono (arriba, ~19px) + etiqueta chica
  (abajo, ~9px):
  1. **Pokémon** — ícono de Pokébola (o el que ya use el proyecto para esta sección).
  2. **Mochila** — ícono de maletín/mochila.
- **Indicador de sección activa**: barra vertical de acento de 2px de ancho, pegada al
  borde izquierdo del rail, con la altura del ítem activo (~34px), color = accent de la
  app. El ítem activo también tinta su ícono y etiqueta con el color de acento; los
  inactivos quedan en `text-muted`.
- Click en un ítem → cambia la sección visible (mismo mecanismo de navegación que hoy
  tienen los tabs Pokémon/Pokédex/Mochila, solo que ahora vive en este control).

## Fila superior (dentro del área derecha, no en el rail)

- Alineada a la izquierda: badge de texto con el juego y generación actual, ej.
  `"Yellow · Gen 1"` — mismo dato que ya se muestra hoy (`Trainer.Game`, `Trainer.Gen`
  o equivalente), solo reposicionado.
- Alineados a la derecha, en este orden, solo íconos (sin texto, agregar `ToolTip` con el
  nombre de la acción ya que hoy no lo tienen):
  1. **Notebook** (flyout existente) — ícono de notebook/libreta.
  2. **Checkpoint de sesión** — ícono de guardado/disco.
  3. **Exportar** — ícono de upload/subida. Abre el modal de exportación (pantalla 3 de
     este hand-off).
- Separador horizontal de 1px debajo de toda la fila, antes del contenido.
- Esta fila reemplaza la posición actual de los mismos controles (`MainWindow.axaml`),
  no agrega funcionalidad nueva — es un reacomodo puramente visual.

## Datos / bindings esperados

- No hay nuevos datos: reutiliza los `Command`/propiedades ya existentes en
  `MainWindowViewModel` para navegación de secciones, notebook, checkpoint, exportar,
  y el badge de juego/gen. Es un refactor de `MainWindow.axaml` (layout), no de
  ViewModels.
- El flag de sección activa para pintar la barra de acento puede ser el mismo que hoy
  determina qué tab está seleccionado (Pokémon/Mochila), simplemente quitando la opción
  Pokédex de ese enum/estado.

## Pendiente de confirmar antes de implementar

1. **Posición del rail respecto a `MainWindow`**: ¿el rail va en el borde izquierdo
   absoluto de toda la ventana (afuera del panel que hoy contiene Trainer/Box/Party), o
   como una franja dentro del panel derecho, por encima de `PokemonEditorView`? En el
   mockup se asumió la primera opción (borde izquierdo absoluto de la ventana) porque
   es la que tiene más sentido como navegación de nivel de app, pero no quedó
   confirmado explícitamente en la sesión de diseño — **validar con el usuario o con
   el estado real del layout en `MainWindow.axaml` antes de implementar**.
2. **Tooltips**: los 3 íconos de acción (notebook, checkpoint, exportar) hoy no
   tienen tooltip. Se recomienda agregarlos al mover a esta fila, dado que quedan sin
   texto acompañante.

## Ver también

- `screen-02-navigation-rail.html` — boceto visual navegable (abrir en cualquier
  navegador).
- `screen-01-empty-state.md` / `.html` — pantalla previa del mismo flujo de hand-off.
