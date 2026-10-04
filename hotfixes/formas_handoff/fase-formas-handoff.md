# Fase de Formas — Handoff para continuar en otro chat

Este documento resume todo el trabajo de diseño e implementación de la fase de
"formas" (forms) de Exxeguttor, para continuar en una conversación nueva sin
perder contexto. Va acompañado de los archivos de código ya modificados
(ver sección final).

---

## 1. Contexto: por qué existe esta fase

Al terminar de corregir la legalidad de creación de Pokémon para todas las
generaciones (Gen1 → Gen9), quedó pendiente un tema aparte: **las formas**.
En la UI del editor existe el campo "Forma" pero no era editable (solo texto
de solo lectura, sin funcionalidad real).

Se identificaron **4 categorías** de formas, cada una con un tratamiento
distinto:

### Caso 1 — Forma de combate reversible, con cambio de stats/tipo/habilidad
Ejemplos: Giratina (Origin/Altered), Arceus (18 placas), Genesect (Drive),
Tornadus/Thundurus/Landorus (Therian), Keldeo (Resolute), Meowstic
(forma = género), Ogerpon (máscaras), Silvally (memorias).

Tratamiento: el usuario puede cambiar la forma libremente desde el combo del
editor. Cada especie tiene efectos secundarios propios que hay que aplicar al
cambiar de forma (ver sección 3, `ApplyForm`).

### Caso 2 — Forma regional/de origen (no es un "toggle")
Ejemplos: Marowak de Alola, Exeggutor de Alola, Vulpix/Ninetales de Alola,
Meowth de Galar, etc.

Tratamiento: **decisión deliberada de NO excluirla especialmente** del combo
de edición. No es un simple toggle de combate — está atada al origen del
encuentro/evolución (dónde y cómo se obtuvo el Pokémon). Si el usuario fuerza
un cambio a una forma regional incompatible con el origen del Pokémon, el
Diagnóstico de legalidad (LegalityAnalysis de PKHeX) la va a marcar como
ilegal de forma natural — no hace falta lógica especial para bloquearla a
priori. Esto es consistente con cómo PKHeX trata el tema.

**Pendiente relacionado (NO es parte de esta fase, fue un hallazgo aparte):**
Actualmente, al *crear* un Pokémon desde cero (no editar uno existente), el
sistema (`BuildPokemon`) **nunca ofrece formas regionales** — siempre
construye forma 0. Se confirmó que abrir un save de Gen7 y crear un Marowak o
Exeggutor no permite elegir la variante de Alola. El usuario pidió
explícitamente terminar primero esta fase (los 4 casos / combo de edición)
antes de atacar ese gap de creación. Queda documentado como la "Fase 2" al
final de este archivo.

### Caso 3 — Forma solo de batalla, nunca debe ser guardable
Ejemplos: Mega Evoluciones, Primal Groudon/Kyogre, Castform (clima), Cherrim
(Flower Gift), Zygarde Complete, etc.

Tratamiento: excluidas directamente del combo de selección usando
`FormInfo.IsBattleOnlyForm(species, form, format)` de PKHeX.Core — el usuario
nunca las ve como opción porque PKHeX ya las marca como "no persistibles en
un save".

### Caso 4 — Forma cosmética, sin impacto en stats/tipo/habilidad
Ejemplos: Unown (28 formas), Vivillon (patrones), Minior (core colors),
Deerling/Sawsbuck (estaciones).

Tratamiento: aparecen en el combo igual que el Caso 1, pero no requieren
ningún efecto secundario (`ApplyForm` simplemente asigna `pkm.Form = form` sin
tocar habilidad/ítem/tipo).

---

## 2. Qué se implementó (resumen funcional)

Se agregó un combo "Forma" editable en el editor de Pokémon, siguiendo
exactamente el mismo patrón que el combo de "Habilidad" ya existente:

- `PokemonService.GetSelectableForms(pkm, strings)` — devuelve la lista de
  formas elegibles para la especie actual, excluyendo las de Caso 3
  (`IsBattleOnlyForm`) y excluyendo especies sin formas múltiples.
- `PokemonService.TryGetFormIndex(pkm, strings, formName, out index)` —
  traduce el nombre elegido en el combo de vuelta a un índice de forma.
- `PokemonService.ApplyForm(pkm, form)` — aplica la forma y todos los efectos
  secundarios según la especie (ver detalle completo en sección 3).
- Wiring completo en las 4 capas de la UI:
  - `PokemonEditorViewModel.cs`: nueva propiedad `AvailableForms`, lógica de
    carga del combo, reseteo de campos.
  - `PokemonInfoView.axaml`: el `TextBlock` de solo lectura de Forma se
    reemplazó por un `ComboBox` (mismo estilo visual que Habilidad, con borde
    rojo de "campo editado").
  - `EditSessionService.cs`: entrada en `CategoryMap`, aplicación en el
    preview de la sesión de edición.
  - `EditApplyService.cs`: aplicación real al guardar.

**Orden de aplicación importante:** en ambos `EditSessionService.cs` y
`EditApplyService.cs`, el cambio de Forma se aplica **antes** que cualquier
edición explícita de Habilidad/Ítem en la misma sesión. Así, si el usuario
cambia la forma (que trae su propia habilidad/ítem por defecto) y además edita
manualmente la habilidad en el mismo combo de edición, su elección manual
gana sobre el efecto secundario automático de la forma.

---

## 3. Detalle técnico de `ApplyForm` (casos especiales por especie)

Todo esto fue **verificado contra PKHeX.Core 25.11.07 real**, compilado en un
sandbox aislado (`/tmp/formtest`), probando 10 casos reales (Giratina ×2
formas, Arceus, Genesect, Tornadus, Thundurus, Landorus, Keldeo, Meowstic,
Ogerpon) con resultado de **0 alertas de legalidad relacionadas a forma**
después de las correcciones.

```csharp
public static void ApplyForm(PKM pkm, byte form)
{
    pkm.Form = form;

    // Arceus Gen4 offset bug workaround — usar GetItemArceus, no el genérico GetItem
    if (pkm.Species == (int)Species.Arceus)
        pkm.HeldItem = FormItem.GetItemArceus(form, pkm.Format);
    else if (pkm.Species is (int)Species.Silvally or (int)Species.Genesect or (int)Species.Ogerpon)
        pkm.HeldItem = FormItem.GetItem(pkm.Species, form);

    // Giratina: Orbe Place (112) — no está en la tabla FormItem (mecánica antigua)
    if (pkm.Species == (int)Species.Giratina)
    {
        const int GriseousOrb = 112;
        if (form == 1) pkm.HeldItem = GriseousOrb;
        else if (pkm.HeldItem == GriseousOrb) pkm.HeldItem = 0;
    }

    // Ogerpon: el Tipo Tera está atado a la máscara
    if (pkm.Species == (int)Species.Ogerpon && pkm is ITeraType tera)
    {
        tera.TeraTypeOverride = (form & 3) switch
        {
            1 => MoveType.Water,
            2 => MoveType.Fire,
            3 => MoveType.Rock,
            _ => (MoveType)TeraTypeUtil.OverrideNone,
        };
    }

    // Refresco universal de habilidad (necesario no solo para el trío Therian,
    // también para Giratina/Ogerpon — confirmado contra PKHeX real)
    var slot = pkm.AbilityNumber switch { 4 => 2, 2 => 1, _ => 0 };
    var pi = pkm.PersonalInfo;
    pkm.RefreshAbility(Math.Min(slot, pi.AbilityCount - 1));

    // Meowstic: la forma ES el género
    if (pkm.Species == (int)Species.Meowstic)
        pkm.Gender = form;

    // Keldeo Resolute requiere Espada Sagrada (548)
    if (pkm.Species == (int)Species.Keldeo && form == 1)
    {
        const ushort SecretSword = 548;
        if (!pkm.HasMove(SecretSword))
        {
            Span<ushort> moves = [pkm.Move1, pkm.Move2, pkm.Move3, SecretSword];
            pkm.SetMoves(moves);
            pkm.HealPP();
        }
    }
}
```

### Bugs reales encontrados y corregidos durante la verificación

| Bug | Causa | Fix |
|---|---|---|
| Arceus → `FormItemInvalid` en Gen4 | `FormItem.GetItem` despacha Arceus siempre vía formato 8 internamente, pero en Gen4 el tipo "???" desplaza el índice de placa en 1 | Usar `FormItem.GetItemArceus(form, pkm.Format)` específicamente para Arceus |
| Giratina/Ogerpon → `AbilityUnexpected` | El refresco de habilidad al cambiar forma se había escrito solo para el trío Therian | Hacerlo incondicional para todas las especies con formas |
| Ogerpon → `TeraTypeIncorrect` | `TeraTypeUtil.IsValidOgerpon` exige que el Tipo Tera coincida con la máscara (Agua/Fuego/Roca) o sea "sin override" para la máscara base (Teal) | Asignar `TeraTypeOverride` explícitamente según `form & 3` |

### Falso positivo descartado
`TransferObedienceLevel` aparecía en TODOS los casos de prueba, incluso un
Pikachu de control sin tocar forma — confirmado como artefacto del arnés de
prueba mínimo (ObedienceLevel nunca inicializado), no un bug real. Excluido
del filtro de "problemas" del harness.

---

## 4. Qué queda pendiente (deuda técnica relacionada, NO resuelta aún)

### "TRAMPA #30": `PokemonDatabase.GetLearnsets` no filtra por `FormId`

`GetLearnsets(int speciesId, int gameId)` en `PokemonDatabase.cs` (línea
~718) solo filtra por `SpeciesId` + `GameId`, nunca por `FormId`. Esto mezcla
movesets de especies con múltiples formas que comparten el mismo
`SpeciesId` (confirmado concretamente con Vulpix/Ninetales Kanto vs Alola en
Gen8a — Leyendas: Arceus).

Hoy está parcialmente compensado en `RefreshMovesetForRigidLevelUpGames` con
una comprobación de "no empeorar" (si el recálculo aumenta el conteo de
movimientos inválidos, se revierte) — **no es un fix real**, solo un parche
defensivo.

**Llamadas actuales a `GetLearnsets` (ninguna pasa `Form` todavía):**
- `PokemonEditorViewModel.cs:2302`
- `PokemonService.cs:516`
- `PokemonService.cs:1228`
- `PokemonService.cs:1372`

**Fix correcto pendiente:** agregar parámetro `formId` a `GetLearnsets`,
filtrar por `FormId` en el SQL, y actualizar los 4 call sites para pasar la
forma actual del PKM/especie. Esto se identificó durante la implementación de
esta fase pero no se llegó a aplicar — quedó para decidir si se incluye en
esta entrega o se trata aparte.

---

## 5. Fase 2 (explícitamente diferida por el usuario): selección de forma al crear

Gap confirmado: `BuildPokemon(speciesId)` no tiene forma de pedir una forma
distinta de 0 al momento de crear un Pokémon nuevo. Se confirmó con un test
que crear un Exeggutor o Marowak en un save de Gen7 siempre construye forma 0
— **no se puede crear la variante de Alola desde cero**, solo editarla
después si ya existe en el save.

El usuario pidió explícitamente terminar primero el trabajo de esta fase (el
combo de 4 casos) antes de abordar este gap. Para cuando se retome, los
puntos a resolver son:

1. `BuildPokemon` necesita un parámetro de forma deseada.
2. `TryEvolveForward` — su resolución de rama ambigua actualmente siempre
   prefiere forma 0; necesitaría poder apuntar a la forma solicitada.
3. El selector de especie en la UI necesita exponer las opciones de forma
   disponibles para esa especie/generación antes de construir el Pokémon.

---

## 6. Estado del entorno / archivos

Los 5 archivos modificados y ya validados lógicamente (pendiente compilar en
el repo real una vez reclonado con el token) son:

1. `src/Exxeguttor.App/Services/PokemonService.cs` — agrega
   `GetSelectableForms`, `TryGetFormIndex`, `ApplyForm`.
2. `src/Exxeguttor.UI/ViewModels/PokemonEditorViewModel.cs` — propiedad
   `AvailableForms`, carga del combo, reseteo.
3. `src/Exxeguttor.UI/Views/PokemonInfoView.axaml` — ComboBox de Forma
   reemplazando el TextBlock de solo lectura.
4. `src/Exxeguttor.UI/Services/EditSessionService.cs` — entrada en
   `CategoryMap`, aplicación en preview.
5. `src/Exxeguttor.UI/Services/EditApplyService.cs` — aplicación real al
   guardar.

**Importante para el próximo chat:** el repo privado `exxeguttor` nunca
persiste entre sesiones — hay que pedirle el token de GitHub a Erick de
nuevo para clonarlo, aplicar estos 5 cambios (el código ya está listo y
validado contra PKHeX.Core real, solo falta integrarlo al repo y compilar),
y entregar los archivos finales.

No se ha hecho push a ningún repo (sin permiso de push). Al cerrar esta fase,
recordar a Erick actualizar `status.md` en `exxeguttor-context`.

---

## 7. Indicaciones para el chat nuevo

Junto con este `.md` se adjunta una carpeta `fase-formas-fragmentos/` con 5
archivos `.snippet` — **no son los archivos completos**, son los fragmentos de
código ya escritos y validados que hay que integrar a mano en el repo real:

- `01_PokemonService.cs.snippet`
- `02_PokemonEditorViewModel.cs.snippet`
- `03_PokemonInfoView.axaml.snippet`
- `04_EditSessionService.cs.snippet`
- `05_EditApplyService.cs.snippet`

Cada uno indica en un comentario al inicio a qué archivo real pertenece y en
qué parte va (reemplazo de bloque existente, inserción antes/después de X,
etc.). Están escritos de memoria del código real visto en esta sesión, **no
fueron re-verificados contra el archivo actual del repo** — al integrarlos,
confirmar que el contexto alrededor (nombres de variables, estructura) siga
coincidiendo antes de pegarlos.

Pasos sugeridos para el chat nuevo:

1. Pedirle a Erick el Personal Access Token de GitHub (nunca persiste entre
   sesiones) y clonar `https://TOKEN@github.com/junko012/exxeguttor.git`.
2. Aplicar los 5 fragmentos en sus archivos correspondientes.
3. Compilar el proyecto y correrlo contra casos reales (al menos los 10 de
   esta fase: Giratina ×2, Arceus, Genesect, Tornadus, Thundurus, Landorus,
   Keldeo, Meowstic, Ogerpon) para confirmar 0 alertas de legalidad por forma,
   igual que se hizo en el harness aislado de esta sesión.
4. Decidir con Erick si la TRAMPA #30 (`GetLearnsets` sin filtro de `FormId`,
   sección 4 de este documento) se resuelve en esta misma entrega o se
   difiere a otra sesión — no se resolvió aquí, solo quedó documentada.
5. Entregar los archivos finales modificados (nunca hacer push — no hay
   permiso).
6. Al cerrar, recordarle a Erick actualizar `status.md` en
   `exxeguttor-context`.
7. La Fase 2 (selección de forma al crear, sección 5 de este documento)
   queda explícitamente para después — no empezarla salvo que Erick lo pida.

---

## 8. Cómo validar contra PKHeX.Core real en el sandbox (en vez de pedirle a Erick que corra tests)

Durante toda esta sesión, cada corrección (por generación y en la fase de
formas) se verificó contra el código real de PKHeX.Core, no por inspección ni
suposición. El sandbox de Claude Code tiene salida a internet para clonar
repos públicos e instalar SDKs, así que el flujo fue:

1. **Clonar PKHeX.Core en el tag exacto del proyecto** (verificar la versión
   real en `Exxeguttor.App.csproj`, en esta sesión era `25.11.07`):
   ```
   git clone --branch 25.11.07 --depth 1 https://github.com/kwsch/PKHeX.git /tmp/pk/src
   ```
   (si el tag no existe con ese nombre exacto, listar tags con
   `git ls-remote --tags https://github.com/kwsch/PKHeX.git` y buscar el más
   cercano a la versión del paquete NuGet que usa el proyecto).

2. **Instalar el SDK de .NET que PKHeX.Core requiera** si el preinstalado no
   alcanza (en esta sesión hizo falta `dotnet-sdk-10.0` vía `apt`, porque
   PKHeX.Core target net9.0/net10.0 y el entorno traía uno más viejo).

3. **Armar un arnés de prueba aislado** (ej. `/tmp/formtest/formtest.csproj`)
   que:
   - Referencia el `.csproj` de `PKHeX.Core` clonado en el paso 1
     (`<ProjectReference Include="/tmp/pk/src/PKHeX.Core/PKHeX.Core.csproj" />`).
   - Construye un `PKM` mínimo de prueba (especie, nivel, juego de origen,
     EC/PID válidos) para cada caso a validar.
   - Aplica la lógica que se está escribiendo (en este caso, `ApplyForm`)
     directamente, copiando/pegando el método — sin necesidad de clonar el
     repo privado completo si solo se está iterando sobre un fragmento de
     lógica aislado.
   - Corre `new LegalityAnalysis(pkm).Valid` / `.Report()` sobre el resultado
     — el mismo motor de legalidad que usa Exxeguttor en producción — y
     reporta qué checks fallan.

4. **Iterar rápido**: compilar (`dotnet run`) el arnés, leer qué alertas tira
   `LegalityAnalysis`, ajustar el código, repetir. Esto permitió encontrar los
   3 bugs reales de esta fase (Arceus Gen4, Giratina/Ogerpon ability refresh,
   Ogerpon Tera type) sin necesidad de que Erick compile ni ejecute nada en su
   laptop durante el desarrollo — recién al final se entregan los archivos ya
   validados.

5. **Para validar sobre el código real del repo privado** (no solo un
   fragmento aislado), se puede extraer el archivo real (ej.
   `PokemonService.cs`) del clon del repo privado y referenciarlo desde el
   arnés de prueba, en vez de reescribir la lógica a mano — así el test corre
   literalmente el mismo código que va a quedar en producción.

Esto es replicable en el chat nuevo sin pedirle nada adicional a Erick más
allá del token de GitHub ya mencionado en la sección 7 — el resto (clonar
PKHeX.Core público, instalar el SDK, armar el arnés) no requiere
credenciales.
