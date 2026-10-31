# Integrasi Halaman Kontributor → Google Drive

## Tujuan

Mengumpulkan usulan dari `kontributor.html` ke **Google Sheet privat** bernama `Kamus Mandailing — Antrean Usulan Kontributor` di dalam folder `Kontribusi Komunitas - Masuk dan Telaah` pada folder proyek Kamus Mandailing. Kontributor tidak mendapat akses tulis maupun baca ke Drive atau repository. Semua catatan baru berstatus **MENUNGGU TELAAH**.

**Status 31 Oktober 2026:** URL Web app telah dipasang pada halaman, tetapi pengujian POST ke tab `Masuk` belum terbukti berhasil. Oleh sebab itu sakelar `kamus-drive-enabled` masih `false` dan tombol publik tetap nonaktif. GitHub Issues sudah aktif sebagai alternatif. Jangan menyatakan usulan tersimpan sebelum ada tanda terima **dan** baris di Sheet privat. Tab `Panel Admin` telah dibuat untuk memantau antrean.

## Konfigurasi satu kali oleh administrator Google

1. Buka https://script.google.com/home/projects/create menggunakan **akun Google yang memiliki akses editor/owner** ke folder kontribusi Kamus Mandailing. Jangan menggunakan akun kontributor umum.
2. Beri nama proyek `Penerima Usulan Kamus Mandailing`.
3. Salin seluruh isi `Code.gs` dari direktori ini ke file `Code.gs` proyek tersebut. Simpan.
4. Buka **Project Settings → Script properties**, buat:
   - `KAMUS_INTAKE_FOLDER_ID` = ID folder privat **Kontribusi Komunitas - Masuk dan Telaah**. Cari ID folder pada arsip admin Google Drive, jangan memublikasikannya ke halaman.
5. Atur juga Script Property `KAMUS_INTAKE_SHEET_ID` ke spreadsheet antrean **yang sudah ada**, lalu pilih fungsi `setupOnce` dan jalankan **Run**. Fungsi ini memeriksa tab `Masuk` dan header yang benar; jika ID tidak diatur, script dapat membuat spreadsheet lain sehingga usulan tidak muncul pada antrean yang diharapkan. Periksa `Executions` bila POST gagal.
6. Pastikan Sheet benar-benar berada pada folder privat dan hanya akun yang diizinkan memiliki hak lihat/edit. Jangan publikasikan Sheet atau folder sebagai `Anyone with the link`.
7. Di Apps Script pilih **Deploy → New deployment → Web app**. Set **Execute as: Me** (akun pemilik script), **Who has access: Anyone** (apabila publik tanpa login diizinkan oleh kebijakan akun). Lakukan deployment, kemudian salin URL yang berakhiran **/exec**.
8. URL Web app diletakkan pada `<meta name="kamus-drive-endpoint" content="...">` di `kontributor.html`. **Memasang URL saja tidak mengaktifkan tombol**: pengelola sengaja menggunakan `<meta name="kamus-drive-enabled" content="false">` sampai pengujian penyimpanan end-to-end lulus. Jangan menggantinya ke `true` sebelum verifikasi.
9. **Lakukan kiriman uji (tanpa data orang sungguhan)** dari halaman, lihat tanda terima pada tab baru, dan periksa satu baris `MENUNGGU TELAAH` tercatat di Sheet. Hapus/arsipkan baris uji. Baru umumkan kanal kontribusi langsung.
10. Di `Settings > Rules` GitHub aktifkan kewajiban persetujuan admin untuk `main` sebelum memberikan akses tambahan (lihat `CODEOWNERS` dan issue pengamanan).

## Mekanisme pengiriman

- Pengunjung mengisi formulir yang sama dengan formulir GitHub, lalu memilih **Kirim langsung ke Google Drive**.
- Form membuat HTTP **POST standar** ke Apps Script di tab baru, bukan `fetch`; pendekatan ini tidak memerlukan CORS browser.
- Script menguji persetujuan, panjang isian, jenis kontribusi, dan honeypot, lalu memakai lock serta batas global sederhana (15/menit).
- Data tidak pernah diterbitkan otomatis. Sheet dan folder harus tetap privat; admin menelaah, memeriksa sumber/dialek, dan menyalin hanya entri yang disetujui ke alur rilis.
- Jika script belum dideploy atau URL belum diisi, tombol Drive **tidak aktif** dan penjelasan kondisi muncul. Tombol GitHub tetap berfungsi.

## Risiko dan tata kelola

- **Penerima publik bisa diserang spam.** Batas global dan honeypot bersifat mitigasi dasar, bukan perlindungan sempurna. Sebelum kampanye besar, gunakan verifikasi manusia (misalnya Google Forms yang mendukung pengaturan pengumpulan) atau backend berautentikasi/rate-limit.
- **Tidak ada lampiran atau audio**. Buat alur privat terpisah untuk rekaman suara beserta bukti persetujuan penutur.
- **Jangan masukkan token, ID akun, atau kata sandi** ke kode browser. URL Apps Script publik bukan rahasia; izin akses Drive harus berada sepenuhnya pada server.
- **Moderasi**: editor bertanggung jawab menilai status, dialek, makna, sumber, dan perizinan. Pengiriman bukan verifikasi.
- **Privasi**: formulir tidak meminta email/nama wajib, tidak otomatis menyimpan alamat IP atau mengidentifikasi penutur. Form juga tidak boleh dipakai mengirim informasi pribadi sensitif.
- **Risiko sheet**: semua isi usulan dianggap data tak tepercaya; `Code.gs` menambahkan prefiks tanda petik pada isian yang berawal tanda formula spreadsheet untuk menghindari eksekusi rumus.
- Untuk migrasi, tautan baru, atau penghentian kanal, perbarui petunjuk dan arsip audit di Google Drive.

## Referensi

- Google Apps Script Web Apps: https://developers.google.com/apps-script/guides/web
- Apps Script Deployments: https://developers.google.com/apps-script/concepts/deployments
- Halaman Kontributor: https://kamusmandailing.github.io/kontributor.html

## Panel admin dan pengambilan keputusan

- Tab **Masuk** adalah sumber usulan dan status yang dapat diubah oleh pengelola berizin.
- Tab **Panel Admin** otomatis menghitung jumlah usulan tiap status dan menampilkan usulan berstatus `MENUNGGU TELAAH`, `DALAM TELAAH`, dan `BUTUH KLARIFIKASI`. Jangan menulis data di panel; ubah status pada tab `Masuk`.
- Tab **Panduan** memuat prosedur editorial: cek dialek, ejaan, arti, sumber/izin, duplikasi, dan catatan editor.
- **DISETUJUI berbeda dari DITERBITKAN.** Status disetujui hanya berarti kandidat dapat ditelaah untuk rilis. Tidak ada API, workflow, atau Sheet yang otomatis mengubah database kamus.
- Untuk menyiapkan paket kandidat, admin mengekspor **tab Masuk sebagai CSV** ke komputer privat dan menjalankan:

```bash
python research/package_approved_contributions.py --csv "/path/pribadi/masuk.csv" --out "/path/pribadi/review-candidates.json"
```

- Program hanya mengambil baris **DISETUJUI** dengan persetujuan `YA`, lemma dan makna valid, serta sumber atau catatan editor; usulan menunggu/ditolak/tanpa persetujuan tidak boleh diekspor. Program menolak menulis file ke repository publik dan tidak menerbitkan kata.
- Peninjauan akhir dan penerbitan harus melalui perubahan versi data, PR/review oleh admin, kemudian verifikasi terbit di GitHub Pages. Jangan menandai `DITERBITKAN` sebelum rilis benar-benar berhasil.

## Diagnosis POST (belum selesai)

1. Pastikan deploy sebagai Web app `Execute as: Me` dan `Who has access: Anyone`; bukalah `/exec` dalam jendela privat untuk membuktikan `doGet` terbuka.
2. Dalam **Project Settings → Script Properties**, periksa kedua ID `KAMUS_INTAKE_FOLDER_ID` dan `KAMUS_INTAKE_SHEET_ID` dengan akun admin. Jalankan `setupOnce()` sampai sukses.
3. Buka **Executions** pada Apps Script. Filter fungsi `doPost` setelah uji. Catatan `Kamus Mandailing intake` memuat kesalahan server; jangan tampilkan informasi pribadi di log publik.
4. Uji pengiriman kata **UJI** saja, baca halaman tanda terima, lalu cek baris baru pada tab `Masuk`; hapus baris uji sesudah proses. Hanya setelah dua bukti itu ada, ubah `kamus-drive-enabled` menjadi `true`.
5. Bila script berubah, pilih **Deploy → Manage deployments → Edit → New version**; Script Properties dapat diubah tanpa mengedit kode. Periksa izin spreadsheet tetap tertutup untuk publik.

