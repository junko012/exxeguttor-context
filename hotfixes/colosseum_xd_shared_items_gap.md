## ⚠️ Gap conocido — ItemGameCodes incompleto para Colosseum/XD

**Detectado**: sesión de categorización de Mochila (post-hotfix `fix_database`).

**Síntoma**: `ItemGameCodes` solo tiene 122 filas para `colosseum`/`galeofdarkness` (31 + 91),
y las 122 son exclusivamente ítems propios de la saga (rango sintético `ItemId >= 90000`:
llaves, discos, ID badges, DNA Sample, etc. — `Category = 'colosseum_xd_exclusive'` o
`'plot-advancement'`). Ítems comunes con el resto de la saga que también existen y se usan en
Colosseum/XD (Poké Ball, Great Ball, Potion, Full Restore, Antidote, etc. — confirmado
verificando esos 5 nombres puntuales) **no tienen ninguna fila** con `GameCode='colosseum'` ni
`'galeofdarkness'`.

**Causa**: el JSON fuente (`item_game_codes.json`, usado por el hotfix `fix_database`) nunca
mapeó los ítems compartidos hacia estos dos juegos — solo los exclusivos.

**Impacto**: la Mochila arma sus tiles consultando `ItemGameCodes.RawItemId`/`UserPouchCategory`
filtrado por `GameId` (ver `context.md`, sección "Módulo Mochila", para el detalle del diseño
final) — un save real de Colosseum/XD hoy solo mostraría la tile "Clave" (con esos 122 ítems) y
ninguna tile de Bolas/Medicina/Objetos, aunque el juego sí tenga esos ítems utilizables.

**Decisión**: se deja como gap conocido, no bloqueante. Retomar cuando se ataque Mochila para
Colosseum/XD específicamente — requiere ampliar `item_game_codes.json` (o la tabla
`ItemGameCodes` directamente) con la lista real de ítems compartidos disponibles en esos dos
juegos, incluyendo su `RawItemId` real para esos formatos (mismo criterio que el resto de la
tabla — ver "Historial de diseño" en `context.md` para por qué `RawItemId`, y no `ItemId`, es la
columna que hay que llenar bien).

---

## Piedras evolutivas — decisión de producto (re-confirmada, no es un bug)

La idea de una tile virtual `"Stones"` (piedras evolutivas con tile propia, separada de
"Objetos") se planteó en una sesión de diseño temprana pero **nunca se implementó**: el hotfix
`fix_database` mapea la categoría veekun `'evolution'` directo a `'Items'` genérico
(`CATEGORY_TO_POUCH['evolution'] = 'Items'` en `add_user_pouch_category.py`). Se volvió a
plantear y se re-confirmó la misma decisión en la sesión de corrección de Mochila: **piedras
evolutivas quedan dentro de la tile "Objetos"**, sin tile propia. Si en algún momento se quiere
separar, el cambio va en `add_user_pouch_category.py` (agregar `'evolution': 'Stones'` y correr
el hotfix de nuevo) — no requiere tocar código de `Exxeguttor.App`/`Exxeguttor.UI`, la
categorización sale entera de la DB.

---

## Nota histórica — conteo de tiles por generación (ver `context.md` para el vigente)

Un conteo de tiles por grupo de juegos calculado durante el hotfix `fix_database` quedó obsoleto
casi de inmediato: se calculó **antes** de encontrarse que `ItemInventoryService` tenía que usar
`ItemGameCodes.RawItemId` (no `ItemId`) para matchear contra `pouch.Items[].Index` — el conteo
de FILAS por categoría en la DB (lo que ese cálculo medía) nunca fue el problema; el problema
era el matcheo de índices en tiempo de lectura del save. Para el estado vigente de qué
categorías aparecen por generación, ver `context.md`, sección "🎒 Módulo Mochila" — no repetido
acá para no mantener dos fuentes de verdad desincronizadas.
