# Diálogo de confirmación — Abrir otro save con ediciones sin exportar

> Diseñado en sesión de UI/UX separada (Claude, chat). Este documento + el boceto
> `rotom-open-other-save-dialog-boceto.html` adjunto son el hand-off para la sesión
> de implementación. Extiende `rotom-confirmation-dialogs.md` (que cubre los otros
> dos disparadores del mismo patrón) con un tercer caso.
>
> **Nota de idioma**: a partir de este documento, todo el texto de UI se redacta en
> español estándar (no argentino) y se entrega ya preparado para localización
> es/en, siguiendo el patrón que ya usa el proyecto (`LocalizationService`, con
> paquetes de idioma adicionales instalables aparte). Los documentos previos del
> flujo de hand-off (`screen-01` a `rotom-confirmation-dialogs.md`) quedan sin
> modificar — este cambio de criterio aplica solo hacia adelante.

## Qué resuelve

Ya existían dos disparadores para el mismo problema (cambios de sesión sin
exportar): cerrar el save (`screen-01-empty-state`... ver
`rotom-confirmation-dialogs.md`, Diálogo 1) y descartar ediciones (mismo documento,
Diálogo 2). Faltaba un **tercer disparador**: intentar **abrir otro archivo de
save** mientras el save actual tiene cambios de sesión sin exportar.

## Por qué reusa el mismo diseño que el Diálogo 1

La consecuencia es idéntica a la de "cerrar sin exportar" — los cambios de sesión
se pierden — solo cambia la acción que lo dispara. Por eso este caso **reusa el
mismo ícono y animación de Rotom-Ventilador** (forma "Fan", `pokemon_id` 10011)
soplando hojas de papel que se alejan volando, en vez de introducir una cuarta
variante visual para un resultado que ya se comunica igual con las dos existentes.

## Diálogo — "¿Abrir otro save sin exportar?"

- **Cuándo aparece**: el usuario selecciona "Abrir save..." (o hace click en una
  fila de "Recientes") mientras el save actualmente cargado tiene cambios de sesión
  sin exportar.

### Texto (es — español estándar)
- Título: `"¿Abrir otro save sin exportar?"`
- Cuerpo: `"Hay cambios de esta sesión que todavía no se exportaron — se
  perderán si abres otro archivo ahora."`
- Botón secundario: `"Cancelar"`
- Botón destructivo: `"Abrir de todos modos"`

### Texto (en)
- Título: `"Open another save without exporting?"`
- Cuerpo: `"This session has unexported changes — they will be lost if you open
  another file now."`
- Botón secundario: `"Cancel"`
- Botón destructivo: `"Open anyway"`

### Composición visual (idéntica al Diálogo 1 de `rotom-confirmation-dialogs.md`)
- Rotom-Ventilador (64px) a la izquierda, con bob vertical sutil.
- 3 hojas de papel pequeñas (rectángulo blanco con líneas simulando texto) saliendo
  despedidas hacia la derecha, rotando y desvaneciéndose, con delay escalonado
  entre cada una para dar sensación de ráfaga continua.
- Layout: ícono a la izquierda, título + texto a la derecha, footer con los dos
  botones alineados a la derecha (botón destructivo en rojo).

## Datos / bindings esperados

- Mismo flag de sesión (`IsDirty` o equivalente, ver GAP CRÍTICO en `CLAUDE.md`) que
  ya disparan los otros dos diálogos — este es un tercer punto de entrada al mismo
  chequeo, no requiere un estado nuevo.
- Claves i18n nuevas y dedicadas (no reusar las de los otros dos diálogos aunque el
  ícono se comparta, ya que el texto es distinto): sugerido
  `Dialog_OpenOtherSave_Title` / `Dialog_OpenOtherSave_Body` /
  `Dialog_OpenOtherSave_Confirm`, siguiendo la convención de nombres ya usada en el
  proyecto (`Dialog_OpenSave_Title`, etc., ver `context.md`).

## Pendiente de confirmar antes de implementar

1. **Texto exacto**: el de este documento es una propuesta redactada en la sesión
   de diseño — si la sesión de implementación ya tiene texto real (como pasó con
   `rotom-confirmation-dialogs.md`, donde el usuario compartió capturas de pantalla
   con el texto ya implementado), ese texto real tiene prioridad sobre esta
   propuesta.
2. **Disponibilidad del sprite** de Rotom-Ventilador (`10011`) en los assets del
   proyecto — mismo pendiente ya anotado en `rotom-confirmation-dialogs.md`.

## Ver también

- `rotom-confirmation-dialogs.md` / `.html` — los otros dos diálogos del mismo
  patrón (Rotom-Ventilador para cerrar, Rotom-Lavadora para descartar), con el
  detalle completo de la animación de hojas de papel que este documento reusa.
- `rotom-open-other-save-dialog-boceto.html` — boceto animado navegable de este
  caso específico.
