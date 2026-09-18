# Panduan Penggunaan Kalkulator Saham dengan yfinance

## Perubahan yang Dilakukan

Program **kalkulator_saham.py** telah dimodifikasi untuk dapat mengambil data keuangan saham secara otomatis dari internet menggunakan library **yfinance**. 

### Fitur Baru:

1. **Import yfinance otomatis**
   - Program akan mendeteksi apakah yfinance terinstall
   - Jika belum, pengguna diminta install dengan `pip install yfinance`
   - Program tetap bisa digunakan tanpa yfinance (input manual)

2. **Fungsi pengambilan data**
   - `ambil_data_yfinance(ticker_symbol)` - Ambil data dari ticker saham
   - `tampilkan_data_yfinance(data)` - Tampilkan data yang diambil
   - Mendukung format ticker Indonesia: `BBCA.JK`, `ASII.JK`, `UNVR.JK`, dll

3. **Opsi input pada setiap metode**
   - Metode 1 (Graham): 3 opsi
     * Opsi 1: Input manual EPS & BVPS
     * Opsi 2: Hitung dari laba/ekuitas/saham
     * Opsi 3: Ambil dari yfinance
   
   - Metode 2 (DCF): 2 opsi
     * Opsi 1: Input manual semua data
     * Opsi 2: Ambil FCF/utang/kas/saham dari yfinance (WACC & growth manual)
   
   - Metode 3 (PE/PBV): 2 opsi
     * Opsi 1: Input manual EPS & BVPS
     * Opsi 2: Ambil dari yfinance

### Data yang Diambil dari yfinance:

- **EPS** (Earnings Per Share)
- **Book Value per Share** (BVPS)
- **Harga pasar saat ini**
- **Free Cash Flow** (FCF)
- **Total Utang** (Debt)
- **Kas & Setara Kas**
- **Jumlah saham beredar** (Shares Outstanding)

## Cara Menggunakan

### Instalasi yfinance:
```bash
pip install yfinance
```

### Menjalankan Program:
```bash
python kalkulator_saham.py
```

### Contoh Penggunaan:

**Metode Graham dengan yfinance:**
1. Jalankan program
2. Pilih menu 1 (Metode Benjamin Graham)
3. Pilih opsi 3 (Ambil dari yfinance)
4. Masukkan kode saham: `BBCA.JK` (atau `ASII.JK`, `UNVR.JK`, dll)
5. Program akan menampilkan data yang diambil dari internet
6. Masukkan harga pasar (bisa dari yfinance juga)
7. Lihat hasil perhitungan

### Format Kode Saham:

Untuk saham-saham di Bursa Efek Indonesia:
- `BBCA.JK` - Bank BCA
- `ASII.JK` - Astra International
- `UNVR.JK` - Unilever Indonesia
- `TLKM.JK` - Telkom
- `SMGR.JK` - Semen Indonesia
- Dan lainnya (format: KODE.JK)

### Struktur Perhitungan:

**Struktur perhitungan tetap sama seperti sebelumnya**, hanya berbeda pada bagian input data:
- Rumus Graham Number: akar(22,5 x EPS x BVPS)
- Rumus DCF: PV dari proyeksi arus kas + Terminal Value
- Rumus PE/PBV: EPS x PE + BVPS x PBV

### Fallback Manual:

Jika data dari yfinance tidak lengkap, program akan:
1. Menampilkan pesan error
2. Secara otomatis switch ke input manual
3. Pengguna bisa melanjutkan dengan input data manual

## Keuntungan:

✓ Tidak perlu mencari data manual di laporan keuangan/website
✓ Data selalu update dengan harga pasar terkini
✓ Hemat waktu dalam input data
✓ Struktur perhitungan tetap terjaga
✓ Masih bisa input manual jika diperlukan
✓ Backward compatible - program tetap jalan tanpa yfinance

## Catatan Penting:

- Data dari yfinance adalah trailing (12 bulan terakhir), bukan proyeksi
- Pastikan koneksi internet stabil saat mengambil data
- Beberapa saham mungkin tidak punya data lengkap di yfinance
- Hasil perhitungan tetap merupakan estimasi, bukan rekomendasi jual/beli
- Selalu verifikasi data penting dengan laporan keuangan resmi
