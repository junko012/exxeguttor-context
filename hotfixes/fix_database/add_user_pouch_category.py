"""
add_user_pouch_category.py
----------------------------
Agrega UserPouchCategory a cada fila de item_game_codes.json.

Regla:
  - Gen4-9: UserPouchCategory = PouchCategory (ya viene fino y fiel al motor real
    del juego -- Items/KeyItems/TMHMs/Medicine/Berries/Balls/BattleItems/MailItems/
    ZCrystals/Candy/Treasure/Ingredients/MegaStones -- no hace falta reclasificar).
  - Gen1-3 + Colosseum/XD:
      - Si PouchCategory ya es algo distinto de 'Items' (Balls/KeyItems/TMHMs/Berries,
        que sí existen como pouch separado en esas generaciones) -> se copia tal cual.
      - Si PouchCategory == 'Items' (el cajón común donde el motor real de Gen1-3
        mete de todo) -> se sub-clasifica usando Items.Category (veekun), con la
        tabla CATEGORY_TO_POUCH de abajo. Si no hay Category útil o cae en una
        categoría marcada None (items obsoletos/no jugables), UserPouchCategory
        queda NULL: no se muestra en ninguna pestaña de mochila, se deja en un
        catch-all "Items" en la UI.

Este mapeo es una decisión de PRODUCTO (cómo agrupar visualmente en Exxeguttor),
no un dato oficial de PKHeX -- a diferencia de PouchCategory, que sí lo es.
Revisar/ajustar CATEGORY_TO_POUCH y MANUAL_OVERRIDES libremente.
"""
import json
from pathlib import Path

HERE = Path(__file__).parent

GEN1_3_AND_SPINOFFS = {
    'redgreen', 'yellow', 'goldsilver', 'crystal', 'rubysapphire', 'emerald',
    'fireredleafgreen', 'colosseum', 'xd',
}

CATEGORY_TO_POUCH = {
    # Balls
    'standard-balls': 'Balls', 'special-balls': 'Balls', 'apricorn-balls': 'Balls',
    # TMs/HMs
    'all-machines': 'TMHMs',
    # Medicina (agrupa curación + vitaminas, igual que el motor real desde Gen8)
    'medicine': 'Medicine', 'healing': 'Medicine', 'revival': 'Medicine',
    'status-cures': 'Medicine', 'pp-recovery': 'Medicine', 'picky-healing': 'Medicine',
    'vitamins': 'Medicine', 'stat-boosts': 'Medicine',
    'effort-training': 'Medicine', 'effort-drop': 'Medicine',
    # Bayas
    'in-a-pinch': 'Berries', 'baking-only': 'Berries',
    # Correo
    'all-mail': 'MailItems',
    # Objetos equipables / generales / vendibles (quedan en la mochila general)
    'held-items': 'Items', 'bad-held-items': 'Items', 'type-enhancement': 'Items',
    'type-protection': 'Items', 'choice': 'Items', 'scarves': 'Items', 'jewels': 'Items',
    'plates': 'Items', 'species-specific': 'Items', 'mega-stones': 'Items',
    'miracle-shooter': 'Items', 'memories': 'Items', 'evolution': 'Items', 'flutes': 'Items',
    'nature-mints': 'Items', 'catching-bonus': 'Items', 'loot': 'Items',
    # Objetos clave / progreso de trama / coleccionables de historia
    'plot-advancement': 'KeyItems', 'spelunking': 'KeyItems', 'dex-completion': 'KeyItems',
    'event-items': 'KeyItems', 'apricorn-box': 'KeyItems', 'data-cards': 'KeyItems',
    'collectibles': 'KeyItems', 'gameplay': 'KeyItems', 'training': 'KeyItems',
    'mulch': 'KeyItems', 'other': 'KeyItems',
    # Deliberadamente sin pouch de UI: obsoletos / no jugables / internos
    'unused': None,               # ej. Slowpoke Tail y Bike marcados obsoletos por veekun
    'dynamax-crystals': None,     # IDs internos de cristal de Guarida Max Raid (SWSH), no un objeto de mochila real
    'colosseum_xd_exclusive': None,  # ya vienen con su propio PouchCategory (KeyItems) casi siempre
}

# Overrides puntuales por nombre, para los pocos ítems sin Category útil de veekun
# o que conviene forzar a mano.
MANUAL_OVERRIDES = {
    'Pokédex': 'KeyItems',
}


def compute_user_pouch(item, pouch_category, game_code):
    if game_code not in GEN1_3_AND_SPINOFFS:
        return pouch_category  # Gen4-9: ya es fino y fiel, se copia tal cual
    if pouch_category != 'Items':
        return pouch_category  # Balls/KeyItems/TMHMs/Berries ya vienen separados
    if item['Name'] in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[item['Name']]
    return CATEGORY_TO_POUCH.get(item['Category'])  # puede devolver None a propósito


def main():
    items = {it['ItemId']: it for it in json.loads((HERE / 'items.json').read_text(encoding='utf-8'))}
    codes = json.loads((HERE / 'item_game_codes.json').read_text(encoding='utf-8'))

    unknown_categories = set()
    for r in codes:
        it = items[r['ItemId']]
        if r['GameCode'] in GEN1_3_AND_SPINOFFS and r['PouchCategory'] == 'Items' \
                and it['Name'] not in MANUAL_OVERRIDES and it['Category'] not in CATEGORY_TO_POUCH \
                and it['Category'] is not None:
            unknown_categories.add(it['Category'])
        r['UserPouchCategory'] = compute_user_pouch(it, r['PouchCategory'], r['GameCode'])

    if unknown_categories:
        print('⚠️  Categorías de veekun sin mapeo definido (agregar a CATEGORY_TO_POUCH):', unknown_categories)

    (HERE / 'item_game_codes.json').write_text(
        json.dumps(codes, ensure_ascii=False, indent=1), encoding='utf-8'
    )

    from collections import Counter
    dist = Counter(r['UserPouchCategory'] for r in codes if r['GameCode'] in GEN1_3_AND_SPINOFFS)
    print('Distribución de UserPouchCategory en Gen1-3 + Colosseum/XD:')
    for k, v in dist.most_common():
        print(' ', k, v)
    print('\nitem_game_codes.json actualizado con UserPouchCategory en las', len(codes), 'filas.')


if __name__ == '__main__':
    main()
