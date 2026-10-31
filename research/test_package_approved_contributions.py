#!/usr/bin/env python3
"""Regression test: private export only packages explicitly approved submissions."""
import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/"research/package_approved_contributions.py"
spec=spec_from_file_location("approved",path)
mod=module_from_spec(spec)
spec.loader.exec_module(mod)

columns=list(mod.REQUIRED_COLUMNS)
with tempfile.TemporaryDirectory(prefix="kamus-approved-") as temporary:
    base=Path(temporary)
    source=base/"masuk.csv"
    output=base/"review.json"
    rows=[
        {"id":"one","status":"DISETUJUI","kata":"hata","makna":"kata atau bahasa","persetujuan":"YA","sumber":"Catatan rujukan penutur","tanggal_utc":"2026-10-31T00:00:00Z"},
        {"id":"pending","status":"MENUNGGU TELAAH","kata":"pribadi","makna":"belum disetujui","persetujuan":"YA","sumber":"Catatan"},
        {"id":"rejected","status":"DITOLAK","kata":"salah","makna":"tidak dipakai","persetujuan":"YA","sumber":"Catatan"},
        {"id":"unconsented","status":"DISETUJUI","kata":"tidakboleh","makna":"tanpa izin","persetujuan":"TIDAK","sumber":"Catatan"},
        {"id":"nosource","status":"DISETUJUI","kata":"tanpasumber","makna":"butuh referensi","persetujuan":"YA","sumber":"","catatan_editor":""},
        {"id":"duplicated","status":"DISETUJUI","kata":"satu","makna":"satu","persetujuan":"YA","catatan_editor":"Diperiksa editor"},
        {"id":"duplicated","status":"DISETUJUI","kata":"duplikat","makna":"dua","persetujuan":"YA","catatan_editor":"Diperiksa editor"}
    ]
    with source.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=columns)
        w.writeheader()
        for row in rows:w.writerow({k:row.get(k,"") for k in columns})
    p=subprocess.run([sys.executable,str(path),"--csv",str(source),"--out",str(output)],capture_output=True,text=True)
    assert p.returncode==0,p.stderr
    data=json.loads(output.read_text(encoding="utf-8"))
    assert data["candidate_count"]==2,data
    assert {x["submission_id"] for x in data["candidates"]}=={"one","duplicated"}
    assert all(x["review_status"]=="disetujui_belum_diterbitkan" for x in data["candidates"])
    assert data["status_counts"]["MENUNGGU TELAAH"]==1
    assert data["status_counts"]["DITOLAK"]==1
    assert len(p.stderr.splitlines())==3
    bad=subprocess.run([sys.executable,str(path),"--csv",str(source),"--out",str(ROOT/"src/words.json")],capture_output=True,text=True)
    assert bad.returncode!=0,"Must refuse changing public dictionary database"
    bad2=subprocess.run([sys.executable,str(path),"--csv",str(source),"--out",str(ROOT/"research/test-review.json")],capture_output=True,text=True)
    assert bad2.returncode!=0,"Must refuse writing candidate export in public git repo"
    incomplete=base/"bad.csv"
    incomplete.write_text("id,status,kata\na,DISETUJUI,hata\n",encoding="utf-8")
    try:
        mod.package_candidates(incomplete)
    except ValueError as e:
        assert "Kolom antrean tidak lengkap" in str(e)
    else:
        raise AssertionError("Missing columns must fail")
print("Private admin review package: PASS")
