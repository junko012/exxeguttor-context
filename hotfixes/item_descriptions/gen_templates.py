#!/usr/bin/env python3
"""Genera descripciones de PLANTILLA para las mega piedras nuevas de Legends: Z-A.

OJO: no es texto oficial del juego (source = 'template'). Se usa solo hasta que haya texto verificado.
Los nombres de especie salen de PKHeX (text_Species_<idioma>.txt), así que cada idioma usa el nombre correcto.

Uso: python3 gen_templates.py --pkhex-text <PKHeX>/PKHeX.Core/Resources/text/other --out out
"""
import argparse, csv, os, re

STONES = {  # piedra -> especie (nombre inglés de PKHeX)
    "Absolite Z": "Absol", "Barbaracite": "Barbaracle", "Baxcalibrite": "Baxcalibur", "Chandelurite": "Chandelure",
    "Chesnaughtite": "Chesnaught", "Chimechite": "Chimecho", "Clefablite": "Clefable", "Crabominite": "Crabominable",
    "Darkranite": "Darkrai", "Delphoxite": "Delphox", "Dragalgite": "Dragalge", "Dragoninite": "Dragonite",
    "Drampanite": "Drampa", "Eelektrossite": "Eelektross", "Emboarite": "Emboar", "Excadrite": "Excadrill",
    "Falinksite": "Falinks", "Feraligite": "Feraligatr", "Floettite": "Floette", "Froslassite": "Froslass",
    "Garchompite Z": "Garchomp", "Glimmoranite": "Glimmora", "Golisopite": "Golisopod", "Golurkite": "Golurk",
    "Greninjite": "Greninja", "Hawluchanite": "Hawlucha", "Heatranite": "Heatran", "Lucarionite Z": "Lucario",
    "Magearnite": "Magearna", "Malamarite": "Malamar", "Meganiumite": "Meganium", "Meowsticite": "Meowstic",
    "Pyroarite": "Pyroar", "Raichunite X": "Raichu", "Raichunite Y": "Raichu", "Scolipite": "Scolipede",
    "Scovillainite": "Scovillain", "Scraftinite": "Scrafty", "Skarmorite": "Skarmory", "Staraptite": "Staraptor",
    "Starminite": "Starmie", "Tatsugirinite": "Tatsugiri", "Victreebelite": "Victreebel", "Zeraorite": "Zeraora",
    "Zygardite": "Zygarde",
}
TEMPLATE = {  # {0} = nombre de la especie
    "en": "Allows {0} to Mega Evolve during battle.",
    "es": "Permite que {0} Megaevolucione durante el combate.",
    "fr": "Permet à {0} de Méga-Évoluer pendant le combat.",
    "de": "Ermöglicht {0} die Mega-Entwicklung im Kampf.",
    "it": "Permette a {0} di Megaevolversi in battaglia.",
    "ja": "{0}にもたせると、バトル中にメガシンカできるようになる。",
    "ko": "{0}에게 지니게 하면 배틀 중에 메가진화할 수 있다.",
    "zh-Hans": "让{0}携带后，可在战斗中进行超级进化。",
    "zh-Hant": "讓{0}攜帶後，可在對戰中進行超級進化。",
}


def species(root, lang):
    with open(os.path.join(root, lang, f"text_Species_{lang}.txt"), encoding="utf-8") as fh:
        return [l.rstrip("\n") for l in fh]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pkhex-text", required=True)
    ap.add_argument("--missing", default="missing_item_descriptions.csv")
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    en = species(a.pkhex_text, "en")
    idx = {n: i for i, n in enumerate(en) if n}
    names = {l: species(a.pkhex_text, l) for l in TEMPLATE}
    with open(a.missing, encoding="utf-8", newline="") as fh:
        ids = {r["name_en"]: int(r["db_item_id"]) for r in csv.DictReader(fh) if r["group"] == "mega_stone_za"}
    rows, problems = [], []
    for stone, sp in STONES.items():
        if stone not in ids:
            problems.append(f"{stone}: no está en la lista de faltantes"); continue
        if sp not in idx:
            problems.append(f"{stone}: especie «{sp}» no existe en PKHeX"); continue
        for lang, t in TEMPLATE.items():
            rows.append((ids[stone], lang, t.format(names[lang][idx[sp]]), "template", ""))
    for stone in ids:
        if stone not in STONES:
            problems.append(f"{stone}: sin especie asignada")
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "items_text_template.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh); w.writerow(["db_item_id", "lang", "text", "source", "version_group_id"]); w.writerows(rows)
    print(f"{len(rows)} filas ({len(rows)//len(TEMPLATE)} piedras). Problemas: {problems or 'ninguno'}")


if __name__ == "__main__":
    main()
