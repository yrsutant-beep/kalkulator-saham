"""
Kalkulator Harga Wajar Saham - Streamlit Web Interface
========================================================

Program web interaktif untuk menghitung estimasi harga wajar (nilai
intrinsik) sebuah saham dengan 3 metode:

  1. Benjamin Graham  -> Graham Number dari EPS & BVPS
  2. Discounted Cash Flow (DCF) -> Free Cash Flow, WACC, Growth Rate
  3. Relative Valuation -> Rasio PE dan PBV

Catatan: hasil perhitungan adalah estimasi berbasis asumsi yang Anda
masukkan, BUKAN rekomendasi jual/beli.
"""

import re
import logging
import streamlit as st
import pandas as pd
try:
    import yfinance as yf
    import requests
except ImportError:
    yf = None
    requests = None

# Import security validation functions
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
    logging.warning("input_validation module not available - skipping validation")

MOS_DEFAULT = 30.0  # margin of safety default (persen)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Pola angka gaya Indonesia dengan satu pemisah ribuan, mis. 1.500 atau -12.750
POLA_RIBUAN = re.compile(r"^-?\d{1,3}\.\d{3}$")

SATUAN = {
    "1": ("Rupiah", 1.0),
    "2": ("Juta (10^6)", 1_000_000.0),
    "3": ("Miliar (10^9)", 1_000_000_000.0),
    "4": ("Triliun (10^12)", 1_000_000_000_000.0),
}

# Initialize session state
if 'riwayat' not in st.session_state:
    st.session_state.riwayat = []


# ---------------------------------------------------------------------------
# Utilitas yfinance
# ---------------------------------------------------------------------------

def buat_session_custom():
    """Buat custom session dengan User-Agent browser untuk menghindari pemblokiran Yahoo Finance."""
    if requests is None:
        return None

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    })
    return session


def ambil_data_yfinance(ticker_symbol):
    """Ambil data keuangan dari yfinance dengan custom session. Contoh ticker: 'BBCA.JK', 'ASII.JK'."""
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
        session = buat_session_custom()

        if session:
            saham = yf.Ticker(ticker_symbol, session=session)
            logging.info(f"Using custom session with browser User-Agent for: {ticker_symbol}")
        else:
            saham = yf.Ticker(ticker_symbol)
            logging.warning(f"requests module not available, using default session for: {ticker_symbol}")

        data = saham.info

        result = {
            'ticker': ticker_symbol,
            'nama': data.get('longName', ticker_symbol),
            'eps': data.get('trailingEps', None),
            'book_value': data.get('bookValue', None),
            'price': data.get('currentPrice', None),
        }

        info_tambahan = {}
        if data.get('freeCashflow'):
            info_tambahan['fcf'] = data['freeCashflow']
        if data.get('totalDebt'):
            info_tambahan['utang'] = data['totalDebt']
        if data.get('totalCash'):
            info_tambahan['kas'] = data['totalCash']
        if data.get('sharesOutstanding'):
            info_tambahan['saham_beredar'] = data['sharesOutstanding']

        result.update(info_tambahan)
        logging.info(f"Successfully fetched data for ticker: {ticker_symbol}")
        return result
    except Exception as e:
        logging.error(f"Error fetching data from yfinance: {e}")
        print(f"  ! Error mengambil data dari yfinance: {e}")
        return None


def tampilkan_data_yfinance(data):
    """Tampilkan data yang diambil dari yfinance."""
    if not data:
        return

    st.subheader(f"📊 Data dari yfinance: {data['ticker']} ({data['nama']})")
    col1, col2, col3 = st.columns(3)
    with col1:
        if data.get('eps') is not None:
            st.metric("EPS", rp(data['eps']))
    with col2:
        if data.get('book_value') is not None:
            st.metric("Book Value/share", rp(data['book_value']))
    with col3:
        if data.get('price') is not None:
            st.metric("Harga pasar", rp(data['price']))

    col4, col5, col6 = st.columns(3)
    with col4:
        if data.get('fcf') is not None:
            st.metric("Free Cash Flow", rp_ringkas(data['fcf']))
    with col5:
        if data.get('utang') is not None:
            st.metric("Total Utang", rp_ringkas(data['utang']))
    with col6:
        if data.get('kas') is not None:
            st.metric("Kas & Setara", rp_ringkas(data['kas']))

    if data.get('saham_beredar') is not None:
        st.info(f"Saham Beredar: {fmt(data['saham_beredar'], 0)} lembar")


# ---------------------------------------------------------------------------
# Utilitas input & format angka
# ---------------------------------------------------------------------------

def normalisasi_angka(teks):
    """Ubah tulisan angka gaya Indonesia menjadi format yang dipahami float().

    Contoh yang diterima: '1234.5', '1.234,56', '1.500.000', '1_500_000',
    '2,5', '1.5e12', '1.500' (dibaca seribu lima ratus).
    """
    teks = teks.strip().replace(" ", "").replace("_", "")
    if "," in teks:
        # koma dianggap pemisah desimal, titik dianggap pemisah ribuan
        return teks.replace(".", "").replace(",", ".")
    if teks.count(".") > 1 or POLA_RIBUAN.match(teks):
        # titik berkelompok 3 angka = pemisah ribuan (1.500.000 atau 1.500)
        return teks.replace(".", "")
    return teks


def fmt_default(nilai):
    """Tampilkan nilai default secara ringkas: 5 -> '5', 1.5 -> '1,5'."""
    if float(nilai) == int(nilai):
        return str(int(nilai))
    return f"{nilai:g}".replace(".", ",")


def minta_float_st(label, minimum=None, maksimum=None, default=None, param_name=None, step=0.01):
    """Widget input untuk bilangan menggunakan Streamlit.

    Args:
        label: Label input
        minimum: Nilai minimum
        maksimum: Nilai maksimum
        default: Nilai default
        param_name: Nama parameter untuk validasi
        step: Langkah perubahan slider
    """
    try:
        nilai = st.number_input(
            label,
            value=float(default) if default is not None else 0.0,
            min_value=float(minimum) if minimum is not None else None,
            max_value=float(maksimum) if maksimum is not None else None,
            step=step,
            format="%.2f"
        )

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
                st.error(str(e))
                return None

        return nilai
    except Exception as e:
        st.error(f"Error dalam input: {e}")
        return None


def minta_int_st(label, minimum=None, maksimum=None, default=None):
    """Widget input untuk bilangan bulat menggunakan Streamlit."""
    return int(st.number_input(
        label,
        value=int(default) if default is not None else 0,
        min_value=int(minimum) if minimum is not None else None,
        max_value=int(maksimum) if maksimum is not None else None,
        step=1,
        format="%d"
    ))


def minta_pilihan_st(label, pilihan_valid, index=0):
    """Widget selectbox menggunakan Streamlit."""
    return st.selectbox(label, pilihan_valid, index=index)


def pilih_satuan(keterangan):
    """Minta pengguna memilih satuan nilai besar agar tidak perlu ketik nol banyak."""
    print(f"\n  Satuan untuk {keterangan}:")
    for kode, (nama, _) in SATUAN.items():
        print(f"    {kode}. {nama}")
    kode = minta_pilihan("  Pilih satuan (1-4):", list(SATUAN))
    nama, pengali = SATUAN[kode]
    print(f"  -> Satuan dipakai: {nama}")
    return pengali, nama


def fmt(x, desimal=2):
    """Format angka dengan pemisah ribuan titik dan desimal koma."""
    s = f"{x:,.{desimal}f}"
    return s.replace(",", "#").replace(".", ",").replace("#", ".")


def rp(x, desimal=2):
    return f"Rp {fmt(x, desimal)}"


def rp_ringkas(x):
    """Tampilkan nilai besar secara ringkas, mis. Rp 12,50 T."""
    tanda = "-" if x < 0 else ""
    n = abs(x)
    for batas, label in ((1e12, "T"), (1e9, "M"), (1e6, "Jt")):
        if n >= batas:
            return f"{tanda}Rp {fmt(n / batas)} {label}"
    return f"{tanda}Rp {fmt(n)}"


def judul(teks):
    st.markdown(f"# {teks}")


def sub(teks):
    st.markdown(f"## {teks}")


# ---------------------------------------------------------------------------
# Kesimpulan & margin of safety
# ---------------------------------------------------------------------------

def minta_harga_pasar():
    return minta_float(
        "Harga pasar saat ini per lembar (isi 0 untuk melewati)",
        minimum=0, default=0,
    )


def tampilkan_kesimpulan(metode, harga_wajar, harga_pasar):
    sub("Hasil Perhitungan")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Metode", metode[:30])
    with col2:
        st.metric("Harga Wajar/lembar", rp(harga_wajar), delta=None)

    if harga_wajar <= 0:
        st.error("❌ Harga wajar <= 0. Berdasarkan asumsi yang dimasukkan, saham ini tidak punya nilai wajar positif. Cek kembali data/asumsi Anda.")
        st.session_state.riwayat.append((metode, harga_wajar, harga_pasar))
        return

    harga_beli_ideal = harga_wajar * (1 - MOS_DEFAULT / 100)
    st.metric("Harga Beli Ideal", f"{rp(harga_beli_ideal)} (MOS {fmt(MOS_DEFAULT, 0)}%)")

    if harga_pasar > 0:
        mos = (harga_wajar - harga_pasar) / harga_wajar * 100
        upside = (harga_wajar - harga_pasar) / harga_pasar * 100

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Harga Pasar", rp(harga_pasar))
        with col2:
            st.metric("Margin of Safety", f"{fmt(mos)}%")
        with col3:
            st.metric("Potensi Upside", f"{fmt(upside)}%")

        if mos >= MOS_DEFAULT:
            status = "✅ UNDERVALUED - diskon cukup besar terhadap nilai wajar"
            status_color = "success"
        elif mos > 0:
            status = "⚠️ SEDIKIT DI BAWAH nilai wajar - margin of safety masih tipis"
            status_color = "warning"
        elif mos > -10:
            status = "⚪ WAJAR / FAIRLY VALUED - harga mendekati nilai wajar"
            status_color = "info"
        else:
            status = "❌ OVERVALUED - harga di atas nilai wajar"
            status_color = "error"

        if status_color == "success":
            st.success(status)
        elif status_color == "warning":
            st.warning(status)
        elif status_color == "error":
            st.error(status)
        else:
            st.info(status)
    else:
        st.warning("⚠️ Harga pasar tidak diisi, perbandingan dilewati")

    st.session_state.riwayat.append((metode, harga_wajar, harga_pasar))


# ---------------------------------------------------------------------------
# Metode 1: Benjamin Graham
# ---------------------------------------------------------------------------

def metode_graham():
    judul("Benjamin Graham (Graham Number)")

    st.markdown("""
    **Rumus:** Harga Wajar = √(22,5 × EPS × BVPS)

    Angka 22,5 berasal dari batas konservatif Graham: PER maksimal 15 dan PBV maksimal 1,5 (15 × 1,5 = 22,5).

    - **EPS** = Earning Per Share = laba bersih / jumlah saham beredar
    - **BVPS** = Book Value / Share = total ekuitas / jumlah saham beredar

    ⚠️ **Syarat:** EPS dan BVPS harus positif (perusahaan untung & ekuitas positif).
    """)

    sub("Pilih Cara Input Data")

    pilihan_mode = ["Input langsung EPS & BVPS", "Hitung dari laba/ekuitas/saham beredar"]
    if yf:
        pilihan_mode.append("Ambil data otomatis dari yfinance")

    cara = st.radio("", pilihan_mode, index=0, horizontal=True)

    col1, col2 = st.columns(2)

    if cara == pilihan_mode[0]:  # Input langsung
        with col1:
            eps = minta_float_st("EPS - laba per lembar saham (Rp)", default=100)
        with col2:
            bvps = minta_float_st("BVPS - nilai buku per lembar saham (Rp)", default=500)

    elif cara == pilihan_mode[1]:  # Hitung dari laba/ekuitas
        satuan_list = list(SATUAN.values())
        satuan_nama = st.selectbox("Satuan untuk laba & ekuitas", [x[0] for x in satuan_list])
        pengali = dict((v[0], v[1]) for v in SATUAN.values())[satuan_nama]

        col1, col2, col3 = st.columns(3)
        with col1:
            laba = minta_float_st("Laba bersih setahun", default=1000)
        with col2:
            ekuitas = minta_float_st("Total ekuitas (book value)", default=10000)
        with col3:
            saham = minta_float_st("Jumlah saham beredar (lembar)", minimum=1, default=100)

        laba *= pengali
        ekuitas *= pengali
        eps = laba / saham if saham > 0 else 0
        bvps = ekuitas / saham if saham > 0 else 0

        st.write(f"**EPS** = {rp_ringkas(laba)} / {fmt(saham, 0)} lembar = {rp(eps)}")
        st.write(f"**BVPS** = {rp_ringkas(ekuitas)} / {fmt(saham, 0)} lembar = {rp(bvps)}")

    else:  # Ambil dari yfinance
        ticker_input = st.text_input("Kode saham (contoh: BBCA.JK, ASII.JK):", "BBCA.JK")
        if ticker_input:
            try:
                if VALIDATION_AVAILABLE:
                    ticker = validate_ticker(ticker_input)
                else:
                    ticker = ticker_input.upper()

                if st.button("📥 Ambil data dari yfinance"):
                    data_yf = ambil_data_yfinance(ticker)
                    if data_yf and data_yf.get('eps') is not None and data_yf.get('book_value') is not None:
                        tampilkan_data_yfinance(data_yf)
                        eps = data_yf['eps']
                        bvps = data_yf['book_value']
                        st.success(f"✓ Data EPS dan BVPS berhasil diambil dari yfinance")
                    else:
                        st.error(f"❌ Data tidak lengkap dari yfinance untuk {ticker}.")
                        with col1:
                            eps = minta_float_st("EPS - laba per lembar saham (Rp)", default=100)
                        with col2:
                            bvps = minta_float_st("BVPS - nilai buku per lembar saham (Rp)", default=500)
            except ValueError as e:
                st.error(f"Error: {e}")
                return

    harga_pasar = minta_float_st("Harga pasar saat ini per lembar (isi 0 untuk melewati)", minimum=0, default=0)

    if eps <= 0 or bvps <= 0:
        st.error("❌ Graham Number tidak bisa dihitung")
        if eps <= 0:
            st.write(f"- EPS = {rp(eps)} (perusahaan rugi / tidak untung).")
        if bvps <= 0:
            st.write(f"- BVPS = {rp(bvps)} (ekuitas negatif).")
        st.info("Metode Graham hanya berlaku untuk perusahaan yang profitabel dengan ekuitas positif. Coba metode lain atau perbaiki data.")
        return

    graham = (22.5 * eps * bvps) ** 0.5
    st.markdown(f"### Perhitungan")
    st.write(f"√(22,5 × {fmt(eps)} × {fmt(bvps)}) = **{rp(graham)}**")

    tampilkan_kesimpulan("Benjamin Graham (Graham Number)", graham, harga_pasar)

    sub("Informasi Tambahan")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("PER pada harga wajar", f"{fmt(graham / eps)}x")
        if harga_pasar > 0:
            st.metric("PER pada harga pasar", f"{fmt(harga_pasar / eps)}x")
    with col2:
        st.metric("PBV pada harga wajar", f"{fmt(graham / bvps)}x")
        if harga_pasar > 0:
            st.metric("PBV pada harga pasar", f"{fmt(harga_pasar / bvps)}x")


# ---------------------------------------------------------------------------
# Metode 2: Discounted Cash Flow
# ---------------------------------------------------------------------------

def metode_dcf():
    judul("Discounted Cash Flow (DCF)")

    st.markdown("""
    **Ide dasar:** Nilai perusahaan = seluruh arus kas masa depan yang didiskontokan ke nilai sekarang.

    - **FCF tahun ke-n** = FCF₀ × (1 + g)ⁿ
    - **PV** = FCF tahun ke-n / (1 + WACC)ⁿ
    - **Terminal Value** = FCF tahun akhir × (1 + g_term) / (WACC - g_term)
    - **Enterprise Value** = Σ PV + PV(Terminal Value)
    - **Equity Value** = Enterprise Value - utang berbunga + kas
    - **Harga wajar** = Equity Value / jumlah saham beredar

    ⚠️ **Syarat:** WACC harus lebih besar dari growth terminal.
    """)

    sub("Pilih Cara Input Data")

    pilihan_mode = ["Input manual semua data"]
    if yf:
        pilihan_mode.append("Ambil dari yfinance (WACC & growth manual)")

    cara = st.radio("", pilihan_mode, index=0, horizontal=True)

    data_yf = None
    if cara == pilihan_mode[1] if len(pilihan_mode) > 1 else False:
        ticker_input = st.text_input("Kode saham (contoh: BBCA.JK, ASII.JK):", "BBCA.JK")
        if ticker_input and st.button("📥 Ambil data dari yfinance", key="dcf_yf"):
            try:
                if VALIDATION_AVAILABLE:
                    ticker = validate_ticker(ticker_input)
                else:
                    ticker = ticker_input.upper()
                data_yf = ambil_data_yfinance(ticker)
                if data_yf and (data_yf.get('fcf') or data_yf.get('kas') or data_yf.get('saham_beredar')):
                    tampilkan_data_yfinance(data_yf)
                else:
                    st.warning(f"⚠️ Data dari yfinance untuk {ticker} tidak lengkap.")
                    data_yf = None
            except ValueError as e:
                st.error(f"Error: {e}")

    satuan_list = list(SATUAN.values())
    satuan_nama = st.selectbox("Satuan untuk FCF, utang, dan kas", [x[0] for x in satuan_list], key="dcf_satuan")
    pengali = dict((v[0], v[1]) for v in SATUAN.values())[satuan_nama]
    nama_satuan = satuan_nama

    col1, col2 = st.columns(2)
    with col1:
        if data_yf and data_yf.get('fcf'):
            fcf0_display = data_yf['fcf'] / pengali
            st.info(f"FCF dari yfinance: {fmt(fcf0_display)} {nama_satuan}")
            fcf0 = minta_float_st(f"Free Cash Flow tahun terakhir ({nama_satuan})", default=fcf0_display, step=1.0)
        else:
            fcf0 = minta_float_st(f"Free Cash Flow tahun terakhir ({nama_satuan})", default=1000, step=1.0)
        fcf0 *= pengali

    with col2:
        tahun = minta_int_st("Periode proyeksi (tahun)", minimum=1, maksimum=30, default=5)

    if fcf0 <= 0:
        st.warning("⚠️ FCF Anda <= 0. DCF akan menghasilkan nilai negatif. Metode DCF sebaiknya dipakai saat FCF positif.")

    col1, col2, col3 = st.columns(3)
    with col1:
        wacc_p = minta_float_st("WACC / discount rate (% per tahun)", minimum=0.01, maksimum=100, default=10, param_name="wacc", step=0.5)
    with col2:
        g_p = minta_float_st("Growth rate FCF (% per tahun)", minimum=-100, maksimum=200, default=5, param_name="growth_rate", step=0.5)
    with col3:
        default_g_term = min(3.0, max(wacc_p - 0.01, 1.0))
        g_term_p = minta_float_st("Growth terminal/perpetual (% per tahun)", minimum=-10, maksimum=wacc_p - 0.01, default=default_g_term, step=0.5)

    col1, col2, col3 = st.columns(3)
    with col1:
        if data_yf and data_yf.get('utang'):
            st.info(f"Utang dari yfinance: {fmt(data_yf['utang'] / pengali)} {nama_satuan}")
            utang = minta_float_st(f"Total utang berbunga ({nama_satuan})", minimum=0, default=data_yf['utang'] / pengali, step=1.0)
        else:
            utang = minta_float_st(f"Total utang berbunga ({nama_satuan})", minimum=0, default=0, step=1.0)
        utang *= pengali

    with col2:
        if data_yf and data_yf.get('kas'):
            st.info(f"Kas dari yfinance: {fmt(data_yf['kas'] / pengali)} {nama_satuan}")
            kas = minta_float_st(f"Kas & setara kas ({nama_satuan})", minimum=0, default=data_yf['kas'] / pengali, step=1.0)
        else:
            kas = minta_float_st(f"Kas & setara kas ({nama_satuan})", minimum=0, default=0, step=1.0)
        kas *= pengali

    with col3:
        if data_yf and data_yf.get('saham_beredar'):
            st.info(f"Saham dari yfinance: {fmt(data_yf['saham_beredar'], 0)}")
            saham = minta_float_st("Jumlah saham beredar (lembar)", minimum=1, default=data_yf['saham_beredar'], step=1.0)
        else:
            saham = minta_float_st("Jumlah saham beredar (lembar)", minimum=1, default=100, step=1.0)

    harga_pasar = minta_float_st("Harga pasar saat ini per lembar (isi 0 untuk melewati)", minimum=0, default=0, step=1.0)

    wacc, g, g_term = wacc_p / 100, g_p / 100, g_term_p / 100

    sub("Proyeksi Arus Kas")

    # Hitung proyeksi
    proyeksi_data = []
    total_pv = 0.0
    fcf_n = fcf0
    for n in range(1, tahun + 1):
        fcf_n = fcf0 * (1 + g) ** n
        faktor = 1 / (1 + wacc) ** n
        pv = fcf_n * faktor
        total_pv += pv
        proyeksi_data.append({
            "Tahun": n,
            "FCF Proyeksi": fcf_n,
            "Faktor Diskon": faktor,
            "Present Value": pv
        })

    df_proyeksi = pd.DataFrame(proyeksi_data)
    df_proyeksi["FCF Proyeksi"] = df_proyeksi["FCF Proyeksi"].apply(lambda x: rp_ringkas(x))
    df_proyeksi["Faktor Diskon"] = df_proyeksi["Faktor Diskon"].apply(lambda x: f"{fmt(x, 4)}")
    df_proyeksi["Present Value"] = df_proyeksi["Present Value"].apply(lambda x: rp_ringkas(x))
    st.dataframe(df_proyeksi, use_container_width=True, hide_index=True)

    terminal_value = fcf_n * (1 + g_term) / (wacc - g_term) if wacc > g_term else 0
    pv_terminal = terminal_value / (1 + wacc) ** tahun if terminal_value > 0 else 0
    enterprise = total_pv + pv_terminal
    equity = enterprise - utang + kas
    harga_wajar = equity / saham if saham > 0 else 0

    sub("Ringkasan Nilai")
    porsi_tv = pv_terminal / enterprise * 100 if enterprise else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(f"PV arus kas {tahun} tahun", rp_ringkas(total_pv))
    with col2:
        st.metric("Terminal Value", rp_ringkas(terminal_value))
    with col3:
        st.metric("PV Terminal Value", f"{rp_ringkas(pv_terminal)}\n({fmt(porsi_tv)}% dari total)", label_visibility="visible")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Enterprise Value", rp_ringkas(enterprise))
    with col2:
        st.metric("(-) Utang berbunga", rp_ringkas(utang))
    with col3:
        st.metric("(+) Kas", rp_ringkas(kas))

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Equity Value", rp_ringkas(equity))
    with col2:
        st.metric("Jumlah saham", f"{fmt(saham, 0)} lembar")

    tampilkan_kesimpulan("Discounted Cash Flow (DCF)", harga_wajar, harga_pasar)

    sub("Analisis Sensitivitas (Harga Wajar per Lembar)")

    daftar_wacc = [wacc_p - 2, wacc_p, wacc_p + 2]
    daftar_g = [g_p - 2, g_p, g_p + 2]

    sensitivitas_data = []
    for w_p in daftar_wacc:
        baris = {"WACC \\ g": f"{fmt(w_p, 1)}%"}
        w = w_p / 100
        for gg_p in daftar_g:
            gg = gg_p / 100
            if w <= g_term or w <= 0:
                baris[f"{fmt(gg_p, 1)}%"] = "n/a"
            else:
                pv_sum = sum(fcf0 * (1 + gg) ** n / (1 + w) ** n for n in range(1, tahun + 1))
                fcf_akhir = fcf0 * (1 + gg) ** tahun
                tv = fcf_akhir * (1 + g_term) / (w - g_term)
                ev = pv_sum + tv / (1 + w) ** tahun
                nilai = (ev - utang + kas) / saham
                baris[f"{fmt(gg_p, 1)}%"] = rp(nilai, 0)
        sensitivitas_data.append(baris)

    df_sensitif = pd.DataFrame(sensitivitas_data)
    st.dataframe(df_sensitif, use_container_width=True, hide_index=True)

    st.info("💡 Perhatikan: perubahan kecil pada WACC/growth mengubah hasil cukup jauh. Itulah mengapa DCF selalu dipakai bersama margin of safety.")


# ---------------------------------------------------------------------------
# Metode 3: Rasio PE & PBV
# ---------------------------------------------------------------------------

def metode_pe_pbv():
    judul("Rasio PE dan PBV (Relative Valuation)")

    st.markdown("""
    **Ide:** Membandingkan saham dengan rasio acuan (rata-rata historis emiten, rata-rata industri, atau rasio pesaing).

    - **Harga wajar (PE)** = EPS × PE acuan
    - **Harga wajar (PBV)** = BVPS × PBV acuan
    - **Harga wajar gabungan** = rata-rata berbobot dari keduanya

    - **PE** = Price to Earning Ratio (harga dibanding laba per saham)
    - **PBV** = Price to Book Value (harga dibanding nilai buku per saham)
    """)

    sub("Pilih Cara Input Data")

    pilihan_mode = ["Input manual EPS & BVPS"]
    if yf:
        pilihan_mode.append("Ambil data otomatis dari yfinance")

    cara = st.radio("", pilihan_mode, index=0, horizontal=True, key="pe_pbv_cara")

    if cara == pilihan_mode[0]:  # Input manual
        col1, col2 = st.columns(2)
        with col1:
            eps = minta_float_st("EPS - laba per lembar saham (Rp)", default=100)
        with col2:
            bvps = minta_float_st("BVPS - nilai buku per lembar saham (Rp)", default=500)

    else:  # Ambil dari yfinance
        ticker_input = st.text_input("Kode saham (contoh: BBCA.JK, ASII.JK):", "BBCA.JK", key="pe_pbv_ticker")
        if ticker_input and st.button("📥 Ambil data dari yfinance", key="pe_pbv_yf"):
            try:
                if VALIDATION_AVAILABLE:
                    ticker = validate_ticker(ticker_input)
                else:
                    ticker = ticker_input.upper()

                data_yf = ambil_data_yfinance(ticker)
                if data_yf and data_yf.get('eps') is not None and data_yf.get('book_value') is not None:
                    tampilkan_data_yfinance(data_yf)
                    eps = data_yf['eps']
                    bvps = data_yf['book_value']
                    st.success(f"✓ Data EPS dan BVPS berhasil diambil dari yfinance")
                else:
                    st.error(f"❌ Data tidak lengkap dari yfinance untuk {ticker}.")
                    col1, col2 = st.columns(2)
                    with col1:
                        eps = minta_float_st("EPS - laba per lembar saham (Rp)", default=100)
                    with col2:
                        bvps = minta_float_st("BVPS - nilai buku per lembar saham (Rp)", default=500)
            except ValueError as e:
                st.error(f"Error: {e}")
                return

    sub("Rasio Acuan")

    col1, col2, col3 = st.columns(3)
    with col1:
        pe_acuan = minta_float_st("PE acuan / target (x)", minimum=0, default=15, param_name="pe_ratio", step=0.5)
    with col2:
        pbv_acuan = minta_float_st("PBV acuan / target (x)", minimum=0, default=1.5, param_name="pbv_ratio", step=0.1)
    with col3:
        bobot_pe = minta_float_st("Bobot untuk metode PE (%)", minimum=0, maksimum=100, default=50, step=5)

    harga_pasar = minta_float_st("Harga pasar saat ini per lembar (isi 0 untuk melewati)", minimum=0, default=0, step=1.0)

    bobot_pbv = 100 - bobot_pe
    wajar_pe = eps * pe_acuan
    wajar_pbv = bvps * pbv_acuan
    wajar_gabungan = (wajar_pe * bobot_pe + wajar_pbv * bobot_pbv) / 100

    sub("Perhitungan")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Harga wajar via PE", f"{rp(eps)} × {fmt(pe_acuan)} = {rp(wajar_pe)}", label_visibility="visible")
    with col2:
        st.metric("Harga wajar via PBV", f"{rp(bvps)} × {fmt(pbv_acuan)} = {rp(wajar_pbv)}", label_visibility="visible")
    with col3:
        st.metric("Bobot", f"PE {fmt(bobot_pe, 0)}% / PBV {fmt(bobot_pbv, 0)}%", label_visibility="visible")

    if eps <= 0:
        st.warning("⚠️ EPS <= 0, sehingga valuasi berbasis PE tidak bermakna. Untuk emiten rugi, andalkan PBV atau metode lain.")
    if bvps <= 0:
        st.error("❌ BVPS <= 0 (ekuitas negatif), valuasi berbasis PBV tidak bermakna.")

    tampilkan_kesimpulan(
        f"Rasio PE & PBV (bobot {fmt(bobot_pe, 0)}/{fmt(bobot_pbv, 0)})",
        wajar_gabungan, harga_pasar,
    )

    if harga_pasar > 0:
        sub("Rasio pada Harga Pasar Sekarang")
        col1, col2 = st.columns(2)
        with col1:
            if eps != 0:
                st.metric("PE sekarang", f"{fmt(harga_pasar / eps)}x", f"(acuan {fmt(pe_acuan)}x)")
            else:
                st.info("PE sekarang: tidak terdefinisi (EPS = 0)")
        with col2:
            if bvps != 0:
                st.metric("PBV sekarang", f"{fmt(harga_pasar / bvps)}x", f"(acuan {fmt(pbv_acuan)}x)")
            else:
                st.info("PBV sekarang: tidak terdefinisi (BVPS = 0)")


# ---------------------------------------------------------------------------
# Ringkasan & penjelasan
# ---------------------------------------------------------------------------

def tampilkan_riwayat():
    judul("📊 Ringkasan Hasil Sesi Ini")

    if not st.session_state.riwayat:
        st.info("ℹ️ Belum ada perhitungan. Lakukan perhitungan metode 1, 2, atau 3 terlebih dahulu.")
        return

    riwayat_data = []
    for metode, wajar, pasar in st.session_state.riwayat:
        riwayat_data.append({
            "Metode": metode[:35],
            "Harga Wajar": rp(wajar)
        })

    df_riwayat = pd.DataFrame(riwayat_data)
    st.dataframe(df_riwayat, use_container_width=True, hide_index=True)

    nilai = [w for _, w, _ in st.session_state.riwayat]
    rata = sum(nilai) / len(nilai)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rata-rata semua metode", rp(rata))
    with col2:
        st.metric("Terendah (paling konservatif)", rp(min(nilai)))
    with col3:
        st.metric("Tertinggi (paling optimistis)", rp(max(nilai)))

    pasar = [p for _, _, p in st.session_state.riwayat if p > 0]
    if pasar:
        harga_pasar = pasar[-1]
        st.markdown(f"**Harga pasar terakhir yang diinput:** {rp(harga_pasar)}")
        murah = sum(1 for v in nilai if v > harga_pasar)
        st.success(f"✓ {murah} dari {len(nilai)} metode menilai saham ini di bawah nilai wajar.")

    st.info("💡 **Praktik umum:** Pakai beberapa metode lalu ambil rentang nilainya, bukan satu angka tunggal.")


def tampilkan_penjelasan():
    judul("📚 Penjelasan Singkat Ketiga Metode")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Graham Number", "DCF", "Rasio PE/PBV", "Istilah Penting", "Peringatan"
    ])

    with tab1:
        st.markdown("""
        ### 1. BENJAMIN GRAHAM (GRAHAM NUMBER)

        **Rumus:** √(22,5 × EPS × BVPS)

        **Data:** EPS, BVPS

        **Cocok untuk:**
        - Perusahaan mapan, berlaba stabil
        - Aset berwujud besar (bank, manufaktur, consumer goods)

        **Kelemahan:**
        - Terlalu ketat untuk perusahaan bertumbuh cepat
        - Tidak cocok untuk perusahaan aset ringan (teknologi, jasa)
        - Tidak bisa dipakai bila EPS atau BVPS negatif
        """)

    with tab2:
        st.markdown("""
        ### 2. DISCOUNTED CASH FLOW (DCF)

        **Rumus:** Jumlahkan PV dari FCF proyeksi + PV terminal value, lalu sesuaikan dengan utang & kas, bagi jumlah saham

        **Data:** FCF terakhir, growth, WACC, growth terminal, utang, kas, saham

        **Cocok untuk:**
        - Perusahaan dengan arus kas positif
        - Arus kas cukup terprediksi

        **Kelemahan:**
        - Sangat sensitif terhadap asumsi
        - WACC naik 1% saja bisa memotong nilai wajar puluhan persen
        - *Solusi:* Program menampilkan tabel sensitivitas untuk analisis lebih lanjut
        """)

    with tab3:
        st.markdown("""
        ### 3. RASIO PE DAN PBV (RELATIVE VALUATION)

        **Rumus:**
        - Harga wajar (PE) = EPS × PE acuan
        - Harga wajar (PBV) = BVPS × PBV acuan

        **Data:** EPS, BVPS, PE & PBV acuan (historis emiten / industri)

        **Cocok untuk:**
        - Perbandingan cepat antar emiten satu sektor

        **Kelemahan:**
        - Ikut salah kalau seluruh sektor sedang overvalued
        - Tidak bermakna saat EPS negatif
        """)

    with tab4:
        st.markdown("""
        ### ISTILAH PENTING

        **EPS** - Earning Per Share
        - Laba bersih dibagi jumlah saham beredar

        **BVPS** - Book Value Per Share
        - Total ekuitas dibagi jumlah saham beredar

        **FCF** - Free Cash Flow
        - Arus kas operasi dikurangi belanja modal (capex)

        **WACC** - Weighted Average Cost of Capital
        - Rata-rata biaya modal berbobot; dipakai sebagai discount rate
        - Semakin berisiko perusahaan, semakin tinggi WACC

        **MOS** - Margin of Safety
        - Selisih diskon harga pasar terhadap nilai wajar
        - Graham menyarankan minimal 20-30%

        ### DI MANA MENCARI DATANYA
        Laporan keuangan / laporan tahunan emiten (situs IDX atau situs perusahaan):
        - Laba bersih
        - Ekuitas
        - Arus kas operasi
        - Capex
        - Utang
        - Kas
        - Jumlah saham beredar
        """)

    with tab5:
        st.warning("""
        ⚠️ **PERINGATAN PENTING**

        Semua hasil hanyalah **estimasi dari asumsi yang Anda masukkan**.

        **Program ini adalah alat bantu belajar, BUKAN rekomendasi investasi.**

        Keputusan investasi harus mempertimbangkan:
        - Analisis kualitatif perusahaan
        - Kondisi pasar dan industri
        - Profil risiko personal Anda
        - Konsultasi dengan advisor keuangan profesional

        Gunakan program ini untuk pembelajaran dan riset saja.
        """)


# ---------------------------------------------------------------------------
# Menu utama
# ---------------------------------------------------------------------------

def main():
    # Configure page
    st.set_page_config(
        page_title="Kalkulator Harga Wajar Saham",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Header
    st.markdown("# 📈 Kalkulator Harga Wajar Saham")
    st.markdown("""
    **Estimasi harga wajar (nilai intrinsik) saham dengan 3 metode:**
    - Benjamin Graham (Graham Number)
    - Discounted Cash Flow (DCF)
    - Relative Valuation (Rasio PE & PBV)
    """)

    # Sidebar info
    with st.sidebar:
        st.markdown("## ℹ️ Informasi")

        st.markdown("### 📝 Catatan Input")
        st.info("""
        Penulisan angka:
        - Desimal: gunakan koma (1.250,75 atau 1250,75)
        - Titik berkelompok 3 angka = pemisah ribuan (1.500 = 1500)
        """)

        if yf is None:
            st.warning("""
            ⚠️ **yfinance tidak tersedia**

            Untuk fitur pengambilan data otomatis dari internet:
            ```bash
            pip install yfinance
            ```
            Anda masih bisa menggunakan kalkulator dengan input manual.
            """)
        else:
            st.success("✓ **yfinance tersedia** - Bisa ambil data otomatis dari internet")

        if VALIDATION_AVAILABLE:
            st.success("""
            ✓ **Security validation AKTIF**
            - Ticker format (KODE.JK)
            - WACC range (0.5% - 20%)
            - Growth rate (-10% - 30%)
            - PE/PBV ratio (1x-100x, 0.1x-10x)
            """)
        else:
            st.warning("""
            ⚠️ **Security validation tidak aktif**

            Pastikan `input_validation.py` ada di folder yang sama.
            """)

    # Main content with tabs
    tab_graham, tab_dcf, tab_pe_pbv, tab_ringkasan, tab_penjelasan = st.tabs([
        "1️⃣ Graham Number",
        "2️⃣ DCF",
        "3️⃣ PE & PBV",
        "📊 Ringkasan",
        "📚 Penjelasan"
    ])

    with tab_graham:
        st.markdown("---")
        metode_graham()

    with tab_dcf:
        st.markdown("---")
        metode_dcf()

    with tab_pe_pbv:
        st.markdown("---")
        metode_pe_pbv()

    with tab_ringkasan:
        st.markdown("---")
        tampilkan_riwayat()

    with tab_penjelasan:
        st.markdown("---")
        tampilkan_penjelasan()

    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📖 Disclaimer")
        st.markdown("""
        Hasil hanyalah **estimasi** dari asumsi Anda.

        **BUKAN rekomendasi investasi.**
        """)
    with col2:
        st.markdown("### 💡 Tips")
        st.markdown("""
        Gunakan **beberapa metode** untuk perbandingan.

        Ambil **rentang nilai** bukan angka tunggal.
        """)
    with col3:
        st.markdown("### 🎯 Margin of Safety")
        st.markdown(f"""
        Default: **{fmt(MOS_DEFAULT, 0)}%**

        Untuk estimasi konservatif.
        """)


if __name__ == "__main__":
    main()
