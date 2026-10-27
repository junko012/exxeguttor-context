#!/usr/bin/env python3
"""Convierte el CSV de la segunda pasada de investigación al JSON de validate_research.py.
Uso: python3 import_second_round.py second_round.csv salida.json
Solo pasan las filas con second_round_status == found_second_round (el resto sigue sin texto)."""
import csv, json, sys

rows = []
with open(sys.argv[1], encoding="utf-8-sig", newline="") as fh:
    for r in csv.DictReader(fh):
        if r["second_round_status"] != "found_second_round":
            continue
        rows.append({
            "db_item_id": int(r["db_item_id"]), "name_en": r["name_en"],
            "description": {"en": r["second_round_description_en"], "es": None, "fr": None, "de": None, "it": None,
                            "ja": None, "ko": None, "zh-Hans": None, "zh-Hant": None},
            "text_kind": r["second_round_text_kind"], "confidence": r["second_round_confidence"],
            "variants": [], "sources": [r["second_round_source_url"]], "notes": r["second_round_notes"],
        })
json.dump(rows, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(rows), "entradas")
