# Boceto: Selector de idioma (menú File → Idioma)

Primera pieza de UI de "preferencias" que tiene el proyecto — hoy no existe ninguna pantalla
de configuración, así que se evitó diseñar una pantalla de Settings completa solo para esto.
Un submenú dentro de File alcanza para v1; si en el futuro aparecen más preferencias, ahí sí
vale la pena promoverlo a una pantalla dedicada.

## Contexto — por qué existe esto

`LocalizationService` (`src/Exxeguttor.UI/i18n/`) ya tenía toda la infraestructura real
(fallback chain, detección de idioma del SO, soporte RTL, y hasta el mecanismo de paquetes
lang externos) pero **nada en la UI la exponía** — `Load()` nunca se llamaba después del
arranque, no había forma de cambiar de idioma sin editar el JSON a mano. Ver
`docs/i18n_project/i18n-plan.md` para el plan completo de esta sesión de trabajo (de la que
este mockup es una pieza).

## Decisiones de esta sesión de diseño

- **Ubicación**: submenú dentro de `File`, no un ícono aparte en el toolbar ni una pantalla
  de Settings nueva — la app ya tiene un menú `File` con acciones de alto nivel (Abrir,
  Guardar, Exportar), cambiar de idioma encaja ahí sin inventar un patrón de navegación
  nuevo.
- **Agrupado en tres secciones**, en este orden:
  1. **Incluidos** — `es`/`en`, los dos que vienen embebidos en el binario, siempre
     disponibles sin instalar nada.
  2. **Paquetes instalados** — cualquier `.json` que el usuario ya puso en
     `/usr/share/exxeguttor/lang/` o `./lang/` (mecanismo que ya existe en código, ver
     `LocalizationService.DetectAvailableLocales`).
  3. **Disponibles para instalar** — lista de códigos conocidos
     (`LocalizationService.KnownLangPackLocales`: ja, pt-BR, ru, de, ko, zh-CN, fr, id, hi,
     ar) que el proyecto sabe que EXISTEN como paquete pero el usuario no instaló — mostrados
     atenuados, sin checkbox activable, como referencia de qué se puede conseguir. **Pendiente
     de confirmar**: si esta lista debería en cambio quedar oculta hasta que haya una fuente
     real de descarga (hoy `KnownLangPackLocales` es solo una lista de nombres conocidos en
     código, no hay ningún lado de donde bajarlos todavía — ver plan, Fase 4).
  4. **Acción final**: "Abrir carpeta de paquetes de idioma…" — atajo para que el usuario
     sepa dónde poner el `.json` manualmente (mismo criterio que otras apps Linux con
     paquetes de idioma/plugins instalados a mano).
- **Reinicio requerido, no cambio en caliente** — decisión ya tomada en la charla previa
  (Opción A del análisis): evita el refactor grande de convertir cada string "asignado una
  vez" en cada ViewModel a una propiedad computada + notificación. Al elegir un idioma
  distinto al activo, aparece el diálogo de confirmación de reinicio (segunda escena del
  boceto) — nunca reinicia sin preguntar.
- **El diálogo de reinicio respeta las ediciones sin exportar** — si hay cambios pendientes,
  el reinicio debe pasar PRIMERO por el mismo diálogo "Cerrar sin exportar" (Rotom-Ventilador,
  ya implementado) antes de efectivamente reiniciar — no es un camino nuevo de pérdida de
  datos, reusa el resguardo que ya existe para cerrar la app o abrir otro save.
- **Sin animación temática** — a diferencia de los loaders y diálogos de confirmación de
  sesiones anteriores, esta es una pantalla de selección puntual (un menú, un diálogo de
  confirmación simple), no hay una acción de "espera" que ambientar con un personaje. No
  todo en la app necesita mascota.

## Pendiente de confirmar antes de implementar

1. **Nombres de display por idioma** — el boceto usa "Español"/"English"/"Français" (el
   nombre en SU PROPIO idioma, convención común — "autoglotónimo"). Hace falta una tabla
   código→nombre propio para al menos los idiomas embebidos + los de `KnownLangPackLocales`.
   Un paquete lang instalado que el proyecto no conoce de antemano (un código no listado en
   ninguna de las dos listas) debería mostrar su propio código como fallback (ej. "eu" si
   alguien arma un paquete de euskera no contemplado).
2. **Qué pasa si el reinicio falla o el usuario está en un AppImage** — ver plan, Fase 2,
   nota sobre `Process.Start`/relanzamiento de AppImages (usan la variable de entorno
   `APPIMAGE`, no el path del binario extraído, para relanzarse correctamente).
3. **La lista "Disponibles para instalar"** — ver nota arriba, puede que convenga sacarla de
   v1 si no hay de dónde bajarlos todavía (solo dejar "Incluidos" + "Paquetes instalados" +
   el atajo a la carpeta).

## Ver también

- `docs/i18n_project/i18n-plan.md` — plan completo de la sesión de idiomas (de la que este
  mockup es la Fase 2), con el resto de las decisiones de producto ya tomadas y el estado de
  avance.
