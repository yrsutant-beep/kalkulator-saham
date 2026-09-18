# Changelog: Integrasi yfinance pada Kalkulator Saham

## Ringkasan Perubahan

File `kalkulator_saham.py` telah dimodifikasi untuk mengintegrasikan library **yfinance** guna mengambil data keuangan saham secara otomatis dari internet. Perubahan ini **tidak mengubah struktur perhitungan** yang sudah ada, hanya menambah kemudahan dalam input data.

---

## Perubahan Detail

### 1. **Import dan Inisialisasi yfinance** (Baris 18-22)

```python
try:
    import yfinance as yf
except ImportError:
    yf = None
```

- Program akan mencoba mengimport yfinance
- Jika tidak terinstall, `yf` akan bernilai `None` dan program tetap bisa berjalan
- Program akan mendeteksi dan memberi tahu pengguna saat startup

### 2. **Fungsi Baru: `ambil_data_yfinance()`** (Baris 43-74)

Mengambil data keuangan dari yfinance berdasarkan ticker symbol:

```python
def ambil_data_yfinance(ticker_symbol):
    """Ambil data keuangan dari yfinance."""
```

Data yang diambil:
- EPS (Earnings Per Share) - `trailingEps`
- Book Value per Share - `bookValue`
- Harga pasar saat ini - `currentPrice`
- Free Cash Flow - `freeCashflow`
- Total Utang - `totalDebt`
- Kas & Setara Kas - `totalCash`
- Saham Beredar - `sharesOutstanding`

### 3. **Fungsi Baru: `tampilkan_data_yfinance()`** (Baris 77-96)

Menampilkan data yang diambil dari yfinance dengan format yang konsisten dengan program.

### 4. **Modifikasi `metode_graham()`** (Baris 276-325)

**Sebelum:**
- 2 opsi: input manual EPS/BVPS atau hitung dari laba/ekuitas

**Sesudah:**
- 3 opsi:
  1. Input langsung EPS & BVPS (manual)
  2. Hitung dari laba / ekuitas / saham beredar (manual)
  3. **[BARU]** Ambil data otomatis dari yfinance

Kode baru:
```python
elif cara == "3":  # ambil dari yfinance
    ticker = input("  Kode saham (contoh: BBCA.JK, ASII.JK): ").strip().upper()
    data_yf = ambil_data_yfinance(ticker)
    
    if not data_yf or data_yf.get('eps') is None or data_yf.get('book_value') is None:
        # Fallback ke input manual jika data tidak lengkap
        print(f"\n  ! Data tidak lengkap dari yfinance untuk {ticker}.")
        print("  Lanjut dengan input manual.")
        eps = minta_float("EPS - laba per lembar saham (Rp)")
        bvps = minta_float("BVPS - nilai buku per lembar saham (Rp)")
    else:
        # Gunakan data dari yfinance
        tampilkan_data_yfinance(data_yf)
        eps = data_yf['eps']
        bvps = data_yf['book_value']
```

### 5. **Modifikasi `metode_dcf()`** (Baris 335-384)

**Perubahan:**
- Menambah opsi untuk mengambil FCF, utang, kas, dan saham beredar dari yfinance
- WACC dan growth rate tetap input manual (karena bersifat asumsi/proyeksi)

Kode baru:
```python
if cara == "2":  # ambil dari yfinance
    ticker = input("  Kode saham (contoh: BBCA.JK, ASII.JK): ").strip().upper()
    data_yf = ambil_data_yfinance(ticker)
    ...
    if data_yf and data_yf.get('fcf'):
        fcf0 = data_yf['fcf'] / pengali
        print(f"  Free Cash Flow (dari yfinance): {fmt(fcf0)} {nama_satuan}")
    # (sama untuk utang, kas, saham)
```

### 6. **Modifikasi `metode_pe_pbv()`** (Baris 445-480)

**Perubahan:**
- Menambah opsi untuk mengambil EPS dan BVPS dari yfinance
- PE dan PBV acuan tetap input manual (karena merupakan asumsi/target)

### 7. **Update `main()` - Pesan Sambutan** (Baris 681-692)

Menambahkan pesan informasi saat startup:

```python
if yf is None:
    print("\n⚠ CATATAN: yfinance tidak terinstall.")
    print("  Untuk menggunakan fitur pengambilan data otomatis dari internet,")
    print("  jalankan: pip install yfinance")
    print("  Anda masih bisa menggunakan kalkulator dengan input manual.")
else:
    print("\n✓ yfinance tersedia. Anda bisa memilih mengambil data dari internet")
```

---

## Fitur Keamanan & Fallback

1. **Error Handling**: Jika yfinance tidak terinstall, program tetap berjalan
2. **Data Validation**: Jika data dari yfinance tidak lengkap, otomatis switch ke input manual
3. **Backward Compatibility**: Semua opsi manual masih tersedia

---

## Testing

Test file `test_yfinance_integration.py` telah dibuat untuk memverifikasi:
- ✓ Pengambilan data dari yfinance bekerja
- ✓ Data EPS, Book Value, Harga pasar dapat diakses
- ✓ Simulasi Graham Number dengan data yfinance berfungsi
- ✓ Fallback ke input manual bekerja jika data tidak lengkap

Hasil test:
```
BBCA.JK: EPS ✓, Book Value ✓, Harga pasar ✓
ASII.JK: EPS ✓, Book Value ✓, Harga pasar ✓, FCF ✓
UNVR.JK: EPS ✓, Book Value ✓, Harga pasar ✓, FCF ✓
```

---

## Struktur Perhitungan

**TIDAK ADA PERUBAHAN** pada struktur perhitungan:
- Graham Number: akar(22,5 × EPS × BVPS) — tetap sama
- DCF: proyeksi FCF + Terminal Value — tetap sama
- PE/PBV: EPS × PE + BVPS × PBV — tetap sama

---

## File-file yang Dimodifikasi

1. **kalkulator_saham.py** - File utama dengan integrasi yfinance
2. **TEST_YFINANCE.md** - Dokumentasi panduan penggunaan
3. **test_yfinance_integration.py** - Test script untuk verifikasi
4. **CHANGELOG_YFINANCE.md** - File ini (dokumentasi perubahan)

---

## Cara Menggunakan

### Instalasi:
```bash
pip install yfinance
python kalkulator_saham.py
```

### Di program:
1. Pilih metode (1, 2, atau 3)
2. Pilih opsi input data
3. Jika memilih yfinance, masukkan kode saham (contoh: BBCA.JK)
4. Program akan menampilkan data dan melanjutkan perhitungan

---

## Contoh Format Ticker

Saham-saham Indonesia yang bisa digunakan:
- `BBCA.JK` - Bank Central Asia
- `ASII.JK` - Astra International
- `UNVR.JK` - Unilever Indonesia
- `TLKM.JK` - Telkom
- `SMGR.JK` - Semen Indonesia
- `INCO.JK` - Vale Indonesia
- Dan ribuan saham lainnya dengan format: **KODE.JK**

---

## Catatan Penting

- Data dari yfinance adalah **trailing** (12 bulan terakhir), bukan proyeksi
- Untuk DCF, WACC dan growth rate tetap harus input manual (asumsi pribadi)
- Hasil tetap merupakan **estimasi**, bukan rekomendasi jual/beli
- Pastikan **koneksi internet** stabil saat mengambil data
- Verifikasi data penting dengan laporan keuangan resmi sebelum keputusan investasi

---

## Status

✅ **SELESAI** - Integrasi yfinance berhasil diimplementasikan
✅ Struktur perhitungan tetap terjaga
✅ Backward compatibility terjaga
✅ Test sukses untuk 3 saham berbeda
