# Tahap 8 — optimasi pencarian dan pemuatan Bank Kosakata

**Tanggal:** 1 November 2026
**Repository:** https://github.com/kamusmandailing/kamusmandailing.github.io
**Rilis data:** 2026-10-30-DEEP03 (konten tidak diubah).
**Pengujian:** https://github.com/kamusmandailing/kamusmandailing.github.io/actions/runs/41222427768

## Hasil implementasi
1. **Index pencarian dibuat hanya saat diperlukan.** Saat halaman pertama dibuka, teks normalisasi untuk 10.821 bentuk belum dibuat (`searchStringsCached=0` pada tes). Pencarian global pertama mengisi index, pencarian selanjutnya memakainya.
2. **Filter sumber mempersempit kandidat lebih dahulu.** Satu subset sumber (`abvd1655`) menguji 237 bentuk, bukan memindai semua bentuk untuk setiap pembaruan. Search terikat sumber hanya memuat rujukan sumber terpilih sehingga glos tidak bocor dari sumber lain.
3. **Cache filter antarpaginasi.** Query/jenis/status/sumber/huruf yang sama memakai array hasil sebelumnya. Skenario otomasi menunjukkan 39 pemindaian ulang saat pindah halaman dan 30 saat mengulang filter sumber dapat dihindari; ini angka operasi terhindar, bukan ukuran peningkatan kecepatan pengguna nyata.
4. **Index tambahan dan panel nama tumbuhan ditunda.** Index huruf dibangun saat bank dibuka/perlu filter huruf; index detail dibuat setelah pengguna membuka rincian bentuk; index perbandingan tumbuhan dan 183 kartu HTML dirender hanya ketika panel dibuka.
5. **HTML mandiri/luring tetap utuh.** Build masih menghasilkan HTML satu berkas dengan data dan skrip tertanam; tautan luar dan database ZIP dapat memerlukan internet.

## Bukti QA
- Workflow `validate-phase8-performance.yml`: berhasil.
- Test unit `research/test_phase8_bank_cache.cjs`: PASS, 10.821 bentuk, cache awal kosong, 39 + 30 pemindaian ulang terhindar.
- Test browser `research/test_phase8_browser_lazy.py`: PASS Chrome desktop 1280×900 dan mobile 390×844, termasuk pemuatan 183 nama tumbuhan ketika dibuka dan uji glos terikat sumber.
- Regression `research/test_phase6_locale_search.py`: PASS desktop 1280×900, 390×844 dan 360×760.
- `research/validate_release.py`: PASS **67 pemeriksaan** untuk HTML, TSV, SQLite, ID, sumber dan ZIP.
- Snapshot statis setelah perubahan: HTML **8.650.035 byte**, gzip **706.373 byte**; JSON tertanam **8.484.469 byte**, JS **71.645 byte**. Ukuran transfer belum berkurang dari tahap sebelumnya; optimasi ini ditujukan untuk pekerjaan awal DOM/CPU/memori, bukan kompresi data.

## Batasan yang belum selesai
- Belum ada pengukuran Web Vitals pada telepon fisik atau jaringan 3G/4G lambat.
- HTML satu berkas masih sekitar 8,65 MB mentah; optimasi ukuran kiriman perlu rancangan `online ringan + ekspor offline` yang disetujui dan diuji dengan sumber identik.
- Pelokalan UI Mandailing perlu penelaah penutur; jangan menebak istilah.
- Kontribusi tanpa akun Google Drive belum terbukti lulus POST & verifikasi baris antrean; tombol masih nonaktif.
- Persetujuan admin GitHub pada branch `main` masih memerlukan ruleset dan penelaahan hak akses.

## Usulan Tahap 9
1. Buat *online-first* terpisah yang memuat data bank secara bertahap, tetap menyediakan HTML mandiri untuk offline (dua jalur rilis, satu sumber data), dengan rollback dan tes kesetaraan jumlah/form/sumber.
2. Buat matriks performa perangkat nyata: LCP, INP, TBT, first-input, kecepatan cari pertama serta setelah cache, dan konsumsi memori. Tetapkan ambang berdasarkan pengukuran nyata.
3. Uji VoiceOver/NVDA dan operasi keyboard pada perangkat nyata.
4. Selesaikan pengujian Apps Script POST dan review 40 entri, tanpa publikasi otomatis.

**Keputusan editorial:** fase ini tidak menambah kata, padanan, audio, sumber, atau contoh yang belum diverifikasi.
