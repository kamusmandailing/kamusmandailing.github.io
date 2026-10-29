# Database Kamus Mandailing

Versi 2026-10-27-DEEP02 · 10,703 bentuk sumber unik · 1,404 entri berpadanan · 27 Oktober 2026.

Bank bertambah 54 bentuk dari rilis 10.649, melalui penggabungan indeks dan pemeriksaan sumber tambahan. Jumlah mencakup variasi ejaan, turunan, gabungan, bentuk terikat, serapan dan nama yang ditulis sumber; bukan jumlah semua kata dasar Mandailing. Label Angkola, Toba, Tapsel dan cakupan studi tidak dihapus. Tanpa label per bentuk tidak berarti Mandailing eksklusif.

9,299 bentuk belum memiliki padanan yang ditelaah. Kolom terjemahan dan contoh tidak diisi dengan tebakan. Glos konsep dan makna ringkas (source_gloss) adalah data sumber, bukan terjemahan baru yang sudah disunting. Koleksi berpadanan tetap 1.404 entri, dengan tiga contoh bersumber dan 1401 contoh berstatus pending.

## Isi dan cara membaca

- JSON: botanicalAudit menyimpan metode dan bentuk sumber yang ditahan; forms memuat seluruh bank; entries memuat koleksi berpadanan. extractionAudit menyimpan geometri dan keputusan calon OCR, bukan kamus kata mentah dari OCR. localNameObservations adalah pembanding terpisah.
- SQLite: lexical_forms memuat seluruh bank. View vocabulary_all menggabungkan padanan yang tersedia; dictionary tetap koleksi berpadanan. lexical_occurrences menyimpan 13,571 lokasi rujukan, label, cakupan, URL, glos sumber dan reference_json yang mempertahankan metadata.
- sources dan source_catalog menyimpan rujukan serta status akses/cakupan. source_coverage adalah audit 248 halaman kamus 2021. additional_coverage merinci pemeriksaan calon 1977, bukan klaim transkripsi penuh.
- local_name_observations memuat 183 catatan nama tumbuhan dengan bahasa per nama yang tidak dipastikan dalam tabel asal. local_name_reviews menyimpan 21 dukungan silang dengan cakupan yang dibedakan, serta catatan konflik takson, risiko homonim dan keterbatasan lainnya. Catatan tabel tidak otomatis menambah jumlah lexical_forms. matched_form_id hanya kecocokan ejaan dengan bank, bukan bukti kesamaan makna.
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
