# Tahap 7 — hasil pencarian, mode Belajar dan aksesibilitas UI

**Status implementasi:** selesai untuk cakupan terpilih, 1 November 2026. **Bukan** seluruh antarmuka empat bahasa.
**Basis data:** 10.821 bentuk sumber, 1.404 entri dengan padanan editorial, 9.417 belum berpadanan, 13.745 catatan rujukan tetap (67 tes integritas lulus).

## Perubahan tersedia

1. `src/language-selector.js` menyediakan fungsi terjemahan **pesan sistem** dan acara `kamus:locale`, tidak menyentuh teks per kata, sumber, contoh, label dialek, atau identitas entri.
2. `src/app.js` memperbarui **judul Semua Kosakata/Kosakata Disimpan**, jumlah kata cocok/tersimpan, pesan tak ada hasil, peringatan koleksi kosong, navigasi halaman dan teks pager secara langsung saat pengunjung mengganti bahasa. Judul kategori yang belum diterjemahkan masih Bahasa Indonesia.
3. `src/inventory.js` menerjemahkan ringkasan bentuk cocok, label tombol dan teks halaman Bank Kosakata. Isi kartu sumber, glos sumber, dan daftar filter dari sumber tetap apa adanya.
4. Mode **Belajar**: progres kartu, prompt untuk menebak padanan, membuka jawaban, ulangi nanti, sudah paham, mengacak, sesi selesai, dan mengulangi sesi mengikuti pemilih antarmuka.
5. `md` **fallback Indonesia terang-terangan** menunggu review penutur Mandailing; tidak ada istilah Mandailing yang diciptakan. `id`, `ms`, dan `en` hanya memengaruhi **UI yang disediakan**, bukan terjemahan leksikon.
6. Penerjemahan dapat berlangsung saat pengguna berada di hasil pencarian, Bank, maupun Belajar. State pencarian, filter, kartu dan kata tersimpan tetap dipertahankan.
7. `src/index.html` menyiapkan modul bahasa sebelum fungsi aplikasi agar pilihan yang dipulihkan dari browser sudah tersedia pada render pertama.

## Pengujian dan catatan batasan

- Tes: `research/test_phase7_dynamic_locale.py`. Chrome headless **1280×900**, **390×844** dan **360×760**: PASS.
- Memeriksa ID→EN→MS→MD→ID pada hasil/paginasi, Bank, kartu Belajar, perubahan status setelah pencarian, fallback `md`, bahasa dokumen yang jujur, serta dialog pilihan yang mengembalikan fokus ke pemicu.
- Tes identitas/export: `research/validate_release.py`, **67 pemeriksaan lulus**. Semua bentuk dan rujukan tetap.
- Tautan CI: https://github.com/kamusmandailing/kamusmandailing.github.io/actions/runs/41220987786
- **Pengukuran ukuran statis (bukan real-user speed):** HTML luring tunggal **8.647.951 byte mentah**, **705.677 byte gzip**, dengan **8.484.469 byte JSON tertanam** dan tanpa skrip/stylesheet luar. Alat `research/audit_offline_payload.py`; snapshot tersedia sebagai artefak CI yang masa simpan terbatas.
- Mode `file://` dapat memuat Kamus, Bank dan Belajar dari file HTML mandiri, tetapi membuka situs referensi dan mengunduh database ZIP dapat memerlukan internet.

## Ruang yang BELUM selesai

- Semua label kategori dan kartu detail per entri, teks yang dihasilkan oleh komponen sumber, formulir kata pribadi, modal kontribusi dan halaman `kontributor.html` belum lengkap diterjemahkan.
- `en` dan `ms` masih antarmuka parsial; label `md` belum mendapat review penutur. Tidak boleh diklaim lengkap.
- Native `<dialog>` diuji untuk fokus buka/tutup pada headless Chrome; belum ada pengujian VoiceOver/NVDA dengan pengguna perangkat fisik atau pengukuran WCAG menyeluruh.
- Ukuran file HTML mentah yang besar perlu evaluasi transfer gzip/HTTP, kecepatan mulai aplikasi pada ponsel sederhana, dan kemungkinan indeks bertahap tanpa menghilangkan fungsi offline.
- Uji POST Apps Script tanpa akun GitHub ke antrean privat Google Drive belum bisa dinyatakan lulus; jangan aktifkan tombol sampai bukti entri muncul di Sheets.
- Persetujuan admin saat merge/publish tetap memerlukan ruleset untuk `main` (issue #6); pilot 40 entri menunggu penelaahan manusia (issue #8).

## Tahap 8 yang disarankan

Audit performa nyata pada perangkat jaringan lambat dan screen reader, lanjutkan lokalisasi panel sumber/formulir, kumpulkan review istilah Mandailing dari penutur, lalu optimalkan pengiriman dataset dengan menjaga dukungan luring. Perlu menjaga pemisahan bentuk sumber vs padanan terkurasi serta persetujuan administrator sebelum rilis.
