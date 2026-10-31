# Integrasi Halaman Kontributor → Google Drive

## Tujuan

Mengumpulkan usulan dari `kontributor.html` ke **Google Sheet privat** bernama `Kamus Mandailing — Antrean Usulan Kontributor` di dalam folder `Kontribusi Komunitas - Masuk dan Telaah` pada folder proyek Kamus Mandailing. Kontributor tidak mendapat akses tulis maupun baca ke Drive atau repository. Semua catatan baru berstatus **MENUNGGU TELAAH**.

**Status setelah commit ini:** kode backend disiapkan tetapi belum dideploy di Google Apps Script, dan pengiriman dari website belum aktif hingga administrator mengonfigurasi URL web app. GitHub Issues tetap tersedia sebagai saluran aktif. Jangan menyatakan usulan sudah tersimpan ke Drive sebelum tab tanda terima dari Apps Script menunjukkan sukses.

## Konfigurasi satu kali oleh administrator Google

1. Buka https://script.google.com/home/projects/create menggunakan **akun Google yang memiliki akses editor/owner** ke folder kontribusi Kamus Mandailing. Jangan menggunakan akun kontributor umum.
2. Beri nama proyek `Penerima Usulan Kamus Mandailing`.
3. Salin seluruh isi `Code.gs` dari direktori ini ke file `Code.gs` proyek tersebut. Simpan.
4. Buka **Project Settings → Script properties**, buat:
   - `KAMUS_INTAKE_FOLDER_ID` = ID folder privat **Kontribusi Komunitas - Masuk dan Telaah**. Cari ID folder pada arsip admin Google Drive, jangan memublikasikannya ke halaman.
5. Di editor Apps Script pilih fungsi `setupOnce`, klik **Run**, lalu izinkan akses yang diperlukan. Fungsi ini membuat sebuah Google Sheet `Kamus Mandailing — Antrean Usulan Kontributor` di folder privat tersebut, dengan tab `Masuk` dan kolom ID, waktu, status, jenis, kata, makna, wilayah, padanan, contoh, sumber, izin, asal, catatan editor. Pemanggilan ulang memeriksa header dan tidak menghapus isi.
6. Pastikan Sheet benar-benar berada pada folder privat dan hanya akun yang diizinkan memiliki hak lihat/edit. Jangan publikasikan Sheet atau folder sebagai `Anyone with the link`.
7. Di Apps Script pilih **Deploy → New deployment → Web app**. Set **Execute as: Me** (akun pemilik script), **Who has access: Anyone** (apabila publik tanpa login diizinkan oleh kebijakan akun). Lakukan deployment, kemudian salin URL yang berakhiran **/exec**.
8. Tambahkan URL tersebut sebagai nilai konten `<meta name="kamus-drive-endpoint" content="...">` pada `kontributor.html` (tanpa token OAuth; URL web app bersifat publik). Setelah commit ke `main`, halaman otomatis mengaktifkan tombol **Kirim langsung ke Google Drive**.
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
