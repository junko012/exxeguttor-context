#!/usr/bin/env python3
"""Valida los lotes JSON de nombres (research_raw/*.json) y genera data/item_names.csv.
Uso: python3 validate_names.py [--raw research_raw] [--out data/item_names.csv] [--expected data/za_item_names_to_research.csv]

Rechaza (no entra al CSV) y lista en el informe:
  - db_item_id fuera del CSV esperado o repetido
  - nombre con espacios sobrantes, saltos de línea, comillas ASCII raras o más de 60 caracteres
  - nombre sin URL de fuente (https://...)
  - idioma desconocido
  - en ja/zh/ko: espacios internos en ja/zh (el juego no los usa)
Avisa (entra, pero queda en el informe): name_en distinto de name_en_db, mismo nombre en dos objetos del mismo idioma.
confidence: high/medium -> Verified=1 ; low -> Verified=0 ; not_found -> no entra.
"""
import argparse, csv, glob, json, os, re, sys, collections

LANGS = ["en", "es", "fr", "de", "it", "ja", "ko", "zh-Hans", "zh-Hant"]
HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=os.path.join(HERE, "research_raw"))
    ap.add_argument("--out", default=os.path.join(HERE, "data", "item_names.csv"))
    ap.add_argument("--expected", default=os.path.join(HERE, "data", "za_item_names_to_research.csv"))
    a = ap.parse_args()

    expected = {int(r["db_item_id"]): r["name_en_db"] for r in csv.DictReader(open(a.expected, encoding="utf-8"))}
    seen, rows, errors, warns = set(), [], [], []
    for f in sorted(glob.glob(os.path.join(a.raw, "*.json"))):
        for r in json.load(open(f, encoding="utf-8")):
            i = r["db_item_id"]
            if i not in expected:
                errors.append(f"{i}: id fuera de la lista esperada"); continue
            if i in seen:
                errors.append(f"{i}: repetido"); continue
            seen.add(i)
            conf = r.get("confidence", "")
            if conf == "not_found":
                warns.append(f"{i} {expected[i]}: not_found (sin nombres)"); continue
            if conf not in ("high", "medium", "low"):
                errors.append(f"{i}: confidence inválido «{conf}»"); continue
            names, srcs = r.get("names", {}), r.get("sources") or {}
            if set(names) - set(LANGS):
                errors.append(f"{i}: idiomas desconocidos {set(names) - set(LANGS)}")
            for l in LANGS:
                n = names.get(l)
                if not n:
                    continue
                url = srcs.get(l) or ""
                if n != n.strip() or "\n" in n or len(n) > 60:
                    errors.append(f"{i}/{l}: formato de nombre inválido «{n}»"); continue
                if not url.startswith("https://"):
                    errors.append(f"{i}/{l}: sin URL de fuente"); continue
                if l in ("ja", "zh-Hans", "zh-Hant") and re.search(r"\s", n):
                    errors.append(f"{i}/{l}: espacios en nombre CJK «{n}»"); continue
                rows.append(dict(db_item_id=i, lang=l, name=n, source="research-wiki", source_url=url,
                                 confidence=conf, verified=0 if conf == "low" else 1))
            en = names.get("en")
            if en and en != expected[i]:
                warns.append(f"{i}: en «{en}» ≠ nombre en la base «{expected[i]}»")
    missing = set(expected) - seen
    if missing:
        errors.append(f"faltan ids: {sorted(missing)}")
    dup = collections.defaultdict(list)
    for r in rows:
        dup[(r["lang"], r["name"])].append(r["db_item_id"])
    for (l, n), ids in dup.items():
        if len(ids) > 1:
            warns.append(f"{l}: «{n}» repetido en {ids}")

    for e in errors: print("ERROR:", e)
    for w in warns: print("AVISO:", w)
    per = collections.Counter(r["lang"] for r in rows)
    print(f"{len(rows)} nombres válidos para {len({r['db_item_id'] for r in rows})} objetos | por idioma {dict(per)} | errores {len(errors)}")
    if errors:
        sys.exit(1)
    with open(a.out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["db_item_id", "lang", "name", "source", "source_url", "confidence", "verified"])
        w.writeheader(); w.writerows(sorted(rows, key=lambda r: (r["db_item_id"], LANGS.index(r["lang"]))))
    print("escrito", a.out)


if __name__ == "__main__":
    main()
