#!/usr/bin/env python3
"""Create an ADMIN-ONLY review package from a manually exported Google Sheets CSV.

This tool never publishes entries, edits the website, or reads Google credentials.
Output remains a candidate review file. Do NOT commit raw sheet CSV or this
output until sources, permissions, private data and editorial review are checked.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_COLUMNS = {
    "id", "tanggal_utc", "status", "jenis", "kata", "makna", "wilayah",
    "padanan", "contoh", "sumber", "persetujuan", "asal", "catatan_editor"
}
APPROVED_STATUS = "DISETUJUI"
DISALLOWED_OUTPUT = {"index.html", "words.json", "inventory.json", "Hata_Kamus_Mandailing.html"}

def package_candidates(csv_file: Path) -> tuple[dict, list[str]]:
    if not csv_file.exists():
        raise ValueError("Berkas ekspor CSV tidak ditemukan.")
    warnings = []
    with csv_file.open("r", encoding="utf-8-sig", newline="") as handle:
        source = csv.DictReader(handle)
        missing = REQUIRED_COLUMNS.difference(source.fieldnames or ())
        if missing:
            raise ValueError("Kolom antrean tidak lengkap: " + ", ".join(sorted(missing)))
        entries = []
        seen = set()
        stats = Counter()
        for n, row in enumerate(source, start=2):
            status = (row.get("status") or "").strip()
            if not any(str(v or "").strip() for v in row.values()):
                continue
            stats[status or "TANPA STATUS"] += 1
            if status != APPROVED_STATUS:
                continue
            id_ = (row.get("id") or "").strip()
            kata = (row.get("kata") or "").strip()
            makna = (row.get("makna") or "").strip()
            consent = (row.get("persetujuan") or "").strip().upper()
            if not id_ or id_ in seen:
                warnings.append(f"Baris {n}: ID kosong atau duplikat; tidak diekspor.")
                continue
            if consent != "YA" or not kata or len(makna) < 3:
                warnings.append(f"Baris {n}: kata, makna atau persetujuan tidak sah; tidak diekspor.")
                continue
            source_text = (row.get("sumber") or "").strip()
            note = (row.get("catatan_editor") or "").strip()
            if not source_text and not note:
                warnings.append(f"Baris {n}: sumber dan catatan editor kosong; perlu klarifikasi sebelum diekspor.")
                continue
            seen.add(id_)
            entries.append({
                "submission_id": id_,
                "received_at_utc": (row.get("tanggal_utc") or "").strip(),
                "jenis": (row.get("jenis") or "").strip(),
                "kata_mandailing": kata,
                "makna_usulan": makna,
                "wilayah_tutur": (row.get("wilayah") or "").strip(),
                "padanan_tambahan": (row.get("padanan") or "").strip(),
                "contoh_kalimat": (row.get("contoh") or "").strip(),
                "sumber_diajukan": source_text,
                "catatan_editor": note,
                "persetujuan_kontributor": True,
                "review_status": "disetujui_belum_diterbitkan"
            })
    return {
        "schema_version": "1.0",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "publication": "TIDAK OTOMATIS",
        "instruction": "Kandidat untuk peninjauan akhir. Periksa dialek, sumber, izin, data pribadi, dan konflik lema sebelum memasukkannya ke kamus publik.",
        "status_counts": dict(sorted(stats.items())),
        "candidate_count": len(entries),
        "candidates": entries
    }, warnings

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True, help="CSV tab Masuk yang diekspor administrator Google Drive.")
    parser.add_argument("--out", type=Path, required=True, help="Berkas JSON calon entri untuk pemeriksaan akhir (privat).")
    args = parser.parse_args(argv)
    if args.out.name in DISALLOWED_OUTPUT:
        parser.error("Dilarang menimpa berkas website atau database resmi.")
    # Private exports should stay outside public repository by default.
    repo_root = Path(__file__).resolve().parents[1]
    target = args.out.resolve()
    if target == repo_root or repo_root in target.parents:
        parser.error("Berkas hasil wajib berada DI LUAR repository publik untuk menghindari kebocoran usulan.")
    try:
        data, warnings = package_candidates(args.csv)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError) as exc:
        print("GAGAL:", str(exc), file=sys.stderr)
        return 1
    for warning in warnings:
        print("PERINGATAN:", warning, file=sys.stderr)
    print(f"Berhasil menyiapkan {data['candidate_count']} kandidat untuk telaah admin: {target}")
    print("Tidak ada data yang otomatis diterbitkan atau diubah di website.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
