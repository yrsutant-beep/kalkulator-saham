# Demo DCF ASII.JK - Ringkasan Hasil

## 📊 Hasil Valuasi DCF

**Harga Wajar per Lembar (DCF): Rp 7.078,26**

```
Perbandingan dengan Harga Pasar:
┌─────────────────────┬──────────────┐
│ Harga Pasar         │ Rp 4.910,00  │
│ Harga Wajar (DCF)   │ Rp 7.078,26  │
│ Selisih             │ Rp 2.168,26  │
│ Persentase          │ +44,16%      │
│ Margin of Safety    │ 30,63%  ✅   │
├─────────────────────┼──────────────┤
│ Harga Beli Ideal    │ Rp 4.954,78  │
│ (MOS 30%)           │ (hampir sama)│
└─────────────────────┴──────────────┘
```

---

## 💰 Komponen Nilai dalam DCF

### Proyeksi 5 Tahun

| Tahun | FCF Proyeksi | Faktor Diskon | Present Value |
|-------|--------------|---------------|---------------|
| 1 | Rp 17,60 T | 0,9217 | Rp 16,22 T |
| 2 | Rp 18,65 T | 0,8495 | Rp 15,84 T |
| 3 | Rp 19,77 T | 0,7829 | Rp 15,48 T |
| 4 | Rp 20,96 T | 0,7216 | Rp 15,12 T |
| 5 | Rp 22,22 T | 0,6650 | Rp 14,77 T |
| **Total** | - | - | **Rp 77,44 T** |

### Terminal Value & Equity Value

```
Terminal Value (nilai dari tahun 6 ke depan):
  FCF tahun 5 × (1 + g_terminal) / (WACC - g_terminal)
  = Rp 22,22 T × 1,03 / (0,085 - 0,03)
  = Rp 416,03 T

PV Terminal Value:
  = Rp 416,03 T / (1,085)^5
  = Rp 276,68 T
  = 78,13% dari total nilai

Enterprise Value:
  = PV Arus Kas 5 Tahun + PV Terminal Value
  = Rp 77,44 T + Rp 276,68 T
  = Rp 354,11 T

Equity Value (nilai untuk pemegang saham):
  = Enterprise Value - Utang Berbunga + Kas
  = Rp 354,11 T - Rp 119,20 T + Rp 47,65 T
  = Rp 282,56 T

Harga per Lembar:
  = Equity Value / Jumlah Saham
  = Rp 282,56 T / 39.920.061.040 lembar
  = Rp 7.078,26
```

---

## 🎯 Asumsi DCF yang Digunakan

### Asumsi Konservatif

| Parameter | Nilai | Penjelasan |
|-----------|-------|-----------|
| **WACC** | 8,5% | Biaya modal untuk perusahaan besar yang solid |
| **Growth Rate** | 6,0% | Pertumbuhan FCF selama 5 tahun proyeksi |
| **Growth Terminal** | 3,0% | Pertumbuhan perpetual (sesuai GDP long-term) |
| **Periode Proyeksi** | 5 tahun | Standar industri untuk perusahaan mapan |

### Mengapa Asumsi Ini Konservatif?

- **WACC 8,5%**: Perusahaan besar dengan credit rating solid (tidak 6%, tidak 10%)
- **Growth 6%**: Di bawah historical growth ASII (tetapi reasonable jika ada headwind)
- **Growth Terminal 3%**: Konservatif vs Indonesia GDP growth (4-5%)
- **5 tahun**: Periode standar (bukan 3 tahun agresif atau 10 tahun spekulatif)

---

## 📈 Analisis Sensitivitas

Tabel di bawah menunjukkan harga wajar dengan berbagai kombinasi WACC dan Growth Rate:

```
WACC \ Growth Rate    4,0%        6,0%       8,0%
─────────────────────────────────────────────────
6,5%             Rp 11.012   Rp 12.211   Rp 13.500  ← Optimistic
8,5%              Rp 6.343    Rp 7.078    Rp 7.868  ← BASE CASE
10,5%             Rp 4.165    Rp 4.685    Rp 5.243  ← Pessimistic
```

### Interpretasi Sensitivitas

**Skenario Optimistic (WACC 6,5% + Growth 8,0%):**
- Harga wajar: Rp 13.500
- Asumsi: Perusahaan tumbuh kuat dan risiko lebih rendah dari estimasi
- Potensi: Keuntungan besar jika terbukti

**Base Case (WACC 8,5% + Growth 6,0%):**
- Harga wajar: Rp 7.078 ← Yang kami gunakan
- Asumsi: Pertumbuhan normal, risiko medium
- Evaluasi: Realistis untuk perusahaan matang seperti ASII

**Skenario Pessimistic (WACC 10,5% + Growth 4,0%):**
- Harga wajar: Rp 4.165
- Asumsi: Pertumbuhan melambat, risiko meningkat
- Caution: Lebih hati-hati jika mendekati nilai ini

### Observasi Penting

⚠️ **Nilai sangat sensitif:**
- Perubahan WACC dari 6,5% ke 10,5% → Nilai turun dari Rp 13.500 ke Rp 4.165 (69% penurunan!)
- Perubahan Growth dari 4% ke 8% → Nilai naik dari Rp 4.165 ke Rp 13.500 (224% kenaikan!)

💡 **Kesimpulan:** Selalu gunakan margin of safety (30%) untuk mengakomodasi ketidakpastian asumsi.

---

## 📊 Perbandingan dengan Metode Graham

| Aspek | Graham | DCF |
|-------|--------|-----|
| **Harga Wajar** | Rp 9.795 | Rp 7.078 |
| **Perbedaan** | Rp 2.717 (27% lebih tinggi) | - |
| **Fokus** | Earnings & Assets saat ini | Proyeksi arus kas masa depan |
| **Base Data** | EPS & BVPS | FCF, Growth, WACC |
| **Kompleksitas** | Sederhana | Kompleks |
| **Untuk Investor** | Konservatif | Dalam |

### Mengapa Graham Lebih Tinggi?

1. **Graham fokus pada assets:** BVPS Rp 5.763 menunjukkan aset yang besar
2. **DCF fokus pada cash generation:** Growth 6% dianggap lebih konservatif
3. **Terminal Value dominan:** 78% dari nilai DCF, sensitif terhadap g_terminal

### Rekomendasi Gabungan

**Ambil rata-rata dari kedua metode:**
```
(Rp 9.795 + Rp 7.078) / 2 = Rp 8.436,50
```

Ini memberikan **middle ground** yang lebih balanced:
- Tidak seterlalu optimis seperti Graham
- Tidak seterlalu konservatif seperti DCF base case
- Dengan MOS 30% → Target beli Rp 5.905

---

## 💡 Key Takeaways

### Tentang DCF

✅ **Kelebihan:**
- Mempertimbangkan proyeksi masa depan
- Paling "fundamental" dan detail
- Fleksibel dengan berbagai skenario

❌ **Kekurangan:**
- Sangat sensitif asumsi
- Memerlukan data historis yang baik
- Sulit untuk startup/emerging companies

### Tentang ASII.JK

✅ **Cocok untuk DCF karena:**
- FCF positif dan stabil: Rp 16,60 T
- Perusahaan mapan dengan business model jelas
- Proyeksi 5 tahun bisa dibuat dengan reasonable

⚠️ **Risiko DCF untuk ASII:**
- Growth 6% mungkin terlalu optimis jika ada resesi
- WACC 8,5% bisa meningkat jika interest rate naik
- Industri otomotif menghadapi disruption (EV transition)

### Untuk Pengambilan Keputusan

🎯 **Harga Target Beli:** Rp 4.910 - Rp 6.856
(DCF MOS sampai Graham Number)

📍 **Status Saat Ini:** Rp 4.910 = TEPAT DI ZONE BELI
(Mencapai DCF MOS target)

⏳ **Waiting Point:** Jika naik ke Rp 6.000 - Rp 7.000
(Perlu evaluate ulang; masih menarik tapi kurang MOS)

❌ **Avoid Zone:** Jika naik di atas Rp 8.000
(Sudah limited upside; MOS negatif)

---

## 🔄 Workflow DCF

```
Input Data (yfinance):
├─ FCF: Rp 16,60 T
├─ Utang: Rp 119,20 T
├─ Kas: Rp 47,65 T
└─ Saham: 39,92 M lembar

                    ↓

Input Asumsi (Manual):
├─ WACC: 8,5%
├─ Growth: 6,0%
└─ Growth Terminal: 3,0%

                    ↓

Proyeksi & Diskon:
├─ Proyeksikan FCF 5 tahun → PV: Rp 77,44 T
├─ Hitung Terminal Value → PV: Rp 276,68 T
└─ Total Enterprise Value: Rp 354,11 T

                    ↓

Adjustment (Utang & Kas):
└─ Equity Value: Rp 282,56 T

                    ↓

Per Lembar:
└─ HARGA WAJAR: Rp 7.078,26 per lembar
```

---

## 📌 Kesimpulan Akhir

**DCF untuk ASII.JK = Rp 7.078,26**

Dengan:
- ✅ Base case assumptions yang konservatif
- ✅ Margin of Safety 30,63% vs harga pasar
- ✅ Sensitivitas analysis yang comprehensive
- ✅ Didukung oleh data yfinance yang aktual

**Status ASII.JK Saat Ini:**
```
Harga Pasar (Rp 4.910) < Harga Beli Target (Rp 4.955)
                        ↓
              SANGAT MENARIK DIBELI
```

---

*Untuk hasil lebih lengkap, jalankan:*
```bash
python demo_dcf_asii.py
```

*Atau bandingkan dengan metode lain:*
```bash
python demo_graham_asii.py
python PERBANDINGAN_METODE_ASII.md
```

---

**Reminder:** Analisis ini untuk tujuan pembelajaran. Pastikan verifikasi data terkini dan kondisi bisnis sebelum keputusan investasi nyata.
