# 📈 Kalkulator Harga Wajar Saham - Streamlit Web Interface

Aplikasi ini telah dikonversi dari terminal interface menjadi web interface menggunakan **Streamlit**.

## 🚀 Cara Menjalankan

### Opsi 1: Menggunakan Command Line Langsung

```bash
streamlit run app.py
```

**Atau** jika streamlit belum di-PATH:

```bash
python -m streamlit run app.py
```

### Opsi 2: Menggunakan Script Batch (Windows)

Buat file `run.bat` di folder project dengan isi:

```batch
@echo off
python -m streamlit run app.py
pause
```

Kemudian double-click file `run.bat`.

### Opsi 3: Menggunakan Python Langsung

```bash
python -c "import streamlit.cli; streamlit.cli.main(['run', 'app.py'])"
```

## 🌐 Akses Aplikasi

Setelah menjalankan command di atas, aplikasi akan otomatis membuka di browser:

```
Local URL:            http://localhost:8501
Network URL:          http://<IP-ADDRESS>:8501
```

Jika tidak membuka otomatis, buka manual ke: **http://localhost:8501**

## 📋 Fitur Aplikasi

### Tab 1️⃣ Graham Number
- Input langsung EPS & BVPS
- Hitung dari laba/ekuitas/saham beredar
- Ambil data otomatis dari yfinance
- Perhitungan Graham Number dengan MOS

### Tab 2️⃣ DCF
- Input manual atau ambil dari yfinance
- Proyeksi arus kas bertahun-tahun
- Analisis sensitivitas (tabel WACC vs Growth)
- Perhitungan Enterprise Value → Equity Value

### Tab 3️⃣ PE & PBV
- Input EPS & BVPS manual atau dari yfinance
- Masukkan PE & PBV acuan
- Bobot antara PE dan PBV
- Hasil valuasi gabungan

### Tab 📊 Ringkasan
- Tabel semua perhitungan dalam sesi
- Statistik: rata-rata, min, max
- Analisis MOS vs harga pasar

### Tab 📚 Penjelasan
- Penjelasan detail ketiga metode
- Istilah-istilah penting (EPS, BVPS, FCF, WACC, MOS)
- Di mana mencari data
- Peringatan disclaimer

## 💻 Requirements

- Python 3.8+
- Streamlit
- Pandas
- yfinance (optional, untuk ambil data otomatis)
- requests
- numpy

Install dependencies:

```bash
pip install -r requirements.txt
```

## ⚙️ Konfigurasi Streamlit

Untuk customize pengalaman Streamlit, buat folder `.streamlit` dan file `config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[client]
showErrorDetails = true
```

## 📝 Catatan

1. **Session State**: Riwayat perhitungan tersimpan dalam sesi browser. Refresh halaman akan mereset riwayat.

2. **yfinance Data**: Untuk ambil data otomatis, pastikan yfinance sudah terinstall dan Anda punya koneksi internet.

3. **Input Format**:
   - Desimal: gunakan koma (1.250,75)
   - Ribuan: titik (1.500 = 1500)

4. **Validation**: Jika `input_validation.py` tersedia, akan ada validasi tambahan untuk ticker, WACC, growth rate, dll.

## 🛑 Menghentikan Aplikasi

Tekan `Ctrl+C` di terminal/command prompt untuk menghentikan Streamlit server.

## 🐛 Troubleshooting

**Error: streamlit command not found**
```bash
python -m streamlit run app.py
```

**Port 8501 sudah terpakai**
```bash
streamlit run app.py --server.port 8502
```

**Aplikasi lambat saat ambil data yfinance**
- Ini normal, yfinance memerlukan waktu untuk fetch data dari internet
- Pastikan koneksi internet stabil

## 📚 Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [yfinance Documentation](https://github.com/ranaroussi/yfinance)
- Benjamin Graham: Intelligent Investor (book)

---

**Catatan Penting**: Semua hasil hanyalah estimasi berbasis asumsi yang Anda masukkan. Program ini adalah alat bantu belajar, BUKAN rekomendasi investasi. Selalu konsultasi dengan advisor keuangan profesional sebelum membuat keputusan investasi.
