#!/usr/bin/env python3
"""
download-sprites.py
Descarga sprites de Pokemon e items desde PokeAPI directamente por URL.
Compatible con Python 3.6+. No requiere git.

Uso:
    python3 scripts/download-sprites.py
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

BASE     = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites"
API      = "https://pokeapi.co/api/v2"
OUT      = Path("src/Exxeguttor.UI/Assets/sprites")

# Tipos de Pokemon
TYPES = [
    "normal","fire","water","electric","grass","ice",
    "fighting","poison","ground","flying","psychic","bug",
    "rock","ghost","dragon","dark","steel","fairy"
]

def get(url, dest):
    dest = Path(dest)
    if dest.exists():
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        urllib.request.urlretrieve(url, str(dest))
        return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise
    except Exception as e:
        print("\n  Error: %s" % e)
        return False

def fetch(url):
    try:
        with urllib.request.urlopen(url) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None

def bar(i, total, label):
    pct = int(i * 100 / total)
    b = "#" * (pct // 5) + "-" * (20 - pct // 5)
    sys.stdout.write("\r  [%s] %3d%% %s" % (b, pct, label[:25]))
    sys.stdout.flush()

def section(t):
    print("\n" + "-"*50 + "\n  " + t + "\n" + "-"*50)

# ── Pokemon (1-1025 por ID numerico) ──────────────────────────────────

# Formas alternativas puntuales que NO caen en el rango 1-1025 (PokeAPI las
# numera 10001+) pero que el proyecto sí necesita embebidas — agregar acá
# cada vez que un mockup pida una forma nueva, en vez de bajarla a mano.
# Verificado a mano que el repo de sprites SÍ las tiene en pokemon/ y
# pokemon/shiny/ (no en female/ ni shiny/female/, son formas sin género):
#   10009 — Rotom-Lavadora (Wash), usada en mockups/confirmation_dialogs
#   10011 — Rotom-Ventilador (Fan), usada en mockups/confirmation_dialogs
EXTRA_FORM_IDS = [10009, 10011]

def pokemon():
    section("Sprites de Pokemon")
    counts = {}
    variants = [
        ("normal",       "%s/pokemon/{id}.png" % BASE),
        ("shiny",        "%s/pokemon/shiny/{id}.png" % BASE),
        ("female",       "%s/pokemon/female/{id}.png" % BASE),
        ("shiny-female", "%s/pokemon/shiny/female/{id}.png" % BASE),
    ]
    for name, url_tpl in variants:
        dest_dir = OUT / "pokemon" / name
        dest_dir.mkdir(parents=True, exist_ok=True)
        count = 0
        ids = list(range(1, 1026)) + EXTRA_FORM_IDS
        total = len(ids)
        for n, i in enumerate(ids, 1):
            bar(n, total, "%s #%d" % (name, i))
            url  = url_tpl.replace("{id}", str(i))
            dest = dest_dir / ("%d.png" % i)
            if get(url, dest):
                count += 1
            time.sleep(0.03)
        print()
        print("  OK %-15s %d sprites" % (name, count))
        counts[name] = count
    return counts

# ── Items (nombres desde la API) ──────────────────────────────────────

def items():
    section("Sprites de items")
    dest_dir = OUT / "items"
    dest_dir.mkdir(parents=True, exist_ok=True)

    print("  Obteniendo lista de items...")
    data = fetch("%s/item?limit=2000" % API)
    if not data:
        print("  ERROR: no se pudo obtener la lista de items")
        return 0

    names = [x["name"] for x in data.get("results", [])]
    print("  %d items encontrados" % len(names))

    count = 0
    for i, name in enumerate(names):
        bar(i+1, len(names), name)
        url  = "%s/items/%s.png" % (BASE, name)
        dest = dest_dir / ("%s.png" % name)
        if get(url, dest):
            count += 1
        time.sleep(0.03)

    print()
    print("  OK %-15s %d sprites" % ("items", count))
    return count

# ── Tipos ─────────────────────────────────────────────────────────────

def types():
    section("Badges de tipos")
    dest_dir = OUT / "types"
    dest_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for i, name in enumerate(TYPES):
        bar(i+1, len(TYPES), name)
        # Intentar Gen 8 primero, luego Gen 6
        url8 = "%s/types/generation-viii/sword-shield/%s.png" % (BASE, name)
        url6 = "%s/types/generation-vi/x-y/%s.png" % (BASE, name)
        dest = dest_dir / ("%s.png" % name)
        if get(url8, dest) or get(url6, dest):
            count += 1
        time.sleep(0.03)

    print()
    print("  OK %-15s %d sprites" % ("types", count))
    return count

# ── Indice ────────────────────────────────────────────────────────────

def index(pokemon_counts, items_count, types_count):
    ids = sorted([
        int(p.stem)
        for p in (OUT / "pokemon" / "normal").glob("*.png")
        if p.stem.isdigit()
    ])
    data = {
        "version": 2,
        "source":  "https://github.com/PokeAPI/sprites",
        "license": "Sprites (c) Nintendo/Creatures Inc./GAME FREAK Inc.",
        "pokemon": {
            "count_normal":       pokemon_counts.get("normal", 0),
            "count_shiny":        pokemon_counts.get("shiny", 0),
            "count_female":       pokemon_counts.get("female", 0),
            "count_shiny_female": pokemon_counts.get("shiny-female", 0),
            "ids": ids,
        },
        "items": {"count": items_count},
        "types": {"count": types_count},
    }
    with open(str(OUT / "index.json"), "w") as f:
        json.dump(data, f, indent=2)

# ── Main ──────────────────────────────────────────────────────────────

def main():
    print("=" * 50)
    print("  Exxeguttor - descarga de sprites")
    print("=" * 50)

    pc = pokemon()
    ic = items()
    tc = types()
    index(pc, ic, tc)

    section("Resumen")
    total = sum(pc.values()) + ic + tc
    print("  Pokemon normales  : %d" % pc.get("normal", 0))
    print("  Pokemon shiny     : %d" % pc.get("shiny", 0))
    print("  Pokemon femeninos : %d" % pc.get("female", 0))
    print("  Pokemon shiny-fem : %d" % pc.get("shiny-female", 0))
    print("  Items             : %d" % ic)
    print("  Tipos             : %d" % tc)
    print("  " + "-"*28)
    print("  Total             : %d archivos" % total)
    print()
    print("  Listo. Ejecuta 'dotnet build'")

if __name__ == "__main__":
    main()
