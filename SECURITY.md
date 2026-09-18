# 🔐 Panduan Keamanan - Kalkulator Saham

## Ringkasan Kebijakan Keamanan

Dokumen ini mendefinisikan aturan keamanan dan praktik terbaik untuk proyek **Kalkulator Saham dengan yfinance**.

**Versi:** 1.0  
**Terakhir Diperbarui:** 2026-09-18

---

## 1. Validasi Input Data

### Format Ticker Saham
```
✅ VALID:   BBCA.JK, ASII.JK, UNVR.JK
❌ INVALID: bbca, BBCA, BBCA.ID, 123.JK
```

**Aturan:**
- Format: `^[A-Z]{1,5}\.JK$`
- Huruf BESAR, maksimal 5 karakter, diikuti `.JK`
- Panjang maksimal: 10 karakter

### Input Numerik
Batasan nilai yang diperbolehkan:

| Parameter | Min | Max | Unit | Deskripsi |
|-----------|-----|-----|------|-----------|
| **WACC** | 0.5% | 20% | % | Weighted Avg Cost of Capital |
| **Growth Rate** | -10% | 30% | % | Tingkat pertumbuhan FCF |
| **PE Ratio** | 1.0x | 100x | - | Price to Earnings |
| **PBV Ratio** | 0.1x | 10x | - | Price to Book Value |

**Contoh validasi:**
```python
if not (0.5 <= wacc <= 20):
    raise ValueError(f"WACC {wacc}% di luar range 0.5% - 20%")
```

---

## 2. Keamanan API (yfinance)

### Batasan Koneksi
```json
{
  "timeout": 10,           // detik
  "max_retries": 3,        // percobaan ulang
  "rate_limit": "none",    // yfinance free
  "fallback": "manual"     // jika gagal
}
```

### Ticker yang Diizinkan
- Format Indonesia: `[A-Z]{1,5}\.JK`
- Contoh: BBCA.JK, ASII.JK, UNVR.JK, TLKM.JK

### Penanganan Error API
```python
try:
    data = yf.Ticker("ASII.JK").info
except Exception as e:
    # Tampilkan pesan generic kepada user
    print("⚠ Tidak bisa mengambil data dari internet")
    print("Silakan input data secara manual")
    # Log detail error untuk debugging
    logger.error(f"yfinance error: {e}")
```

---

## 3. Keamanan File

### Ekstensi yang Diizinkan
```
✅ .py     - Python scripts
✅ .json   - JSON configs
✅ .md     - Markdown docs
✅ .txt    - Text files
✅ .csv    - CSV data
```

### Ekstensi yang Diblokir
```
❌ .exe, .bat, .sh, .cmd, .ps1, .dll, .so
```

### Batasan File
- **Ukuran maksimal:** 100 MB
- **Encoding:** UTF-8
- **Lokasi:** Folder proyek lokal saja

---

## 4. Penanganan Data Sensitif

### Data yang TIDAK Boleh Di-Log

❌ **JANGAN PERNAH LOG:**
- API keys atau tokens
- Password atau credentials
- Nomor rekening atau kartu kredit
- Informasi pribadi (nama, email, telepon)
- Internal server details

### Contoh Aman
```python
# ❌ JANGAN
logger.info(f"User login: {username}, password: {pwd}")

# ✅ BOLEH
logger.info(f"User {username} login successful")
```

### Sanitasi Input
```python
def safe_ticker(input_str):
    # 1. Strip whitespace
    clean = input_str.strip()
    
    # 2. Validasi format
    if not re.match(r'^[A-Z]{1,5}\.JK$', clean):
        raise ValueError("Format ticker tidak valid")
    
    # 3. Return safe value
    return clean
```

---

## 5. Validasi Output

### Cegah Injeksi Output
```python
# Format semua output untuk keamanan
output = f"Harga: Rp {harga:,.2f}"  # ✅ Safe

# Hindari evaluasi string dinamis
eval(user_input)  # ❌ JANGAN PERNAH
```

### Error Messages yang Aman
```python
# ❌ JANGAN (expose detail teknis)
print(f"Database connection error: {conn.error}")

# ✅ BOLEH (generic message)
print("Tidak bisa terhubung ke server")
# Log detail ke file untuk debugging
logger.error(f"DB error: {conn.error}")
```

---

## 6. Praktik Terbaik Keamanan

### 1. Selalu Validasi Input
```python
# ✅ BAIK
ticker = validate_ticker(user_input)
wacc = validate_percentage(user_input_wacc)

# ❌ BURUK
ticker = user_input  # tidak divalidasi
```

### 2. Gunakan Fallback Gracefully
```python
if yfinance_available and data_complete:
    data = ambil_data_yfinance(ticker)
else:
    print("⚠ Pakai mode manual input")
    data = ambil_data_manual()
```

### 3. Handle Errors dengan Baik
```python
try:
    result = risky_operation()
except SpecificError as e:
    # Log dan tampilkan user-friendly message
    logger.error(f"Error detail: {e}")
    print("Operasi gagal. Silakan coba lagi.")
except Exception as e:
    # Jangan expose stack trace
    logger.exception("Unexpected error")
    print("Terjadi kesalahan. Admin telah diberitahu.")
```

### 4. Batasi Akses Resource
```python
# Timeout untuk API calls
requests.get(url, timeout=10)

# Validasi ukuran file
if file_size > 100_000_000:  # 100MB
    raise ValueError("File terlalu besar")
```

### 5. Log yang Aman
```python
# ✅ AMAN - log hanya informasi penting
logger.info(f"Valuasi {ticker} selesai: {harga_wajar}")

# ❌ TIDAK AMAN - log data sensitif
logger.info(f"Input pengguna: {raw_user_input}")
```

---

## 7. Checklist Keamanan

Sebelum melepas fitur baru, verifikasi:

- [ ] **Input Validation**
  - [ ] Format ticker divalidasi dengan regex
  - [ ] Numeric inputs dicek range-nya
  - [ ] String input dibersihkan (strip, sanitize)

- [ ] **API Security**
  - [ ] Timeout diatur 10 detik
  - [ ] Error handling graceful
  - [ ] Fallback ke manual tersedia

- [ ] **Data Protection**
  - [ ] Sensitive data tidak di-log
  - [ ] Output di-escape dari injeksi
  - [ ] Error messages generic saja

- [ ] **File Operations**
  - [ ] File size dibatasi 100MB
  - [ ] Extension divalidasi
  - [ ] Path traversal dicegah

- [ ] **Error Handling**
  - [ ] Stack trace tidak ditampilkan user
  - [ ] Exception di-log penuh
  - [ ] User dapat melakukan recovery

---

## 8. Testing Keamanan

### Unit Test untuk Input Validation
```python
def test_ticker_validation():
    # ✅ Valid tickers
    assert validate_ticker("BBCA.JK") == "BBCA.JK"
    assert validate_ticker("ASII.JK") == "ASII.JK"
    
    # ❌ Invalid tickers
    with pytest.raises(ValueError):
        validate_ticker("bbca")      # lowercase
        validate_ticker("BBCAA.JK")  # > 5 chars
        validate_ticker("BBCA")      # no .JK
```

### Boundary Testing
```python
def test_wacc_boundaries():
    assert validate_wacc(0.5) == 0.5      # min
    assert validate_wacc(20.0) == 20.0    # max
    
    with pytest.raises(ValueError):
        validate_wacc(0.1)      # terlalu kecil
        validate_wacc(25.0)     # terlalu besar
```

---

## 9. Reporting Keamanan

### Jika Menemukan Celah Keamanan
1. **JANGAN** posting di public forum
2. **LAKUKAN** dokumentasi detail (tanpa expose exploit)
3. **HUBUNGI** melalui private channel
4. **TUNGGU** patch sebelum disclose publik

### Template Laporan
```
Judul: [SECURITY] Deskripsi singkat celah

Deskripsi:
- Jenis celah (XSS, Injection, dll)
- Kondisi yang trigger
- Impact (low/medium/high)

Reproduksi:
1. Langkah pertama
2. Langkah kedua
3. Hasil: [apa yang terjadi]

Mitigasi:
- Validasi input di point X
- Escape output di point Y
```

---

## 10. Compliance

### Untuk Pengguna Program
✅ Program ini aman untuk:
- Pembelajaran fundamental analysis
- Screening kandidat investasi
- Analisis saham lokal

⚠️ Program ini BUKAN untuk:
- Dasar keputusan investasi sendirian
- Menggantikan financial advisor
- Perdagangan otomatis

### Update Keamanan
- Review kebijakan keamanan setiap kuartal
- Update dependencies (yfinance, dll) secara regular
- Patch bugs keamanan segera

---

## Referensi

- OWASP Top 10: https://owasp.org/Top10/
- Input Validation: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html
- yfinance Security: https://github.com/ranaroussi/yfinance

---

**Terakhir Diperbarui:** 2026-09-18  
**Maintained by:** Security Team  
**Next Review:** 2026-12-18
