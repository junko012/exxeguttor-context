# Prompt para investigar descripciones de objetos Pokémon — ronda 3, 28 objetos restantes (para otra IA)

Copia todo lo de abajo en la otra IA y adjunta `missing_item_descriptions_round3.csv`.

---

## Contexto
Mantengo un editor de partidas guardadas de Pokémon (Max Potion). Necesito la **descripción oficial dentro del juego** de objetos que mi base de datos no tiene. El CSV adjunto trae un objeto por fila:

- `db_item_id`: id interno (devuélvelo tal cual).
- `name_en`: nombre en inglés.
- `group`: `other_legends` (Legends: Arceus y Legends: Z-A, incluye DLC Mega Dimension), `mega_stone_za`, `hyper_berry` (bayas Hyper de Z-A) o `colosseum_xd` (Pokémon Colosseum / XD: Gale of Darkness).
- `games`: juegos donde aparece el objeto en mi base.

## Nota de esta ronda
Son los 28 objetos que siguen sin descripción tras las rondas anteriores (mayormente objetos clave, ingredientes y materiales de Legends: Arceus, Escarlata/Púrpura y Legends: Z-A). `group` es siempre `other`. Fuentes que ya funcionaron para texto del juego: Dittobase (dittobase.com/<juego>/items/<objeto>), GamerGuides, Serebii, Bulbapedia. Ya está resuelto el resto de objetos de picnic; **Gold Bottle** necesita confirmar su texto en una segunda fuente.

## Tarea
Para cada fila, busca el **texto de descripción que muestra el juego** (la línea de la mochila, no la guía ni el wiki) y devuélvelo.

## Idiomas
`en` primero. Si encuentras el texto oficial en otros idiomas, inclúyelo: `es`, `fr`, `de`, `it`, `ja`, `ko`, `zh-Hans`, `zh-Hant`. Si no hay texto oficial en un idioma, pon `null`. **No traduzcas tú ni rellenes con traducciones propias.**

## Reglas (importantes)
1. **No inventes.** Si no encuentras el texto oficial de un objeto, devuelve `description: null` y `confidence: "not_found"`. Es mejor vacío que inventado.
2. Distingue el origen en `text_kind`: `"in_game"` (texto copiado del juego, tal como aparece) o `"wiki_summary"` (resumen de una wiki; no es el texto del juego).
3. Cada objeto con texto lleva **al menos una URL fuente** en `sources` (la página concreta, no la portada del sitio). Si no hay URL, no lo incluyas con texto.
4. Si el mismo nombre existe en más de un juego con texto distinto, devuelve una entrada por juego en `variants`.
5. Conserva el texto tal cual: sin añadir comillas, sin cambiar mayúsculas, sin unir ni partir frases. Normaliza solo los saltos de línea (un espacio).
6. Si dos fuentes se contradicen, anótalo en `notes` y usa `confidence: "low"`.
7. Los textos de objetos son cortos y pertenecen a Nintendo / Game Freak. Esto es para uso personal en una herramienta de edición; no los republiques.

## Formato de salida
Un único bloque JSON, una lista, sin texto fuera del bloque. Procesa en lotes de máximo 40 filas y numera los lotes.

```json
[
  {
    "db_item_id": 1234,
    "name_en": "Example Item",
    "description": {
      "en": "Text as shown in game.",
      "es": null, "fr": null, "de": null, "it": null,
      "ja": null, "ko": null, "zh-Hans": null, "zh-Hant": null
    },
    "text_kind": "in_game",
    "confidence": "high",
    "variants": [],
    "sources": ["https://..."],
    "notes": ""
  }
]
```

`confidence`: `high` (texto del juego visto en 2 fuentes o en capturas), `medium` (1 fuente fiable), `low` (dudoso o contradictorio), `not_found`.

## Orden de trabajo sugerido
1. `mega_stone_za` y `hyper_berry`: suelen tener texto en wikis con tablas (Bulbapedia, Serebii).
2. `other_legends`: por juego (Arceus y Z-A) y por categoría de mochila.
3. `colosseum_xd`: al final; si no hay fuente, `not_found`.

Al terminar cada lote dime cuántos quedaron `not_found`.
