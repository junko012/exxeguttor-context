# Tab IVs/EVs — radar fijo + barras integradas (mockup v1)

Archivo: `ivs-evs-layout.html` (autocontenido, interactivo; datos de ejemplo: Garchomp nivel 100).

## Problema
Hoy el tab apila editor → Total EVs/Poder Oculto/Naturaleza → radar → barras. En la columna de 400 px los gráficos quedan fuera de la primera pantalla, así que al editar un IV/EV no se ve su efecto sin scrollear.

## Decisión de diseño (opción C)
1. **Encabezado fijo** (fuera del scroll): **leyenda en una sola fila** arriba; debajo, en una fila, **Poder Oculto** (título + valor, pegado a la izquierda), el **radar** al centro (~200 px, casi pegado a la leyenda y a la lista) y **Naturaleza** (título + valor + modificadores, pegado a la derecha). Se probó Naturaleza apilada a la izquierda y se descartó.
2. **Lista de 6 filas con scroll propio**: cada fila = stat + stepper IV + stepper EV + Total. Debajo, **la barra verde del stat y, aparte debajo de ella, la barra gris de la base** (75% del alto de la verde, sin superponerse). El gráfico de barras separado desaparece.
3. **Pie**: solo la fila de EVs totales (con medidor).
4. Estimado de altura: pestañas ~34 + leyenda ~16 + radar ~205 + columnas 22 + 6 filas × ~45 + pie ~28 = ~580 px, muy justo con la ventana mínima de 600 px. Si falta alto, el scroll afecta solo a la lista y el pie.

## Lectura de los gráficos
| Elemento | Significado |
|---|---|
| Barra verde sólida | Stat total actual (hasta el valor original o el actual, el menor) |
| Tramo verde claro | Aumento respecto del save |
| Tramo rojo rayado | Disminución respecto del save |
| Marca negra vertical | Valor original del save |
| Barra gris aparte, debajo de la verde (75% de su alto) | Stat base de la especie |
| Radar: polígono verde | Stats actuales |
| Radar: contorno oscuro | Original del save (fantasma) |
| Radar: contorno gris punteado | Base de la especie (como hoy) |
| Punto del vértice | Verde si sube, rojo si baja |
| Insignia **+** verde en la esquina del radar y etiqueta del stat en verde | Stat que la naturaleza **aumenta** (×1.1) |
| Insignia **−** roja en la esquina del radar y etiqueta del stat en rojo | Stat que la naturaleza **reduce** (×0.9) |

## Indicadores de naturaleza en el radar
- Cada eje cuyo stat modifica la naturaleza lleva una insignia circular (**+** verde / **−** roja) colocada **justo a la derecha del nombre del stat** (posición medida con el ancho real del texto) para no taparlo, y la etiqueta del stat se pinta del mismo color; tooltip: "Naturaleza: Vel +10%".
- Naturaleza neutra (Fuerte, Dócil, Seria, Tímida, Rara): sin insignias. Gen 1/2 (sin naturalezas): sin insignias y el bloque Naturaleza atenuado (`BoolToOpacityConverter`, como hoy).
- Las insignias son independientes de IV/EV: solo cambian si se cambia la naturaleza en el tab Info.
- PS nunca recibe insignia (las naturalezas no lo afectan).

## Interacciones
- **Resaltado cruzado**: hover/foco en una fila ilumina su vértice, eje y etiqueta en el radar; hover sobre un vértice ilumina la fila.
- **Delta numérico** bajo el Total (`+8` / `−5`), vacío si no hay cambio.
- Steppers `−`/`+` (Shift = ±10), campo editable, `max` (IV) y `min` (EV) como hoy.
- EVs totales: medidor y texto en rojo si pasan de 510.
- Botón "Volver al original" solo en el mockup (referencia de comportamiento, no propuesta de UI).

## Notas para la implementación (fase posterior)
- El "original" sale del valor prístino que ya captura `EditSessionService.CapturePristine`; falta exponer el stat total original en `PokemonEditorViewModel` (hoy solo hay `Radar*` / `RadarBase*` actuales).
- Sin cambios en `RadarPointsConverter` ni `AnglesDeg`; hace falta un tercer polígono (`RadarOriginal*`).
- Gen 1/2: 5 filas (Especial unificado), DV 0-15, Stat Exp hasta 65.535, DV de PS deshabilitado — el layout no cambia, solo los topes.
- La caja amarilla de "DIAGNÓSTICO TEMPORAL" no aparece en el mockup; al removerla se libera espacio extra.

## Decisiones abiertas
1. **Escala del radar**: el mockup normaliza el total a 0-500 y la base a 0-255 (como hoy, por eso el polígono base se ve chico). ¿Unificar escalas o mantener así?
2. **Resaltado de IVs vs EVs**: la barra no separa cuánto aporta cada uno. ¿Se quiere ese desglose (dos tonos) o alcanza con el total?

## i18n (es / en)
| Clave | es | en |
|---|---|---|
| `Stats_Radar_Current` | Actual | Current |
| `Stats_Radar_Original` | Original del save | Original (from save) |
| `Stats_Radar_Base` | Base de la especie | Species base |
| `Stats_EvTotal` | EVs totales | Total EVs |
| `Stats_HiddenPower` | Poder Oculto | Hidden Power |
| `Stats_Nature` | Naturaleza | Nature |
