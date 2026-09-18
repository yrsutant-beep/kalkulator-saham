# Integration Guide: Security Validation dalam Kalkulator Saham

## 📋 Ringkasan Integrasi

File `input_validation.py` telah berhasil diintegrasikan ke dalam `kalkulator_saham.py`, menambahkan lapisan keamanan untuk semua input pengguna.

**Status:** ✅ ACTIVE  
**Validation Available:** True

---

## 🔒 Apa yang Divalidasi

### 1. Ticker Format Validation
```
Input user:  "bbca.jk"
Validation:  Format tidak valid - harus UPPERCASE dengan format X.JK
Output:      Error message yang jelas
```

**Rules:**
- Format: `^[A-Z]{1,5}\.JK$`
- Contoh valid: BBCA.JK, ASII.JK, UNVR.JK
- Case-insensitive input dikonversi otomatis ke UPPERCASE

### 2. WACC Validation
```
Input user:  "25" atau "0.1"
Validation:  Range 0.5% - 20%
Output:      Error jika di luar range
```

**Rules:**
- Minimum: 0.5%
- Maximum: 20.0%
- Unit: Persen (%)

### 3. Growth Rate Validation
```
Input user:  "50" atau "-15"
Validation:  Range -10% - 30%
Output:      Error jika di luar range
```

**Rules:**
- Minimum: -10%
- Maximum: 30.0%
- Unit: Persen (%)

### 4. PE Ratio Validation
```
Input user:  "0.5" atau "150"
Validation:  Range 1x - 100x
Output:      Error jika di luar range
```

**Rules:**
- Minimum: 1.0x
- Maximum: 100.0x

### 5. PBV Ratio Validation
```
Input user:  "0.01" atau "15"
Validation:  Range 0.1x - 10x
Output:      Error jika di luar range
```

**Rules:**
- Minimum: 0.1x
- Maximum: 10.0x

---

## 🔧 Perubahan dalam Kalkulator Saham

### Import Additions
```python
import logging

try:
    from input_validation import (
        validate_ticker,
        validate_wacc,
        validate_growth_rate,
        validate_pe_ratio,
        validate_pbv_ratio,
        validate_graham_inputs,
        validate_dcf_inputs,
        ValidationError
    )
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False
```

### Modified Functions

#### 1. `ambil_data_yfinance(ticker_symbol)`
**Sebelum:**
```python
def ambil_data_yfinance(ticker_symbol):
    if yf is None:
        return None
    try:
        saham = yf.Ticker(ticker_symbol)
        # ...
```

**Sesudah:**
```python
def ambil_data_yfinance(ticker_symbol):
    if yf is None:
        return None
    
    # Validasi ticker format
    if VALIDATION_AVAILABLE:
        try:
            ticker_symbol = validate_ticker(ticker_symbol)
        except ValueError as e:
            print(f"  ! Ticker tidak valid: {e}")
            return None
    
    try:
        saham = yf.Ticker(ticker_symbol)
        # ...
        logging.info(f"Successfully fetched data for ticker: {ticker_symbol}")
        # ...
```

#### 2. `minta_float(label, minimum, maksimum, default, param_name)`
**Sebelum:**
```python
def minta_float(label, minimum=None, maksimum=None, default=None):
    # Manual range checking saja
```

**Sesudah:**
```python
def minta_float(label, minimum=None, maksimum=None, default=None, param_name=None):
    # Gunakan validation module untuk param_name tertentu
    # Fallback ke manual range checking
    
    if VALIDATION_AVAILABLE and param_name:
        try:
            if param_name.lower() == 'wacc':
                nilai = validate_wacc(nilai)
            elif param_name.lower() == 'growth_rate':
                nilai = validate_growth_rate(nilai)
            elif param_name.lower() == 'pe_ratio':
                nilai = validate_pe_ratio(nilai)
            elif param_name.lower() == 'pbv_ratio':
                nilai = validate_pbv_ratio(nilai)
        except ValueError as e:
            print(f"  ! {e}")
            continue
```

#### 3. Ticker Input di Setiap Metode
**Metode Graham (metode_graham):**
```python
else:  # cara == "3", ambil dari yfinance
    while True:
        try:
            ticker_input = input("  Kode saham: ").strip()
            if VALIDATION_AVAILABLE:
                ticker = validate_ticker(ticker_input)
            else:
                ticker = ticker_input.upper()
            break
        except ValueError as e:
            print(f"  ! {e}")
            continue
    data_yf = ambil_data_yfinance(ticker)
```

**Metode DCF (metode_dcf):**
```python
if cara == "2":
    while True:
        try:
            ticker_input = input("  Kode saham: ").strip()
            if VALIDATION_AVAILABLE:
                ticker = validate_ticker(ticker_input)
            else:
                ticker = ticker_input.upper()
            break
        except ValueError as e:
            print(f"  ! {e}")
            continue
    data_yf = ambil_data_yfinance(ticker)
```

**Metode PE/PBV (metode_pe_pbv):**
```python
else:  # cara == "2", ambil dari yfinance
    while True:
        try:
            ticker_input = input("  Kode saham: ").strip()
            if VALIDATION_AVAILABLE:
                ticker = validate_ticker(ticker_input)
            else:
                ticker = ticker_input.upper()
            break
        except ValueError as e:
            print(f"  ! {e}")
            continue
    data_yf = ambil_data_yfinance(ticker)
```

#### 4. Parameter Input Metode
**WACC & Growth Rate (metode_dcf):**
```python
wacc_p = minta_float(
    "WACC / discount rate (% per tahun)",
    minimum=0.01, maksimum=100, default=10,
    param_name="wacc"  # ← Tambahan
)

g_p = minta_float(
    "Growth rate FCF selama proyeksi (% per tahun)",
    minimum=-100, maksimum=200, default=5,
    param_name="growth_rate"  # ← Tambahan
)
```

**PE & PBV Ratio (metode_pe_pbv):**
```python
pe_acuan = minta_float(
    "PE acuan / target (x)",
    minimum=0, default=15,
    param_name="pe_ratio"  # ← Tambahan
)

pbv_acuan = minta_float(
    "PBV acuan / target (x)",
    minimum=0, default=1.5,
    param_name="pbv_ratio"  # ← Tambahan
)
```

---

## 📊 Startup Messages

Ketika program berjalan, status validasi ditampilkan:

```
Selamat datang di Kalkulator Harga Wajar Saham.
...

✓ Security validation AKTIF
  - Ticker format validation (format: KODE.JK)
  - WACC range validation (0.5% - 20%)
  - Growth rate range validation (-10% - 30%)
  - PE/PBV ratio validation (1x - 100x, 0.1x - 10x)
```

atau jika validation tidak available:

```
⚠ Security validation tidak aktif
  - Pastikan input_validation.py ada di folder yang sama
  - atau install dependencies yang diperlukan
```

---

## ✅ Testing Integration

### Test 1: Import Module
```bash
python -c "from kalkulator_saham import VALIDATION_AVAILABLE; print(VALIDATION_AVAILABLE)"
# Output: True
```

### Test 2: Run Program
```bash
python kalkulator_saham.py
```

Seharusnya menampilkan pesan "✓ Security validation AKTIF" di startup.

### Test 3: Test Ticker Validation
```
Pilih metode Graham → Opsi 3 → Input: "bbca" 
Output: "! Format ticker tidak valid..."

Pilih metode Graham → Opsi 3 → Input: "BBCA.JK"
Output: "Mengambil data untuk BBCA.JK..."
```

### Test 4: Test WACC Validation
```
Pilih metode DCF → Input WACC: "25"
Output: "! WACC 25% lebih besar dari maksimum 20%"

Pilih metode DCF → Input WACC: "8.5"
Output: "WACC: 8.5 valid" (log), continue to next input
```

---

## 🔄 Fallback Behavior

### Jika input_validation.py tidak tersedia:
- Program masih berjalan dengan `VALIDATION_AVAILABLE = False`
- Validation khusus (WACC, growth_rate, etc.) di-skip
- Manual range checking masih aktif (minimum/maksimum pada minta_float)
- Ticker format tidak divalidasi dengan ketat

### Jika yfinance tidak tersedia:
- Tidak ada perubahan dari implementasi sebelumnya
- User masih bisa input manual

---

## 📝 Logging

Setiap transaksi penting di-log:

```python
logging.info(f"Successfully fetched data for ticker: {ticker_symbol}")
logging.error(f"Error fetching data from yfinance: {e}")
```

Log diarahkan ke console (stdout).

---

## 🚀 Usage Examples

### Example 1: Graham Number dengan Validasi Ticker
```
Metode 1 → Opsi 3 → "bbca.jk" 
→ "Format ticker tidak valid"
→ Coba lagi: "BBCA.JK"
→ Data berhasil diambil ✓
```

### Example 2: DCF dengan Validasi WACC
```
Metode 2 → Opsi 2 → "ASII.JK"
→ Data berhasil diambil ✓
→ WACC: "25"
→ "WACC 25.0% lebih besar dari maksimum 20%"
→ WACC: "8.5"
→ Diterima ✓
```

### Example 3: PE/PBV dengan Validasi Ratio
```
Metode 3 → Opsi 2 → "UNVR.JK"
→ Data berhasil diambil ✓
→ PE acuan: "0.5"
→ "PE Ratio 0.5 lebih kecil dari minimum 1.0"
→ PE acuan: "15"
→ Diterima ✓
```

---

## ⚙️ Configuration

### Validation Ranges (dari security-rules.json)
```json
{
  "numeric_inputs": {
    "allowed_range": {
      "wacc": { "min": 0.5, "max": 20.0, "unit": "%" },
      "growth_rate": { "min": -10.0, "max": 30.0, "unit": "%" },
      "pe_ratio": { "min": 1.0, "max": 100.0 },
      "pbv_ratio": { "min": 0.1, "max": 10.0 }
    }
  }
}
```

Jika ingin mengubah range, edit `input_validation.py` pada bagian `NUMERIC_RANGES`:

```python
NUMERIC_RANGES = {
    'wacc': {'min': 0.5, 'max': 20.0, 'unit': '%'},
    'growth_rate': {'min': -10.0, 'max': 30.0, 'unit': '%'},
    'pe_ratio': {'min': 1.0, 'max': 100.0},
    'pbv_ratio': {'min': 0.1, 'max': 10.0},
}
```

---

## 📚 Files Involved

| File | Role | Status |
|------|------|--------|
| `kalkulator_saham.py` | Main program (MODIFIED) | ✅ Integrated |
| `input_validation.py` | Validation module (NEW) | ✅ Active |
| `security-rules.json` | Configuration | ✅ Reference |
| `SECURITY.md` | Documentation | ✅ Reference |
| `.env` | Environment vars | ✅ Available |
| `.gitignore` | File exclusions | ✅ Active |

---

## 🔐 Security Benefits

✅ **Ticker Format Protection**
- Mencegah input format tidak valid
- Standar format Indonesia (.JK)

✅ **Range Validation**
- WACC dibatasi 0.5% - 20% (realistic untuk pasar)
- Growth rate dibatasi -10% - 30% (reasonable range)
- PE/PBV ratio dibatasi sesuai standar pasar

✅ **Graceful Fallback**
- Jika validation module tidak ada, program masih jalan
- Jika yfinance error, fallback ke manual input
- No hard crashes, user-friendly error messages

✅ **Logging Integration**
- Semua operasi di-log untuk debugging
- Error tracking untuk maintenance

---

## 🐛 Troubleshooting

### Issue: "input_validation module not available"
**Solusi:** Pastikan file `input_validation.py` ada di folder yang sama dengan `kalkulator_saham.py`

### Issue: Validation tidak berjalan
**Solusi:** Periksa Python version (minimal 3.6), dan pastikan tidak ada error saat import

### Issue: Error message tidak jelas
**Solusi:** Error message dari validation module sudah dirancang user-friendly. Jika ada suggestion, lakukan sesuai instruksi

---

## 📈 Next Steps

### Future Enhancements
- [ ] Tambah validation untuk EPS/BVPS (positive check)
- [ ] Tambah validation untuk FCF (non-zero check)
- [ ] Tambah rate limiting untuk API calls
- [ ] Tambah caching untuk hasil yfinance
- [ ] Tambah unit tests untuk setiap validation function

### Monitoring
- Pantau log file untuk error patterns
- Review security checklist monthly
- Update range boundaries jika market conditions berubah

---

## 📞 Support

Untuk pertanyaan atau issues:
1. Baca `SECURITY.md` untuk panduan keamanan
2. Baca `SECURITY_CHECKLIST.md` untuk verifikasi
3. Jalankan `python input_validation.py` untuk test validation
4. Check file `.env` untuk environment configuration

---

**Integration Status:** ✅ COMPLETE  
**Last Updated:** 2026-09-18  
**Version:** 1.0
