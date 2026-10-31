#!/usr/bin/env python3
"""Create a 40-entry pilot review worksheet from ALREADY PUBLIC curated entries.

Selection is deterministic and stratified across initial letters and categories.
Original translations are shown for checking, never promoted as verified.
No new linguistic claims, made-up examples, or personal data are introduced.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BATCH="PILOT-40-2026-10-31"
HEADERS=[
  "batch","entry_id","kata_mandailing","padanan_indonesia_editorial",
  "padanan_melayu_editorial","padanan_inggris_editorial","kategori",
  "sumber_id","lema_sumber","halaman_cetak","halaman_pdf","label_bahasa_sumber",
  "status_contoh","prioritas_review","status_keputusan","alasan_keputusan",
  "penelaah","wilayah_penutur_yang_dikonsultasi","bukti_tambahan","tanggal_telaah"
]
PRIORITY={"Mdl":0,"shared-pronunciation":1,"unmarked":2,"Tapsel":3}

def select(words,limit=40):
    groups=defaultdict(list)
    for w in words:
        name=w["md"].strip()
        if w.get("status")!="source_attested" or not name or not w.get("sourceRef"):
            continue
        letter=name[0].upper()
        if not letter.isalpha():
            continue
        groups[letter].append(w)
    if sum(map(len,groups.values()))<limit:
        raise ValueError("Not enough eligible curated entries for review.")
    remaining={key:list(values) for key,values in sorted(groups.items())}
    cats=Counter()
    selected=[]
    while len(selected)<limit:
        progressed=False
        for letter,items in remaining.items():
            if not items or len(selected)>=limit: continue
            items.sort(key=lambda w:(
               cats[w["category"]],
               PRIORITY.get(w["sourceRef"].get("languageLabel"),4),
               0 if w.get("exampleStatus")=="source_quoted" else 1,
               w["md"].casefold(),w["id"]
            ))
            word=items.pop(0)
            selected.append(word)
            cats[word["category"]]+=1
            progressed=True
        if not progressed: raise ValueError("Could not select enough distinct entries.")
    return selected

def as_rows(words):
    rows=[]
    for w in words:
        ref=w["sourceRef"]
        lang=ref.get("languageLabel","")
        priority={
         "Mdl":"tinggi: label Mdl (tetap perlu pemeriksaan penutur)",
         "shared-pronunciation":"tinggi: lafal gabungan perlu penelaahan",
         "unmarked":"cek cakupan: kamus gabungan tanpa label per kata",
         "Tapsel":"cek cakupan: konteks Tapsel"
        }.get(lang,"cek label dan sumber")
        fields=[
         BATCH,w["id"],w["md"],w["idn"],w["my"],w["en"],w["category"],
         ref.get("id",""),ref.get("lemma",""),str(ref.get("printedPage","")),str(ref.get("pdfPage","")),
         lang,w.get("exampleStatus",""),priority,"BELUM DITELAAH","","","","",""
        ]
        if any("\t" in str(v) or "\n" in str(v) or "\r" in str(v) for v in fields):
            raise ValueError("Unsafe tab or line break in source record.")
        rows.append(fields)
    return rows

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",required=True,type=Path,help="Write to a review-only path, not the public dictionary.")
    args=p.parse_args()
    words=json.loads((ROOT/"src/words.json").read_text(encoding="utf-8"))
    sample=select(words)
    assert len(sample)==40 and len({w["id"] for w in sample})==40
    destination=args.out.resolve()
    if destination in {(ROOT/"src/words.json").resolve(),(ROOT/"src/inventory.json").resolve()}:
        p.error("Refusing to overwrite official vocabulary.")
    destination.parent.mkdir(parents=True,exist_ok=True)
    with destination.open("w",encoding="utf-8-sig",newline="") as handle:
        writer=csv.writer(handle,delimiter="\t",lineterminator="\n")
        writer.writerow(HEADERS)
        writer.writerows(as_rows(sample))
    print(json.dumps({"batch":BATCH,"entries":len(sample),
        "letters":len({w["md"][0].upper() for w in sample}),
        "category_counts":dict(Counter(w["category"] for w in sample)),
        "status":"BELUM DITELAAH","published":False},ensure_ascii=False))

if __name__=="__main__":
    main()
