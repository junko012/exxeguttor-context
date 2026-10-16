# PLAN DE RENOMBRE — `Exxeguttor` → `{{NOMBRE NUEVO}}` (valor actual: **Max-Potion**)

> **Generado en una sesión de análisis** (2026-10-15) sobre `junko012/exxeguttor@af2bc6e` y
> `junko012/exxeguttor-context@99e2f4d`. Está pensado para que **otra sesión de Claude** (o Juan a mano)
> lo ejecute paso a paso. Nada de esto se aplicó todavía. El script de la sección 6 fue **probado en una
> copia desechable** de ambos repos (cero residuos del nombre viejo, cero falsos positivos con *Exeggutor*),
> pero **no se compiló** (el sandbox no tiene dotnet SDK / NuGet): la compilación y el arranque los verifica Juan.

## 0. Reglas para quien ejecute este plan

1. **Nunca hacer push.** Entregar los archivos con `present_files` (o el script ya aplicado sobre un clon que
   Juan descarga) y Juan sube desde su terminal, directo a `master`.
2. **No usar Git LFS** para nada (incluido `pokemon.db`). Si se ve un puntero LFS, avisar.
3. El token de GitHub se pide al empezar y **no persiste** entre sesiones. Si ya fue pegado en un chat,
   recomendar revocarlo.
4. Empezar con **clon fresco** de los dos repos (código privado con token; contexto público sin token).
5. El nombre nuevo es un **dato**: todo se deriva de la tabla de tokens (sección 1). Si Juan cambia el nombre,
   solo se cambian los tokens y se vuelve a correr el script.
6. **Búsqueda siempre sensible a mayúsculas y con la cadena exacta `Exxeguttor`.** Prohibido usar patrones
   difusos tipo `Exx?eg*`, `exeg` o `-i` sobre `exeggutor`: ver trampa T1.
7. Esta es una tarea de **un solo commit lógico** en cada repo (mensaje sugerido: `rename project Exxeguttor -> <Nuevo>`).
8. Al terminar: recordar a Juan **actualizar `status.md`** (sección 7, paso G5) y los demás puntos externos (sección 8).

## 1. Tabla de tokens (única fuente de verdad)

Un mismo nombre aparece en **7 formas distintas** según el contexto. No se pueden mezclar: p. ej. un guion
(`Max-Potion`) **no es válido** en un namespace C#.

| Token | Para qué se usa | Valor actual (viejo) | Valor nuevo (Max-Potion) |
|---|---|---|---|
| `DISPLAY` | Texto visible al usuario, README, `.desktop Name=`, `<Product>`, título de ventana, comentarios en prosa | `Exxeguttor` | `Max-Potion` |
| `PASCAL` | Namespaces C#, nombres de proyecto/carpeta/`.csproj`, `x:Class`, `using:`, nombres de recurso embebido, último segmento del Flatpak ID | `Exxeguttor` | `MaxPotion` |
| `SLUG` | Nombre de paquete deb/rpm, rutas `/usr/share/<slug>`, `~/.config/<slug>`, `.desktop`, `.ico`, `.sln`, `Icon=`, comando `/usr/bin/<slug>`, User-Agent | `exxeguttor` | `max-potion` |
| `ASSEMBLY` | `<AssemblyName>` del proyecto UI (nombre del ejecutable) y host de `avares://<assembly>/…` | `exxeguttor` | `max-potion` *(ver decisión D2)* |
| `UPPER` | Wordmark del splash (`SplashWindow.axaml`) y mockups | `EXXEGUTTOR` | `MAX-POTION` |
| `ENVPREFIX` | Prefijo de variables de entorno (hoy `EXXEGUTTOR_PROFILE`) | `EXXEGUTTOR` | `MAX_POTION` |
| `REPO_CODE` / `REPO_CTX` / `OWNER` | Nombres de repos GitHub y dueño | `exxeguttor` / `exxeguttor-context` / `junko012` | `max-potion` / `max-potion-context` / `junko012` |
| `FLATPAK` | App ID (hoy `io.github.exxeguttor.Exxeguttor`, con un org `exxeguttor` que no existe) | `io.github.exxeguttor.Exxeguttor` | `io.github.junko012.MaxPotion` *(ver D3)* |

Restricciones por token (verificar si Juan cambia el nombre):
- `PASCAL`: solo `[A-Za-z0-9]`, no puede empezar con dígito, sin guiones/espacios/puntos.
- `ASSEMBLY` y el host `avares://`: **sin guion bajo `_`** (un host de URI no admite `_`). El guion `-` sí es válido en URI, y .NET lo admite como nombre simple de ensamblado, pero ver D2.
- `FLATPAK`: último segmento sin guiones (usar `PASCAL`).
- `FR_DE` (francés): `d'` si el nombre empieza con vocal o `h`; `de ` si empieza con consonante (el script lo calcula).

## 2. Trampas conocidas (leer antes de tocar nada)

- **T1 — Falso positivo con `Exeggutor` (el Pokémon).** Parece casi igual a `Exxeguttor`. **16 archivos del repo de código**
  contienen ambos (p. ej. `PokedexService.cs`, `RegionalFormCatalog.cs`, `PokedexFormsTests.cs`). Un reemplazo difuso o
  case-insensitive corrompería nombres de especie. **Línea base que debe quedar intacta tras el renombre:**
  - Repo código: `Exeggutor` = **60**, `exeggutor` = **42**, `EXEGGUTOR` = **3** apariciones.
  - Repo contexto: `Exeggutor` = **20**, `exeggutor` = **4**, `EXEGGUTOR` = **0**.
  (Comando: `git grep -I -o -h -F Exeggutor | wc -l`.)
- **T2 — El ensamblado de la UI se llama en minúscula (`exxeguttor`) pero el namespace es `Exxeguttor.UI`.** Son dos tokens distintos
  (`ASSEMBLY` vs `PASCAL`). `avares://exxeguttor/...` usa el **ensamblado**; los nombres de recurso embebido
  (`Exxeguttor.UI.Assets.…`) usan el **RootNamespace**. Si se desincronizan, la compilación pasa pero la app falla en
  ejecución (recurso no encontrado, sin error de build).
- **T3 — Recursos embebidos por nombre literal** (8 sitios, sección 5.2). `GetManifestResourceStream("<Namespace>.Assets.x.json")`
  devuelve `null` en silencio si el namespace no coincide con `RootNamespace` + ruta de carpetas.
- **T4 — Un solo nombre bare `Exxeguttor` en código *no comentario/no string* rompería la compilación** al volverse `Max-Potion`.
  Se auditó: hoy **no existe** ningún caso (todo `Exxeguttor` bare está en comentarios, `<Product>`, `Title=` o strings de UI).
  Los usos como identificador son siempre `Exxeguttor.UI|App|Tests` y el script los mapea a `PASCAL`.
- **T5 — Rutas de datos de usuario cambian** (`~/.config/exxeguttor/recent.json`): sin migración, los usuarios existentes pierden la
  lista "Recientes". Ver paso F1.
- **T6 — Artefactos viejos.** `bin/` y `obj/` (ignorados por git) contienen `exxeguttor.dll`/`Exxeguttor.App.dll`. Borrarlos antes de compilar.
- **T7 — La DB `pokemon.db` (51 MB, blob normal) contiene el nombre viejo en 2 filas de `Metadata`** (no se usa en ejecución). Ver D4.
- **T8 — El historial de `status.md` es un log append-only**: no se reescribe, solo se agrega una entrada nueva.
- **T9 — CRLF/BOM:** `perl -pi` en modo bytes preserva finales de línea y BOM. No usar `sed -i` con `\n` ni reformatear archivos.
- **T10 — Discrepancias preexistentes** (no causadas por el renombre, pero el renombre las toca): ver sección 9.

## 3. Decisiones abiertas (con recomendación)

| ID | Decisión | Recomendación por defecto | Impacto si se cambia |
|---|---|---|---|
| D1 | Nombre final y sus 7 formas (sección 1) | Max-Potion / MaxPotion / max-potion | Solo tokens |
| D2 | `ASSEMBLY` con guion (`max-potion`) o sin guion (`maxpotion`) | `max-potion` (coincide con el comando y el paquete). **Si la primera compilación/ejecución falla al resolver `avares://max-potion/…`, usar `maxpotion`** y renombrar en el empaquetado (`install … maxpotion → /usr/bin/max-potion`) | `<AssemblyName>`, 3 URIs en `SplashWindow.axaml`, `.desktop StartupWMClass`, specs de paquete |
| D3 | Dueño del Flatpak ID | `io.github.junko012.MaxPotion` (dueño real del repo). El actual `io.github.exxeguttor.…` apunta a un usuario/org que no existe | `.csproj`, `control`, `.desktop` |
| D4 | Metadatos del DB (`Generator='Exxeguttor.DataBuilder.v06'`, `MigrationSource='Exxeguttor.UI.Assets.JSON.v1'`) | **Dejarlos** (son procedencia histórica; no se leen en código). Si se quieren cambiar, hacerlo con un hotfix SQL (`UPDATE Metadata SET Value=… WHERE Key=…`) que genera un blob nuevo de ~51 MB | `pokemon.db` |
| D5 | Textos históricos (`status.md`, `hotfixes/formas_handoff/**`) | **No reescribir**; agregar nota de renombre al final de `status.md` | Ninguno |
| D6 | Títulos de los `.html` de mockups (`<title>Exxeguttor — …`) | Actualizar (cosmético, lo hace el script) | Solo contexto |
| D7 | Migrar datos de usuario `~/.config/exxeguttor/` → `~/.config/<slug>/` | **Sí**, migración única al arrancar (paso F1) | `RecentSavesService.cs` |
| D8 | Identidad gráfica: `Assets/exxeguttor.ico` (260 KB) y wordmark del splash | El script renombra el archivo pero **no cambia la imagen**; decidir logo nuevo aparte. El wordmark `MAX-POTION` tiene 10 caracteres, igual que `EXXEGUTTOR`, así que el layout de `Press Start 2P` no debería cambiar; si el nombre nuevo tiene otro largo, revisar a ojo | Arte |
| D9 | Texto de copyright/autores (`exxeguttor contributors`) | `Max-Potion contributors` (nombre del proyecto, no de persona). Confirmar con Juan por ser texto legal de `LICENSE` | `LICENSE`, `.csproj`, specs |
| D10 | Email falso `exxeguttor@github.com` en `control`/`.spec` | Sustituir a mano por un email real o `noreply`; el script lo vuelve `max-potion@github.com` (tampoco existe) | `control`, `.spec` |
| D11 | Renombrar repos de GitHub (código y contexto) | Sí, **al final** (sección 8) | URLs, instrucciones del Project |
| D12 | Compatibilidad de paquetes (`Provides/Obsoletes/Conflicts/Replaces` del nombre viejo) | Sí, para que `apt/dnf` actualicen desde `exxeguttor` | `control`, `.spec` |

## 4. Inventario medido (línea base para verificar)

**Repo de código `exxeguttor`** (194 archivos de texto con alguna variante; 0 archivos binarios con el nombre salvo 2 filas del DB):

| Forma | Líneas | Archivos | Notas |
|---|---|---|---|
| `Exxeguttor.UI` | 252 | 123 | namespaces, `using`, `x:Class`, `xmlns … using:`, nombres de recurso |
| `Exxeguttor.App` | 96 | 78 | idem |
| `Exxeguttor.Tests` | 24 | 24 | `namespace` de tests |
| `Exxeguttor` (total, incl. lo anterior) | 437 | 192 | de ellas: 144 `namespace`, 94 `using`, el resto comentarios/strings/XAML/docs |
| `exxeguttor` (minúscula) | 75 | 18 | rutas, assembly, paquetes, .desktop, README |
| `EXXEGUTTOR` | 3 | 2 | `SplashWindow.axaml:64` (wordmark) y `Perf.cs` (variable de entorno) |

**Rutas con el nombre** (10 renombres con `git mv`; los directorios arrastran ~4.170 archivos de sprites/assets, que Git detecta como renames):

```
exxeguttor.sln
src/Exxeguttor.App/                  (dir)   + Exxeguttor.App.csproj
src/Exxeguttor.UI/                   (dir)   + Exxeguttor.UI.csproj + Assets/exxeguttor.ico
tests/Exxeguttor.Tests/              (dir)   + Exxeguttor.Tests.csproj
packaging/debian/exxeguttor.desktop
packaging/rpm/exxeguttor.spec
```

**Repo de contexto `exxeguttor-context`**: 47 archivos con el nombre, 0 rutas. El script reescribe 40 y **excluye** `status.md` (16 líneas, log) y
`hotfixes/formas_handoff/**` (7 archivos, handoff histórico).

**No existe en el repo de código:** `.github/` (workflows), `.gitattributes`, `.editorconfig`, `Directory.Build.props`, `global.json`, `nuget.config`, `.vscode/`, `.idea/`.
(`CLAUDE.md` menciona `.github/workflows/build.yml` y `release.yml`, pero **no están en el árbol clonado**: confirmar con Juan si existen en otro lado.)

## 5. Plan atomizado

Convención: ✅ = lo hace el script (sección 6) · ✋ = paso manual / semántico · 🧪 = verificación. Los números de línea son del commit `af2bc6e` y
pueden desplazarse un poco; buscar por contenido.

### FASE A — Pre-vuelo
- [ ] **A1** ✋ Clonar `junko012/exxeguttor` (token) y `junko012/exxeguttor-context` (público). `git log -1` de ambos y compararlos con `af2bc6e` / `99e2f4d`. Si hay commits nuevos, leer el diff antes de seguir.
- [ ] **A2** ✋ Confirmar con Juan los tokens (sección 1) y las decisiones D2, D3, D7, D9, D10.
- [ ] **A3** 🧪 Anotar la línea base: los conteos de la sección 4 y los de *Exeggutor* (T1).
- [ ] **A4** ✋ Árbol limpio (`git status --porcelain` vacío). El script aborta si no lo está.

### FASE B — Ejecución mecánica (script, sección 6)
- [ ] **B1** ✅ Correr `SCOPE=code ./rename_project.sh <clon-codigo> --dry-run` y revisar la lista (esperado: **194** archivos).
- [ ] **B2** ✅ Correr sin `--dry-run`. Reglas aplicadas, en este orden (de lo específico a lo general):
  1. `io.github.exxeguttor.Exxeguttor` → `FLATPAK`
  2. `https://github.com/exxeguttor/exxeguttor` → `https://github.com/OWNER/REPO_CODE`
  3. `exxeguttor-context` → `REPO_CTX`
  4. `junko012/exxeguttor` → `junko012/REPO_CODE`
  5. `exxeguttor-pokemon-database` → `SLUG-pokemon-database`
  6. `<AssemblyName>exxeguttor</AssemblyName>` → `ASSEMBLY`
  7. `avares://exxeguttor/` → `avares://ASSEMBLY/`
  8. `Exxeguttor.(UI|App|Tests|DataBuilder)` → `PASCAL.\1`
  9. `EXXEGUTTOR_` → `ENVPREFIX_` y `EXXEGUTTOR` → `UPPER`
  10. `d'Exxeguttor` → `FR_DE + DISPLAY` (solo francés)
  11. `Exxeguttor` (resto) → `DISPLAY`
  12. `exxeguttor` (resto) → `SLUG`
- [ ] **B3** ✅ Los 10 `git mv` (carpetas, `.csproj`, `.sln`, `.ico`, `.desktop`, `.spec`).
- [ ] **B4** 🧪 `git grep -I -n -E 'Exxeguttor|exxeguttor|EXXEGUTTOR'` → **0 resultados**; `git ls-files | grep -i exxegu` → **vacío**; conteos *Exeggutor* = línea base (T1).
- [ ] **B5** Repetir B1–B4 con `SCOPE=context` sobre el repo de contexto (esperado: 40 archivos reescritos; residuos permitidos **solo** en `status.md` y `hotfixes/formas_handoff/**`).

### FASE C — Revisión de lo que el script resuelve "bien pero conviene ver" (✋ leer el diff)
Después del script, estas líneas deben quedar así (con valores Max-Potion):

**C1 Solución y proyectos**
- `max-potion.sln` líneas 6/8/10: `"MaxPotion.UI", "src\MaxPotion.UI\MaxPotion.UI.csproj"` (idem `.App`, `tests\MaxPotion.Tests\MaxPotion.Tests.csproj`). **Los GUID `{A1B2C3D4-0001-…}` no se tocan.**
- `src/MaxPotion.UI/MaxPotion.UI.csproj`: `<AssemblyName>max-potion</AssemblyName>`, `<RootNamespace>MaxPotion.UI</RootNamespace>`, `<Product>Max-Potion</Product>`, `<Authors>max-potion contributors</Authors>` (D9: pasar a `Max-Potion contributors`), `<Copyright>… max-potion contributors</Copyright>`, `<FlatpakAppId>io.github.junko012.MaxPotion</FlatpakAppId>`, `<ProjectReference Include="..\MaxPotion.App\MaxPotion.App.csproj" />`, y el comentario del bloque Tips (`"MaxPotion.UI.Assets.Tips.tips_ES.json"`).
- `src/MaxPotion.App/MaxPotion.App.csproj`: `RootNamespace`/`AssemblyName` = `MaxPotion.App`; el comentario que cita `exxeguttor-context` pasa a `REPO_CTX`.
- `tests/MaxPotion.Tests/MaxPotion.Tests.csproj`: `RootNamespace` = `MaxPotion.Tests`; `ProjectReference` a `..\..\src\MaxPotion.App\MaxPotion.App.csproj`.
- `src/MaxPotion.UI/app.manifest` línea 3: `assemblyIdentity name="MaxPotion.UI"`.

**C2 Código C# (mecánico)**: 144 `namespace`, 94 `using`, y referencias calificadas `Exxeguttor.UI.ViewModels.PokemonSlotKey` (35 en `EditSessionService.cs`) → todas a `MaxPotion.*`.

**C3 AXAML**: en 18 archivos, `xmlns:…="using:MaxPotion.UI.*"` y `x:Class="MaxPotion.UI.*"` (1 en `App.axaml`, 17 en `Views/*`, más `xmlns:app="using:MaxPotion.App.Services"` en `PokemonInfoView` y `PokemonStatsView`).
- `Views/MainWindow.axaml:11` → `Icon="/Assets/max-potion.ico"` (coincide con el `.ico` renombrado).
- `Views/MainWindow.axaml:283,287,692` comentarios que citan `exxeguttor-context` → `REPO_CTX`.
- `Views/SplashWindow.axaml`: `:5 Title="Max-Potion"`, `:64 Text="MAX-POTION"`, `:50,:52,:67 avares://max-potion/Assets/...` (**ASSEMBLY**, ver T2/D2).

**C4 Recursos embebidos por nombre literal (T3)** — deben coincidir con `RootNamespace` + carpeta:

| Archivo:línea | Antes | Después |
|---|---|---|
| `App/Services/AlternateFormCatalog.cs:79` | `Exxeguttor.App.Assets.creatable_forms.json` | `MaxPotion.App.Assets.creatable_forms.json` |
| `App/Services/CreatableSpecies.cs:67` | `Exxeguttor.App.Assets.uncreatable_species.json` | `MaxPotion.App.Assets.uncreatable_species.json` |
| `App/Services/UncreatableForms.cs:52` | `Exxeguttor.App.Assets.uncreatable_forms.json` | `MaxPotion.App.Assets.uncreatable_forms.json` |
| `App/Services/PokedexService.cs:376,378` | `Exxeguttor.App.Assets.restricted_dex_availability.json` (+ mensaje de error línea 378) | `MaxPotion.App.…` |
| `UI/Services/MovesetDatabase.cs:81` | `Exxeguttor.UI.Assets.movesets_all_combined.json` | `MaxPotion.UI.…` |
| `UI/Services/SoundService.cs:26` | `Exxeguttor.UI.Assets.sounds.spark_chime.wav` | `MaxPotion.UI.…` |
| `UI/Services/SpriteService.cs:26` (`const NS`) + comentarios `:11-16`, `:142` | `Exxeguttor.UI.Assets.sprites` | `MaxPotion.UI.Assets.sprites` |
| `UI/Services/TipsService.cs:57` | `$"Exxeguttor.UI.Assets.Tips.tips_{locale}.json"` | `$"MaxPotion.UI.Assets.Tips.tips_{locale}.json"` |
| `UI/i18n/LocalizationService.cs:81` | `$"Exxeguttor.UI.i18n.{locale}.json"` | `$"MaxPotion.UI.i18n.{locale}.json"` |

**C5 Rutas de ejecución / sistema** (el script las pone en `SLUG`):

| Archivo:línea | Antes | Después |
|---|---|---|
| `App/Services/PokemonDatabase.cs:157` | `/usr/share/exxeguttor/pokemon.db` | `/usr/share/max-potion/pokemon.db` |
| `App/Services/RecentSavesService.cs:30` (+ doc `:7`) | `ApplicationData/exxeguttor/recent.json` | `ApplicationData/max-potion/recent.json` |
| `UI/i18n/LocalizationService.cs:92,96,164` | `/usr/share/exxeguttor/lang` | `/usr/share/max-potion/lang` |
| `UI/Services/SoundService.cs:80` | archivo temporal `exxeguttor_<recurso>` | `max-potion_<recurso>` |
| `UI/Services/Perf.cs:7,13` | variable de entorno `EXXEGUTTOR_PROFILE` | `MAX_POTION_PROFILE` |
| `UI/ViewModels/MainWindowViewModel.cs:980` | comentario con `~/.config/exxeguttor/recent.json` | `~/.config/max-potion/recent.json` |

**C6 Textos visibles al usuario**
- `UI/ViewModels/PokemonEditorViewModel.cs:3041`: `"Aviso de Exxeguttor (no es una regla de PKHeX…"` → `"Aviso de Max-Potion …"`.
- `UI/Services/…` y `App/Services/SaveFileService.cs:8`, `Program.cs:4`, `LocalizationService.cs:8`: comentarios en prosa → `Max-Potion`.
- `i18n/es.json`, `i18n/en.json` (líneas 2, 10, 99): `App_Title`, `Menu_Help_About`, `Dialog_About_Title`.
- `lang/{ar,de,fr,hi,id,ja,ko,pt-BR,ru,zh-CN}.json` (líneas 2, 10, 52; en `ar.json` líneas 5, 13, 55): mismas 3 claves. **Revisar a mano gramática por idioma** (el script solo reemplaza el nombre):
  - `fr`: `À propos d'Exxeguttor` → `À propos de Max-Potion` (el script elide `d'` según la inicial).
  - `ja`: `Exxeguttorについて` → `Max-Potionについて` · `ko`: `Exxeguttor 정보` → `Max-Potion 정보` · `hi`: `Exxeguttor के बारे में` → `Max-Potion के बारे में`.
  - `ar` (RTL): el nombre latino dentro de texto árabe; verificar visualmente que no se invierta el orden (`حول Max-Potion`).
  - `ru`, `de`, `id`, `pt-BR`, `zh-CN`: sin cambio gramatical.

**C7 Scripts Python del repo**
- `scripts/download-sprites.py:21` `OUT = Path("src/MaxPotion.UI/Assets/sprites")` y `:169` texto de consola.
- `scripts/gen-trainer-sprites.py:8` (docstring) y `:20` (`"src", "MaxPotion.UI", …`).
- `scripts/fetch-species-extra.py:60` User-Agent `max-potion-data-fetch/1.0`.
- `src/MaxPotion.UI/Assets/sprites/pokemon/ghost/gen_ghost.py:11-12`: **rutas absolutas del sandbox** `/home/claude/max-potion/src/…`. ✋ Cambiarlas a rutas relativas (hoy dependen del nombre de la carpeta de clonado).
- `src/MaxPotion.UI/Assets/sprites/README.md:22,46`: referencias a `MaxPotion.App.Services.SpeciesFormResolver` y `MaxPotion.UI.ViewModels.TrainerViewModel`.

### FASE D — Documentación del repo de código
- [ ] **D-1** ✅ `README.md` (11 líneas): título `# Max-Potion`; `max-potion_1.0.0_amd64.deb`, `max-potion-lang_1.0.0_all.deb`, `max-potion-1.0.0.x86_64.rpm`, `max-potion-1.0.0-linux-x64.tar.gz`, `./max-potion-1.0.0-linux-x64/max-potion`, `git clone https://github.com/junko012/max-potion.git`, `cd max-potion`, `dotnet build max-potion.sln`, `dotnet run --project src/MaxPotion.UI`. ✋ Verificar que el `cd` coincida con el nombre real del directorio que crea el clon.
- [ ] **D-2** ✅ `.gitignore:2` (comentario de cabecera). 
- [ ] **D-3** ✅ `LICENSE:4`: `Copyright (C) 2025 max-potion contributors` (D9). ✋ Confirmar con Juan: es texto legal.
- [ ] **D-4** ✅ `pokemon-database/README.md` (líneas 1, 3, 7, 69 `max-potion-pokemon-database`, 286 `MaxPotion.DataBuilder`, 331), `pokemon-database/LICENCE:3`, `pokemon-database/CHANGELOG.md:57` (`MaxPotion.DataBuilder-v06`: nombre histórico de una herramienta; ✋ decidir si se deja como estaba en la época; por defecto el script lo renombra).
- [ ] **D-5** ✋ Agregar al tope de `pokemon-database/CHANGELOG.md` una línea: `* Project renamed Exxeguttor -> <Nuevo> (no schema change)`.

### FASE E — Empaquetado (`packaging/`)
Tras el script quedan renombrados `max-potion.desktop` y `max-potion.spec`. Revisar y completar a mano:
- [ ] **E1** `packaging/debian/control` (15 líneas): `Package: max-potion`, `Recommends: max-potion-lang`, `Suggests: max-potion-devel`, `Package: max-potion-lang`, `Depends: max-potion (= 1.0.0)`, `Homepage`, `X-Flatpak-AppID`, rutas `/usr/share/max-potion/lang/` y `/usr/share/doc/max-potion/lang-template.json`, `Maintainer` (D10).
- [ ] **E2** ✋ `control`: agregar compatibilidad (D12): `Replaces: exxeguttor`, `Conflicts: exxeguttor`, `Provides: exxeguttor` (y lo análogo para `-lang`) en el paquete principal.
- [ ] **E3** `packaging/rpm/max-potion.spec` (29 líneas): `Name:`, `URL:` (D3/D2), `Recommends: max-potion-lang`, `%package lang`/`devel` (`Requires: max-potion = %{version}`), todos los `install`/`mkdir` hacia `/usr/lib/max-potion`, `/usr/share/max-potion/lang`, `/usr/share/doc/max-potion`, `%files`, `%changelog` (D10).
- [ ] **E4** ✋ `.spec`: agregar `Obsoletes: exxeguttor < 1.0.0-2` y `Provides: exxeguttor = %{version}` (D12).
- [ ] **E5** `packaging/debian/max-potion.desktop`: `Name=` y `Name[es|en|zh_CN]=Max-Potion`, `Exec=/usr/bin/max-potion %f`, `Icon=max-potion`, `StartupWMClass=` (**debe coincidir con la WM_CLASS real que reporta la ventana; ver 🧪 I8**), `X-Flatpak-AppID`.
- [ ] **E6** ✋ Si el `<AssemblyName>` y el nombre del paquete difieren (D2 con `maxpotion`): en el `.spec` y en el empaquetado deb, instalar el binario `maxpotion` como `/usr/bin/max-potion`.
- [ ] **E7** ✋ **Archivos que el `.spec` referencia y NO existen en el repo** (preexistente, ver T10): `packaging/rpm/exxeguttor.sh` (launcher), `src/…/Assets/exxeguttor.png` (el icono real es `.ico`), `lang-template.json`. Crearlos o corregir el `.spec`; el renombre solo cambia el nombre en la referencia.

### FASE F — Datos de usuario y migración (D7)
- [ ] **F1** ✋ En `RecentSavesService` (ctor sin parámetros): si **no** existe `ApplicationData/<slug>/recent.json` y **sí** existe `ApplicationData/exxeguttor/recent.json`, moverlo (o copiarlo) una única vez y seguir. Constante del nombre viejo documentada con un comentario `// legacy (pre-rename)`. Agregar un test de la migración. Ojo: el ctor `internal RecentSavesService(string filePath)` **no es visible** desde `tests/` (no hay `InternalsVisibleTo` en el repo); hay que agregar `[assembly: InternalsVisibleTo("MaxPotion.Tests")]` en `MaxPotion.App` o hacer el ctor público. Hoy no existe ningún test de `RecentSavesService`.
- [ ] **F2** ✋ Evaluar el mismo patrón para cualquier otro archivo de usuario. Nota: la documentación del repo de contexto menciona `~/.config/exxeguttor/settings.json` (selector de idioma), pero **no se encontró código que lo lea/escriba en el árbol actual** (`git grep -i settings -- '*.cs'` sin resultados relevantes). Confirmar con Juan si el selector de idioma ya persiste y dónde.
- [ ] **F3** ✋ No es necesario fallback a `/usr/share/exxeguttor/…` (el paquete nuevo reemplaza al viejo por E2/E4).

### FASE G — Repo de contexto `exxeguttor-context` (público)
- [ ] **G1** ✅ Script `SCOPE=context`: reescribe `CLAUDE.md` (17 líneas), `context.md` (23), `docs/**`, `hotfixes/**` salvo `formas_handoff/**`, `mockups/**` (títulos y wordmark `EXXEGUTTOR` → `MAX-POTION`).
- [ ] **G2** ✋ `CLAUDE.md`: revisar a mano los puntos que **dan instrucciones** (no solo mencionan): `git clone https://TOKEN@github.com/junko012/max-potion.git`, nombre del repo de contexto, rutas `src/MaxPotion.UI/…`, "Proyecto Exxeguttor" → nuevo nombre, y la frase de la sección *Sobre el proyecto*.
- [ ] **G3** ✋ `context.md`: mismo repaso; agregar una sección corta **"Nombre del proyecto"** con la tabla de tokens (sección 1) y la fecha del renombre.
- [ ] **G4** ✅/✋ Herramientas en `hotfixes/*/tools/*.cs.txt` (`using MaxPotion.App.Services; namespace MaxPotion.Tests;`) y `hotfixes/fix_database/*.py`: actualizadas por el script; verificar que sigan coherentes con el nuevo namespace del proyecto de tests.
- [ ] **G5** ✋ **`status.md`: agregar una entrada nueva al final** (no reescribir las viejas): fecha, "Proyecto renombrado de Exxeguttor a <Nuevo>", commits de ambos repos, tabla de tokens, decisiones D1–D12 tomadas, y la lista de pendientes (compilación, empaquetado, Flatpak, logo).
- [ ] **G6** ✋ `mockups/confirmation_dialogs/download-sprites.py:21` (`OUT = Path("src/MaxPotion.UI/Assets/sprites")`) queda actualizado por el script; es una copia vieja de `scripts/download-sprites.py`.
- [ ] **G7** ✋ Guardar este mismo archivo como `docs/rename/RENAME_PLAN.md` en el repo de contexto (histórico del cambio).

### FASE H — Tests (`tests/MaxPotion.Tests`)
- [ ] **H1** ✅ 24 archivos de test: `namespace MaxPotion.Tests;` y `using MaxPotion.App.Services;`. `BagItemCategoryDiagnosticTests.cs:51` usa `MaxPotion.App.Services.PokemonDatabase.Instance…` calificado.
- [ ] **H2** ✋ Agregar un test de **guardia de recursos embebidos** (T3) en el proyecto de tests (solo ve `App`, no `UI`), con el estilo de diagnóstico del repo:
  ```csharp
  [Fact]
  public void EmbeddedResources_UseNewNamespace()
  {
      var names = typeof(MaxPotion.App.Services.PokemonDatabase).Assembly.GetManifestResourceNames();
      names.Should().Contain("MaxPotion.App.Assets.creatable_forms.json");
      names.Should().Contain("MaxPotion.App.Assets.uncreatable_species.json");
      names.Should().Contain("MaxPotion.App.Assets.uncreatable_forms.json");
      names.Should().Contain("MaxPotion.App.Assets.restricted_dex_availability.json");
      names.Should().NotContain(n => n.StartsWith("Exxeguttor", StringComparison.Ordinal));
  }
  ```
  Los recursos de la capa `UI` (sprites, sonido, tips, i18n, movesets) solo se pueden verificar arrancando la app (🧪 I6/I7).

### FASE I — Verificación (🧪; la hace Juan en su máquina porque el sandbox no tiene dotnet)
- [ ] **I1** `git grep -I -n -E 'Exxeguttor|exxeguttor|EXXEGUTTOR'` → vacío (código). En contexto: solo `status.md` y `hotfixes/formas_handoff/**`.
- [ ] **I2** `git ls-files | grep -i exxegu | grep -v -i exeggu` → vacío.
- [ ] **I3** Conteos de *Exeggutor* = línea base (T1: 60/42/3 y 20/4/0).
- [ ] **I4** Borrar artefactos viejos: `find . -type d \( -name bin -o -name obj \) -prune -exec rm -rf {} +` y carpetas de IDE (`.vs/`, `.idea/`).
- [ ] **I5** `dotnet clean && dotnet build max-potion.sln` sin errores ni warnings nuevos. `dotnet test` verde (incluye H2).
- [ ] **I6** `dotnet run --project src/MaxPotion.UI`: la ventana arranca; **splash** muestra `MAX-POTION` con texturas y fuente (prueba de `avares://<assembly>/`, T2/D2); el título es `Max-Potion — Editor de archivos…`; el ícono de la ventana carga.
- [ ] **I7** Abrir un save: sprites de Pokémon/ítems/tipos visibles; sonido de la Pokédex suena; Tips se abre; selector de idioma funciona; mochila y Pokédex cargan (prueban todos los recursos embebidos de `UI`).
- [ ] **I8** `xprop WM_CLASS` sobre la ventana (X11) o `app_id` (Wayland) y compararlo con `StartupWMClass` del `.desktop`.
- [ ] **I9** Diálogo *Acerca de* y título en **los 12 idiomas** (`es, en, ar, de, fr, hi, id, ja, ko, pt-BR, ru, zh-CN`), con foco en `fr`, `ar`, `hi`, `ja`, `ko`.
- [ ] **I10** Recientes: con un `~/.config/exxeguttor/recent.json` previo, tras F1 el nuevo `~/.config/max-potion/recent.json` aparece con las mismas entradas.
- [ ] **I11** `MAX_POTION_PROFILE=1 dotnet run …` activa el perfilado (`Perf.cs`).
- [ ] **I12** Build de paquetes (si se usan): `dpkg-deb`/`rpmbuild` instalan en `/usr/lib/max-potion`, `/usr/share/max-potion/{pokemon.db,lang/}`; la app encuentra `pokemon.db` (`PokemonDatabase.ResolveDbPath`, ruta 1).

### FASE J — Rollback
Un solo commit por repo: `git revert <hash>` (o `git reset --hard <hash-previo>` en local antes de pushear). Si ya se renombraron los repos de GitHub, GitHub mantiene redirecciones del nombre viejo, pero conviene volver a renombrar y restaurar `origin`.

## 6. Script de ejecución (`rename_project.sh`, probado en copias desechables)

Cubre B1–B3 y B5. **No** cubre los pasos ✋ (migración F1, compatibilidad de paquetes E2/E4, gramática de idiomas, archivos faltantes del `.spec`, `status.md`).

```bash
#!/usr/bin/env bash
# rename_project.sh — mecaniza las fases mecánicas del renombre Exxeguttor -> <NUEVO NOMBRE>.
# Uso:  SCOPE=code    ./rename_project.sh /ruta/al/clon/exxeguttor          [--dry-run]
#       SCOPE=context ./rename_project.sh /ruta/al/clon/exxeguttor-context  [--dry-run]
# NO hace commit ni push. Trabaja sobre un clon fresco con el árbol limpio.
set -euo pipefail

REPO="${1:?ruta al clon}"; DRY="${2:-}"
SCOPE="${SCOPE:?definir SCOPE=code|context}"

# ---------- TOKENS (editar SOLO esto si el nombre cambia) ----------
export NEW_DISPLAY="${NEW_DISPLAY:-Max-Potion}"      # texto visible: título, README, desktop Name
export NEW_PASCAL="${NEW_PASCAL:-MaxPotion}"         # namespaces, proyectos, carpetas (sin guiones ni espacios)
export NEW_SLUG="${NEW_SLUG:-max-potion}"            # paquetes, rutas /usr/share, ~/.config, .desktop, .ico, .sln
export NEW_ASSEMBLY="${NEW_ASSEMBLY:-$NEW_SLUG}"     # <AssemblyName> del .exe de la UI y host avares://
export NEW_UPPER="${NEW_UPPER:-MAX-POTION}"          # wordmark del splash
export NEW_ENVPREFIX="${NEW_ENVPREFIX:-MAX_POTION}"  # prefijo de variable de entorno (_PROFILE)
export OWNER="${OWNER:-junko012}"
export REPO_CODE="${REPO_CODE:-$NEW_SLUG}"           # repo de código (privado)
export REPO_CTX="${REPO_CTX:-$NEW_SLUG-context}"     # repo de contexto (público)
export FLATPAK="${FLATPAK:-io.github.$OWNER.$NEW_PASCAL}"
# Francés: "d'Exxeguttor" -> "de Max-Potion" salvo que el nombre nuevo empiece con vocal/h
case "${NEW_DISPLAY:0:1}" in [AEIOUHaeiouh]) export FR_DE="d'";; *) export FR_DE="de ";; esac

cd "$REPO"
[ -z "$(git status --porcelain)" ] || { echo "Árbol sucio: abortar."; exit 1; }

# Exclusiones: historial que NO se reescribe (log append-only y handoffs históricos)
EXCL='^$'
if [ "$SCOPE" = context ]; then EXCL='^(status\.md|hotfixes/formas_handoff/)'; fi

mapfile -d '' FILES < <(git ls-files -z | xargs -0 grep -I -l -Z -E 'Exxeguttor|exxeguttor|EXXEGUTTOR' 2>/dev/null || true)
SEL=()
for f in "${FILES[@]}"; do [[ "$f" =~ $EXCL ]] || SEL+=("$f"); done
echo "Archivos con contenido a reescribir: ${#SEL[@]}"

if [ "$DRY" = "--dry-run" ]; then printf '%s\n' "${SEL[@]}"; echo "(dry-run: nada modificado)"; exit 0; fi

# ---------- FASE CONTENIDO (orden importa: de lo más específico a lo más general) ----------
perl -pi -e '
  s{io\.github\.exxeguttor\.Exxeguttor}{$ENV{FLATPAK}}g;
  s{https://github\.com/exxeguttor/exxeguttor(?![\w-])}{https://github.com/$ENV{OWNER}/$ENV{REPO_CODE}}g;
  s{exxeguttor-context}{$ENV{REPO_CTX}}g;
  s{junko012/exxeguttor(?![\w-])}{junko012/$ENV{REPO_CODE}}g;
  s{exxeguttor-pokemon-database}{$ENV{NEW_SLUG}-pokemon-database}g;
  s{<AssemblyName>exxeguttor</AssemblyName>}{<AssemblyName>$ENV{NEW_ASSEMBLY}</AssemblyName>}g;
  s{avares://exxeguttor/}{avares://$ENV{NEW_ASSEMBLY}/}g;
  s{Exxeguttor\.(UI|App|Tests|DataBuilder)}{$ENV{NEW_PASCAL}.$1}g;
  s{EXXEGUTTOR_}{$ENV{NEW_ENVPREFIX}_}g;
  s{EXXEGUTTOR}{$ENV{NEW_UPPER}}g;
  s{d\x27Exxeguttor}{$ENV{FR_DE}$ENV{NEW_DISPLAY}}g;
  s{Exxeguttor}{$ENV{NEW_DISPLAY}}g;
  s{exxeguttor}{$ENV{NEW_SLUG}}g;
' "${SEL[@]}"

# ---------- FASE RENOMBRE DE RUTAS (git mv conserva historial) ----------
if [ "$SCOPE" = code ]; then
  git mv src/Exxeguttor.App   "src/$NEW_PASCAL.App"
  git mv src/Exxeguttor.UI    "src/$NEW_PASCAL.UI"
  git mv tests/Exxeguttor.Tests "tests/$NEW_PASCAL.Tests"
  git mv "src/$NEW_PASCAL.App/Exxeguttor.App.csproj"     "src/$NEW_PASCAL.App/$NEW_PASCAL.App.csproj"
  git mv "src/$NEW_PASCAL.UI/Exxeguttor.UI.csproj"       "src/$NEW_PASCAL.UI/$NEW_PASCAL.UI.csproj"
  git mv "tests/$NEW_PASCAL.Tests/Exxeguttor.Tests.csproj" "tests/$NEW_PASCAL.Tests/$NEW_PASCAL.Tests.csproj"
  git mv "src/$NEW_PASCAL.UI/Assets/exxeguttor.ico"      "src/$NEW_PASCAL.UI/Assets/$NEW_SLUG.ico"
  git mv exxeguttor.sln                                  "$NEW_SLUG.sln"
  git mv packaging/debian/exxeguttor.desktop             "packaging/debian/$NEW_SLUG.desktop"
  git mv packaging/rpm/exxeguttor.spec                   "packaging/rpm/$NEW_SLUG.spec"
fi
echo "OK. Revisar con: git status && git diff --stat"
```

Uso (cada repo es independiente, con árbol limpio):

```bash
SCOPE=code    ./rename_project.sh ~/work/exxeguttor          --dry-run   # lista; no modifica
SCOPE=code    ./rename_project.sh ~/work/exxeguttor                      # aplica
SCOPE=context ./rename_project.sh ~/work/exxeguttor-context  --dry-run
SCOPE=context ./rename_project.sh ~/work/exxeguttor-context
# Otro nombre: NEW_DISPLAY="Foo Bar" NEW_PASCAL=FooBar NEW_SLUG=foo-bar NEW_UPPER="FOO BAR" NEW_ENVPREFIX=FOO_BAR SCOPE=code ./rename_project.sh …
```

Resultado de la prueba (copias en `/tmp`, nombre Max-Potion): 194 archivos de código y 40 de contexto reescritos; 0 residuos del nombre viejo
(fuera de las exclusiones de contexto); 0 rutas con el nombre viejo; *Exeggutor* sin cambios (60/42/3 y 20/4/0); el nombre `Max-Potion` con guion
aparece en `.cs/.axaml/.csproj` **solo** en comentarios, `<Product>`, `Title=` y strings de UI (nunca como identificador).

## 7. Orden global recomendado

1. **A** (pre-vuelo) → 2. **B** (script código) → 3. **C–F** (revisión + manuales de código/empaquetado/migración) →
4. **H** (tests) → 5. **I** (verificación local, Juan compila) → 6. commit + push **código** →
7. **G** (repo de contexto + `status.md`) → commit + push **contexto** →
8. **Sección 8** (renombrar repos de GitHub y actualizar lo externo).

Razón: renombrar los repos al final evita que las URLs de las instrucciones del Project y los clones se rompan a mitad de trabajo.

## 8. Fuera de los repos (no lo toca ningún script)

- [ ] **X1** GitHub → *Settings → General → Repository name*: `exxeguttor` → `max-potion` y `exxeguttor-context` → `max-potion-context`. GitHub redirige las URLs viejas de git; **no confiar** en que las `raw.githubusercontent.com` viejas sigan sirviendo para siempre.
- [ ] **X2** `git remote set-url origin https://github.com/junko012/max-potion.git` (y el de contexto) en la máquina de Juan. Renombrar también las carpetas locales (`exxeguttor/` → `max-potion/`).
- [ ] **X3** **Instrucciones del Project de Claude.ai** (hoy se llama "exxeguttor"): cambiar el nombre del Project y las 3 URLs `raw.githubusercontent.com/junko012/exxeguttor-context/master/{CLAUDE,context,status}.md`, la URL de la API `…/exxeguttor-context/contents/mockups|hotfixes`, el título "PROYECTO: Exxeguttor" y los `git clone https://TOKEN@github.com/junko012/exxeguttor.git`. **Sin esto, las sesiones futuras leerán rutas viejas.**
- [ ] **X4** Memoria del Project (Claude): actualizar el nombre en los archivos de memoria del proyecto una vez hecho el renombre.
- [ ] **X5** Revocar el PAT que se pegó en el chat y generar uno nuevo con permisos mínimos.
- [ ] **X6** Flatpak/Flathub (si aplica): registrar el nuevo App ID (D3); el viejo queda huérfano.
- [ ] **X7** Cualquier release/etiqueta/artefacto ya publicado con el nombre viejo (no hay `.github/` en el árbol clonado).
- [ ] **X8** Logo/ícono nuevo (D8) y capturas/README con el nombre viejo.

## 9. Hallazgos preexistentes (no son parte del renombre, pero conviene resolverlos en la misma pasada)

1. `packaging/rpm/*.spec` referencia `packaging/rpm/exxeguttor.sh` y `Assets/exxeguttor.png` y el `control` menciona `lang-template.json`: **ninguno existe** en el repo.
2. `Homepage`/`URL` apuntan a `https://github.com/exxeguttor/exxeguttor` (dueño inexistente); el repo real es `junko012/exxeguttor`.
3. `Maintainer`/`%changelog` usan un email inventado (`exxeguttor@github.com`).
4. `.github/workflows/*` figuran en `CLAUDE.md` pero no están en el árbol.
5. `gen_ghost.py` tiene rutas absolutas del sandbox de Claude (`/home/claude/exxeguttor/…`).
6. La doc menciona `settings.json` de preferencias, sin código visible que lo use.
7. Metadatos del DB con nombres de herramientas históricos (`Exxeguttor.DataBuilder.v06`).
8. `status.md` ya tiene entradas duplicadas (bloques repetidos en las secciones del 11 oct): limpiar al agregar la entrada del renombre, sin borrar contenido útil.
