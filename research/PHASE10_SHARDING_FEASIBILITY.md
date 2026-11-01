# Evaluasi Pemecahan Berkas Bank Kosakata

**Tanggal:** 1 November 2026  
**Dasar:** tindak lanjut yang dicatat pada laporan Tahap 9  
**Sumber data:** `src/inventory.json`, dibandingkan dengan `data/bank-online.json`

## Ringkasan

Pemecahan berkas dapat mempercepat tampilan daftar Bank pertama, tetapi tidak mengurangi ukuran total Bank secara berarti. Pencarian saat ini mencakup bentuk, induk, glos sumber, takson, dan padanan editorial. Karena kecocokan dapat muncul pada bentuk dengan huruf awal berbeda, pencarian, filter, dan ekspor harus menunggu semua berkas terkait atau memakai indeks pencarian lengkap. Hasil parsial tidak boleh ditampilkan sebagai hasil lengkap.

## Metode

Skrip `research/benchmark_bank_shards.py` membaca inventaris kanonis, memastikan salinan rilis sama, lalu mengukur serialisasi kandidat dan gzip deterministik Python level 9. Kandidat huruf awal mengelompokkan bentuk berdasarkan huruf pertama ternormalisasi. Kandidat berurutan membagi daftar kanonis menjadi potongan 128, 256, 512, atau 1.024 bentuk; urutan rekaman di dalam potongan dipertahankan. Manifest kandidat mempertahankan seluruh metadata tingkat atas selain daftar bentuk, serta jumlah bentuk per potongan.

Angka gzip ini untuk membandingkan kandidat lokal, bukan ukuran transfer nyata dari GitHub Pages. Tidak ada simulasi RTT, jaringan 3G/4G, konsumsi RAM ponsel, atau pengukuran LCP/INP/TBT.

## Hasil

| Ukuran | Hasil |
| --- | ---: |
| Bentuk kanonis | 10.821 |
| Bank penuh mentah | 7.587.993 byte |
| Bank penuh gzip lokal | 599.063 byte |
| Manifest lengkap | 185.189 byte mentah |
| Total semua potongan gzip + manifest, ukuran potongan 128 | 673.843 byte |
| Total semua potongan gzip + manifest, ukuran potongan 256 | 636.441 byte |
| Total semua potongan gzip + manifest, ukuran potongan 512 | 618.550 byte |
| Total semua potongan gzip + manifest, ukuran potongan 1.024 | 608.275 byte |

| Bentuk per potongan berurutan | Jumlah berkas | Unduhan awal + manifest mentah | Gzip lokal awal | Gzip seluruh Bank |
| ---: | ---: | ---: | ---: | ---: |
| 128 | 85 | 283.575 byte | 25.644 byte | 673.843 byte |
| 256 | 43 | 380.081 byte | 33.549 byte | 636.441 byte |
| 512 | 22 | 581.021 byte | 48.681 byte | 618.550 byte |
| 1.024 | 11 | 947.568 byte | 76.545 byte | 608.275 byte |

Daftar pertama 24 bentuk berada di potongan berurutan pertama. Kandidat 128 bentuk mengunduh 128 bentuk beserta manifest sekitar 25,6 KB gzip lokal—sekitar 4,3% dari gzip Bank penuh. Semua potongan 128 bentuk bersama-sama sekitar 12,5% lebih besar daripada satu berkas gzip karena setiap berkas dikompresi terpisah. Potongan 512 bentuk mengurangi biaya itu menjadi sekitar 3,2%, dengan unduhan awal sekitar 48,7 KB gzip.

Sebagai pembanding, pembagian menurut huruf awal menghasilkan 22 berkas; huruf `a` sendiri berisi 963 bentuk. Untuk menampilkan 24 bentuk pertama, pendekatan itu membutuhkan sekitar 72,6 KB gzip bersama manifest. Pembagian berdasarkan urutan daftar kanonis lebih cocok untuk paginasi karena menjaga urutan data tanpa pengurutan ulang.

Kecocokan pencarian contoh melintasi beberapa potongan: `Piper betle` pada huruf `b` dan `s`; `fish` pada delapan huruf awal. Karena itu, pencarian teks yang tampak sederhana dapat kehilangan hasil bila hanya potongan awal yang sudah dimuat.

## Prototipe Tahap 10

Cabang lokal ini memakai potongan berurutan **512 bentuk** sebagai kompromi awal. `build.py` menghasilkan manifest dan 22 berkas potongan ber-checksum SHA-256 dari inventaris kanonis; `data/bank-online.json` tetap dibuat sebagai keluaran kompatibilitas dan pembanding. Saat Bank dibuka, halaman mengambil manifest dan potongan pertama. Paginasi mengambil potongan yang dibutuhkan; pencarian, filter global, dan kedua jenis ekspor mengambil semua potongan sebelum memberi hasil.

Build aktif tersebut menghasilkan manifest 188.703 byte dan potongan pertama 395.832 byte; bersama-sama 584.535 byte mentah / 50.097 byte gzip lokal (gzip terpisah per berkas). Seluruh manifest dan 22 potongan berjumlah 7.588.403 byte mentah / 619.968 byte gzip lokal. Angka ini mengukur keluaran prototipe sebenarnya. Tabel di atas tetap merupakan perbandingan kandidat kompak dan dapat berbeda karena skema manifest kandidat lebih kecil.

Uji lokal merekonstruksi manifest dan semua potongan menjadi `src/inventory.json` secara identik. Chromium lulus pada 1280×900 dan viewport 390×844 untuk pemuatan hanya manifest+potongan pertama, anggaran awal di bawah 600 KB mentah, paginasi sampai potongan kedua, pencarian global, filter 9.417 bentuk belum berpadanan, ekspor TSV kurasi dan kedua TSV Bank lengkap, fokus dialog, serta kegagalan manifest dan potongan berikutnya dengan retry/jalur offline. Validasi rilis lulus 67 pemeriksaan; pemeriksaan Bank lama dan audit HTML offline mandiri juga lulus.

Ukuran potongan dibandingkan ulang melalui `BANK_CHUNK_SIZE=<ukuran> python3 build.py` dan `node research/test_mobile_network.cjs`; tanpa variabel itu, ukuran bawaan tetap 512 dan dipakai oleh CI. Semua kandidat memakai profil Chrome DevTools yang sama: viewport 390×844, jaringan 400 kbps, RTT 150 ms, CPU 4× lebih lambat, dan cache dimatikan. Angka byte adalah `encodedBodySize` respons, tidak termasuk header HTTP; waktu adalah satu kali jalan per kandidat.

| Bentuk per potongan | Potongan | Muatan Bank pertama | Waktu Bank pertama | Waktu pencarian lengkap | Total byte terenkode |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 256 | 43 | 36.003 byte | 1,13 dtk | 12,94 dtk | 635.515 byte |
| 512 | 22 | 49.906 byte | 1,38 dtk | 11,91 dtk | 616.319 byte |
| 1.024 | 11 | 76.978 byte | 1,97 dtk | 10,97 dtk | 605.346 byte |

Satu kali pengukuran per ukuran menunjukkan pilihan 512 sebagai kompromi: 256 menghemat sekitar 0,25 detik saat Bank pertama dibuka tetapi menambah sekitar 19 KB dan satu detik pada pencarian penuh; 1.024 mempercepat pencarian penuh sekitar 0,94 detik tetapi menambah sekitar 27 KB dan 0,59 detik pada Bank pertama. Ini hasil emulasi desktop satu profil sintetis, bukan pengukuran ponsel atau GitHub Pages. Workflow CI menguji ukuran bawaan 512 dan menyimpan JSON hasil simulasi sebagai artefak.

**Batas simulasi:** HTML offline mandiri dan inventaris kamus tetap tidak berubah. Profil desktop memberi RTT dan batas kecepatan, tetapi tidak mengukur konsumsi memori, Core Web Vitals lapangan, atau aksesibilitas NVDA/VoiceOver pada ponsel. Uji smoke iPhone dilakukan setelah prototipe ini; rinciannya ada di bawah.

## Smoke test iPhone, 1 November 2026

Saya membuka build lokal di Chrome pada iPhone melalui server HTTP sementara di jaringan Wi-Fi yang sama. Halaman awal menampilkan 1.404 entri berpadanan. Setelah Bank dibuka, perangkat menerima manifest dan hanya `chunk-000.json`; daftar menyatakan 512 bentuk dimuat dari 10.821. Pencarian `poda` meminta semua 22 potongan, seluruh permintaan mendapat HTTP 200, dan hasil menampilkan 12 bentuk yang cocok dari 10.821. Nilai data, arti, label, atau rujukan tidak diubah.

Saat kolom pencarian difokuskan pada uji pertama, Chrome memperbesar halaman karena ukuran teks kontrol 12 px. CSS seluler sekarang memakai 16 px untuk input dan select Bank, dan tes browser memeriksa ukuran tersebut pada viewport 390×844. Pengulangan di iPhone mempertahankan lebar halaman dan pencarian tetap menampilkan 12 hasil tanpa pembesaran otomatis. Server lokal dihentikan setelah uji.

Ini smoke test fungsi dan tampilan, bukan pengukuran performa lapangan: saya tidak mengukur LCP/INP/TBT, penggunaan memori, jaringan 3G/4G, Safari, atau teknologi bantu VoiceOver. Karena itu klaim performa CI tetap simulasi desktop dan persoalan aksesibilitas pembaca layar masih terbuka.

**Status tinjauan:** implementasi ada pada draft PR #11, belum tayang; kode kamus offline mandiri dan inventaris kanonis tetap tidak berubah. Persetujuan editor untuk mengubah draft menjadi siap ditinjau atau menggabungkannya masih diperlukan.
