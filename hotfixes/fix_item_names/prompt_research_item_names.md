# Prompt para investigar nombres oficiales de objetos de Pokémon Legends: Z-A (para otra IA)

Copia todo lo de abajo en la otra IA y adjunta `za_item_names_to_research.csv`.

---

## Contexto
Mantengo un editor de partidas guardadas de Pokémon. Para **Pokémon Legends: Z-A** (incluido el DLC *Mega Dimension*) mi
librería de datos no trae el nombre de 65 objetos nuevos, en ningún idioma. El CSV adjunto trae un objeto por fila:

- `db_item_id`: id interno (devuélvelo tal cual).
- `name_en_db`: nombre en inglés que tengo en mi base. **Puede tener errores tipográficos o no coincidir con el nombre oficial**: confírmalo.
- `group`: `mega_stone`, `butter` u `other`.

## Tarea
Para cada objeto, busca su **nombre oficial dentro del juego** en estos 9 idiomas:

| clave | idioma |
|---|---|
| `en` | inglés |
| `es` | español de España (el de las versiones europeas de Nintendo) |
| `fr` | francés |
| `de` | alemán |
| `it` | italiano |
| `ja` | japonés (con kanji/katakana tal como aparece en el juego) |
| `ko` | coreano |
| `zh-Hans` | chino simplificado |
| `zh-Hant` | chino tradicional |

## Reglas (importantes)
1. **No inventes ni deduzcas nombres.** No los construyas a partir del nombre de la especie ni por analogía con otras piedras
   (p. ej. "[especie] + ナイト"). Si no encuentras el nombre oficial en un idioma, pon `null`. Es mejor `null` que un nombre plausible pero falso.
2. **No traduzcas tú.** Solo transcribe nombres que aparezcan en una fuente.
3. Cada nombre debe tener fuente: una **URL concreta** (no la portada de un sitio). Indica en `text_kind` si es
   `"in_game"` (visto en el juego, capturas o volcado de texto) o `"wiki"` (lo trae una wiki/base de datos sin captura).
   Fuentes útiles: Bulbapedia (tablas de objetos por idioma, "In other languages"), Serebii, Pokémon Wiki en cada idioma
   (por ejemplo Wiki Pokémon en español/francés/alemán/italiano, Bulbagarden JP, 神奇宝贝百科 / 神奇寶貝百科, 포켓몬 위키), la web oficial de Pokémon de cada región.
4. Copia los caracteres **exactos**: tildes, mayúsculas, signos (`’` vs `'`), espacios, y los números de ancho completo en japonés/chino si el juego los usa.
5. Si el nombre inglés de mi CSV es incorrecto, pon el correcto en `en` y explica la diferencia en `notes`.
6. Si dos fuentes se contradicen, anótalo en `notes` y baja `confidence`.
7. Si un objeto tiene nombres distintos en el juego base y en el DLC, devuelve las dos opciones en `notes` y usa el del juego base en el campo principal.

## Formato de salida
Un único bloque JSON, una lista, sin texto fuera del bloque. Procesa en lotes de máximo 20 filas y numéralos.

```json
[
  {
    "db_item_id": 1234,
    "name_en_db": "Example Name",
    "names": {
      "en": "Official English", "es": null, "fr": null, "de": null, "it": null,
      "ja": null, "ko": null, "zh-Hans": null, "zh-Hant": null
    },
    "text_kind": "in_game",
    "confidence": "high",
    "sources": {
      "en": "https://...", "es": null, "fr": null, "de": null, "it": null,
      "ja": null, "ko": null, "zh-Hans": null, "zh-Hant": null
    },
    "notes": ""
  }
]
```

`confidence`: `high` (dos fuentes que coinciden o captura del juego), `medium` (una fuente fiable), `low` (dudoso o contradictorio),
`not_found` (no se encontró nada; todos los `names` en `null`).

## Orden de trabajo sugerido
1. `mega_stone` (suelen estar en una tabla de Bulbapedia con todos los idiomas).
2. `butter`.
3. `other`.

Al terminar cada lote, dime cuántos quedaron `not_found` y cuántos idiomas quedaron en `null`.
