# PILOT-40 — lembar penelaahan penutur / editor

Tahap pengembangan kamus keseluruhan: sampel 40 entri **yang sudah memiliki padanan editorial**. Sampel dipilih secara deterministik, merata melalui huruf awal dan kategori agar berguna untuk audit; **bukan** pembuktian sudah disahkan masyarakat.

## Penggunaan
1. Jalankan `python research/select_editorial_pilot.py --out /path/privat/pilot_40.tsv`, atau unduh artefak workflow GitHub `Generate 40-entry editorial pilot`.
2. Simpan TSV di ruang telaah editor berizin di Google Drive (boleh import ke Google Sheets untuk penelaahan; jangan mempublikasikan nama penutur).
3. Untuk tiap baris, cek **makna, kelas kata/kategori, variasi ejaan dan dialek, bukti pada sumber asli, kewajaran padanan ID/MS/EN, serta status contoh kalimat**.
4. Gunakan kolom `status_keputusan`: `BELUM DITELAAH`, `DISETUJUI`, `PERLU BUKTI`, atau `DITOLAK`; catat alasan dan tanggal, serta cakupan wilayah yang disepakati tanpa menyebut data pribadi.
5. Minimal dua penelaah jika mungkin, termasuk penutur kompeten yang mengizinkan penggunaan data. Pertahankan perbedaan pendapat dan jangan menambah IPA, contoh, atau etimologi tanpa sumber.
6. Pengesahan per entri tidak otomatis mengubah `src/words.json` atau website. Rilis hanya melalui PR/review dan persetujuan administrator.

## Definisi penting
- `source_attested` berarti bentuk memiliki rujukan sumber; bukan berarti semua padanan sudah disahkan penutur.
- `Mdl` adalah label langsung sumber pada bentuk; `unmarked` berasal dari kamus gabungan Angkola–Mandailing; `Tapsel` tidak otomatis berarti Mandailing eksklusif.
- Angka 40 hanya **volume sampel** untuk diperiksa; jumlah disetujui bergantung bukti, tidak dipaksakan.
- Status contoh `pending` tidak boleh diganti dengan kalimat rekaan.

## Gerbang selesai pilot
- 40 baris diperiksa dan diberi keputusan, termasuk yang ditolak/ditunda.
- Catatan sumber/halaman dan cakupan dialek disimpan.
- Tiap keputusan linguistik disetujui editor/penutur berizin.
- Tidak ada nama lengkap informan atau data pribadi yang disebarkan melalui repo.
