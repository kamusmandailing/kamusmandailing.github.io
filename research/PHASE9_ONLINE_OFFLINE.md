# Tahap 9 — Versi Online Ringan + HTML Offline Mandiri

**Tanggal:** 1 November 2026  
**Situs:** https://kamusmandailing.github.io/online.html  
**Versi lengkap:** https://kamusmandailing.github.io/  
**Sumber kanonis:** `src/words.json`, `src/inventory.json`, `src/sources.json`, `research/release_snapshot.json`.

## Implementasi

- Halaman `online.html` dibangun dari `src/online.html`, `src/online.css`, `src/online.js` oleh `build.py`. Dari awal, halaman menyertakan **1.404 entri berpadanan**, judul sumber, dan snapshot angka rilis.
- Inventaris **10.821 bentuk / 13.745 rujukan** berada di `data/bank-online.json` dan baru diambil lewat `fetch()` ketika tab **Bank Kosakata** dibuka. Bank memuat 9.417 bentuk belum berpadanan yang **tetap kosong**, bukan ditambahkan arti rekaan.
- Filter Bank: istilah, induk, glos, takson, kategori bentuk, label/cakupan sumber, sumber tertentu, padanan tersedia/belum, glos sumber. Ekspor TSV 5 kolom dan TSV berlabel tetap tersedia untuk hasil filter.
- Saat pengambilan Bank gagal, status tampil di area `aria-live`, tersedia tombol **Coba lagi** dan tautan ke berkas offline lengkap. Tombol pemilihan mode tetap bisa digunakan.
- `index.html` dan `Hata_Kamus_Mandailing.html` tetap hasil build **satu berkas mandiri**, dengan pencarian, fitur Belajar, koleksi pribadi, sumber, dan ekspor sebelumnya. Halaman lengkap menautkan ke versi ringan sebagai pilihan, bukan dipindahkan secara paksa.
- Semua file hasil build berasal dari **satu sumber data kanonis**, bukan dump publik lain atau salinan Google Sheets kontribusi privat. Tidak ada kata baru, terjemahan otomatis, atau penerbitan tanpa editor.

## Audit dan bukti

Pengujian: https://github.com/kamusmandailing/kamusmandailing.github.io/actions/workflows/validate-phase9-online.yml

| Ukuran/kontrol | Hasil |
| --- | ---: |
| HTML lengkap mentah | 8.650.494 byte |
| HTML online ringan mentah | 907.063 byte |
| HTML online ringan dengan gzip | 67.210 byte |
| Pengurangan ukuran HTML awal (bukan total transfer Bank) | **89,5%** |
| Berkas Bank terpisah | 7.587.993 byte mentah |
| Entri berpadanan | 1.404 |
| Bentuk sumber | 10.821 |
| Rujukan sumber | 13.745 |
| Bentuk belum berpadanan | 9.417 |
| Pemeriksaan integritas historis | 67 lulus |

Tes `research/test_phase9_online.py` membandingkan seluruh JSON Bank online dengan `src/inventory.json` dan data yang disisipkan pada HTML offline; membandingkan semua ID, bentuk, sumber, dan padanan yang sama melalui objek penuh. Tes browser headless memeriksa halaman awal, pencarian berpadanan, pemuatan Bank setelah klik, padanan status, istilah takson `Piper betle`/`simanat`, filter sumber terikat, dialog bukti, dan penanganan kegagalan jaringan.

**Penafsiran ukuran:** 89,5% adalah pengurangan *HTML awal mentah*, bukan persentase penghematan total data jika Bank telah dibuka. Bila Bank dikunjungi, berkas inventaris terpisah diunduh. Tidak ada pengukuran LCP/INP pada ponsel fisik atau koneksi lambat; hasil Chrome headless hanyalah tes kesetaraan dan respons tampilan.

## Batasan dan rencana berikutnya

- `online.html` adalah **mode ringan berfokus pencarian**; halaman lengkap tetap menyediakan Belajar, simpan kata pribadi, dan materi rinci. Jangan mengklaim kedua UI sama fitur demi fitur—**data kanonis dan hasil pencarian/filter dasar** yang dijaga.
- Belum ada verifikasi NVDA/VoiceOver dengan pengguna pada perangkat fisik.
- Belum mengukur Core Web Vitals pengguna nyata, konsumsi memori, dan waktu pencarian pertama pada ponsel lambat.
- Endpoint Google Drive untuk usulan publik belum lulus verifikasi POST ke antrean privat; jangan mengaktifkan tombol secara prematur.
- Proteksi persetujuan admin di GitHub dan pilot penelaahan 40 entri masih tertunda.

**Rollback:** tautan versi ringan dapat disembunyikan dari `src/index.html` tanpa menghilangkan `index.html` atau `Hata_Kamus_Mandailing.html`. Dua produk rilis dibuat lewat `python build.py` dan diverifikasi CI terpisah.
