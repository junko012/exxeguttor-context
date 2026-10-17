# PLAN — Producto **MaxPotion**, proyecto interno **Exxeguttor** (con instaladores Linux y Windows)

> Generado en una sesión de análisis (2026-10-16) sobre `junko012/exxeguttor@af2bc6e` y `junko012/exxeguttor-context@99e2f4d`.
> **Reemplaza** al plan anterior (renombre total). Nada de esto se aplicó todavía. Incluye las decisiones que Juan confirmó el 2026-10-16 (sección 0-bis).
>
> **Qué se probó y qué no.** Probado en copias desechables: el script de marca (`brand_maxpotion.sh`, todas sus sustituciones con verificación de
> cantidad exacta, y los chequeos de la sección 7), el armado de los dos `.deb` (con un ejecutable ficticio, inspeccionados con `dpkg-deb`), el generador de iconos y el icono provisional (poción).
> **NO probado** (el sandbox no tiene dotnet, rpmbuild, Inno Setup ni Wine): compilación de la solución, `dotnet publish`, el `.spec` de RPM,
> el instalador de Windows y el comportamiento en ejecución (splash, `WM_CLASS`, sonido). Esos puntos están marcados 🧪 para que los verifique Juan.

## 0. Alcance en una frase

El proyecto sigue llamándose **Exxeguttor** por dentro (namespaces, carpetas, `.csproj`, `.sln`, tests, repos, documentación de contexto, base de datos).
Lo que **el usuario ve** pasa a llamarse **MaxPotion** (sin guion): ejecutable, paquetes `.deb`/`.rpm`/instalador Windows, rutas instaladas, carpeta de configuración,
ventana, splash, diálogo *Acerca de* en los 12 idiomas, acceso directo, propiedades del `.exe`, textos del README de uso.

Consecuencia clave: como `RootNamespace` **no cambia** (`Exxeguttor.UI` / `Exxeguttor.App`), **los 9 nombres de recurso embebido siguen valiendo tal cual**.
Solo cambia el nombre del *ensamblado* de la UI (`exxeguttor` → `maxpotion`), que ya era distinto del namespace.

## 0-bis. Decisiones ya tomadas por Juan (2026-10-16)

1. **Nunca se generó ningún ejecutable ni paquete `exxeguttor`.** Por lo tanto **no hay** `Replaces/Conflicts/Obsoletes` hacia el nombre viejo: ningún metadato de paquete lo menciona (D5).
2. **`LICENSE` pasa a `Copyright (C) 2025 MaxPotion contributors`** (D4). El script lo hace.
3. **Maintainer:** `MaxPotion contributors <junkoemc@proton.me>` (D3). Queda visible en `apt show` / `rpm -qi`.
4. **Icono:** por ahora un **icono provisional** (una poción) generado por código; el arte final se define luego (D7). Se adjuntan `maxpotion.png` y `maxpotion.ico` ya generados.

## 1. Reglas para quien ejecute este plan

1. **Nunca hacer push.** Entregar con `present_files`; Juan sube desde su terminal, directo a `master`. Sin Git LFS (incluido `pokemon.db`). El token se pide al empezar y no persiste.
2. Clon fresco de `junko012/exxeguttor` (privado, con token) y `junko012/exxeguttor-context` (público). Comparar `git log -1` con `af2bc6e` / `99e2f4d`; si hay commits nuevos, leer el diff antes.
3. **No hacer reemplazos globales.** Este plan es *selectivo por diseño*: cambiar `Exxeguttor` globalmente rompería namespaces y rutas internas. El script ya está acotado archivo por archivo y **aborta** si una sustitución no encuentra exactamente las apariciones esperadas (señal de que el código cambió desde este análisis).
4. Un commit lógico por repo. Mensaje sugerido: `rebrand: user-facing name MaxPotion (internal name stays Exxeguttor); win installer`.
5. Al terminar: recordar a Juan **actualizar `status.md`** (Fase F) y revocar el PAT usado.

## 2. Tokens

| Token | Uso | Valor |
|---|---|---|
| `BRAND` | Texto visible, `<Product>`, `Name=` del `.desktop`, README de uso, título de ventana | `MaxPotion` |
| `SLUG` | Ejecutable/ensamblado, paquetes, `/usr/share/<slug>`, `~/.config/<slug>`, `.desktop`, icono, `%APPDATA%\<slug>`, host `avares://` | `maxpotion` |
| `WORDMARK` | Texto del splash | `MAXPOTION` |
| `ENVV` | Variable de entorno (`_PROFILE`) | `MAXPOTION` |
| `FLATPAK` | App ID (hoy `io.github.exxeguttor.Exxeguttor`, con dueño inexistente) | `io.github.junko012.MaxPotion` |
| **Se queda** | Namespaces, carpetas `src/Exxeguttor.*`, `tests/Exxeguttor.Tests`, `exxeguttor.sln`, repos, docs de contexto, `~/.config/exxeguttor` solo como ruta *legacy* de migración | `Exxeguttor` |

Restricciones: `SLUG` sin `_` (el host de una URI `avares://` no lo admite) y sin espacios. Francés: `d'` solo si `BRAND` empieza con vocal/h; con `M` corresponde `de MaxPotion` (el script lo hace).

## 3. Decisiones abiertas (con recomendación)

| ID | Decisión | Recomendación |
|---|---|---|
| D1 | `AssemblyName`: `maxpotion` (minúscula) o `MaxPotion` | `maxpotion`: convención Linux, coincide con paquete/comando; en Windows queda `maxpotion.exe` y el nombre visible sale de `Product`/`FileDescription` |
| D2 | `Homepage`/`URL` en paquetes (hoy apuntan a `github.com/exxeguttor/exxeguttor`, dueño inexistente; el repo real es privado y se llama Exxeguttor) | **Eliminarlos** hasta tener una página pública de MaxPotion (el script ya los quita) |
| D3 | `Maintainer`/email (hoy `exxeguttor@github.com`, inventado) | **RESUELTO:** `MaxPotion contributors <junkoemc@proton.me>` (ya está en los controls del anexo 3 y el script lo aplica al `.spec`) |
| D4 | Texto de copyright en `LICENSE`, que se instala en `/usr/share/doc/maxpotion/` y se muestra en el instalador de Windows | **RESUELTO (confirmado):** `MaxPotion contributors`; el script lo cambia (`LICENSE:4`) |
| D5 | `Replaces/Conflicts: exxeguttor` en `.deb` y `Obsoletes` en rpm | **RESUELTO:** nunca existió un paquete `exxeguttor`; **no se agregan**. Los controls del anexo 3 ya vienen sin ellos |
| D6 | Flatpak: hoy solo existe la propiedad `FlatpakAppId` y una línea en el `.desktop`; no hay manifest | Mantener el ID `io.github.junko012.MaxPotion`; crear el manifest queda fuera de este plan |
| D7 | **Logo/icono.** El `Assets/exxeguttor.ico` original es una sola imagen de **251×251** (no es un `.ico` multi-tamaño válido para Windows) y es un sprite de huevo ligado al nombre viejo | **RESUELTO provisionalmente:** icono de poción generado por código (`scripts/gen-placeholder-icon.py`, anexo 5), ya generado y adjunto (`maxpotion.png` 256×256 + `maxpotion.ico` 16–256 px). El arte final se decide luego y se aplica con `scripts/make-icons.py` (anexo 4) |
| D8 | Firma de código en Windows (SmartScreen advierte con ejecutables sin firmar y *self-extract*) | Fuera de alcance; documentado en sección 5-E |
| D9 | Instalación Windows por usuario (sin UAC) o por máquina | Por usuario por defecto, con diálogo para elegir "todos los usuarios" (así está el `.iss`) |
| D10 | Arquitecturas Windows | Solo `win-x64` por ahora (ARM64 queda aparte) |
| D11 | Variable de entorno `EXXEGUTTOR_PROFILE` → `MAXPOTION_PROFILE` (solo desarrolladores) | Renombrar (el script lo hace). Sin compatibilidad con la vieja |
| D12 | Sonido de la Pokédex en Windows (hoy solo `paplay`/`aplay`) | Opcional: rama con `winmm.PlaySound` (sección 5-E). Sin ella la app funciona, simplemente sin sonido |
| D13 | Subpaquete `-devel` (rpm: `%files devel` vacío; deb: `Suggests: …-devel` a un paquete inexistente) | **Eliminarlo**: además, un paquete de símbolos expondría `Exxeguttor.App.pdb` |

## 4. Matriz: qué cambia y qué se queda

**CAMBIA (visible al usuario)** — el script lo hace con verificación; ≈ 30 archivos tocados y 3 `git mv` (icono, `.desktop`, `.spec`):

| Zona | Archivo | Cambio |
|---|---|---|
| Ejecutable | `src/Exxeguttor.UI/Exxeguttor.UI.csproj` | `AssemblyName`→`maxpotion`; `Product`→`MaxPotion`; **nuevos** `AssemblyTitle`, `Company`, `ApplicationIcon` (icono dentro del `.exe` de Windows); `Authors`/`Copyright`→`MaxPotion contributors`; `Description` sin "for Linux"; `FlatpakAppId` |
| Ejecutable | `src/Exxeguttor.UI/app.manifest` | `assemblyIdentity name="MaxPotion"` |
| Icono | `Assets/exxeguttor.ico` → `Assets/maxpotion.ico`; `Views/MainWindow.axaml:11` | renombre + referencia |
| Splash | `Views/SplashWindow.axaml` | `Title`, wordmark `MAXPOTION`, y **3** URIs `avares://maxpotion/…` (host = nombre del ensamblado) |
| Idiomas | `i18n/es.json`, `i18n/en.json`, `lang/{ar,de,fr,hi,id,ja,ko,pt-BR,ru,zh-CN}.json` | 3 claves por archivo: `App_Title`, `Menu_Help_About`, `Dialog_About_Title`. `fr`: `À propos de MaxPotion` |
| Texto en código | `PokemonEditorViewModel.cs:3041` | `"Aviso de MaxPotion (no es una regla de PKHeX…"` |
| Rutas | `App/Services/PokemonDatabase.cs:157` | `/usr/share/maxpotion/pokemon.db` |
| Rutas | `UI/i18n/LocalizationService.cs:92,96,164` | `/usr/share/maxpotion/lang` |
| Rutas | `App/Services/RecentSavesService.cs:7,30` y `MainWindowViewModel.cs:980` | `~/.config/maxpotion/recent.json` (+ migración manual, 5-C) |
| Temporales | `UI/Services/SoundService.cs:80` | `maxpotion_<recurso>.wav` en el directorio temporal |
| Entorno | `UI/Services/Perf.cs:7,13` | `MAXPOTION_PROFILE` |
| Empaquetado | `packaging/debian/control`, `exxeguttor.desktop`→`maxpotion.desktop`, `packaging/rpm/exxeguttor.spec`→`maxpotion.spec` | nombres, rutas, `Name=`, `Exec`, `Icon`, `StartupWMClass`, flatpak ID; quita `Homepage`/`URL`. **Las rutas internas `src/Exxeguttor.UI/…` del `.spec` se preservan** |
| README | `README.md` (solo hasta `## Compilar desde fuente`) | título, nombres de paquetes, comandos de instalación y de ejecución |
| Licencia | `LICENSE:4` | `Copyright (C) 2025 MaxPotion contributors` |

**SE QUEDA (interno)**: 144 `namespace` + 94 `using` + `x:Class`/`xmlns:…using:` de 18 AXAML; los 9 nombres de recurso embebido; `RootNamespace`, `ProjectReference`, nombres de `.csproj`; carpetas `src/Exxeguttor.App|UI`, `tests/Exxeguttor.Tests`; `exxeguttor.sln`; sección "Compilar desde fuente" del README (`git clone …/exxeguttor`, `dotnet build exxeguttor.sln`, `dotnet run --project src/Exxeguttor.UI`); `scripts/*.py`; `pokemon-database/**` (incluida su `LICENCE`) y los 2 metadatos del DB (`Generator`, `MigrationSource`: no se leen en código y es un blob de 51 MB); todo el repo de contexto salvo las notas de la sección 8.

**Sigue existiendo el nombre viejo, pero no lo ve un usuario normal**: metadatos gestionados dentro del `.exe` (nombres de tipos), trazas de pila de un crash, comentarios XML, metadatos del DB, y un mensaje de error interno en `PokedexService.cs:378` (`"…embebido en Exxeguttor.App."`; opcional: cambiarlo a *"…en el ensamblado principal"*). La carpeta de config vieja `~/.config/exxeguttor/` solo se menciona como ruta legacy en el código de migración.

> **Trampa a recordar:** con `PublishSingleFile=true` el ensamblado `Exxeguttor.App.dll` viaja **dentro** del ejecutable. Si alguien publica sin *single-file*, aparecerían archivos `Exxeguttor.App.dll`/`.pdb` sueltos. Mantener `PublishSingleFile` y `-p:DebugType=none` en los dos sistemas.

## 5. Plan atomizado

Convención: ✅ lo hace un script · ✋ manual · 🧪 verificación (la hace Juan, necesita dotnet/Windows/Fedora).

### FASE A — Pre-vuelo
- [ ] **A1** ✋ Clones frescos; comparar commits (regla 2).
- [ ] **A2** ✋ Ya resueltas: D3, D4, D5, D7 (sección 0-bis). Quedan con recomendación por defecto, sin bloquear: D1, D2, D6, D8–D13 (confirmar si Juan quiere otra cosa).
- [ ] **A3** ✋ Árbol limpio (`git status --porcelain` vacío). El script aborta si no.

### FASE B — Script de marca (anexo 1)
- [ ] **B1** ✅ Guardar `brand_maxpotion.sh` fuera del repo y ejecutar: `./brand_maxpotion.sh ~/work/exxeguttor`. Si aborta con `ASSERT … esperado=N encontrado=M`, el código cambió: ver esa línea, ajustar el esperado y seguir (no forzar).
- [ ] **B2** 🧪 Correr los chequeos de la sección 7 (V1–V4, V6): todos vacíos salvo el caso permitido de V3.

### FASE C — Pasos manuales de código
- [ ] **C1 Icono provisional (D7)** ✋ Copiar los adjuntos `maxpotion.png` (256×256) y `maxpotion.ico` (16–256 px) a `src/Exxeguttor.UI/Assets/`, **pisando** el `.ico` que el script acaba de renombrar (el original es de 251×251 y de un solo tamaño). Para regenerarlos: `python3 scripts/gen-placeholder-icon.py` (anexo 5, requiere Pillow). Con arte final: `python3 scripts/make-icons.py <arte.png>` (anexo 4). El `.spec` y `build-deb.sh` exigen que exista `Assets/maxpotion.png`.
- [ ] **C2 Migración de configuración (evita perder "Recientes")** ✋ En `RecentSavesService.cs`, reemplazar el ctor sin parámetros (el script ya cambió la ruta a `maxpotion`) por:
  ```csharp
  public RecentSavesService() : this(ResolveDefaultPath()) { }

  private static string ResolveDefaultPath()
  {
      var baseDir = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
      var current = Path.Combine(baseDir, "maxpotion", "recent.json");
      var legacy  = Path.Combine(baseDir, "exxeguttor", "recent.json"); // legacy: nombre previo al rebranding
      try
      {
          if (!File.Exists(current) && File.Exists(legacy))
          {
              Directory.CreateDirectory(Path.GetDirectoryName(current)!);
              File.Move(legacy, current);
          }
      }
      catch { /* mejor esfuerzo: si falla, arranca sin recientes */ }
      return current;
  }
  ```
  Esa línea `"exxeguttor"` es la **única excepción permitida** en el chequeo V3. Nota: el ctor `internal RecentSavesService(string filePath)` no es visible desde `tests/` (no hay `InternalsVisibleTo` en el repo); para testear la migración hay que agregar `[assembly: InternalsVisibleTo("Exxeguttor.Tests")]` en `Exxeguttor.App`.
- [ ] **C3 `WM_CLASS` de la ventana (Linux)** 🧪 Tras compilar, `xprop WM_CLASS` sobre la ventana (X11). El valor debe coincidir con `StartupWMClass=maxpotion` del `.desktop`. Si no coincide, fijarlo explícitamente en `Program.cs` (✋, comprobar que compila con Avalonia 11.3.8):
  ```csharp
  return AppBuilder.Configure<App>().UsePlatformDetect()
      .With(new X11PlatformOptions { WmClass = "maxpotion" })
      .WithInterFont().LogToTrace().StartWithClassicDesktopLifetime(args);
  ```
- [ ] **C4 README** ✋ (a) Línea 3: `Editor nativo de archivos de guardado Pokémon para Linux y Windows.` (b) Agregar antes de `### Portable (cualquier distro)`:
  ```markdown
  ### Windows 10/11 (x64)
  Descarga y ejecuta `maxpotion-1.0.0-win-x64-setup.exe`, o usa la versión portable
  `maxpotion-1.0.0-win-x64.zip` (descomprimir y abrir `maxpotion.exe`).
  ```
  (c) Sección *Requisitos*: agregar `Windows 10 u 11, x64`. (d) `README.md:78` clona `github.com/exxeguttor/exxeguttor.git` (dueño inexistente): corregir a `github.com/junko012/exxeguttor.git` solo si el repo pasa a ser público.
- [ ] **C5 LICENSE (D4)** ✅ lo hace el script (`LICENSE:4`). 🧪 `git grep -n -i exxeguttor -- LICENSE` → vacío. `pokemon-database/LICENCE` no se toca.
- [ ] **C6 Mensaje interno opcional** ✋ `PokedexService.cs:378`: cambiar `"… embebido en Exxeguttor.App."` por `"… embebido en el ensamblado principal."`.

### FASE D — Paquetes Linux
> Hoy el repo **no tiene ningún script que arme los paquetes**, y el `packaging/debian/control` actual mezcla dos paquetes en un archivo (formato de fuente), que `dpkg-deb --build` no acepta. Se reemplaza por un control por paquete + un script (probado).
- [ ] **D1** ✋ Crear `packaging/debian/maxpotion.control` y `packaging/debian/maxpotion-lang.control` (anexo 3) y **borrar** `packaging/debian/control`. Ya traen el `Maintainer` real (D3) y no llevan `Replaces/Conflicts` (D5).
- [ ] **D2** ✋ Crear `packaging/build-deb.sh` (anexo 3, probado con un ejecutable ficticio). Reemplaza el launcher `maxpotion.sh` que el `.spec` referencia y **no existe** por un symlink `/usr/bin/maxpotion → ../lib/maxpotion/maxpotion`. Instala `LICENSE` como `/usr/share/doc/maxpotion/copyright`.
- [ ] **D3 RPM** ✋ Corregir `packaging/rpm/maxpotion.spec` (no probado, sin `rpmbuild` en el sandbox):
  - quitar `Source0` (no se usa) y todo el bloque `%package devel` / `%description devel` / `%files devel` (D13);
  - `%install`: reemplazar `install -m 755 packaging/rpm/maxpotion.sh …/usr/bin/maxpotion` por `ln -s ../lib/maxpotion/maxpotion %{buildroot}/usr/bin/maxpotion`;
  - `%install` del paquete `lang`: `install -m 644 lang/*.json %{buildroot}/usr/share/maxpotion/lang/` (hoy solo instala `zh-CN` pero la descripción promete 10 idiomas);
  - **`%changelog` (error previo):** la fecha `* 2025-01-01 …` no es válida para rpm (exige `Día Mes DD AAAA`). Dejar `* Fri Oct 16 2026 MaxPotion contributors <junkoemc@proton.me> - 1.0.0-1`; sin `Obsoletes` (D5);
  - el binario debe estar en la raíz del árbol de build (`cp artifacts/linux-x64/maxpotion .`) y ejecutar `rpmbuild -bb --build-in-place --define "_topdir $PWD/artifacts/rpm" packaging/rpm/maxpotion.spec`;
  - 🧪 probar en Fedora/contenedor `fedora`; `rpmlint` debe quedar sin errores (advertencia por falta de `URL` aceptada por D2).
- [ ] **D4 Portable `.tar.gz`** ✋ `mkdir -p artifacts/maxpotion-1.0.0-linux-x64/lang && cp artifacts/linux-x64/maxpotion pokemon-database/database/pokemon.db LICENSE artifacts/maxpotion-1.0.0-linux-x64/ && cp lang/*.json artifacts/maxpotion-1.0.0-linux-x64/lang/ && tar -C artifacts -czf artifacts/maxpotion-1.0.0-linux-x64.tar.gz maxpotion-1.0.0-linux-x64`. `PokemonDatabase` y `LocalizationService` ya buscan junto al ejecutable (`AppContext.BaseDirectory`).
- [ ] **D5** 🧪 `sudo apt install ./artifacts/maxpotion_1.0.0_amd64.deb` → aparece **MaxPotion** en el menú, con el icono; se ejecuta con `maxpotion`.

### FASE E — Windows
**Estado actual:** no existe nada para Windows. El código es casi portable: `ApplicationData` ya resuelve a `%APPDATA%`, `pokemon.db` y `lang/` se buscan junto al ejecutable (`AppContext.BaseDirectory`, rutas ya presentes en el código), las rutas se arman con `Path.Combine`, y `app.manifest` ya declara `PerMonitorV2`. Lo que falta:
- [ ] **E1** ✋ `Exxeguttor.UI.csproj` ya recibe `ApplicationIcon`, `Company`, `AssemblyTitle` del script (el `.exe` mostrará Producto/Empresa/Icono). Agregar `<FileVersion>1.0.0.0</FileVersion>`. 🧪 Propiedades del `.exe` → *Detalles*: debe decir MaxPotion, nunca Exxeguttor.
- [ ] **E2** ✋ **RuntimeIdentifier.** El `.csproj` fija `<RuntimeIdentifier>linux-x64</RuntimeIdentifier>`; al publicar con `-r win-x64` el valor de la línea de comandos tiene prioridad, pero un `dotnet build` en Windows seguiría generando linux-x64. Cambiarlo a: `<RuntimeIdentifier Condition="'$(RuntimeIdentifier)' == '' And $([MSBuild]::IsOSPlatform('Linux'))">linux-x64</RuntimeIdentifier>`.
- [ ] **E3** ✋ (D12, opcional) Sonido en Windows: en `SoundService.Play`, antes de `TryStart("paplay"…)`:
  ```csharp
  if (OperatingSystem.IsWindows()) { PlaySound(path, IntPtr.Zero, SND_FILENAME | SND_ASYNC | SND_NODEFAULT); return; }
  // …
  [System.Runtime.InteropServices.DllImport("winmm.dll", CharSet = System.Runtime.InteropServices.CharSet.Unicode)]
  private static extern bool PlaySound(string pszSound, IntPtr hmod, uint fdwSound);
  private const uint SND_ASYNC = 0x0001, SND_NODEFAULT = 0x0002, SND_FILENAME = 0x00020000;
  ```
- [ ] **E4** ✋ Crear `packaging/windows/maxpotion.iss` (anexo 2). El `AppId` ya trae un GUID generado; **no cambiarlo nunca**.
- [ ] **E5 Publish Windows** (ver sección 6): produce `artifacts/win-x64/maxpotion.exe`.
- [ ] **E6 Instalador** ✋ En Windows: instalar Inno Setup 6.3+ (`choco install innosetup`) y `iscc packaging\windows\maxpotion.iss /DAppVersion=1.0.0` → `artifacts\maxpotion-1.0.0-win-x64-setup.exe`. Desde Linux requiere Wine + Inno (no probado). Alternativa CI: runner `windows-latest` de GitHub Actions (hoy el repo no tiene `.github/`).
- [ ] **E7 Portable ZIP** ✋ `artifacts/maxpotion-1.0.0-win-x64/{maxpotion.exe, pokemon.db, LICENSE, lang/*.json}` → `maxpotion-1.0.0-win-x64.zip`.
- [ ] **E8** 🧪 En una VM Windows 10/11 limpia: el instalador muestra *MaxPotion* (asistente, Menú Inicio, "Agregar o quitar programas" con editor *MaxPotion contributors*); instala en `%LOCALAPPDATA%\Programs\MaxPotion`; la app arranca (splash `MAXPOTION`), encuentra `pokemon.db`, abre un save, lista los 12 idiomas, guarda "Recientes" en `%APPDATA%\maxpotion\recent.json`; desinstalar elimina los archivos y deja `%APPDATA%\maxpotion` (los datos del usuario).
- [ ] **E9** 🧪 Riesgos Windows aún no cubiertos por pruebas: nombres de backup de saves (`SaveFileService` usa `ː` en lugar de `:`, ya contemplado), rutas largas, antivirus/SmartScreen con ejecutables *self-extract* sin firma. Firmar (`signtool`) queda fuera de este plan (D8).

### FASE F — Repo de contexto
- [ ] **F1** ✋ Agregar a `CLAUDE.md` (sección de reglas) y a `context.md` (sección "Nombre del proyecto"): *"Nombre interno: Exxeguttor (código, namespaces, carpetas, repos, DB, documentación). Nombre de producto: MaxPotion (ejecutable `maxpotion`, paquetes, rutas instaladas, UI, instaladores). **Regla: nada visible al usuario dice Exxeguttor.** Al agregar texto de UI, rutas de ejecución o nombres de paquetes usar MaxPotion/maxpotion; al agregar namespaces/carpetas/tests seguir usando Exxeguttor."*
- [ ] **F2** ✋ `status.md`: **entrada nueva** (no reescribir las viejas): fecha, alcance (producto MaxPotion / interno Exxeguttor), commits de ambos repos, decisiones D1–D13 (con las 4 confirmadas), y pendientes (arte final del icono, rpm probado, instalador probado en VM, firma, página pública, email del Maintainer definitivo).
- [ ] **F3** ✋ Guardar este archivo como `docs/branding/PLAN_MAXPOTION.md`.
- [ ] **F4** ✋ Opcional: `mockups/splash_screen/splash_screen_boceto.html` (líneas 328, 380, 540) muestran el wordmark `EXXEGUTTOR`; actualizarlas a `MAXPOTION` si Juan quiere que el boceto refleje lo implementado.
- [ ] **F5** **Nada que cambiar** en las instrucciones del Project de Claude.ai, URLs raw ni `git clone`: los repos conservan su nombre. Solo revocar el PAT que se pegó en el chat.

### FASE G — Rollback
Un commit por repo: `git revert <hash>`. No hay renombres de carpetas ni de repos, así que revertir no deja nada huérfano. Si ya hubo migración de `recent.json`, el archivo habrá quedado en `~/.config/maxpotion/` (moverlo de vuelta a mano si se vuelve a un build viejo).

## 6. Build y publicación (comandos, no probados)

```bash
# Linux x64 (mismo árbol para .deb, .rpm y .tar.gz)
dotnet publish src/Exxeguttor.UI -c Release -r linux-x64 --self-contained \
  -p:PublishSingleFile=true -p:DebugType=none -p:DebugSymbols=false -o artifacts/linux-x64
# Windows x64 (se puede ejecutar desde Linux o desde Windows)
dotnet publish src/Exxeguttor.UI -c Release -r win-x64 --self-contained \
  -p:PublishSingleFile=true -p:DebugType=none -p:DebugSymbols=false -o artifacts/win-x64
```
🧪 `ls artifacts/linux-x64 artifacts/win-x64`: debe aparecer `maxpotion` / `maxpotion.exe` y **ningún** archivo con `exxeguttor` en el nombre (`find artifacts -iname '*exxeguttor*'` vacío). Si aparecen `.dll`/`.pdb` sueltos, revisar que `PublishSingleFile` y `DebugType=none` llegaron al build.
Luego: `packaging/build-deb.sh artifacts/linux-x64 1.0.0` · `rpmbuild …` (D3) · `iscc …` (E6).
Versión: hoy está escrita a mano en 4 sitios (`<Version>` del csproj, los dos controls, el `.spec`) y el instalador la recibe por `/DAppVersion`. Mantenerlas iguales al publicar.

## 7. Verificación (los chequeos 1–5 están probados contra la copia transformada)

```bash
# V1 perímetro de usuario: debe estar VACÍO
git grep -n -i exxeguttor -- lang 'src/Exxeguttor.UI/i18n/*.json' packaging | grep -v 'src/Exxeguttor.UI/Assets/maxpotion.png'
# V2 AXAML: solo namespaces/x:Class/enlaces de contexto -> VACÍO
git grep -n -i exxeguttor -- '*.axaml' | grep -v -E 'using:Exxeguttor\.|x:Class="Exxeguttor\.|exxeguttor-context'
# V3 strings en C# con el nombre, excluyendo nombres de recurso y comentarios XML.
#    Únicas apariciones permitidas: PokedexService.cs:378 (opcional C6) y la ruta legacy de RecentSavesService (C2)
git grep -n -E '"[^"]*[Ee]xxeguttor[^"]*"' -- '*.cs' | grep -v -E '///|"Exxeguttor\.(UI|App)\.(Assets|i18n)\.|Exxeguttor\.UI\.i18n'
# V4 README: solo la sección "Compilar desde fuente"
git grep -n -i exxeguttor -- README.md
# V5 csproj UI: solo RootNamespace, ProjectReference y el comentario de Tips
grep -n -i exxeguttor src/Exxeguttor.UI/Exxeguttor.UI.csproj
# V6 rutas con el nombre viejo fuera de las carpetas internas: VACÍO
git ls-files | grep -i exxeguttor | grep -v -E '^(src/Exxeguttor\.(App|UI)/|tests/Exxeguttor\.Tests/|exxeguttor\.sln)'
```
🧪 En ejecución (Juan): ventana y *Acerca de* dicen MaxPotion en **los 12 idiomas** (mirar `fr`, `ar`, `hi`, `ja`, `ko`); splash `MAXPOTION` con texturas y fuente (prueba del host `avares://maxpotion/`); sprites, sonido, tips, mochila y Pokédex cargan (recursos embebidos intactos); `~/.config/maxpotion/recent.json` conserva los recientes viejos tras C2; `dpkg -L maxpotion` y `apt show maxpotion` sin el nombre viejo (cero apariciones, incluso en `Depends`/`Replaces`); `ps`/`top` muestran `maxpotion`; `/tmp/maxpotion_spark_chime.wav` al sonar; `~/.net/maxpotion/` (extracción de nativas) en vez de `~/.net/exxeguttor/`.

## 8. Hallazgos que ya existían (no son del cambio de nombre)

1. El `.spec` referenciaba `exxeguttor.sh` y un icono `.png` que **no existen** (D2/C1); el `control` mencionaba `lang-template.json`, tampoco existe.
2. El `control` actual no es válido para `dpkg-deb` (dos paquetes en un archivo; campo `X-Flatpak-AppID` no estándar).
3. El `.spec` instalaba solo `zh-CN` en el paquete de idiomas aunque la descripción promete 10.
4. `Homepage`/`URL` con un dueño de GitHub inexistente; email de mantenedor inventado.
5. `CLAUDE.md` menciona `.github/workflows/*`, que no están en el árbol clonado.
6. `README` dice "Copia `lang/en.json`" para crear un idioma, pero `en.json` vive en `src/Exxeguttor.UI/i18n/`.
7. `gen_ghost.py` tiene rutas absolutas del sandbox de Claude.
8. `status.md` tiene bloques duplicados (11 oct); limpiar al agregar la entrada nueva.
9. El icono original es de un solo tamaño (251×251).
10. El `%changelog` del `.spec` usaba una fecha en formato ISO, inválida para rpm.

---

## Anexo 1 — `brand_maxpotion.sh` (probado)

```bash
#!/usr/bin/env bash
# brand_maxpotion.sh — cambia SOLO lo visible al usuario: Exxeguttor -> MaxPotion.
# El código/proyecto/repos siguen llamándose Exxeguttor (namespaces, carpetas, .csproj, .sln, tests).
# Uso: ./brand_maxpotion.sh /ruta/al/clon/exxeguttor
# Aborta si el árbol está sucio o si alguna sustitución no encuentra EXACTAMENTE las apariciones esperadas.
set -euo pipefail
REPO="${1:?ruta al clon del repo de código}"; cd "$REPO"
[ -z "$(git status --porcelain)" ] || { echo "Árbol sucio: abortar."; exit 1; }

BRAND="MaxPotion"; SLUG="maxpotion"; ENVV="MAXPOTION"; FLATPAK="io.github.junko012.MaxPotion"
EMAIL="junkoemc@proton.me"   # Maintainer (decisión D3)

# sub FILE FROM TO [N_ESPERADO=1] — reemplazo literal con verificación de cantidad
sub() {
  local f="$1" from="$2" to="$3" n="${4:-1}" c
  [ -f "$f" ] || { echo "FALTA ARCHIVO: $f"; exit 1; }
  c=$(grep -o -F -- "$from" "$f" | wc -l)
  [ "$c" -eq "$n" ] || { echo "ASSERT $f: '$from' esperado=$n encontrado=$c"; exit 1; }
  FROM="$from" TO="$to" perl -pi -e 's/\Q$ENV{FROM}\E/$ENV{TO}/g' "$f"
}

UI=src/Exxeguttor.UI; APP=src/Exxeguttor.App

# 1) Metadatos del ejecutable (UI.csproj). RootNamespace/ProjectReference NO se tocan.
sub $UI/Exxeguttor.UI.csproj '<AssemblyName>exxeguttor</AssemblyName>' "<AssemblyName>$SLUG</AssemblyName>"
sub $UI/Exxeguttor.UI.csproj '<Product>Exxeguttor</Product>' \
    "<Product>$BRAND</Product>
    <AssemblyTitle>$BRAND</AssemblyTitle>
    <Company>$BRAND contributors</Company>
    <ApplicationIcon>Assets\\$SLUG.ico</ApplicationIcon>"
sub $UI/Exxeguttor.UI.csproj 'exxeguttor contributors' "$BRAND contributors" 2
sub $UI/Exxeguttor.UI.csproj 'io.github.exxeguttor.Exxeguttor' "$FLATPAK"
sub $UI/Exxeguttor.UI.csproj '<Description>Pokémon save file editor for Linux</Description>' '<Description>Pokémon save file editor</Description>'   # el ejecutable ahora también sale para Windows
sub $UI/app.manifest 'name="Exxeguttor.UI"' "name=\"$BRAND\""

# 2) Icono: renombrar archivo y su referencia
git mv $UI/Assets/exxeguttor.ico $UI/Assets/$SLUG.ico
sub $UI/Views/MainWindow.axaml '/Assets/exxeguttor.ico' "/Assets/$SLUG.ico"

# 3) Splash (título, wordmark, host avares = nombre del ensamblado)
sub $UI/Views/SplashWindow.axaml 'Title="Exxeguttor"' "Title=\"$BRAND\""
sub $UI/Views/SplashWindow.axaml 'Text="EXXEGUTTOR"' "Text=\"${BRAND^^}\""
sub $UI/Views/SplashWindow.axaml 'avares://exxeguttor/' "avares://$SLUG/" 3

# 4) Textos de interfaz: 3 claves por idioma (App_Title, Menu_Help_About, Dialog_About_Title)
for f in $UI/i18n/es.json $UI/i18n/en.json lang/{ar,de,hi,id,ja,ko,pt-BR,ru,zh-CN}.json; do
  sub "$f" 'Exxeguttor' "$BRAND" 3
done
sub lang/fr.json "d'Exxeguttor" "de $BRAND" 2      # elisión: "d'" solo si el nombre empieza con vocal/h
sub lang/fr.json 'Exxeguttor' "$BRAND" 1
sub $UI/ViewModels/PokemonEditorViewModel.cs 'Aviso de Exxeguttor' "Aviso de $BRAND"

# 5) Rutas de ejecución (datos del sistema, config de usuario, temporales, variable de entorno)
sub $APP/Services/PokemonDatabase.cs '"share", "exxeguttor"' "\"share\", \"$SLUG\""
sub $UI/i18n/LocalizationService.cs '/usr/share/exxeguttor' "/usr/share/$SLUG" 3
sub $APP/Services/RecentSavesService.cs '"exxeguttor",' "\"$SLUG\","
sub $APP/Services/RecentSavesService.cs '~/.config/exxeguttor/recent.json' "~/.config/$SLUG/recent.json"
sub $UI/ViewModels/MainWindowViewModel.cs '~/.config/exxeguttor/recent.json' "~/.config/$SLUG/recent.json"
sub $UI/Services/SoundService.cs '$"exxeguttor_{' "\$\"${SLUG}_{"
sub $UI/Services/Perf.cs 'EXXEGUTTOR_PROFILE' "${ENVV}_PROFILE" 2

# 6) Empaquetado: todo el directorio packaging/ es de cara al usuario
for f in packaging/debian/control packaging/debian/exxeguttor.desktop packaging/rpm/exxeguttor.spec; do
  FLATPAK="$FLATPAK" BRAND="$BRAND" SLUG="$SLUG" EMAIL="$EMAIL" perl -pi -e '
    s{io\.github\.exxeguttor\.Exxeguttor}{$ENV{FLATPAK}}g;
    s{exxeguttor contributors <exxeguttor\@github\.com>}{$ENV{BRAND} contributors <$ENV{EMAIL}>}g;
    s{exxeguttor contributors}{$ENV{BRAND} contributors}g;
    s{Exxeguttor\.(UI|App|Tests)}{\x01KEEP\x01$1}g;   # rutas internas del repo (src/Exxeguttor.UI/...) NO se tocan
    s{Exxeguttor}{$ENV{BRAND}}g;
    s{exxeguttor}{$ENV{SLUG}}g;
    s{\x01KEEP\x01(UI|App|Tests)}{Exxeguttor.$1}g;
  ' "$f"
done
# Homepage/URL apuntaban a un dueño inexistente y el repo real es privado: se eliminan (decisión D4)
perl -ni -e 'print unless /^Homepage:/' packaging/debian/control
perl -ni -e 'print unless /^URL:/' packaging/rpm/exxeguttor.spec
git mv packaging/debian/exxeguttor.desktop packaging/debian/$SLUG.desktop
git mv packaging/rpm/exxeguttor.spec       packaging/rpm/$SLUG.spec

# 6b) LICENSE (decisión D4 confirmada): texto de copyright que se instala con los paquetes y se muestra en el instalador de Windows
sub LICENSE 'exxeguttor contributors' "$BRAND contributors"

# 7) README: solo la parte de uso/instalación (hasta "## Compilar desde fuente"); build desde fuente NO cambia
perl -pi -e '
  BEGIN{$stop=0}
  $stop=1 if /^## Compilar desde fuente/;
  unless($stop){ s{exxeguttor}{maxpotion}g; s{Exxeguttor}{MaxPotion}g; }
' README.md

echo "OK. Siguiente: pasos manuales (icono multi-tamaño, migración de config, Windows, LICENSE)."
```

## Anexo 2 — `packaging/windows/maxpotion.iss` (NO probado: sin Inno Setup en el sandbox)

```ini
; packaging/windows/maxpotion.iss — instalador de MaxPotion para Windows (Inno Setup 6.3+)
; Compilar:  iscc packaging\windows\maxpotion.iss /DAppVersion=1.0.0
; Entrada esperada:  artifacts\win-x64\maxpotion.exe   (salida de dotnet publish -r win-x64, ver sección 5)
#define AppName   "MaxPotion"
#define AppExe    "maxpotion.exe"
#define Publisher "MaxPotion contributors"
#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif

[Setup]
; AppId: GUID FIJO. Generado una vez; NO cambiarlo nunca (identifica el programa para actualizar/desinstalar).
AppId={{F702B6C1-080F-4541-A0F8-2CEC32797C9A}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#Publisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\{#AppExe}
UninstallDisplayName={#AppName}
OutputDir=..\..\artifacts
OutputBaseFilename=maxpotion-{#AppVersion}-win-x64-setup
SetupIconFile=..\..\src\Exxeguttor.UI\Assets\maxpotion.ico
LicenseFile=..\..\LICENSE
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
; Instala por usuario por defecto (sin UAC); el usuario puede elegir "para todos" en el diálogo.
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
VersionInfoVersion={#AppVersion}
VersionInfoProductName={#AppName}
VersionInfoCompany={#Publisher}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Components]
Name: "main"; Description: "{#AppName}"; Types: full compact custom; Flags: fixed
Name: "lang"; Description: "Additional languages / Idiomas adicionales"; Types: full

[Files]
Source: "..\..\artifacts\win-x64\{#AppExe}";            DestDir: "{app}";      Flags: ignoreversion; Components: main
Source: "..\..\pokemon-database\database\pokemon.db";    DestDir: "{app}";      Flags: ignoreversion; Components: main
Source: "..\..\LICENSE";                                 DestDir: "{app}";      Flags: ignoreversion; Components: main
Source: "..\..\lang\*.json";                             DestDir: "{app}\lang"; Flags: ignoreversion; Components: lang

[Icons]
Name: "{group}\{#AppName}";   Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent
```

## Anexo 3 — Paquetes `.deb` (probados con un ejecutable ficticio)

`packaging/build-deb.sh`
```bash
#!/usr/bin/env bash
# build-deb.sh — arma maxpotion_<ver>_amd64.deb y maxpotion-lang_<ver>_all.deb
# Uso: packaging/build-deb.sh <dir-publish-linux-x64> [version]
#   <dir-publish-linux-x64> debe contener el ejecutable "maxpotion" (salida de dotnet publish, ver sección de build)
set -euo pipefail
PUB="${1:?directorio de publish (con el ejecutable maxpotion)}"; VER="${2:-1.0.0}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; OUT="$ROOT/artifacts"; B="$ROOT/artifacts/deb-staging"
[ -x "$PUB/maxpotion" ] || { echo "No existe $PUB/maxpotion (¿AssemblyName=maxpotion?)"; exit 1; }
for f in pokemon-database/database/pokemon.db LICENSE packaging/debian/maxpotion.desktop src/Exxeguttor.UI/Assets/maxpotion.png; do
  [ -f "$ROOT/$f" ] || { echo "Falta $f"; exit 1; }; done
rm -rf "$B"; mkdir -p "$OUT"

# ---- paquete principal ----
P="$B/maxpotion"
install -d "$P/DEBIAN" "$P/usr/lib/maxpotion" "$P/usr/bin" "$P/usr/share/applications" \
           "$P/usr/share/icons/hicolor/256x256/apps" "$P/usr/share/maxpotion" "$P/usr/share/doc/maxpotion"
install -m 755 "$PUB/maxpotion"                         "$P/usr/lib/maxpotion/maxpotion"
ln -s ../lib/maxpotion/maxpotion                        "$P/usr/bin/maxpotion"
install -m 644 "$ROOT/packaging/debian/maxpotion.desktop" "$P/usr/share/applications/maxpotion.desktop"
install -m 644 "$ROOT/src/Exxeguttor.UI/Assets/maxpotion.png" "$P/usr/share/icons/hicolor/256x256/apps/maxpotion.png"
install -m 644 "$ROOT/pokemon-database/database/pokemon.db"  "$P/usr/share/maxpotion/pokemon.db"
install -m 644 "$ROOT/LICENSE"                          "$P/usr/share/doc/maxpotion/copyright"
SIZE=$(du -sk "$P" | cut -f1)
sed -e "s/@VERSION@/$VER/" -e "s/@SIZE@/$SIZE/" "$ROOT/packaging/debian/maxpotion.control" > "$P/DEBIAN/control"
dpkg-deb --root-owner-group --build "$P" "$OUT/maxpotion_${VER}_amd64.deb"

# ---- paquete de idiomas (arquitectura all) ----
L="$B/maxpotion-lang"
install -d "$L/DEBIAN" "$L/usr/share/maxpotion/lang"
install -m 644 "$ROOT"/lang/*.json "$L/usr/share/maxpotion/lang/"
SIZE=$(du -sk "$L" | cut -f1)
sed -e "s/@VERSION@/$VER/" -e "s/@SIZE@/$SIZE/" "$ROOT/packaging/debian/maxpotion-lang.control" > "$L/DEBIAN/control"
dpkg-deb --root-owner-group --build "$L" "$OUT/maxpotion-lang_${VER}_all.deb"
echo "Listo: $OUT"
```

`packaging/debian/maxpotion.control`
```
Package: maxpotion
Version: @VERSION@
Architecture: amd64
Maintainer: MaxPotion contributors <junkoemc@proton.me>
Installed-Size: @SIZE@
Depends: libx11-6, libice6, libsm6, libfontconfig1, libgcc-s1, libstdc++6
Recommends: maxpotion-lang
Section: games
Priority: optional
Description: Pokémon save file editor for Linux
 MaxPotion is a native Linux editor for Pokémon save files, built on
 top of PKHeX.Core. Supports all mainline Pokémon games.
 .
 Features:
  - Open, edit and save Pokémon save files
  - Edit Pokémon stats, moves, items and more
  - Legality checking via PKHeX.Core
  - Native Linux UI via Avalonia (no Wine required)
 .
 Includes Spanish and English interfaces.
 Install maxpotion-lang for 10 additional languages.
```

`packaging/debian/maxpotion-lang.control`
```
Package: maxpotion-lang
Version: @VERSION@
Architecture: all
Maintainer: MaxPotion contributors <junkoemc@proton.me>
Installed-Size: @SIZE@
Depends: maxpotion (= @VERSION@)
Section: games
Priority: optional
Description: Language packs for MaxPotion
 Additional interface languages for MaxPotion.
 .
 Included languages: ja, pt-BR, ru, de, ko, zh-CN, fr, id, hi, ar (RTL).
 .
 To add more languages, drop a BCP-47 named .json file into
 /usr/share/maxpotion/lang/.
```

## Anexo 4 — `scripts/make-icons.py` (probado)

```python
# scripts/make-icons.py — genera maxpotion.png (256) y maxpotion.ico (multi-tamaño) desde UNA imagen fuente.
# Uso: python3 scripts/make-icons.py <fuente.png|ico> [dir-salida=src/Exxeguttor.UI/Assets]
# Requiere Pillow. La fuente ideal es un PNG cuadrado >= 512x512 con fondo transparente.
import sys, os
from PIL import Image
src = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else "src/Exxeguttor.UI/Assets"
im = Image.open(src).convert("RGBA")
w, h = im.size
if w != h:                       # centrar en lienzo cuadrado transparente
    s = max(w, h); c = Image.new("RGBA", (s, s), (0, 0, 0, 0)); c.paste(im, ((s-w)//2, (s-h)//2)); im = c
base = im.resize((256, 256), Image.LANCZOS)
base.save(os.path.join(out, "maxpotion.png"))
base.save(os.path.join(out, "maxpotion.ico"),
          sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
print("OK:", os.path.join(out, "maxpotion.png"), os.path.join(out, "maxpotion.ico"))
```

## Anexo 5 — `scripts/gen-placeholder-icon.py` (probado; genera el icono provisional)

```python
# scripts/gen-placeholder-icon.py — icono PROVISIONAL de MaxPotion (una poción), dibujado por código y reproducible.
# Uso: python3 scripts/gen-placeholder-icon.py [dir-salida=src/Exxeguttor.UI/Assets]
# Genera maxpotion.png (256x256) y maxpotion.ico (16-256 px). Requiere Pillow. Reemplazable luego con scripts/make-icons.py <arte-final>.
import sys, os
from PIL import Image, ImageDraw, ImageFilter

OUT = sys.argv[1] if len(sys.argv) > 1 else "src/Exxeguttor.UI/Assets"
S = 1024                                   # se dibuja grande y se reduce (suaviza bordes)
INK = (43, 43, 51, 255)                    # contorno
CORAL = (217, 88, 78, 255)                 # #D9584E, color de acento de la app

img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# --- corcho ---
d.rounded_rectangle((418, 70, 606, 178), 28, fill=(176, 120, 72, 255), outline=INK, width=26)
# --- borde del cuello y cuello ---
d.rounded_rectangle((372, 150, 652, 212), 26, fill=(235, 245, 250, 255), outline=INK, width=26)
d.rectangle((420, 200, 604, 380), fill=(235, 245, 250, 255))
d.line((420, 200, 420, 380), fill=INK, width=26); d.line((604, 200, 604, 380), fill=INK, width=26)
# --- cuerpo (vidrio) ---
body = (170, 330, 854, 970)
d.ellipse(body, fill=(235, 245, 250, 255), outline=INK, width=30)

# --- líquido: degradado coral -> rosa, recortado al interior del cuerpo ---
liq = Image.new("RGBA", (S, S), (0, 0, 0, 0))
ld = ImageDraw.Draw(liq)
top, bot = 560, 960
for y in range(top, bot):
    t = (y - top) / (bot - top)
    ld.line((0, y, S, y), fill=(int(255 - 38 * t), int(120 - 32 * t), int(130 - 52 * t), 255))
mask = Image.new("L", (S, S), 0)
ImageDraw.Draw(mask).ellipse((body[0] + 24, body[1] + 24, body[2] - 24, body[3] - 24), fill=255)
liq.putalpha(Image.composite(liq.getchannel("A"), Image.new("L", (S, S), 0), mask))
img.alpha_composite(liq)
d = ImageDraw.Draw(img)
d.line((205, 560, 819, 560), fill=(255, 190, 190, 255), width=10)       # superficie

# --- cruz blanca (curación) ---
cx, cy, a, w = 512, 740, 105, 52
d.rounded_rectangle((cx - w // 2, cy - a, cx + w // 2, cy + a), 14, fill=(255, 255, 255, 255))
d.rounded_rectangle((cx - a, cy - w // 2, cx + a, cy + w // 2), 14, fill=(255, 255, 255, 255))
# --- brillos y burbujas ---
d.arc((230, 400, 640, 900), 190, 245, fill=(255, 255, 255, 235), width=34)
for (bx, by, br) in [(660, 640, 22), (610, 600, 13), (700, 690, 12)]:
    d.ellipse((bx - br, by - br, bx + br, by + br), outline=(255, 255, 255, 220), width=7)

# --- estrella "MAX" sobre el cuello (acento) ---
import math
pts = []
for i in range(10):
    r = 46 if i % 2 == 0 else 20
    ang = -math.pi / 2 + i * math.pi / 5
    pts.append((512 + r * math.cos(ang), 285 + r * math.sin(ang)))
d.polygon(pts, fill=CORAL, outline=INK)

base = img.resize((256, 256), Image.LANCZOS)
base.save(os.path.join(OUT, "maxpotion.png"))
base.save(os.path.join(OUT, "maxpotion.ico"),
          sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
img.resize((512, 512), Image.LANCZOS).save("/tmp/maxpotion_preview512.png")
print("OK:", os.path.join(OUT, "maxpotion.png"), os.path.join(OUT, "maxpotion.ico"))
```
