# Revisión de los datos de investigación (otra IA)

Entradas: 23 lotes JSON (879 objetos) + CSV de segunda pasada (264 objetos que salieron `not_found`).

## Hallazgos
- Todos los ids existen en la lista de faltantes; sin duplicados entre lotes. Un solo nombre difería por tipografía
  (`Miraidon’s Poke Ball` vs `Poké Ball`): el validador ahora compara sin tildes ni signos.
- Pasada 1: 615 con texto, 264 `not_found`. Pasada 2 (exactamente esos 264): 199 encontrados, 65 siguen sin texto.
- **Solo inglés**: ningún texto en otros idiomas (la app los mostrará en inglés como respaldo).
- **Todo es `wiki_summary` / `medium`**, de Serebii (≈650), Bulbapedia (≈150) y GameGuides (9). Ninguno confirmado
  con captura del juego; las propias notas lo dicen.
- Revisión automática: sin restos de marcado/URL/HTML, sin espacios raros, todos terminan en puntuación, largo 19–176.
  Las 45 mega piedras mencionan la especie correcta (Floettite/Zygardite con texto especial, correcto).
- Textos repetidos legítimos: materiales ("Material accidentally dropped by a Pokémon…", 222 objetos), Battle CD (60),
  poemas, fragmentos Tera, amuletos. Coherente con los juegos, pero **una mala fuente se multiplicaría ×222**: conviene
  comprobar a mano una muestra de cada texto repetido.
- `Data ROM` (90011) trae un texto distinto para Colosseum y para XD; el esquema guarda un texto por objeto, así que
  queda en la cola de revisión (decidir cuál usar).
- No pude abrir las fuentes desde aquí (sin acceso): la fidelidad al texto del juego NO está verificada por mí.

## Criterio aplicado
`--trust-wiki`: fuente Serebii/Bulbapedia + confianza medium/high ⇒ `verified=1` (804 filas). GameGuides (9 objetos
picnic: Pink Bottle/Cup/Tablecloth, Polka-Dot…, Red/Yellow Dish, Yellow Cup) ⇒ `verified=0` (no se muestran hasta aprobarlos).
Sin `--trust-wiki` todo quedaría `verified=0`.

## Resultado en la base (copia de prueba)
Objetos en mochilas (sin MT/MO/DT): 2116 → **2042 con descripción verificada, 74 sin ella**
(65 `still_not_found` + 9 sin verificar; `Data ROM` y `Safe Key` incluidos).
Los 65 sin texto: Herba Mystica, Tera Shard Rock, Picnic Set, Pokédex, Guidebook, varios Pick/Dish/Cup de picnic,
Lunar Feather, Secret Medicine, Treats, Slates, etc. (lista completa en `research_raw/second_round.csv`, estado `still_not_found`).
