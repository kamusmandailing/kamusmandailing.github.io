# Panduan Kontributor Komunitas — Kamus Mandailing (Hata)

Terima kasih telah membantu mendokumentasikan bahasa Mandailing. Anda dapat ikut berkontribusi sebagai penutur, perantau, peneliti, pengajar, atau pemerhati budaya.

## Mengajukan kontribusi

1. Buka halaman [Kontributor Kamus Mandailing](https://kamusmandailing.github.io/kontributor.html).
2. Pilih jenis kontribusi: kosakata baru, koreksi ejaan/makna, variasi tutur, contoh kalimat, istilah budaya, atau sumber tertulis.
3. Isi bentuk kata, makna, dan bukti secukupnya. Tandai wilayah tutur secara umum, bila relevan.
4. Klik **Lanjutkan ke GitHub**, masuk ke akun GitHub, periksa isinya, lalu kirim laporan. Alternatifnya gunakan [formulir GitHub langsung](https://github.com/kamusmandailing/kamusmandailing.github.io/issues/new?template=01-kontribusi-kosakata.yml).
5. Ikuti diskusi pada GitHub Issue apabila editor meminta klarifikasi.

**Jalur GitHub sudah aktif.** Data isian diteruskan ke halaman penyusunan GitHub Issue melalui tautan saat Anda memilih GitHub; usulan menjadi publik jika Anda mengirimnya di GitHub. **Jalur Google Drive sedang dipersiapkan**: setelah administrator mengaktifkan penerima Apps Script, pengunjung dapat mengirim melalui POST standar ke antrean privat Google Drive. Sampai aktivasi tersebut, tombol Drive dinonaktifkan dan belum ada pengiriman otomatis ke Drive.

## Ketentuan data dan izin

- Tuliskan bentuk yang benar-benar diketahui, jangan menduga atau menciptakan kutipan penutur.
- Sebutkan bahasa padanan dan sumber/halaman apabila tersedia.
- Hindari mencantumkan nomor telepon, alamat pribadi, nama lengkap informan, atau materi sensitif dalam GitHub Issue.
- Jangan unggah rekaman atau potret orang tanpa izin yang layak.
- Jangan salin isi buku atau sumber berhak cipta secara massal; utamakan rujukan dan pengutipan secukupnya.
- Jika mengusulkan klaim tentang dialek/desa, beri konteks dan bukti; bahasa berbeda tidak otomatis dianggap salah.
- Pengakuan kredit dapat mengikuti akun GitHub atau preferensi yang disampaikan secara sukarela. Nama informan tidak otomatis diterbitkan.

## Tahap editorial

| Tahap | Penanggung jawab | Hasil |
| --- | --- | --- |
| Usulan | Kontributor publik | GitHub Issue — belum diverifikasi |
| Triase awal | Editor/pengelola | Periksa duplikasi dan kelengkapan |
| Pemeriksaan | Editor/penutur/sumber | Koreksi, bukti, status dialek |
| Keputusan | Admin atau editor berizin | Terima, tunda, minta klarifikasi, atau tolak |
| Penerbitan | Admin/repositori berizin | Rilis website/database melalui alur review |
| Jejak perubahan | GitHub | Issue terkait commit atau PR, jika diterima |

Mengirim GitHub Issue **tidak** memberikan hak tulis ke repository. Hak menulis dan menerbitkan hanya diberikan oleh admin. Berkas [CODEOWNERS](.github/CODEOWNERS) menetapkan pengelola kode, tetapi aturan branch protection terpisah masih harus diaktifkan oleh admin agar persetujuan menjadi wajib.

## Cara pelapor memantau

- Buka [daftar usulan](https://github.com/kamusmandailing/kamusmandailing.github.io/issues).
- Lihat status, balasan editor, dan rujukan bukti pada Issue terkait.
- Status "diterima untuk ditelaah" **bukan** berarti padanan telah terverifikasi atau masuk database.
- Jika diputuskan diterbitkan, pengelola dapat menautkan Issue ke PR/commit dan rilis terkait.

## Rencana pengembangan berikutnya

Tahap awal menggunakan GitHub Issues yang memerlukan akun GitHub. Jalur tanpa akun GitHub disiapkan melalui Google Apps Script yang menyimpan usulan pada Sheet privat di folder Drive proyek; **jalur itu belum aktif sebelum deployment dan uji administrator**. Panduan internal ada di [integrations/google-drive-intake/README.md](integrations/google-drive-intake/README.md). Rekaman suara, dashboard reviewer dan ekspor leksikografi memerlukan tata kelola tambahan sebelum diaktifkan.

Perubahan prosedur akan dicatat dan diuji tanpa menghilangkan jejak sumber.
