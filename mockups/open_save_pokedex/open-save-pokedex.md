# Boceto: Pokédex escaneando al abrir un save (reemplaza Loader 1)

Reemplaza el Loader 1 (`BusyKind.OpenSave`: Hitmonlee patea a Voltorb, que rueda y choca contra
Dugtrio) por la misma Pokédex roja de los loaders 4 y 5 (legalidad / catálogo de especies),
con la barra de progreso real al pie. Texto de título sin cambios: "Abriendo partida guardada…".

## Por qué se reemplaza

- La coreografía de Hitmonlee depende de varios elementos animados a la vez (ghosts, patada,
  Voltorb, Dugtrio) y de una ventana de tiempo concreta (la patada, 14%–22% del ciclo). El
  trabajo de carga corre en el hilo de UI, que se congela y hace que la escena se vea cortada
  o adelantada. Una escena más simple y continua tolera mejor esos frames perdidos.
- Unifica los tres loaders "Pokédex" bajo el mismo lenguaje visual (ícono de color sólido).

## Elementos de la escena

- **Pokédex grande** (escala 1.6 respecto al Loader 4), centrada, con el mismo vaivén (±3°) y
  parpadeo de lente.
- **Escaneo "por todos lados"**, centrado en la lente: tres anillos que se expanden en
  cascada, un rayo que gira 360° y dos líneas (horizontal y vertical) que cruzan el cuerpo de
  la Pokédex. Ciclo de 2.4 s, igual que el resto de las Pokédex.
- **Barra de progreso real**, mismo patrón que Loader 1/4 (`BusyState.Progress` +
  `StarWidthConverter`). Debajo, a la izquierda la etapa actual y a la derecha el porcentaje.
- Sin checklist ni sprite de Pokémon: acá no hay un Pokémon analizado, es el save completo.

## Etapas (hitos reales, ya reportados por `OpenSaveFromPathAsync`)

| Progreso | Etiqueta (neutral, i18n) |
|---|---|
| 0 → 45 % | Leyendo el archivo… |
| 45 → 55 % | Cargando entrenador… |
| 55 → 75 % | Preparando cajas… |
| 75 → 85 % | Preparando equipo… |
| 85 → 100 % | Preparando mochila… |

Las etiquetas se agregarían a `LocalizationService` (es/en) al implementar.

## Equivalencias en Avalonia (para la fase de implementación)

- Anillos: `Ellipse` con `ScaleTransform` + `Opacity` animados (retardos 0 / 0.8 / 1.6 s).
- Rayo giratorio: `Border` con `RotateTransform` (origen en la lente) y `LinearGradientBrush`.
- Líneas horizontal/vertical: `Border` de 2 px con `TranslateTransform`, dentro de un
  `Border` con `ClipToBounds`.
- Pokédex y lente: se reutilizan los estilos `pkdx-*` de `App.axaml` (como Loader 4/5), con una
  escala mayor. Nada de conic-gradient ni blur, que no existen en Avalonia.

## Por revisar antes de implementar

1. **Interpretación de "escaneado por todos lados"**: se tomó como la Pokédex escaneando en
   todas direcciones (anillos + rayo giratorio + líneas cruzadas). Si en cambio querías algo
   distinto, hay que ajustar este punto antes de pasar a código.
2. **Etiqueta de etapa bajo la barra**: incluida en el boceto, pero es opcional (se puede dejar
   solo el porcentaje o solo la barra).
3. **Congelamiento del hilo de UI** (causa probable de "no se pinta bien"): el boceto no lo
   resuelve por sí solo. Al implementar, `Box.Initialize` debería ceder el hilo cada pocas
   cajas; así el progreso 55 → 75 % también sería real por caja y la animación no se congelaría.
   Con eso, el piso artificial de 650 ms (solo existía para la patada de Hitmonlee) se puede
   quitar.
4. **Limpieza**: al implementar, borrar de código y assets lo exclusivo del Loader 1
   (`Loader1HitmonleeSprite`, `GetHitmonleeGhostSprite`, el sprite `ghost.106.png`, estilos
   `l1-*` de `App.axaml`).
