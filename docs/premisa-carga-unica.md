# Premisa: carga única al abrir el save

**Sesión:** revisión de arquitectura de carga + Loader 1 (Hitmonlee) atado a progreso real.

## La idea

El save file que se abre **nunca se modifica en el lugar** — todas las ediciones se
trackean en memoria vía `EditSessionService`, y recién al exportar se construye un save
file **nuevo** con esas ediciones aplicadas (`EditApplyService`). Esto significa que el
momento de abrir el save es la **única vez** en toda la sesión donde el archivo de origen
"cambia" de verdad (pasa de no existir en memoria a estar completamente parseado).

De ahí la premisa: todo lo que la UI vaya a necesitar de acá hasta el export debería
quedar resuelto **una sola vez**, en ese momento de apertura — el mismo momento que ya
tiene un loader dedicado (Hitmonlee pateando a Voltorb, Loader 1). Después de esa carga
inicial, cualquier interacción del usuario (cambiar de caja, entrar a Mochila, clickear un
Pokémon) debería ser **lectura en memoria pura**, sin volver a golpear `pokemon.db` con
consultas pesadas — como mucho, consultas puntuales livianas (un lookup indexado por ID).

## Auditoría — qué se revisó

Se repasó todo el flujo de `OpenSaveFromPathAsync` y todos los handlers/comandos que se
disparan después (navegación de Cajas/Equipo, entrar a Mochila, clickear un Pokémon, abrir
el picker de crear Pokémon) buscando dos patrones problemáticos:

1. Trabajo que se recalcula en cada interacción cuando podría calcularse una sola vez al
   abrir el save.
2. Falta de cache en memoria para datos que no cambian entre consultas repetidas dentro de
   la misma sesión.

### Ya cumplía la premisa (sin cambios)

| Módulo | Por qué está bien |
|---|---|
| Navegación de Cajas (`BoxViewModel.PreviousBox`/`NextBox`) | `_pokemonService.GetBox()` lee directo de la estructura del `SaveFile` de PKHeX.Core ya parseado en RAM — cero SQLite por click. |
| Navegación de Equipo (`PartyViewModel.Load`) | Mismo criterio, `_pokemonService.GetParty()` es lectura en memoria. |
| Lista de especies del picker de crear Pokémon (`SpeciesPickerViewModel._allSpecies`) | Se carga una sola vez por sesión (`if (_allSpecies.Count == 0) LoadAllSpecies()`), nunca se vuelve a pedir. Y `PokemonDatabase.GetAllSpeciesSummaries()` ya estaba bien resuelto de una sesión anterior (una query para nombres + una query batch para tipos, evita N+1 sobre ~1000 especies). |

### Violaba la premisa (corregido en esta sesión)

#### 1. `Bag.Initialize()` se re-ejecutaba en cada click al rail de Mochila

```csharp
// ANTES
SwitchToBagModeCommand = new RelayCommand(() => { CurrentMode = AppMode.Bag; Bag.Initialize(); });

// AHORA
SwitchToBagModeCommand = new RelayCommand(() => CurrentMode = AppMode.Bag);
```

`Bag.Initialize()` ya se llamaba una vez al abrir el save (`OpenSaveFromPathAsync`), pero
el rail de Mochila la volvía a llamar en **cada** entrada al modo — releyendo pouches e
ítems de `pokemon.db` aunque nada hubiera cambiado desde la última vez. Se confirmó que
nada fuera de Mochila modifica pouches/ítems, y que las ediciones de cantidad ya se
trackean en `EditSessionService` y se superponen en memoria sobre los datos base sin
necesitar releerlos — la única fuente real de "por si se editó algo" es la propia Mochila,
que ya no necesita este re-fetch. Se verificó además que nada limpia (`Bag.Clear()`) el
estado al salir del modo, así que el dato ya calculado sigue siendo válido al volver.

De paso, esto ya venía con un bug de rendimiento arreglado en la sesión anterior (N+1
queries en `ItemInventoryService.GetItems`, ver historial) — con este cambio ese costo,
además de estar arreglado, ni siquiera se vuelve a pagar en cada visita.

#### 1b. El primer click a Mochila seguía siendo lento — causa distinta (sesión posterior)

Con el fix de arriba ya aplicado y compilado, el usuario reportó que el **primer** click al
rail de Mochila seguía demorando, aunque los siguientes ya eran rápidos. La causa no era de
datos sino de **render**: `ItemNameToSpriteConverter` decodifica el PNG de cada ícono de
ítem recién cuando el `Image` de esa fila se renderiza por primera vez
(`SpriteService.GetItemSprite` sí cachea por nombre, pero solo después de la primera
decodificación) — la decodificación de imagen es un costo de la UI, no de `Bag.Initialize()`,
así que el fix de datos de arriba no lo tocaba.

```csharp
// BagViewModel.Initialize() — al final, después de SwitchStore(BagStore.Bag)
PrewarmSprites();

private void PrewarmSprites()
{
    // Fuerza la decodificación de TODOS los íconos de TODAS las categorías (Mochila y PC),
    // no solo la que se ve primero, llamando directo a la capa de datos (_inventoryService.
    // GetItems) en vez de LoadItemsForSelectedPouch — así no dispara CapturePristine sobre
    // categorías que el usuario todavía no visitó.
    foreach (var tile in _bagPouches)
        foreach (var info in _inventoryService.GetItems(tile.Type, useAlternateStorage: false))
            SpriteService.Instance.GetItemSprite(info.Name);

    foreach (var tile in _pcPouches)
        foreach (var info in _inventoryService.GetItems(tile.Type, useAlternateStorage: true))
            SpriteService.Instance.GetItemSprite(info.Name);
}
```

Con esto, TODAS las categorías (no solo la primera) quedan con sus sprites ya decodificados
antes de que el usuario vea la Mochila por primera vez — el primer click a cualquier
categoría es tan liviano como los siguientes.

#### 2. `SpeciesDatabase.GetById` no cacheaba nada

`PokemonEditorViewModel.LoadPokemon` llama a esto en **cada click** sobre un Pokémon, y
sin cache eso son 3 queries SQLite (fila base + tipos + habilidades) repetidas cada vez
que el usuario vuelve a abrir el **mismo** Pokémon/especie — muy común en un flujo normal
de edición (entrar, salir, volver a entrar al mismo slot).

```csharp
// AHORA — cache en memoria por speciesId, para siempre dentro de la sesión (los datos de
// especie son estáticos, no dependen de qué save esté cargado ni cambian entre aperturas)
private readonly Dictionary<int, SpeciesEntry?> _cache = new();

public SpeciesEntry? GetById(int id)
{
    if (_cache.TryGetValue(id, out var cached)) return cached;
    // ... consulta real solo la primera vez que se ve este id ...
    _cache[id] = entry;
    return entry;
}
```

Es un cache **lazy** (se llena en el primer click de cada especie), no una precarga
completa en el loader de apertura — una sesión típica solo toca un subconjunto chico de
las ~1000 especies, así que precargarlas todas de una sería trabajo desperdiciado en la
mayoría de los casos. `null` también se cachea (especie inexistente) para no re-consultar
un ID inválido una y otra vez.

## Loader 1 atado a progreso real

Con `OpenSaveFromPathAsync` ahora haciendo de verdad "todo el trabajo pesado de una sola
vez" (Cajas, Equipo, Mochila — ya no solo Cajas/Equipo), el loader de apertura pasa a
representar trabajo real y no un tiempo de espera artificial. Se aprovechó para atar la
**barra de progreso** a avance real:

- `BusyStateService.Progress` (double, 0.0–1.0) + `ReportProgress(value)`, nuevo.
- `OpenSaveFromPathAsync` reporta progreso en 5 puntos: parseo del archivo (45%),
  capacidades/entrenador (55%), Cajas (75%), Equipo (85%), Mochila (100%).
- Entre cada paso se cede el hilo al dispatcher (`Dispatcher.UIThread.InvokeAsync(..., DispatcherPriority.Render)`)
  — sin esto, como todo el bloque es sincrónico, Avalonia coalescería los 5 cambios de
  `Progress` en un solo repintado final y la barra saltaría de 0 a 100 de golpe en vez de
  mostrar avance real.
- La barra en XAML pasó de un `Style.Animation` decorativo de 2.8s fijos en loop a un
  `ProgressBar` real bindeado directo a `BusyState.Progress`, con un `DoubleTransition` en
  `Value` para suavizar los saltos entre los 5 checkpoints.

### La coreografía de Hitmonlee sigue siendo decorativa — por qué

Se evaluó atar también el movimiento de Hitmonlee/Voltorb/Dugtrio al progreso real, pero
se descartó por ahora: esa coreografía es un `Style.Animation` declarativo de Avalonia con
`Duration` fija (2.8s) e `IterationCount="Infinite"` — escalarla a una duración variable
según cuánto tarde cada apertura implicaría abandonar el enfoque declarativo (CSS-like) por
uno imperativo, manejando cada `RenderTransform` cuadro a cuadro desde código en vez de
`Style.Animations` con keyframes. Es un cambio de arquitectura bastante más grande que
atar la barra, que si se puede resolver con un binding directo.

Como pedido explícito del usuario ("lo ideal sería ambas, pero la barra sola ya es algo"),
se priorizó la barra (100% real) y se mantiene un mínimo de 2.9s de espera total —
**sin bloquear el reporte de progreso real** — solo para que la coreografía llegue a
completar un ciclo entero al menos una vez antes de cerrar el loader. Si el trabajo real ya
tardó más que eso, no se espera nada extra (la barra ya muestra 100% desde antes).

## Iconos de categoría (sesión aparte) → prewarming más granular

En una sesión posterior, cambiar los iconos de categoría de la grilla central de Mochila
(emoji → sprites reales, ver commits de esa sesión) llevó a probar con un save de Gen 4, y
ahí apareció una tercera vuelta de tuerca sobre el prewarming de sprites de la sección
anterior: el catálogo de ítems de Gen4+ es mucho más grande que el de Gen1-3 (~100 MTs/MOs
vs ~50, más objetos generales), así que ese paso podía tardar perceptiblemente más para
esas generaciones. **No era una regresión de los iconos nuevos** (esos son ~15 sprites fijos,
no escalan con nada) — era el mismo prewarming ya descripto arriba, que siempre escaló con
el catálogo, solo que recién se notó al probar con Gen4.

El problema real no era el tiempo en sí (ese trabajo DEBE pasar en el loader, esa es la
premisa) sino que `Bag.Initialize()` solo reportaba progreso al principio y al final de ese
paso — para catálogos grandes la barra se quedaba pegada en 85% todo ese rato y después
saltaba a 100% de golpe, sintiéndose "trabada" en vez de progresando.

Se separó `BagViewModel.Initialize()` (sync, sin progreso — sigue usándolo
`PerformClearEdits`, una acción rápida sin loader visible) de un nuevo
`InitializeAsync(Action<double>? onProgress)` (usado por `OpenSaveFromPathAsync`), que
recorre las categorías una por una reportando avance real y cediendo el hilo al dispatcher
entre cada una — mismo mecanismo de "yield en prioridad Render" ya usado para el resto de
los pasos del Loader 1. Con esto la barra avanza de forma continua durante todo el
prewarming sin importar el tamaño del catálogo — el tiempo total todavía puede variar según
la generación (correcto y esperado: es trabajo real pasando en el loader en vez de filtrarse
a la primera interacción del usuario), pero ya no se siente trabado.

## "Sigue la demora" — análisis con calma (la causa real)

Después de la corrección anterior, seguía habiendo demora la primera vez que se entraba a
Mochila, y apareció un síntoma nuevo: a veces **Pokémon** (el cambio de modo en sí, sin
ninguna carga de datos asociada) también tardaba. Como el segundo síntoma no tiene relación
alguna con Mochila, era señal de que el diagnóstico anterior estaba incompleto — tocaba
parar de parchear el síntoma y mirar la causa de nuevo, con más cuidado.

**La causa real: `BagItemListView.axaml` renderiza la lista de ítems sin virtualizar.**
Cada fila tiene ~10 controles (5 botones, una imagen, 4 textos). El `ItemsControl` usaba el
panel default (`StackPanel`, no virtualizante) dentro de un `ScrollViewer` — eso significa
que Avalonia mide y dibuja **todas** las filas de la categoría de una sola vez la primera
vez que se muestran, sin importar cuántas entren en la pantalla visible. Para una categoría
de Gen4 con ~100 ítems, son ~1000 controles individuales realizados de golpe. Ningún cache
de datos (sprites, `BagItemRowViewModel`) toca este costo, porque es un costo de **render**,
no de datos — por eso ninguna de las correcciones anteriores lo resolvía del todo.

**Fix:** `ItemsPanel` del `ItemsControl` pasa a `VirtualizingStackPanel` — con esto Avalonia
solo realiza las filas visibles en pantalla (+ un margen chico), sin importar el tamaño de
la categoría. Es la corrección estándar de Avalonia para listas largas con templates
pesados.

**Sobre el síntoma nuevo (Pokémon lento a veces):** la sospecha es que la corrección de la
ronda anterior — construir y cachear las filas COMPLETAS de TODAS las categorías (visitadas
o no) durante el loader — sumó varios cientos de objetos y suscripciones a eventos
retenidos en memoria sin necesidad real (si el usuario nunca visita una categoría, no hace
falta tener sus filas construidas). Eso probablemente generó más presión sobre el
recolector de basura de .NET, causando pausas esporádicas que no tienen que ver con qué
botón se clickea — de ahí que "a veces" afectara también a Pokémon. Se revirtió esa parte:
`PrewarmSprites`/`PrewarmSpritesAsync` vuelven a precalentar solo los **sprites** (liviano,
acotado — solo decodificación de imagen, sin construir ViewModels) para todas las
categorías; la construcción de filas completas (`GetOrBuildRows`/`BuildRowsForCategory`)
quedó **lazy** — se arma la primera vez que el usuario visita de verdad una categoría, y
ahí sí se cachea para revisitas. Con la virtualización ya resolviendo el costo real de
render, esa construcción lazy es lo bastante liviana como para no necesitar precalentarse
de antemano.

## Archivos tocados (sesión completa, las tres rondas)

- `src/Exxeguttor.UI/ViewModels/MainWindowViewModel.cs` — `SwitchToBagModeCommand` sin
  re-init; `OpenSaveFromPathAsync` reescrito con pasos de progreso real.
- `src/Exxeguttor.UI/Services/BusyStateService.cs` — nueva propiedad `Progress` +
  `ReportProgress()`.
- `src/Exxeguttor.UI/Services/SpeciesDatabase.cs` — cache en memoria por `speciesId` en
  `GetById`.
- `src/Exxeguttor.UI/Views/MainWindow.axaml` — barra de progreso reemplazada por
  `ProgressBar` real; comentarios actualizados.
- `src/Exxeguttor.UI/App.axaml` — estilo `l1-progress-fill` (decorativo, ya sin uso)
  eliminado; comentarios actualizados.
- `src/Exxeguttor.UI/ViewModels/BagViewModel.cs` — `PrewarmSprites()` (sync, sin progreso) +
  nuevo `InitializeAsync`/`PrewarmSpritesAsync` (con progreso granular por categoría, usado
  por el loader de apertura); cache lazy de filas por categoría (`_rowsCache`/
  `GetOrBuildRows`/`BuildRowsForCategory`).
- `src/Exxeguttor.UI/Views/BagItemListView.axaml` — `ItemsPanel` de la lista de ítems pasa a
  `VirtualizingStackPanel` (la corrección real del "primera vez tarda").

## Pendiente / para otra sesión

Este audit se enfocó en los dos casos más claros y de mayor impacto (Mochila y especies
por click). No se revisó exhaustivamente **todo** el codebase — si en el futuro aparece
otro síntoma de "se queda pensando" en algún otro módulo, el mismo criterio de este
documento (¿esto se recalcula cuando podría calcularse una sola vez? ¿este dato se
consulta repetido sin cache?) es el primer lugar por dónde mirar.
