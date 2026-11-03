# Liberar Pokémon — botón "−" en slots + confirmación con Rotom

> Boceto de UI/UX (sesión de diseño, sin tocar código). Hand-off: `release-pokemon-boceto.html`
> (abrir en un navegador; interactivo: hover sobre un Pokémon muestra el "−", clic abre la confirmación).
> Estado: **decisiones confirmadas por Erick (Rotom-Corte cortando un lazo, liberación individual,
> confirmación en todos los casos)** — pendiente de implementar.

## Qué es
Permitir quitar ("liberar") un Pokémon de un save desde el panel de cajas y desde el equipo, para
limpiar Pokémon mal creados o sobrantes. Cambio de sesión pendiente de exportar, como una creación.

## El botón "−"
- Círculo rojo de 18 px con borde blanco, esquina **superior izquierda** del slot (caja: celda;
  equipo: fila).
- Oculto por defecto; aparece con hover y con foco de teclado (Tab). Hover del botón: rojo oscuro,
  escala 1.12, tooltip "Liberar Pokémon".
- **Deshabilitado** (gris) en el único Pokémon del equipo; tooltip "El equipo necesita al menos un
  Pokémon". **No existe** en slots vacíos.
- No interfiere con el clic normal del slot (seleccionar/editar): el clic del botón no se propaga.

## Diálogo 1 — Liberar (caja o equipo)
- Layout idéntico a los diálogos con Rotom ya implementados (`confirmation_dialogs`): escena a la
  izquierda, título + texto a la derecha, footer con dos botones.
- **Rotom-Corte** (forma "Mow", `pokemon_id` 10012). Escena (loop ~2.8 s): el Pokémon está atado a
  Rotom por un **lazo** (geometría simple, sin asset); Rotom se echa hacia atrás, hace el corte con un
  destello blanco/azul, el lazo se parte en dos mitades que caen/se desvanecen y el Pokémon sube, se
  encoge y se desvanece con tres chispas amarillas.
- ⚠️ **Asset nuevo**: los sprites de Rotom-Corte (`10012.png`) NO están embebidos. Agregarlos en
  `Assets/sprites/pokemon/normal/` y `shiny/` y añadir 10012 a `EXTRA_FORM_IDS` de
  `scripts/download-sprites.py` (igual que 10009/10011; Rotom no tiene variantes de género).
- Título: `¿Liberar a {Especie}?` (si tiene apodo, el apodo).
- Cuerpo: `Se quita del save y no se puede recuperar desde la app una vez exportado. Antes de exportar
  podés deshacerlo.`
- Chip con la ubicación: `Caja 2 · Slot 5 · Nv.30` / `Equipo · #3 · Nv.52`.
- Botones: `Cancelar` (secundario, foco por defecto) / `Liberar` (destructivo, rojo).
- Variante 1c (huevo): título `¿Liberar el huevo?`, chip `Caja 1 · Slot 12 · Huevo`, misma escena.
- Variante 1b: si lleva objeto, aviso ámbar extra: `Lleva equipado: {Objeto}. El objeto también se pierde.`

## Diálogo 2 — Último del equipo (bloqueado)
- Si se intenta liberar el único Pokémon del equipo (por si se llega por otra vía, p. ej. atajo de
  teclado), diálogo informativo: título `No se puede liberar`, cuerpo `Es el único Pokémon del equipo y
  el juego necesita al menos uno. Mové otro Pokémon al equipo y volvé a intentarlo.`, botón `Entendido`.
- Rotom con un leve "no" (sacudida), sin animación de liberar.

## Después de confirmar
- Caja: el slot queda vacío con su "+". Equipo: los siguientes suben (sin huecos).
- Aviso inferior `{Especie} liberado · pendiente de exportar` con acción `Deshacer`.
- Entra en el modal de revisión previo a exportar (`Dragonair — Caja 2, Slot 5: liberado`).
- "Descartar ediciones" lo restaura (la edición vive en la sesión, el save original no se toca hasta
  exportar).

## Notas técnicas (para la implementación)
- Equipo: `SaveFile.DeletePartySlot(index)` (PKHeX; corre los demás hacia arriba). Caja:
  `SetBoxSlotAtIndex(save.BlankPKM, box, slot)`.
- Debe registrarse como edición de sesión (igual que "created pending export") para poder deshacer y
  mostrarse en la revisión.
- Pendiente de verificar antes de implementar: Gen 1/2 (cajas como lista compacta con contador),
  Let's Go (Pokémon inicial/compañero), y que `EditSessionService` mantenga las claves de slot
  correctas tras reacomodar el equipo.
- Textos con voseo para coincidir con los diálogos existentes; localizar es/en como el resto.

## Decisiones tomadas
1. Rotom-Corte cortando un lazo (no Rotom base).
2. Liberación **individual** (sin selección múltiple por ahora).
3. **Siempre** se pide confirmación: Pokémon normales, huevos, ilegales, con objeto, etc.
   (la única excepción es el bloqueo del último del equipo, que es un aviso informativo).
