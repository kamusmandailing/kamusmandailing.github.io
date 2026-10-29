# Pendalaman kosakata dan nama tumbuhan — tahap 2

27 Oktober 2026 · Rilis 2026-10-27-DEEP02 · Skema 5

Bank bertambah dari **10.649 menjadi 10.703 bentuk unik**, dengan **99 rujukan tambahan**, sehingga kini memuat **13.571 rujukan dari 19 sumber bentuk**. Sebanyak **54 bentuk belum terdapat pada rilis sebelumnya**. Koleksi multibahasa tetap **1.404 entri**; 9.299 bentuk belum memiliki padanan multibahasa yang ditelaah. Glos sumber dan nama ilmiah tidak otomatis mengisi kolom terjemahan kurasi.

## Hasil menurut sumber

| Sumber | Rujukan tambahan | Seleksi dan batas |
| --- | ---: | --- |
| Silalahi, Purba & Mustaqim, buku botani 2018 | 17 | Hanya nama berkode MA; 16 ejaan karena pisang muncul untuk dua takson |
| Febrialisti & Nasution, pernikahan Mandailing 2022 | 43 | 36 nama tabel dan tujuh istilah kegiatan adat |
| Sakinah & Nasution, Zingiberaceae 2023 | 8 | Hanya bentuk pada lokasi yang jelas; kolom terjemahan yang meragukan ditahan |
| Hasibuan, Hasairin & Hartono, Patuaekkon 2024 | 13 | Sepuluh baris tabel dan tiga bentuk yang eksplisit pada paragraf sebelumnya |
| Silalahi & Nisyawati, pasak bumi 2015 | 1 | Ampahan gunjo dengan label Angkola–Mandailing |
| Pengantar Parinduri 2009, diterbitkan ulang 2014 | 17 | Contoh bunyi, ragam bahasa, dan akronim; bukan edisi kamus 2019 |
| **Total** | **99** | 81 ejaan dalam tambahan; 54 baru dan 27 memperkaya bentuk lama |

Sumber dan keputusan berada pada `extension_20261027b.json`, `botanical_audit_20261027.json`, dan katalog sumber. Nama ilmiah pada bank dapat ditelusuri melalui `data/nama_botani_sumber.tsv`: 75 lokasi nama–takson, termasuk frasa perlengkapan upacara. Jumlah ini bukan jumlah spesies unik.

## Bukti bahasa yang lebih spesifik

Buku *Tumbuhan Obat Sumatera Utara Jilid I: Monokotiledon* terbit Desember **2018**, menurut halaman penerbitan PDF 6. Nama berkas revisinya mengandung tahun 2019; tahun itu tidak dipakai sebagai tahun terbit buku. Penulisnya Marina Silalahi, Endang C. Purba dan Wendy A. Mustaqim; penerbit UKI Press, ISBN 978-979-8348-82-8.

Petunjuk halaman cetak 5 / PDF 15 menjelaskan kode **MA = Mandailing–Angkola**, sedangkan K, P, S dan T merujuk kelompok lain. Hanya 17 lokasi nama berkode MA yang dipilih. Nama pada uraian pemanfaatan, nama berkode kelompok lain, serta nama tanpa kode MA tidak ditambahkan dari buku ini. Halaman nama dan penjelasan kode diperiksa secara visual.

Contoh nama berkode MA ialah salin batu (Acorus calamus), pining (Areca catechu), harambir (Cocos nucifera), silinjuang (Cordyline fruticosa), honas (Ananas comosus), hasihor (Kaempferia galanga), dan pege (Zingiber officinale). Kode gabungan ini tetap ditampilkan sebagai MA, bukan diubah menjadi label Mandailing eksklusif.

## Penelitian adat dan mutu kolom nama

Penelitian pernikahan 2022 menyediakan tabel 43 baris. Enam label yang diawali kata Inggris *Banana* ditahan sebagai bahan pemeriksaan, tidak langsung dipromosikan sebagai nama Mandailing. Baris *Pohon bargot* juga tidak dijadikan bentuk Mandailing baru. Catatan itu masih dapat mendukung telaah Bargot dengan keterangan deskriptor aslinya. Dari tabel dipilih 36 bentuk, kemudian ditambah tujuh istilah adat yang eksplisit dalam uraian, antara lain manyurdu burangir, horja pabuat boru, indahan tungkus, dan gulo bargot.

PDF Zingiberaceae 2023 benar-benar mencetak beberapa kata yang meragukan di kolom nama lokal: *pedestal*, *Unique*, *Curcuma*, *Incor*, dan *the lamp*. Ini terlihat pada halaman cetak 191 / PDF 6, sehingga bukan semata-mata salah OCR. Bentuk tersebut tidak diimpor sebagai kata Mandailing. Hunik, alas, dan lampuyang diambil dari lokasi lain yang menyebutkannya secara jelas, termasuk tabel 3–4 pada halaman cetak 199 / PDF 14. Ejaan pegeh dan pegeh narara tetap mengikuti sumber; tidak diam-diam diganti menjadi pege.

Artikel Patuaekkon 2024 mempertemukan nama lokal, Indonesia dan Latin pada halaman cetak 334 / PDF 4. Perbedaan bentuk *pisang si tabar* pada tabel dan *pisang sitabar* pada paragraf tetap disimpan sesuai lokasi. Frasa *mare-mare ni pining* ditandai sebagai istilah perlengkapan upacara, bukan dianggap tambahan spesies. Glos Indonesia tertentu mengikuti tabel atau paragraf yang disebutkan, dan tetap berstatus glos sumber.

## Telaah seluruh 183 nama pembanding

Nama ilmiah pada baris yang sama kini tersimpan untuk **182 observasi**. Satu pengecualian ialah **Tampar bue**: kolom nama ilmiahnya memang kosong pada sumber 2022. Isinya tidak dipinjam dari baris sebelum atau sesudahnya.

Nama ilmiah disalin sebagaimana cetakan, termasuk singkatan genus dan kemungkinan salah eja. `taxonExpanded` hanya membantu membaca singkatan genus berdasarkan nama lengkap terdekat pada tabel; ini bukan pengesahan nomenklatur modern. Identitas dan label bahasa asli 183 observasi tidak diubah.

| Status telaah | Jumlah | Arti |
| --- | ---: | --- |
| Dukungan silang dengan bukti Mandailing sebelumnya | 2 | Tanaon dan Burangir; bukti lama dipertahankan |
| Dukungan dengan kode/cakupan gabungan MA | 11 | Nama dan takson cocok; cakupan gabungan tetap dinyatakan |
| Dukungan pada cakupan studi Mandailing | 8 | Nama–takson cocok dalam penelitian Mandailing, tanpa klaim eksklusivitas bahasa |
| Bahasa dan makna masih perlu ditelaah | 152 | Takson asal boleh tersedia, tetapi hubungan bahasanya belum terbukti |
| Risiko homonim leksikal | 1 | Langge pada kamus dan nama tumbuhan mempunyai makna berbeda |
| Identifikasi sumber masih tingkat genus | 2 | Hotang/otang dan Bulu belum otomatis menunjukkan spesies yang sama |
| Perbedaan spesies/kultivar | 1 | Pisang sitabar memerlukan pemeriksaan identitas lebih lanjut |
| Konflik takson yang nyata pada nama sama | 1 | Palaga mengacu ke Scaphium macropodum dan Amomum compactum di sumber berbeda |
| Perbedaan ejaan nama ilmiah | 2 | Hunik tindosan dan Sihala dairi tidak dikoreksi otomatis |
| Takson tidak dicantumkan sumber | 1 | Tampar bue |
| Nama di kolom lokal berbahasa Inggris | 2 | Mexican clover dan Spearmint belum menjadi bukti nama Mandailing |
| **Total** | **183** | 21 mendapat dukungan silang dengan kategori cakupan yang berbeda |

Sebutan Palaga menunjukkan alasan nama lokal tidak boleh disatukan hanya berdasarkan ejaannya. Demikian pula Bambusa sp. tidak otomatis menjadi Bambusa vulgaris, dan Calamus sp. tidak otomatis menjadi Calamus caesius. Semua perbedaan tetap dapat dilihat pada hasil telaah.

Tabel hasil per observasi tersedia pada `data/telaah_nama_tumbuhan.tsv`. Antarmuka menyediakan pencarian nama ilmiah dan filter dukungan sumber, pemeriksaan khusus, serta bahasa yang belum dipastikan. Tautan bukti silang ditampilkan bersama catatannya.

## Kemajuan dan kendala buku yang ditargetkan

- **Parinduri 2019:** isi edisi 2019 belum diperoleh. Ditemukan bagian *Sekapur Sirih* bertanggal 18 Maret 2009 yang secara eksplisit dikreditkan kepada Mhd. Bakhsan Parinduri dan diterbitkan ulang pada blog Edi Nasution pada 2014. Sebanyak 17 rujukan terpilih diberi sumber terpisah `parinduri2009`. Daftar usulan pembaca setelah bagian itu dan komentar tidak diimpor. Pratinjau pengantar tidak berarti seluruh kamus 2009 atau 2019 sudah terindeks.
- **Syahminan 2023:** PDF resmi kembali menghasilkan HTTP 503. Enam bentuk abstrak tetap dipertahankan dengan batas cakupan yang sama; penelitian Zingiberaceae 2023 adalah publikasi lain dan tidak menggantikannya.
- **Harahap 2007:** penelusuran katalog dan hubungan ABVD belum menghasilkan isi leksikal lengkap. Bank tetap hanya menyatakan 241 catatan ABVD yang sudah diperoleh.
- **Siregar 1977:** 54 rujukan tambahan pada tahap sebelumnya tetap tersimpan. Tahap ini tidak mengklaim pemeriksaan pindai baru atau transkripsi penuh.

Tidak dilakukan wawancara penutur baru. Dokumentasi tuturan dan pengetahuan masyarakat pada tahap ini berasal dari penelitian yang sudah dipublikasikan. Resep, dosis, klaim pengobatan dan data pribadi informan tidak dipindahkan ke kamus.

## Integrasi dan pemeriksaan

Skema 5 menambahkan kolom `taxon_as_printed` pada `lexical_occurrences`, serta `taxon_as_printed`, `taxon_expanded`, dan `taxon_note` pada `local_name_observations`. Tabel dan ID lama dipertahankan. `src/words.json` tetap identik dengan rilis sebelumnya. Paket JSON, SQLite, TSV, HTML luring, dan kode sumber dibangun dari data yang sama.

Uji rilis memeriksa hitungan, stabilitas ID, blanko terjemahan, sumber dan label per rujukan, seluruh status telaah, takson yang kosong, konflik Palaga, pengecualian label Inggris yang meragukan, filter serta ekspor antarmuka, dan integritas SQLite. Hasil aktual tersedia pada `coverage_audit.json`. Teks atau metadata sumber yang tidak tersedia tidak direka untuk memenuhi target jumlah.

## Rujukan utama tahap 2

- Buku botani 2018: https://repository.uki.ac.id/648/1/Jilid%20I_revised%2008-01-2019.pdf
- Pernikahan Mandailing 2022: https://jurnal.unimed.ac.id/2012/index.php/biosains/article/view/36497
- Zingiberaceae 2023: https://jurnal.unimed.ac.id/2012/index.php/biosains/article/view/39061
- Patuaekkon 2024: https://jurnal.kopusindo.com/index.php/jpst/article/download/407/424
- Pasak bumi 2015: https://doi.org/10.13057/psnmbi/m010410
- Pengantar Parinduri 2009/2014: https://gondang.blogspot.com/2014_08_11_archive.html
- Tabel Tanjung Julu 2022: https://journal.uinjkt.ac.id/kauniyah/article/download/17958/pdf/81362
- Tabel Lubuk Barumun 2026: https://journal.ipm2kpe.or.id/index.php/BIOEDUSAINS/article/download/19050/12173

Rilis ini memperluas bukti dan keterlacakan, bukan menetapkan jumlah maksimal kosakata Mandailing atau menyatakan semua bahan sudah selesai ditelaah.
