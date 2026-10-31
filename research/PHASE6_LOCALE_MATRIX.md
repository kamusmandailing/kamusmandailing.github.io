# Tahap 6 — Matriks bahasa antarmuka dan pencarian

**Tanggal pemeriksaan:** 31 Oktober 2026
**Ruang lingkup:** pengaturan bahasa untuk elemen navigasi dan kontrol pencarian; **bukan** penerjemahan otomatis arti kamus atau konten riset.

## Status yang benar

| Kode pemilih | Bahasa | Perlakuan saat ini | Batasan yang diumumkan ke pengunjung |
| --- | --- | --- | --- |
| `id` | Bahasa Indonesia | Bahasa dasar antarmuka | Semua teks aplikasi belum tentu mencerminkan ejaan editorial final |
| `ms` | Melayu Malaysia | Terjemahan parsial label inti melalui `src/language-selector.js` | Hasil dinamis, detail sumber dan beberapa panel masih Indonesia |
| `en` | English | Terjemahan parsial label inti melalui `src/language-selector.js` | Hasil dinamis, detail sumber dan beberapa panel masih Indonesia |
| `md` | Mandailing | **Fallback Indonesia eksplisit**; belum ada terjemahan UI Mandailing yang disahkan penutur | Banner menjelaskan bahwa pilihan bahasa bukan pengesahan terjemahan Mandailing |

Atribut `<html lang>` sengaja tetap `id` karena mayoritas isi aplikasi tetap Bahasa Indonesia; label yang telah diterjemahkan ditandai `lang` masing-masing. Pemilihan bahasa disimpan pada `localStorage` (tanpa akun) tetapi tidak memodifikasi data kata atau padanan leksikon.

## Elemen utama yang kini dilokalkan (ID/MS/EN)

- Menu Kamus, Bank kosakata, Disimpan, Belajar, Catatan & sumber.
- Tombol Tambah / usulkan (pemilih jalur pribadi vs usulan komunitas).
- Label dan placeholder pencarian Kamus, bahasa pencarian, pilihan Semua bahasa.
- Semua huruf, status penelaahan, semua status, entri bersumber, draf awal, kata pribadi.
- Judul hasil, label ekspor TSV, sort, nama tampilan kartu/tabel pada pembaca layar.
- Bank Kosakata: label pencarian, placeholder, jenis bentuk, label bahasa sumber, status padanan dan sumber.
- Tombol Hapus pencarian pada kedua halaman, termasuk label pembaca layar.

**Belum dilokalkan sepenuhnya**: narasi hero, formulir kata pribadi, pilihan kategori dinamis, tampilan daftar/kartu dan jumlah hasil yang dibentuk `src/app.js`/`src/inventory.js`, teks detail sumber, mode belajar, konten panduan dan seluruh `kontributor.html`. Ini bukan implementasi empat bahasa penuh; mengiklankan sebaliknya akan menyesatkan.

## Perbaikan pencarian

Dua tombol `#search-clear` dan `#bank-search-clear` menghapus **query saja**, tidak mereset filter kategori/label, mengembalikan fokus ke input, lalu menghitung kembali hasil. Kontrol diberi label `aria-label` sesuai bahasa yang dipilih.

Aksi keyboard `/` untuk masuk ke pencarian yang telah ada tetap dipertahankan; data browser pribadi dan database terkurasi tidak diubah.

## Pengujian

- Kode: `research/test_phase6_locale_search.py`.
- CI: `.github/workflows/validate-phase6-locale-search.yml`.
- Browser: Chrome headless pada **1280×900, 390×844, 360×760**; semua lulus.
- Skenario: memilih id/en/ms/md; banner fallback dan `lang`; placeholder, label/aksesibilitas; pencarian yang tidak cocok; hapus query; fokus keyboard; jumlah hasil Bank dipulihkan; lebar viewport tidak overflow.
- Integritas basis: `research/validate_release.py` memeriksa **67 kontrak** setelah membangun ulang HTML/database: 10.821 bentuk; 1.404 entri; 13.745 rujukan tetap.
- Bukti: https://github.com/kamusmandailing/kamusmandailing.github.io/actions/runs/41216914124

## Pekerjaan lanjutan yang membutuhkan verifikasi manusia

1. Mintakan dua penutur/penelaah Mandailing untuk memeriksa istilah UI Mandailing sebelum mengubah `md` dari fallback menjadi terjemahan, termasuk ejaan dan ragam.
2. Perluas pilihan terjemahan id/ms/en ke pesan dinamis dan halaman Belajar; uji seluruh string yang muncul setelah filter/paginasi dan aplikasi luring.
3. Audit penggunaan pembaca layar sungguhan (NVDA/VoiceOver), navigasi Tab/Shift+Tab dalam modal, dan performa jaringan lambat pada perangkat nyata.
4. Telaah 40 entri pilot dari berkas Drive terpisah; jangan mengisi 9.417 padanan pending tanpa bukti.
5. Kontribusi Google Drive dan ruleset admin masih merupakan proyek terpisah dengan gerbang verifikasi sendiri.

**Aturan editorial:** jangan menciptakan padanan Mandailing, contoh, pelafalan, atau arti tanpa penelaahan yang terdokumentasi.
