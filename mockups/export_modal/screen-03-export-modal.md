# Pantalla 3 — Modal de exportación (revisión pre-exportación)

> Diseñada en sesión de UI/UX separada (Claude, chat). Este documento + el boceto
> `screen-03-export-modal.html` adjunto son el hand-off para la sesión de implementación.
> Ver también `CLAUDE.md` / `context.md` del proyecto para contexto general de arquitectura,
> en particular la sección de "Export review modal" (legality correlation, safety guard).

## Qué reemplaza

El modal de exportación ya existente (legality correlation + horizontal card scroll +
fixed category order + safety guard) se mantiene en su lógica de fondo, pero se
rediseña la presentación de las tarjetas: pasa de scroll horizontal simple a un
**carrusel plano** con checklist de legalidad visible directamente en cada tarjeta.

## Layout general del modal

```
┌──────────────────────────────────────────────────────────────────┐
│ Revisar antes de exportar        [4 de 5 seleccionados] [1 a revisar] │  ← header
│ ⬆ Se exportará a pokemon_yellow.sav                                │
├──────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ‹  [Eevee] [Ditto]  [PIKACHU — focalizada]  [Charmander] [Bulba] › │  ← carrusel
│                                                                      │
│              ● ● ⬤ ● ●   (paginación, color por estado)             │
├──────────────────────────────────────────────────────────────────┤
│                                          [Cancelar]  [Exportar]     │  ← footer
└──────────────────────────────────────────────────────────────────┘
```

- Modal centrado, ancho fijo aproximado 680px (ajustar al contenedor real de diálogos
  de la app), alto flexible según contenido.
- Tres secciones apiladas: header, cuerpo (carrusel), footer — cada una separada por un
  borde horizontal de 1px.

## Header

- Línea 1: título "Revisar antes de exportar" a la izquierda; a la derecha, dos badges:
  - Badge de selección: `"{n} de {total} seleccionados"` (fondo tenue del color de
    acento de la app).
  - Badge de advertencias: `"{n} a revisar"` (fondo tenue ámbar/warning) — **solo se
    muestra si hay al menos 1 tarjeta con alguna categoría en warning**; si todas están
    limpias, se omite este badge.
- Línea 2 (debajo): ícono de exportar + texto chico atenuado: `"Se exportará a
  {nombre_archivo}.sav"` — refuerza el destino antes de confirmar, relacionado con la
  guarda de seguridad que ya existe para no sobrescribir el original.

## Cuerpo — Carrusel plano (sin profundidad 3D)

**Decisión de diseño explícita**: las tarjetas están todas en el mismo plano, **sin
rotación ni perspectiva** (se evaluaron variantes con `rotateY`/cover-flow 3D y se
descartaron a favor de esta versión, por legibilidad y simplicidad de implementación).

- **Tarjetas laterales** (no focalizadas): todas comparten el mismo tamaño entre sí
  (no hay escala decreciente por distancia al centro). Contenido completo y legible,
  solo más chicas que la focalizada:
  - Sprite, nombre, nivel.
  - Checklist reducido de categorías clave (3-4 filas, ej. Moves / IVs-EVs / Ability /
    Nature) con ícono check (verde) o warning (ámbar) por fila.
  - Opacidad reducida (~75%) respecto a la tarjeta focalizada, sin cambiar de tamaño
    entre sí — es un único estado visual "no focalizada".
- **Tarjeta focalizada** (la del centro / la que el usuario está revisando): más grande
  que las laterales, con:
  - Borde de acento de ~1.5px (en vez del borde estándar de 0.5px de las laterales).
  - Checkbox de selección en la esquina superior izquierda — **ver semántica abajo**.
  - Checklist completo, en el **orden fijo ya definido en el proyecto** (Moves, IVs/EVs,
    Ability, Nature, Met Location, y demás categorías correlacionadas por
    `LegalityAnalysis` — mismo orden que usa hoy el modal existente).
  - Badge inferior resumen: `"{n} a revisar"` si hay categorías con warning en esa
    tarjeta específica, o se omite si está todo correcto.
- **Navegación**: flechas `‹` `›` en los bordes izquierdo/derecho del carrusel, más
  clickeable en cualquier tarjeta lateral para que pase a ser la focalizada.
- **Paginación (puntos debajo del carrusel)**: un punto por Pokémon en la exportación,
  **coloreado según el estado de legalidad de esa tarjeta específica** (verde = sin
  observaciones, ámbar = tiene al menos una categoría a revisar) — no es solo un
  indicador de posición, es un mini-resumen visual del conjunto completo. El punto de
  la tarjeta activa se muestra más grande y con un halo sutil alrededor.

### Semántica del checkbox

El checkbox en la tarjeta focalizada **controla si ese Pokémon se incluye en el archivo
exportado**. No es un simple "ya lo revisé" — afecta directamente qué se escribe al
save. Ver "Pendiente de confirmar" para el estado inicial (todo marcado vs. todo
desmarcado por defecto).

## Footer

- Alineado a la derecha: botón "Cancelar" (secundario) + botón "Exportar" (primario,
  color de acento).
- Botón "Exportar" dispara el flujo de escritura ya existente (safety guard incluida
  para no sobrescribir el save original sin confirmación).

## Datos / bindings esperados

- Reutiliza la correlación de legalidad ya implementada (clonar PKM pristine, aplicar
  campos seguros, correr `LegalityAnalysis`, correlacionar `CheckResult.Identifier` a
  categorías de UI) — este diseño no cambia esa lógica, solo cómo se presenta.
- Cada tarjeta necesita, además de lo que ya usa el modal actual:
  - Un bool `IsSelectedForExport` (bindeado al checkbox).
  - Un estado agregado por tarjeta (`HasWarnings: bool`) para pintar el punto de
    paginación correspondiente.
  - Un bool `IsFocused` (o el índice actual del carrusel) para aplicar el estilo de
    tarjeta focalizada vs. lateral.

## Pendiente de confirmar antes de implementar

1. **Overflow con equipos de 6 Pokémon**: como todas las laterales comparten tamaño fijo
   (sin escala decreciente que las "empuje" hacia afuera), con más de ~4-5 tarjetas
   visibles simultáneamente el ancho del modal no alcanza. Definir si se recortan con
   `ClipToBounds` (parcialmente visibles, invita a hacer scroll/click en flecha) o si
   directamente no se renderizan hasta que el usuario navegue hacia ese lado.
2. **Estado inicial de los checkboxes**: ¿arrancan todos marcados (exportar todo por
   defecto, el usuario desmarca lo que no quiere incluir) o todos desmarcados (opt-in
   explícito por Pokémon)?
3. **Botón "Exportar" con warnings pendientes**: ¿se deshabilita hasta que no haya
   categorías en warning, se exporta igual sin restricción, o pide una confirmación
   extra (ej. diálogo "2 Pokémon tienen campos a revisar, ¿exportar de todos modos?")?
4. **Detalle de una categoría en warning**: hoy el ícono de warning en una fila (ej.
   "Met Location") no explica la razón. Evaluar si al hacer click/hover en esa fila se
   muestra el texto de `CheckResult` correspondiente (tooltip o expansión inline) — no
   se definió el mecanismo exacto en la sesión de diseño.

## Ver también

- `screen-03-export-modal.html` — boceto visual navegable (abrir en cualquier navegador).
- `screen-01-empty-state.md` / `.html` y `screen-02-navigation-rail.md` / `.html` —
  pantallas previas del mismo flujo de hand-off.
