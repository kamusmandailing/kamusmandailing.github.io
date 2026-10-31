#!/usr/bin/env python3
"""Canonical, reproducible release snapshot for Kamus Mandailing.

The latest evidence index in research/coverage_audit.json is authoritative for
release-level statistics. research/progress.json is intentionally historical.
This check does not certify meanings, speaker approval, or copyright.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = "research/release_snapshot.json"

def read(root, relative):
    return json.loads((root / relative).read_text(encoding="utf-8"))

def make_snapshot(root=ROOT):
    audit = read(root, "research/coverage_audit.json")
    bank = read(root, "src/inventory.json")
    curated = read(root, "src/words.json")
    archive = read(root, "research/progress.json")
    stats = audit["stats"]
    current = bank["stats"]

    for name in ("uniqueForms","reviewedTranslations","pendingTranslations",
                 "referenceRecords","sourceCount"):
        if stats[name] != current[name]:
            raise ValueError(f"Stale release statistics: {name} audit={stats[name]} vs bank={current[name]}")
    if audit["version"] != bank["version"]:
        raise ValueError("Release version differs between audit and inventory.")
    if stats["uniqueForms"] != len(bank["forms"]):
        raise ValueError("Unique form count differs from bank rows.")
    if stats["reviewedTranslations"] != len(curated):
        raise ValueError("Curated entry count differs from words.json.")
    if stats["uniqueForms"] != stats["reviewedTranslations"] + stats["pendingTranslations"]:
        raise ValueError("Source forms do not partition into curated and pending.")
    if stats["referenceRecords"] != sum(len(form["references"]) for form in bank["forms"]):
        raise ValueError("Reference count differs from observed source references.")
    if len({form["id"] for form in bank["forms"]}) != len(bank["forms"]):
        raise ValueError("Duplicate form ID detected.")
    if len({word["id"] for word in curated}) != len(curated):
        raise ValueError("Duplicate curated entry ID detected.")
    if archive["inventory"]["uniqueForms"] >= stats["uniqueForms"]:
        raise ValueError("Historical progress is not older than current snapshot; review migration logic.")
    if archive["total"] != len(curated):
        raise ValueError("Historic curated count differs from current; verify before release.")
    if archive["sourceExamples"] + archive["pendingExamples"] != len(curated):
        raise ValueError("Reported example coverage disagrees with curated entries.")
    if not archive["inventory"]["referenceRecords"] < stats["referenceRecords"]:
        raise ValueError("Historical reference count is not older; review audit.")
    if not all(isinstance(form.get("references"), list) for form in bank["forms"]):
        raise ValueError("Malformed references.")

    return {
        "schemaVersion": 1,
        "releaseVersion": audit["version"],
        "sourceOfTruth": "research/coverage_audit.json",
        "counts": {
            "sourceForms": stats["uniqueForms"],
            "curatedEntries": stats["reviewedTranslations"],
            "pendingTranslations": stats["pendingTranslations"],
            "referenceRecords": stats["referenceRecords"],
            "sourceCount": stats["sourceCount"],
            "examplesWithSource": archive["sourceExamples"],
            "curatedEntriesWithoutSourceExample": archive["pendingExamples"]
        },
        "historicalProgress": {
            "version": archive["version"],
            "updatedAt": archive["updatedAt"],
            "sourceForms": archive["inventory"]["uniqueForms"],
            "referenceRecords": archive["inventory"]["referenceRecords"]
        },
        "scope": {
            "sourceForms": "Bentuk dari sumber; mencakup variasi, turunan dan frasa, bukan jumlah lema dasar yang telah disahkan.",
            "curatedEntries": "Memiliki padanan editorial; label sumber bukan pengesahan seluruh penutur/dialek.",
            "pendingTranslations": "Tercatat sebagai bentuk, belum mempunyai padanan terkurasi.",
            "examplesWithSource": "Contoh dari sumber tercatat, bukan klaim verifikasi baru oleh penutur.",
            "speakerVerifiedSenseCount": None
        }
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Refresh the tracked release snapshot after a reviewed data release.")
    args = parser.parse_args()
    snapshot = make_snapshot()
    output = ROOT / SNAPSHOT_PATH
    content = json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"
    if args.write:
        output.write_text(content, encoding="utf-8")
        print(f"Updated {SNAPSHOT_PATH} from verified source counts.")
    elif not output.exists() or output.read_text(encoding="utf-8") != content:
        raise SystemExit("FAIL: Release snapshot is stale. Review changes, then run python research/release_snapshot.py --write")
    print(json.dumps({"status":"PASS","version":snapshot["releaseVersion"],"counts":snapshot["counts"]},ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
