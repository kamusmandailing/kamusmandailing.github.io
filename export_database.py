"""Export the same reviewed data used by the static app. Standard library only."""
from pathlib import Path
import json,sqlite3,zipfile,hashlib

ROOT=Path(__file__).resolve().parent

SCHEMA='''PRAGMA page_size=8192;
PRAGMA foreign_keys=ON;
CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE sources (id TEXT PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL, url TEXT NOT NULL, document_url TEXT NOT NULL, short_title TEXT NOT NULL);
CREATE TABLE entries (
 id TEXT PRIMARY KEY, mandailing TEXT NOT NULL COLLATE NOCASE UNIQUE,
 category TEXT NOT NULL, part_of_speech TEXT NOT NULL DEFAULT '',
 status TEXT NOT NULL CHECK(status IN ('source_attested','draft','personal')),
 batch TEXT, reviewed_at TEXT, scope TEXT NOT NULL, note TEXT NOT NULL,
 example_status TEXT NOT NULL CHECK(example_status IN ('source_quoted','pending','draft'))
);
CREATE TABLE translations (
 entry_id TEXT NOT NULL REFERENCES entries(id), language TEXT NOT NULL CHECK(language IN ('id','ms-MY','en')),
 value TEXT NOT NULL CHECK(length(trim(value))>0), status TEXT NOT NULL,
 PRIMARY KEY(entry_id,language)
);
CREATE TABLE aliases (entry_id TEXT NOT NULL REFERENCES entries(id), alias TEXT NOT NULL, PRIMARY KEY(entry_id,alias));
CREATE TABLE entry_references (
 entry_id TEXT PRIMARY KEY REFERENCES entries(id), source_id TEXT NOT NULL REFERENCES sources(id),
 source_lemma TEXT NOT NULL, location_kind TEXT NOT NULL, printed_page TEXT NOT NULL,
 pdf_page INTEGER NOT NULL CHECK(pdf_page>0), language_label TEXT NOT NULL, homonym TEXT
);
CREATE TABLE translation_references (
 entry_id TEXT NOT NULL REFERENCES entries(id), language TEXT NOT NULL,
 source_id TEXT NOT NULL REFERENCES sources(id), url TEXT NOT NULL, note TEXT NOT NULL
);
CREATE TABLE examples (
 entry_id TEXT PRIMARY KEY REFERENCES entries(id), mandailing TEXT NOT NULL,
 indonesia TEXT NOT NULL, source_id TEXT NOT NULL REFERENCES sources(id),
 printed_page TEXT NOT NULL, pdf_page INTEGER NOT NULL, note TEXT NOT NULL
);
CREATE INDEX entries_category_idx ON entries(category);
CREATE INDEX translations_value_idx ON translations(value COLLATE NOCASE);
CREATE INDEX aliases_lookup_idx ON aliases(alias COLLATE NOCASE);
CREATE VIEW dictionary AS
 SELECT e.id, e.mandailing AS Mandailing,
 ti.value AS Indonesia, tm.value AS "Melayu Malaysia", te.value AS English,
 CASE WHEN x.mandailing IS NOT NULL THEN 'Mandailing: '||x.mandailing||' — Indonesia: '||x.indonesia ELSE '' END AS "Contoh Kalimat"
 FROM entries e JOIN translations ti ON ti.entry_id=e.id AND ti.language='id'
 JOIN translations tm ON tm.entry_id=e.id AND tm.language='ms-MY'
 JOIN translations te ON te.entry_id=e.id AND te.language='en'
 LEFT JOIN examples x ON x.entry_id=e.id;
CREATE TABLE lexical_forms (
 id TEXT PRIMARY KEY, form TEXT NOT NULL COLLATE NOCASE UNIQUE,
 curated_entry_id TEXT REFERENCES entries(id), status TEXT NOT NULL,
 kinds_json TEXT NOT NULL, labels_json TEXT NOT NULL, usage_tags_json TEXT NOT NULL
);
CREATE TABLE lexical_occurrences (
 id INTEGER PRIMARY KEY, form_id TEXT NOT NULL REFERENCES lexical_forms(id),
 source_id TEXT NOT NULL REFERENCES sources(id), printed_page TEXT NOT NULL,
 pdf_page INTEGER CHECK(pdf_page IS NULL OR pdf_page>0), kind TEXT NOT NULL, parent_form TEXT NOT NULL,
 homonym TEXT NOT NULL, labels_json TEXT NOT NULL, label_basis TEXT NOT NULL,
 layout_status TEXT NOT NULL, source_column INTEGER, source_x REAL, source_y REAL,
 cross_reference TEXT NOT NULL, printed_notation TEXT NOT NULL, normalization_note TEXT NOT NULL,
 source_url TEXT NOT NULL, source_locator TEXT NOT NULL, source_scope TEXT NOT NULL,
 source_gloss TEXT NOT NULL, gloss_language TEXT NOT NULL, annotation TEXT NOT NULL, reference_json TEXT NOT NULL,
 taxon_as_printed TEXT NOT NULL
);
CREATE TABLE source_coverage (
 source_id TEXT NOT NULL REFERENCES sources(id), printed_page INTEGER NOT NULL,
 pdf_page INTEGER NOT NULL, body_span_count INTEGER NOT NULL, lexical_record_count INTEGER NOT NULL,
 PRIMARY KEY(source_id,printed_page)
);
CREATE TABLE source_catalog (id TEXT PRIMARY KEY, title TEXT NOT NULL, url TEXT NOT NULL, inventory_status TEXT NOT NULL, note TEXT NOT NULL, sha256 TEXT NOT NULL);
CREATE TABLE extraction_audit (
 source_id TEXT NOT NULL REFERENCES sources(id), candidate_id INTEGER NOT NULL,
 pdf_page INTEGER NOT NULL, printed_page INTEGER NOT NULL, source_column INTEGER NOT NULL,
 bbox_json TEXT NOT NULL, candidate_kind TEXT NOT NULL, review_status TEXT NOT NULL,
 accepted_printed_forms_json TEXT NOT NULL, PRIMARY KEY(source_id,candidate_id)
);
CREATE TABLE additional_coverage (source_id TEXT PRIMARY KEY REFERENCES sources(id), details_json TEXT NOT NULL);
CREATE TABLE local_name_observations (
 id TEXT PRIMARY KEY, name TEXT NOT NULL, source_id TEXT NOT NULL REFERENCES sources(id),
 printed_page TEXT NOT NULL, pdf_page INTEGER NOT NULL, source_locator TEXT NOT NULL,
 language_status TEXT NOT NULL, scope TEXT NOT NULL, normalization_note TEXT NOT NULL,
 matched_form_id TEXT REFERENCES lexical_forms(id),
 taxon_as_printed TEXT NOT NULL, taxon_expanded TEXT NOT NULL, taxon_note TEXT NOT NULL
);
CREATE TABLE local_name_reviews (
 observation_id TEXT PRIMARY KEY REFERENCES local_name_observations(id),
 review_status TEXT NOT NULL, note TEXT NOT NULL, taxon_as_printed TEXT NOT NULL,
 evidence_json TEXT NOT NULL
);
CREATE TABLE second_pass_extraction_audit (
 source_id TEXT NOT NULL REFERENCES sources(id), candidate_id INTEGER NOT NULL,
 pdf_page INTEGER NOT NULL, source_column INTEGER NOT NULL,
 bbox_json TEXT NOT NULL, review_status TEXT NOT NULL, accepted_forms_json TEXT NOT NULL,
 PRIMARY KEY(source_id,candidate_id)
);
CREATE INDEX lexical_occurrences_form_idx ON lexical_occurrences(form_id);
CREATE INDEX lexical_occurrences_parent_idx ON lexical_occurrences(parent_form);
CREATE VIEW vocabulary_all AS
 SELECT f.id, f.form AS Mandailing, d.Indonesia, d."Melayu Malaysia", d.English,
 d."Contoh Kalimat", f.status, f.curated_entry_id, f.kinds_json, f.labels_json
 FROM lexical_forms f LEFT JOIN dictionary d ON d.id=f.curated_entry_id;
PRAGMA user_version=5;
'''

def export_database():
    words=json.loads((ROOT/'src/words.json').read_text())
    sources=json.loads((ROOT/'src/sources.json').read_text())
    progress=json.loads((ROOT/'research/progress.json').read_text())
    bank=json.loads((ROOT/'src/inventory.json').read_text())
    catalog=json.loads((ROOT/'research/source_catalog.json').read_text())
    target=ROOT/'data/database';target.mkdir(parents=True,exist_ok=True)
    audit=json.loads((ROOT/'research/1977_extraction_geometry.json').read_text())
    second_audit=json.loads((ROOT/'research/1977_second_pass_audit.json').read_text())
    manifest={'schemaVersion':5,'datasetVersion':bank['version'],'updatedAt':progress['updatedAt'],
              'entryCount':len(words),'notExhaustive':True,'notes':progress['notes'],
              'sources':sources,'entries':words,'inventoryStats':bank['stats'],'forms':bank['forms'],
              'sourceCoverage':bank['coverage'],'sourceCatalog':catalog,'additionalCoverage':bank['additionalCoverage'],
              'extractionAudit':audit,'secondPassExtractionAudit':second_audit,
              'researchUpdate':bank['researchUpdate'],'localNameObservations':bank['localNames'],
              'botanicalAudit':json.loads((ROOT/'research/botanical_audit_20261027.json').read_text())}
    (target/'kamusmandailing.json').write_text(json.dumps(manifest,ensure_ascii=False,separators=(',',':'))+'\n')
    (target/'schema.sql').write_text(SCHEMA)
    dbfile=target/'kamusmandailing.sqlite';temporary=target/'kamusmandailing.sqlite.tmp'
    temporary.unlink(missing_ok=True)
    con=sqlite3.connect(temporary);con.executescript(SCHEMA)
    con.execute('INSERT INTO metadata VALUES (?,?)',('dataset',json.dumps({k:v for k,v in manifest.items() if k not in ['sources','entries','forms','sourceCoverage','extractionAudit','secondPassExtractionAudit','localNameObservations']},ensure_ascii=False)))
    for s in sources:con.execute('INSERT INTO sources VALUES (?,?,?,?,?,?)',(s['id'],s['title'],s['meta']+' — '+s['use'],s['url'],s.get('documentUrl',''),s.get('shortTitle',s['title'])))
    for w in words:
        con.execute('INSERT INTO entries VALUES (?,?,?,?,?,?,?,?,?,?)',(w['id'],w['md'],w['category'],w.get('pos',''),w['status'],w.get('batch'),w.get('reviewedAt'),w.get('scope',''),w.get('note',''),w['exampleStatus']))
        for key,lang in [('idn','id'),('my','ms-MY'),('en','en')]:
            con.execute('INSERT INTO translations VALUES (?,?,?,?)',(w['id'],lang,w[key],w.get('translationStatus',{}).get(key,'editorial')))
        for a in w.get('aliases',[]):con.execute('INSERT INTO aliases VALUES (?,?)',(w['id'],a))
        ref=w.get('sourceRef')
        if ref:con.execute('INSERT INTO entry_references VALUES (?,?,?,?,?,?,?,?)',(w['id'],ref['id'],ref['lemma'],ref['kind'],str(ref['printedPage']),ref['pdfPage'],ref['languageLabel'],ref.get('homonym')))
        for ref in w.get('translationRefs',[]):con.execute('INSERT INTO translation_references VALUES (?,?,?,?,?)',(w['id'],{'my':'ms-MY','idn':'id','en':'en'}.get(ref['language'],ref['language']),ref['id'],ref['url'],ref.get('note','')))
        if w.get('exampleMd'):
            ref=w['exampleRef'];con.execute('INSERT INTO examples VALUES (?,?,?,?,?,?,?)',(w['id'],w['exampleMd'],w['exampleId'],ref['id'],str(ref['printedPage']),ref['pdfPage'],ref.get('note','')))
    encode=lambda v:json.dumps(v,ensure_ascii=False,separators=(',',':'))
    source_map={s['id']:s for s in sources}
    def ref_url(ref):
        src=source_map[ref['sourceId']];base=ref.get('url') or src.get('documentUrl') or src['url']
        return base.split('#')[0]+'#page='+str(ref['pdfPage']) if ref.get('pdfPage') and src.get('documentUrl') and not ref.get('url') else base
    for f in bank['forms']:
        con.execute('INSERT INTO lexical_forms VALUES (?,?,?,?,?,?,?)',(f['id'],f['form'],f['entryId'],f['status'],encode(f['kinds']),encode(f['labels']),encode(f['usageTags'])))
        for ref in f['references']:
            con.execute('INSERT INTO lexical_occurrences(form_id,source_id,printed_page,pdf_page,kind,parent_form,homonym,labels_json,label_basis,layout_status,source_column,source_x,source_y,cross_reference,printed_notation,normalization_note,source_url,source_locator,source_scope,source_gloss,gloss_language,annotation,reference_json,taxon_as_printed) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
             (f['id'],ref['sourceId'],str(ref['printedPage']),ref['pdfPage'],ref['kind'],ref['parent'],ref['homonym'],encode(ref['labels']),ref['labelBasis'],ref['layoutStatus'],ref['column'],ref['x'],ref['y'],ref['crossReference'],ref['printedNotation'],ref['normalizationNote'],ref_url(ref),ref.get('sourceLocator',''),ref.get('sourceScope',''),ref.get('sourceGloss',''),ref.get('glossLanguage',''),ref.get('annotation',''),encode(ref),ref.get('taxonAsPrinted','')))
    for p in bank['coverage']:con.execute('INSERT INTO source_coverage VALUES (?,?,?,?,?)',('dictionary',p['printedPage'],p['pdfPage'],p['bodySpanCount'],p['records']))
    for c in catalog:con.execute('INSERT INTO source_catalog VALUES (?,?,?,?,?,?)',(c['id'],c['title'],c['url'],c['inventoryStatus'],c['note'],c['sha256']))
    for row in audit['records']:
        con.execute('INSERT INTO extraction_audit VALUES (?,?,?,?,?,?,?,?,?)',
            ('dictionary1977',row['id'],row['pdfPage'],row['printedPage'],row['column'],encode(row['bbox']),row['kind'],row['reviewStatus'],encode(row.get('acceptedPrintedForms',[]))))
    con.execute('INSERT INTO additional_coverage VALUES (?,?)',('dictionary1977',encode(bank['additionalCoverage'])))
    form_ids={f['form'].casefold():f['id'] for f in bank['forms']}
    for row in bank['localNames']:
        con.execute('INSERT INTO local_name_observations VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
            (row['id'],row['name'],row['sourceId'],str(row['printedPage']),row['pdfPage'],row['sourceLocator'],row['languageStatus'],row['scope'],row['normalizationNote'],form_ids.get(row['name'].casefold()),row.get('taxonAsPrinted',''),row.get('taxonExpanded',''),row.get('taxonNote','')))
        review=row['review']
        con.execute('INSERT INTO local_name_reviews VALUES (?,?,?,?,?)',
            (row['id'],review['status'],review['note'],review.get('taxonAsPrinted',''),encode(review.get('evidence',[]))))
    for row in second_audit['records']:
        con.execute('INSERT INTO second_pass_extraction_audit VALUES (?,?,?,?,?,?,?)',
            ('dictionary1977',row['id'],row['pdfPage'],row['column'],encode(row['bbox']),row['reviewStatus'],encode(row['acceptedForms'])))
    con.commit()
    assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    assert not con.execute('PRAGMA foreign_key_check').fetchall()
    assert con.execute('SELECT count(*) FROM dictionary').fetchone()[0]==len(words)
    assert con.execute('SELECT count(*) FROM translations').fetchone()[0]==len(words)*3
    assert con.execute('SELECT count(*) FROM vocabulary_all').fetchone()[0]==bank['stats']['uniqueForms']
    assert con.execute('SELECT count(*) FROM lexical_occurrences').fetchone()[0]==bank['stats']['referenceRecords']
    con.close();temporary.replace(dbfile)
    guide=f'''# Database Kamus Mandailing

Versi {bank['version']} · {bank['stats']['uniqueForms']:,} bentuk sumber unik · {len(words):,} entri berpadanan · 27 Oktober 2026.

Bank bertambah {bank['stats']['releaseAddedUniqueForms']:,} bentuk dari rilis 10.649, melalui penggabungan indeks dan pemeriksaan sumber tambahan. Jumlah mencakup variasi ejaan, turunan, gabungan, bentuk terikat, serapan dan nama yang ditulis sumber; bukan jumlah semua kata dasar Mandailing. Label Angkola, Toba, Tapsel dan cakupan studi tidak dihapus. Tanpa label per bentuk tidak berarti Mandailing eksklusif.

{bank['stats']['pendingTranslations']:,} bentuk belum memiliki padanan yang ditelaah. Kolom terjemahan dan contoh tidak diisi dengan tebakan. Glos konsep dan makna ringkas (source_gloss) adalah data sumber, bukan terjemahan baru yang sudah disunting. Koleksi berpadanan tetap 1.404 entri, dengan tiga contoh bersumber dan {progress['pendingExamples']} contoh berstatus pending.

## Isi dan cara membaca

- JSON: botanicalAudit menyimpan metode dan bentuk sumber yang ditahan; forms memuat seluruh bank; entries memuat koleksi berpadanan. extractionAudit menyimpan geometri dan keputusan calon OCR, bukan kamus kata mentah dari OCR. localNameObservations adalah pembanding terpisah.
- SQLite: lexical_forms memuat seluruh bank. View vocabulary_all menggabungkan padanan yang tersedia; dictionary tetap koleksi berpadanan. lexical_occurrences menyimpan {bank['stats']['referenceRecords']:,} lokasi rujukan, label, cakupan, URL, glos sumber dan reference_json yang mempertahankan metadata.
- sources dan source_catalog menyimpan rujukan serta status akses/cakupan. source_coverage adalah audit 248 halaman kamus 2021. additional_coverage merinci pemeriksaan calon 1977, bukan klaim transkripsi penuh.
- local_name_observations memuat {bank['stats']['localNameObservations']} catatan nama tumbuhan dengan bahasa per nama yang tidak dipastikan dalam tabel asal. local_name_reviews menyimpan 21 dukungan silang dengan cakupan yang dibedakan, serta catatan konflik takson, risiko homonim dan keterbatasan lainnya. Catatan tabel tidak otomatis menambah jumlah lexical_forms. matched_form_id hanya kecocokan ejaan dengan bank, bukan bukti kesamaan makna.
- kosakata_semua.tsv menyediakan tepat lima kolom sesuai format awal; padanan belum ditelaah kosong. Gunakan kosakata_berlabel.tsv untuk mempertahankan label cakupan dan jenis. inventaris_sumber.tsv memberikan lokasi setiap rujukan. nama_tumbuhan_pembanding.tsv menyimpan observasi terpisah.

Contoh kueri:

```sql
SELECT count(*) FROM lexical_forms;
SELECT * FROM vocabulary_all WHERE Mandailing LIKE 'a%' ORDER BY Mandailing;
SELECT f.form,r.source_id,r.source_url,r.source_scope
FROM lexical_forms f JOIN lexical_occurrences r ON r.form_id=f.id
WHERE f.form='mangabahon';
SELECT source_id,count(*) FROM lexical_occurrences GROUP BY source_id;
SELECT review_status,count(*) FROM extraction_audit GROUP BY review_status;
SELECT name,scope FROM local_name_observations;
```

## Batas cakupan

Kamus 2021: indeks leksikal halaman 1–248. Kamus 1977: audit awal 3.403 calon dari deteksi OCR, dilanjutkan 1.395 crop unik pada pemeriksaan kedua; kandidat yang tidak layak tidak dipromosikan. Ini belum transkripsi semua isi buku. ABVD 1655: 241 catatan dataset; bukan seluruh kamus Harahap 2007. Kamus mandiri 2024: indeks bentuk pada PDF 3–17. Idiom 2012: 75 bentuk pada tabel. Ensiklopedia budaya 2021: 650 lokasi istilah terpilih dalam cakupan Angkola–Mandailing, bukan semua isi ensiklopedia. Metafora flora 2015: 13 bentuk pada abstrak. Kamus idiom 2023: enam bentuk dari abstrak penerbit; PDF penuh gagal diakses. Kamus Parinduri 2019 dan Eggink 1936 belum diperoleh isinya. Lihat analisis_lanjutan_20261027.md dan source_catalog.json.

Skema 5 mempertahankan tabel lama, mempertahankan second_pass_extraction_audit dan local_name_reviews serta menambahkan kolom takson pada lexical_occurrences dan local_name_observations, serta membolehkan pdf_page NULL untuk sumber web dan menambah lokasi web, metadata rujukan, audit ekstraksi, serta observasi nama lokal. Ekspor merupakan berkas baru, bukan migrasi yang dijalankan pada database pengguna. ID entri lama dan ID bentuk tetap dipertahankan.

Pendalaman tahap 2, 27 Oktober 2026: 54 bentuk baru dan 99 rujukan tambahan. Lihat research/analisis_lanjutan_20261027.md. nama_botani_sumber.tsv memuat 75 lokasi nama–takson; 182 nama ilmiah pada observasi pembanding disalin sebagaimana sumber. Satu baris sumber memang kosong. Glos sumber dibedakan dari terjemahan kurasi; local_name_reviews mempertahankan dukungan silang per nama.

Aplikasi statis menyimpan favorit, progres dan kata pribadi di peramban. SQLite adalah ekspor, bukan backend server. Untuk membangun ulang dari sumber repo, jalankan python3 build.py. Tidak perlu jaringan atau paket Python tambahan untuk build biasa. PDF dan definisi lengkap buku tidak disalin ke paket ini.
'''
    (target/'README.md').write_text(guide)
    package_files={p.name:p for p in target.iterdir() if p.is_file() and p.suffix!='.tmp'}
    package_files.update({'kamus.tsv':ROOT/'data/kamus.tsv','jejak_sumber.tsv':ROOT/'data/jejak_sumber.tsv','analisis_AZ.md':ROOT/'research/analisis_AZ.md','kosakata_semua.tsv':ROOT/'data/kosakata_semua.tsv','inventaris_sumber.tsv':ROOT/'data/inventaris_sumber.tsv','analisis_inventaris.md':ROOT/'research/analisis_inventaris.md','source_catalog.json':ROOT/'research/source_catalog.json'})
    package_files.update({'kosakata_berlabel.tsv':ROOT/'data/kosakata_berlabel.tsv','nama_tumbuhan_pembanding.tsv':ROOT/'data/nama_tumbuhan_pembanding.tsv','telaah_nama_tumbuhan.tsv':ROOT/'data/telaah_nama_tumbuhan.tsv','nama_botani_sumber.tsv':ROOT/'data/nama_botani_sumber.tsv'})
    for name in ['additional_inventory.json','1977_extraction_geometry.json','1977_review_decisions.txt','local_name_observations.json','coverage_audit.json','1977_second_pass_audit.json','extension_20261027.json','research_update_20261027.json','analisis_pendalaman_20261027.md','extension_20261027b.json','botanical_audit_20261027.json','analisis_lanjutan_20261027.md']:
        package_files['research/'+name]=ROOT/'research'/name
    checks='\n'.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+name for name,p in sorted(package_files.items()))+'\n'
    with zipfile.ZipFile(ROOT/'data/Kamus_Mandailing_Database.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,p in sorted(package_files.items()):z.write(p,name)
        z.writestr('SHA256SUMS.txt',checks)
    print(f'Database exported: {bank["stats"]["uniqueForms"]} forms, {len(words)} curated entries, SQLite integrity OK.')

if __name__=='__main__':export_database()
