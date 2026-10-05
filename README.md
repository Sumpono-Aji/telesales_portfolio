# Telesales CRM Portfolio

Aplikasi CRM terminal sederhana untuk mendemonstrasikan alur kerja telesales menggunakan Python dan SQLite. Cocok sebagai project portofolio personal.

## Fitur
- Menyimpan data prospek (nama, telepon, perusahaan, sumber, status, catatan).
- Mencatat aktivitas telepon, hasil panggilan, durasi, dan catatan percakapan.
- Menjadwalkan dan memantau follow-up jatuh tempo.
- Dashboard: total prospek, aktivitas call, connect rate, conversion rate, rata-rata durasi.
- Melihat profil dan riwayat interaksi tiap prospek.
- Memperbarui status prospek dan ekspor rekap ke CSV.
- Database lokal SQLite, otomatis dibuat saat aplikasi pertama kali dijalankan.

## Kebutuhan
- Python 3.9 atau lebih baru
- Tidak membutuhkan instalasi package tambahan.

## Cara menjalankan
1. Ekstrak ZIP project.
2. Buka terminal / Command Prompt di folder project.
3. Jalankan `python app.py` (Windows dapat menggunakan `py app.py`).
4. Pilih menu `9` untuk memasukkan data demo, lalu gunakan menu lainnya.

## Struktur
- `app.py` — kode aplikasi utama.
- `README.md` — panduan penggunaan.
- `telesales.db` — dibuat otomatis saat aplikasi berjalan.
- `telesales_report.csv` — dibuat saat ekspor laporan.

## Alur demo portofolio
1. Jalankan aplikasi dan masukkan data demo.
2. Buka dashboard untuk melihat metrik awal.
3. Lihat prospek dan riwayat panggilan.
4. Tambahkan prospek baru dan catat hasil call.
5. Buka menu follow-up dan ekspor laporan CSV.

## Catatan metrik
Connect rate pada demo didefinisikan sebagai jumlah outcome selain `No Answer` dibagi total aktivitas panggilan. Definisi ini dapat disesuaikan dengan SOP perusahaan. Conversion rate dihitung dari jumlah prospek berstatus `Converted` dibagi seluruh prospek.

## Pengembangan lanjutan
Untuk versi berikutnya, aplikasi dapat dikembangkan menjadi dashboard web (Streamlit/Flask), login multi-user, filter periode, target harian, dan visualisasi tren.
