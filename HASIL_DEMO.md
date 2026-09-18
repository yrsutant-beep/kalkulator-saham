# Hasil Demo: Kalkulator Saham dengan yfinance

## Ringkasan

Program `kalkulator_saham.py` berhasil dijalankan dengan mengambil data otomatis dari yfinance untuk 2 saham populer Indonesia.

---

## Demo 1: BBCA.JK (Bank Central Asia)

### Data yang Diambil dari yfinance:
| Item | Nilai |
|------|-------|
| **Nama** | PT Bank Central Asia Tbk |
| **EPS** | Rp 471,81 |
| **BVPS** | Rp 2.201,51 |
| **Harga Pasar** | Rp 6.225,00 |
| **Total Utang** | Rp 52,02 T |
| **Kas & Setara** | Rp 78,02 T |
| **Saham Beredar** | 122.841.751.300 lembar |

### Hasil Perhitungan:
```
Graham Number = akar(22,5 × 471,81 × 2.201,51) = Rp 4.834,32
```

### Analisis:
| Metrik | Nilai | Kesimpulan |
|--------|-------|-----------|
| **Harga Wajar** | Rp 4.834,32 | - |
| **Harga Pasar** | Rp 6.225,00 | **OVERVALUED** |
| **Margin of Safety** | -28,77% | ❌ Negatif (harga terlalu mahal) |
| **Potensi Upside** | -22,34% | ❌ Negatif (bukan peluang) |
| **Harga Beli Ideal** | Rp 3.384,02 | (dengan 30% MOS) |
| **PER Sekarang** | 13,19x | Lebih tinggi dari nilai wajar (10,25x) |
| **PBV Sekarang** | 2,83x | Lebih tinggi dari nilai wajar (2,20x) |

**Kesimpulan:** BBCA.JK saat ini **kurang menarik** untuk dibeli karena harganya sudah jauh di atas nilai intrinsik.

---

## Demo 2: ASII.JK (Astra International)

### Data yang Diambil dari yfinance:
| Item | Nilai |
|------|-------|
| **Nama** | PT Astra International Tbk |
| **EPS** | Rp 739,90 |
| **BVPS** | Rp 5.763,22 |
| **Harga Pasar** | Rp 4.910,00 |
| **Free Cash Flow** | Rp 16,60 T |
| **Total Utang** | Rp 119,20 T |
| **Kas & Setara** | Rp 47,65 T |
| **Saham Beredar** | 39.920.061.040 lembar |

### Hasil Perhitungan:
```
Graham Number = akar(22,5 × 739,90 × 5.763,22) = Rp 9.795,13
```

### Analisis:
| Metrik | Nilai | Kesimpulan |
|--------|-------|-----------|
| **Harga Wajar** | Rp 9.795,13 | - |
| **Harga Pasar** | Rp 4.910,00 | **UNDERVALUED** |
| **Margin of Safety** | 49,87% | ✅ Positif (melebihi 30% target) |
| **Potensi Upside** | 99,49% | ✅ Potensi keuntungan 99,49% |
| **Harga Beli Ideal** | Rp 6.856,59 | (dengan 30% MOS) |
| **PER Sekarang** | 6,64x | Lebih rendah dari nilai wajar (13,24x) |
| **PBV Sekarang** | 0,85x | Lebih rendah dari nilai wajar (1,70x) |

**Kesimpulan:** ASII.JK saat ini **sangat menarik** untuk dibeli karena harganya masih jauh di bawah nilai intrinsik dengan margin of safety yang besar.

---

## Perbandingan Ringkas

### BBCA.JK vs ASII.JK

```
                BBCA.JK         ASII.JK
────────────────────────────────────────────
Graham Number   Rp 4.834        Rp 9.795
Harga Pasar     Rp 6.225        Rp 4.910
Status          OVERVALUED      UNDERVALUED
MOS             -28,77%         49,87%
Upside          -22,34%         99,49%
Rekomendasi     ❌ Jangan beli   ✅ Menarik membeli
```

---

## Keunggulan Program dengan yfinance

✅ **Otomatis & Cepat**
- Tidak perlu manual mencari data di laporan keuangan
- Cukup input kode saham (BBCA.JK)
- Program langsung ambil data dari internet

✅ **Data Selalu Update**
- Menggunakan data trailing 12 bulan terbaru
- Harga pasar real-time dari yfinance

✅ **Fleksibel**
- Bisa pilih input manual jika diperlukan
- Fallback otomatis jika data tidak lengkap
- 3 metode valuasi berbeda tersedia

✅ **Struktur Perhitungan Tetap**
- Formula Graham Number sama: akar(22,5 × EPS × BVPS)
- DCF, PE/PBV tetap seperti sebelumnya
- Transparansi penuh dalam perhitungan

---

## Cara Menjalankan

### Untuk Menjalankan Program Interaktif:
```bash
python kalkulator_saham.py
```

Lalu:
1. Pilih Metode (1, 2, atau 3)
2. Pilih Opsi Input Data (opsi 3 untuk yfinance)
3. Masukkan Kode Saham (contoh: BBCA.JK, ASII.JK)
4. Program menampilkan hasil perhitungan

### Untuk Menjalankan Demo:
```bash
python demo_bbca.py    # Demo dengan BBCA.JK
python demo_asii.py    # Demo dengan ASII.JK
```

---

## Saham-Saham yang Bisa Digunakan

Format: **KODE.JK** untuk saham di Indonesia

Contoh populer:
- `BBCA.JK` - Bank Central Asia
- `ASII.JK` - Astra International
- `UNVR.JK` - Unilever Indonesia
- `TLKM.JK` - Telkom
- `SMGR.JK` - Semen Indonesia
- `INCO.JK` - Vale Indonesia
- `ADHI.JK` - Adhi Karya
- `WSKT.JK` - Waskita Karya
- Dan ribuan saham lainnya

---

## Catatan Penting

⚠️ **Ini adalah alat bantu pembelajaran, BUKAN nasihat investasi**

- Data dari yfinance adalah **trailing** (12 bulan terakhir), bukan proyeksi
- Hasil perhitungan adalah **estimasi** berdasarkan asumsi yang dimasukkan
- **Selalu verifikasi** data penting dengan laporan keuangan resmi
- Pastikan **koneksi internet stabil** saat mengambil data
- **Jangan keputusan investasi hanya dari satu metode** - gunakan beberapa metode dan ambil rentang nilainya

---

## File-File yang Tersedia

1. **kalkulator_saham.py** - Program utama (interaktif)
2. **demo_bbca.py** - Demo otomatis untuk BBCA.JK
3. **demo_asii.py** - Demo otomatis untuk ASII.JK
4. **test_yfinance_integration.py** - Test untuk verifikasi
5. **TEST_YFINANCE.md** - Dokumentasi penggunaan
6. **CHANGELOG_YFINANCE.md** - Detail perubahan teknis

---

## Status ✅

Program berhasil dimodifikasi dan ditest:
- ✅ yfinance terintegrasi dengan baik
- ✅ Data dapat diambil otomatis dari internet
- ✅ Fallback manual tersedia jika data tidak lengkap
- ✅ Struktur perhitungan tetap terjaga
- ✅ Demo berhasil dengan 2 saham berbeda (BBCA.JK, ASII.JK)

Program siap digunakan! 🚀
