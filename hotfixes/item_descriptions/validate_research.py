#!/usr/bin/env python3
"""Fase 2: valida el JSON que devuelven otras IAs (formato de prompt_research_items.md).

Nada entra sin pasar por aquí. Salidas en --out:
  items_text_research.csv  filas ACEPTADAS: db_item_id,lang,text,source,source_url,verified
  review_queue.csv         filas que necesitan revisión humana, con el motivo
  validation_report.md     resumen

verified=1 solo si text_kind=in_game y confidence=high; el resto entra con verified=0 (la app no lo
mostraría hasta que se apruebe). Entradas con errores graves van a review_queue, no a la base.

Uso: python3 validate_research.py lote1.json lote2.json --missing missing_item_descriptions.csv --out out
"""
import argparse, csv, json, os, re, collections

LANGS = ["en", "es", "fr", "de", "it", "ja", "ko", "zh-Hans", "zh-Hant"]
KINDS = {"in_game", "wiki_summary"}
CONF = {"high", "medium", "low", "not_found"}
MAXLEN = 220
HOME_ONLY = re.compile(r"^https?://[^/]+/?$")  # URL de portada: no sirve como fuente
KANA = re.compile(r"[぀-ヿ]")
HANGUL = re.compile(r"[가-힣]")
HAN = re.compile(r"[一-鿿]")


def lang_ok(lang, t):
    if lang in ("es", "fr", "de", "it", "en"):
        return not (KANA.search(t) or HANGUL.search(t) or HAN.search(t))
    if lang == "ja":
        return bool(KANA.search(t) or HAN.search(t))
    if lang == "ko":
        return bool(HANGUL.search(t))
    return bool(HAN.search(t)) and not KANA.search(t) and not HANGUL.search(t)  # zh-Hans / zh-Hant


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--missing", default="missing_item_descriptions.csv")
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    with open(a.missing, encoding="utf-8", newline="") as fh:
        expected = {int(r["db_item_id"]): r["name_en"] for r in csv.DictReader(fh)}

    accepted, review, seen = [], [], {}
    stats = collections.Counter()

    def reject(item_id, name, lang, reason, text=""):
        review.append((item_id, name, lang, reason, text))
        stats["review"] += 1

    for path in a.files:
        data = json.load(open(path, encoding="utf-8"))
        if not isinstance(data, list):
            raise SystemExit(f"{path}: se esperaba una lista JSON")
        for e in data:
            iid, name = e.get("db_item_id"), e.get("name_en", "")
            if iid not in expected:
                reject(iid, name, "", "db_item_id desconocido"); continue
            if expected[iid] != name:
                reject(iid, name, "", f"el nombre no coincide con la lista (esperado «{expected[iid]}»)"); continue
            if iid in seen:
                reject(iid, name, "", f"duplicado (ya venía en {seen[iid]})"); continue
            seen[iid] = os.path.basename(path)
            kind, conf = e.get("text_kind"), e.get("confidence")
            if kind not in KINDS or conf not in CONF:
                reject(iid, name, "", f"text_kind/confidence inválidos: {kind!r}/{conf!r}"); continue
            if conf == "not_found":
                stats["not_found"] += 1; continue
            if e.get("variants"):
                reject(iid, name, "", "trae variantes por juego: decidir a mano"); continue
            urls = [u for u in e.get("sources", []) if isinstance(u, str) and u.startswith("http") and not HOME_ONLY.match(u)]
            desc = e.get("description") or {}
            if not urls:
                reject(iid, name, "", "sin URL de fuente válida (o solo portada)"); continue
            got_any = False
            for lang, t in desc.items():
                if t is None:
                    continue
                if lang not in LANGS:
                    reject(iid, name, lang, "idioma no soportado", t); continue
                t2 = re.sub(r"\s+", "" if lang in ("ja", "zh-Hans", "zh-Hant") else " ", t).strip()
                if not t2:
                    continue
                if len(t2) > MAXLEN:
                    reject(iid, name, lang, f"texto demasiado largo ({len(t2)})", t2); continue
                if t2[0] in "\"'“‘«" and t2[-1] in "\"'”’»":
                    reject(iid, name, lang, "comillas envolventes", t2); continue
                if not lang_ok(lang, t2):
                    reject(iid, name, lang, "el texto no parece estar en ese idioma", t2); continue
                got_any = True
                ok = kind == "in_game" and conf == "high"
                if not ok:
                    review.append((iid, name, lang, f"entra como no verificado ({kind}/{conf})", t2))
                accepted.append((iid, lang, t2, "research", urls[0], 1 if ok else 0))
                stats["accepted"] += 1
            if not got_any:
                reject(iid, name, "", "sin ningún texto utilizable")

    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "items_text_research.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh); w.writerow(["db_item_id", "lang", "text", "source", "source_url", "verified"]); w.writerows(sorted(accepted))
    with open(os.path.join(a.out, "review_queue.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh); w.writerow(["db_item_id", "name_en", "lang", "reason", "text"]); w.writerows(review)
    pending = len(expected) - len(seen)
    rep = (f"# Validación de datos de investigación\n\n- Filas aceptadas: {stats['accepted']} "
           f"(verified=1: {sum(1 for r in accepted if r[5])})\n- Para revisión: {stats['review']}\n"
           f"- not_found: {stats['not_found']}\n- Objetos de la lista aún sin respuesta: {pending}\n")
    open(os.path.join(a.out, "validation_report.md"), "w", encoding="utf-8").write(rep)
    print(rep)


if __name__ == "__main__":
    main()
