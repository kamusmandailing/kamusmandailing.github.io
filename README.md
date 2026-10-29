# Hata — Kamus Mandailing

**10.703 bentuk sumber unik**, bertambah **54** dari rilis 10.649. Bank menggabungkan **19 sumber bentuk**, dengan **13.571 catatan rujukan**. Koleksi berpadanan tetap **1.404 entri**; **9.299 bentuk** lainnya menunggu penelaahan padanan. Ada **183 catatan nama tumbuhan pembanding**, dengan 182 nama ilmiah asal serta 21 dukungan silang yang membedakan label Mandailing, kode gabungan MA, dan cakupan studi; konflik takson dan risiko homonim dicatat.

[Buka aplikasi](https://kamusmandailing.github.io/) · [Bank kosakata](https://kamusmandailing.github.io/#bank) · [Analisis dan batas cakupan](research/analisis_lanjutan_20261027.md) · [Database JSON/SQLite](data/Kamus_Mandailing_Database.zip) · [Paket aplikasi lengkap](Hata_Kamus_Mandailing_Lengkap.zip)

Repositori tujuan proyek: [kamusmandailing/kamusmandailing.github.io](https://github.com/kamusmandailing/kamusmandailing.github.io). Seluruh aplikasi, database, hasil penelitian, dan paket unduhan disiapkan bersama untuk alamat utama baru pada 29 Oktober 2026. Lihat [catatan pemindahan](research/migrasi_20261029.md).

Jumlah ini mencakup variasi, turunan, frasa, serapan dan bentuk terikat yang ditulis sumber; bukan klaim seluruh kata dasar Mandailing atau semua kosakata semua dialek sudah terkumpul. Label Angkola, Toba, Tapsel dan cakupan penelitian dipertahankan. PDF 1977 masih merupakan indeks tambahan parsial; buku Parinduri 2019 dan isi penuh kamus idiom 2023 belum diperoleh.

[Hasil pendalaman tahap 2, 27 Oktober 2026](research/analisis_lanjutan_20261027.md) · [Telaah per nama tumbuhan](data/telaah_nama_tumbuhan.tsv)

## Menggunakan aplikasi

Buka Bank kosakata untuk mencari bentuk, induk, padanan yang tersedia atau glos konsep sumber. Filter menurut huruf, jenis bentuk, label bahasa, status padanan dan sumber. Lihat sumber menampilkan halaman PDF atau lokasi web yang tepat, anotasi serta catatan ejaan. Ekspor mengikuti hasil filter; tersedia TSV lima kolom dan TSV berlabel. Panel nama tumbuhan merupakan data pembanding dengan bahasa per nama yang belum ditetapkan, bukan tambahan lema Mandailing.

Tab Kamus, Disimpan dan Belajar memakai koleksi berpadanan. Desain mempertahankan ornamen tenun Mandailing. Favorit, progres dan kata pribadi tetap tersimpan di peramban, dengan ID lama dipertahankan. HTML unduhan dapat dipakai secara luring; tautan rujukan membutuhkan internet.

## Data dan cakupan

- [Seluruh bank, TSV lima kolom](data/kosakata_semua.tsv): padanan belum ditelaah kosong.
- [Seluruh bank dengan label](data/kosakata_berlabel.tsv): label sumber, jenis dan identitas disertakan.
- [Lokasi rujukan lengkap](data/inventaris_sumber.tsv): satu baris per catatan rujukan.
- [Nama botani dan lokasi sumber](data/nama_botani_sumber.tsv): 75 rujukan nama–takson yang terpilih.
- [Nama tumbuhan pembanding](data/nama_tumbuhan_pembanding.tsv): 183 pengamatan terpisah.
- [Katalog akses dan batas sumber](research/source_catalog.json), [audit rilis](research/coverage_audit.json), [panduan skema](data/database/README.md).
- [Koleksi berpadanan](data/kamus.tsv), [jejak kurasi lama](data/jejak_sumber.tsv), [riwayat A–Z](research/analisis_AZ.md).

Verifikasi bentuk berarti terbaca pada sumber, bukan pengesahan penutur semua dialek. Mdl-scope dibedakan dari label Mdl per bentuk; unmarked tidak berarti Mandailing eksklusif. Terjemahan Melayu/Inggris bersifat editorial. Hanya tiga contoh kalimat yang mempunyai rujukan; 1.401 entri berpadanan lain belum memiliki contoh terverifikasi. Tidak ada padanan atau kalimat pengisi yang direka.

## Membangun dan menyunting

Jalankan `python3 build.py` dengan Python standar. `prepare_inventory.py` menggabungkan indeks 2021 dan `research/build_additional_inventory.py`; seluruh keputusan tambahan tersedia dalam repo. `src/words.json` memuat koleksi berpadanan, `src/inventory.json` memuat bank aplikasi, `src/sources.json` memuat sumber. `src/app.js` dan `src/inventory.js` memuat logika; CSS dan SVG dalam `src/` mempertahankan desain. SVG merupakan adaptasi digital, bukan motif adat yang diautentikasi.

Build menghasilkan HTML yang sama di root dan `dist/`, TSV, JSON, SQLite serta paket database. Ekstraksi ulang PDF memerlukan pustaka yang disebutkan skrip penelitian; build biasa tidak memerlukan jaringan. PDF dan definisi lengkap tidak didistribusikan dalam repo. GitHub Pages menerbitkan main, folder root, dengan `.nojekyll`.

## Skema 5

`forms` JSON dan tabel SQLite `lexical_forms` adalah seluruh bank. `entries` dan view `dictionary` adalah koleksi berpadanan. `vocabulary_all` menggabungkan keduanya. `lexical_occurrences` mempertahankan semua metadata termasuk sumber web dengan pdf_page NULL. `extraction_audit` menyimpan geometri/status calon OCR, bukan teks mentah definisi. `local_name_observations` tidak menambah hitungan bentuk Mandailing. `second_pass_extraction_audit` menyimpan audit tambahan pindai 1977; `local_name_reviews` menyimpan dukungan silang dan risiko homonim. Kolom takson pada lexical_occurrences dan local_name_observations mempertahankan nama ilmiah cetakan sumber. SQLite adalah ekspor yang dapat dibuka lokal, bukan backend server situs statis.
