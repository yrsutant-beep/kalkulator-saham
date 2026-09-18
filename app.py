"""
Aplikasi Web Streamlit untuk Kalkulator Harga Wajar Saham
=========================================================

Aplikasi interaktif yang menggunakan logika dari kalkulator_saham.py
untuk menghitung estimasi harga wajar saham dengan 3 metode:
  1. Benjamin Graham (Graham Number)
  2. Discounted Cash Flow (DCF)
  3. Relative Valuation (PE & PBV)
"""

import streamlit as st
import pandas as pd
from kalkulator_saham import (
    ambil_data_yfinance,
    normalisasi_angka,
    fmt,
    rp,
    rp_ringkas,
)

# Config halaman
st.set_page_config(
    page_title="Kalkulator Harga Wajar Saham",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS custom untuk styling
st.markdown("""
    <style>
    .metric-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .result-box {
        background-color: #e8f5e9;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4caf50;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fff3e0;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff9800;
        margin: 10px 0;
    }
    .error-box {
        background-color: #ffebee;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #f44336;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'riwayat' not in st.session_state:
    st.session_state.riwayat = []

# Utility functions
def fmt_indo(nilai, desimal=2):
    """Format angka dengan pemisah ribuan titik dan desimal koma (gaya Indonesia)."""
    return fmt(nilai, desimal)

def tampilkan_hasil(metode, harga_wajar, harga_pasar=0, info_tambahan=None):
    """Tampilkan hasil perhitungan harga wajar saham."""
    st.markdown("### 📊 HASIL PERHITUNGAN")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Metode", metode)
        st.metric("Harga Wajar/Lembar", rp(harga_wajar))

    with col2:
        if harga_pasar > 0:
            mos = (harga_wajar - harga_pasar) / harga_wajar * 100
            upside = (harga_wajar - harga_pasar) / harga_pasar * 100
            st.metric("Harga Pasar", rp(harga_pasar))
            st.metric("Margin of Safety", f"{fmt_indo(mos)}%")
            st.metric("Potensi Upside", f"{fmt_indo(upside)}%")

    # Analisis MOS
    if harga_pasar > 0:
        st.markdown("---")
        if harga_wajar <= 0:
            st.markdown('<div class="error-box"><strong>⚠️ Harga wajar ≤ 0</strong><br>Berdasarkan asumsi Anda, saham ini tidak punya nilai wajar positif.</div>', unsafe_allow_html=True)
        else:
            mos = (harga_wajar - harga_pasar) / harga_wajar * 100
            harga_beli_ideal = harga_wajar * 0.7  # MOS 30%

            st.write(f"**Harga beli ideal (MOS 30%):** {rp(harga_beli_ideal)}")

            if mos >= 30:
                status = "🟢 UNDERVALUED - Diskon cukup besar terhadap nilai wajar"
                box_class = "result-box"
            elif mos > 0:
                status = "🟡 SEDIKIT DI BAWAH nilai wajar - Margin of safety masih tipis"
                box_class = "warning-box"
            elif mos > -10:
                status = "⚪ WAJAR / FAIRLY VALUED - Harga mendekati nilai wajar"
                box_class = "metric-box"
            else:
                status = "🔴 OVERVALUED - Harga di atas nilai wajar"
                box_class = "error-box"

            st.markdown(f'<div class="{box_class}"><strong>{status}</strong></div>', unsafe_allow_html=True)

    # Info tambahan
    if info_tambahan:
        st.markdown("---")
        st.markdown("### 📋 INFO TAMBAHAN")
        for label, nilai in info_tambahan.items():
            st.write(f"**{label}:** {nilai}")

    # Simpan ke riwayat
    st.session_state.riwayat.append({
        'metode': metode,
        'harga_wajar': harga_wajar,
        'harga_pasar': harga_pasar,
    })

# ==================== METODE 1: BENJAMIN GRAHAM ====================
def metode_graham():
    st.markdown("# 1️⃣ Metode Benjamin Graham (Graham Number)")
    st.markdown("""
    **Rumus:** Harga Wajar = √(22,5 × EPS × BVPS)

    - Angka 22,5 = batas konservatif Graham (PER maks 15 × PBV maks 1,5)
    - EPS = laba per lembar saham
    - BVPS = nilai buku per lembar saham
    - **Cocok untuk:** Perusahaan mapan, berlaba stabil, aset berwujud besar
    """)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📥 INPUT DATA")
        input_mode = st.radio(
            "Pilih cara input data:",
            ["Input Langsung EPS & BVPS", "Hitung dari Laba & Ekuitas", "Ambil dari yfinance"],
            key="graham_mode"
        )

    data_yf = None

    if input_mode == "Input Langsung EPS & BVPS":
        eps = st.number_input("EPS (Rp) - laba per lembar saham", min_value=0.0, step=100.0, key="graham_eps")
        bvps = st.number_input("BVPS (Rp) - nilai buku per lembar saham", min_value=0.0, step=100.0, key="graham_bvps")

    elif input_mode == "Hitung dari Laba & Ekuitas":
        st.write("**Pilih satuan:**")
        satuan = st.selectbox(
            "Satuan untuk laba & ekuitas:",
            ["Rupiah", "Juta", "Miliar", "Triliun"],
            key="graham_satuan"
        )
        pengali = {"Rupiah": 1, "Juta": 1_000_000, "Miliar": 1_000_000_000, "Triliun": 1_000_000_000_000}[satuan]

        laba = st.number_input(f"Laba bersih setahun ({satuan})", min_value=0.0, step=1.0, key="graham_laba") * pengali
        ekuitas = st.number_input(f"Total ekuitas/book value ({satuan})", min_value=0.0, step=1.0, key="graham_ekuitas") * pengali
        saham = st.number_input("Jumlah saham beredar (lembar)", min_value=1.0, step=1.0, key="graham_saham")

        eps = laba / saham if saham > 0 else 0
        bvps = ekuitas / saham if saham > 0 else 0

        st.write(f"**Hasil perhitungan:**")
        st.write(f"- EPS = {rp_ringkas(laba)} / {fmt_indo(saham, 0)} lembar = {rp(eps)}")
        st.write(f"- BVPS = {rp_ringkas(ekuitas)} / {fmt_indo(saham, 0)} lembar = {rp(bvps)}")

    else:  # Ambil dari yfinance
        ticker = st.text_input("Kode saham (contoh: BBCA.JK, ASII.JK)", key="graham_ticker")
        if ticker:
            with st.spinner(f"Mengambil data {ticker} dari yfinance..."):
                data_yf = ambil_data_yfinance(ticker)

            if data_yf and data_yf.get('eps') and data_yf.get('book_value'):
                st.success(f"✓ Data berhasil diambil dari yfinance")
                st.write(f"**{data_yf['nama']}** ({data_yf['ticker']})")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("EPS", rp(data_yf['eps']))
                with col2:
                    st.metric("BVPS", rp(data_yf['book_value']))
                with col3:
                    st.metric("Harga Sekarang", rp(data_yf.get('price', 0)))

                eps = data_yf['eps']
                bvps = data_yf['book_value']
            else:
                st.error("❌ Data tidak lengkap dari yfinance. Gunakan input manual.")
                eps = st.number_input("EPS (Rp)", min_value=0.0, step=100.0, key="graham_eps_manual")
                bvps = st.number_input("BVPS (Rp)", min_value=0.0, step=100.0, key="graham_bvps_manual")

    harga_pasar = st.number_input("Harga pasar saat ini (Rp, isi 0 untuk melewati)", min_value=0.0, step=100.0, key="graham_pasar")

    with col2:
        st.subheader("🧮 PERHITUNGAN")

        if st.button("Hitung Graham Number", key="btn_graham"):
            if eps <= 0 or bvps <= 0:
                st.markdown('<div class="error-box"><strong>❌ Perhitungan tidak bisa dilakukan</strong><br>', unsafe_allow_html=True)
                if eps <= 0:
                    st.write(f"- EPS = {rp(eps)} (perusahaan rugi atau tidak untung)")
                if bvps <= 0:
                    st.write(f"- BVPS = {rp(bvps)} (ekuitas negatif)")
                st.write("Metode Graham hanya berlaku untuk perusahaan yang profitabel dengan ekuitas positif.</div>", unsafe_allow_html=True)
            else:
                graham = (22.5 * eps * bvps) ** 0.5
                st.write(f"**Perhitungan:** √(22,5 × {fmt_indo(eps)} × {fmt_indo(bvps)}) = {rp(graham)}")

                info_tambahan = {
                    f"PER pada harga wajar": f"{fmt_indo(graham / eps)}x",
                    f"PBV pada harga wajar": f"{fmt_indo(graham / bvps)}x",
                }

                if harga_pasar > 0:
                    info_tambahan["PER pada harga pasar"] = f"{fmt_indo(harga_pasar / eps)}x"
                    info_tambahan["PBV pada harga pasar"] = f"{fmt_indo(harga_pasar / bvps)}x"

                tampilkan_hasil("Benjamin Graham (Graham Number)", graham, harga_pasar, info_tambahan)

# ==================== METODE 2: DISCOUNTED CASH FLOW ====================
def metode_dcf():
    st.markdown("# 2️⃣ Metode Discounted Cash Flow (DCF)")
    st.markdown("""
    **Konsep:** Nilai perusahaan = seluruh arus kas masa depan yang didiskontokan ke nilai sekarang

    **Rumus:**
    - FCF tahun ke-n = FCF₀ × (1 + g)ⁿ
    - Enterprise Value = Σ PV(FCF) + PV(Terminal Value)
    - Equity Value = Enterprise Value - Utang + Kas
    - Harga wajar = Equity Value / Jumlah Saham
    """)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📥 INPUT DATA")
        input_mode = st.radio(
            "Pilih cara input data:",
            ["Input Manual", "Ambil dari yfinance"],
            key="dcf_mode"
        )

        data_yf = None
        if input_mode == "Ambil dari yfinance":
            ticker = st.text_input("Kode saham (contoh: BBCA.JK, ASII.JK)", key="dcf_ticker")
            if ticker:
                with st.spinner(f"Mengambil data {ticker} dari yfinance..."):
                    data_yf = ambil_data_yfinance(ticker)

                if data_yf and (data_yf.get('fcf') or data_yf.get('kas')):
                    st.success(f"✓ Data berhasil diambil")
                    st.write(f"**{data_yf['nama']}** ({data_yf['ticker']})")

        st.write("**Pilih satuan:**")
        satuan = st.selectbox(
            "Satuan untuk FCF, utang, dan kas:",
            ["Rupiah", "Juta", "Miliar", "Triliun"],
            key="dcf_satuan"
        )
        pengali = {"Rupiah": 1, "Juta": 1_000_000, "Miliar": 1_000_000_000, "Triliun": 1_000_000_000_000}[satuan]

        # FCF
        if data_yf and data_yf.get('fcf'):
            fcf0 = data_yf['fcf'] / pengali
            st.write(f"**FCF (dari yfinance):** {fmt_indo(fcf0)} {satuan}")
        else:
            fcf0 = st.number_input(f"Free Cash Flow tahun terakhir ({satuan})", min_value=0.0, step=1.0, key="dcf_fcf") * pengali

        # Periode & asumsi
        tahun = st.slider("Periode proyeksi (tahun)", min_value=1, max_value=30, value=5, key="dcf_tahun")
        wacc_p = st.slider("WACC / discount rate (% per tahun)", min_value=0.1, max_value=30.0, value=10.0, step=0.5, key="dcf_wacc")
        g_p = st.slider("Growth rate FCF selama proyeksi (% per tahun)", min_value=-50.0, max_value=50.0, value=5.0, step=0.5, key="dcf_g")
        g_term_p = st.slider("Growth terminal / perpetual (% per tahun)", min_value=-5.0, max_value=min(10.0, wacc_p - 0.5), value=min(3.0, wacc_p - 1.0), step=0.5, key="dcf_gterm")

        # Utang & Kas
        if data_yf and data_yf.get('utang'):
            utang = data_yf['utang'] / pengali
            st.write(f"**Utang (dari yfinance):** {fmt_indo(utang)} {satuan}")
        else:
            utang = st.number_input(f"Total utang berbunga ({satuan})", min_value=0.0, step=1.0, key="dcf_utang") * pengali

        if data_yf and data_yf.get('kas'):
            kas = data_yf['kas'] / pengali
            st.write(f"**Kas (dari yfinance):** {fmt_indo(kas)} {satuan}")
        else:
            kas = st.number_input(f"Kas & setara kas ({satuan})", min_value=0.0, step=1.0, key="dcf_kas") * pengali

        # Saham beredar
        if data_yf and data_yf.get('saham_beredar'):
            saham = data_yf['saham_beredar']
            st.write(f"**Saham beredar (dari yfinance):** {fmt_indo(saham, 0)} lembar")
        else:
            saham = st.number_input("Jumlah saham beredar (lembar)", min_value=1.0, step=1.0, key="dcf_saham")

        harga_pasar = st.number_input("Harga pasar saat ini (Rp, isi 0 untuk melewati)", min_value=0.0, step=100.0, key="dcf_pasar")

    with col2:
        st.subheader("🧮 PERHITUNGAN")

        if st.button("Hitung Nilai Wajar DCF", key="btn_dcf"):
            if fcf0 <= 0:
                st.markdown('<div class="warning-box"><strong>⚠️ Catatan:</strong> FCF ≤ 0. DCF akan menghasilkan nilai negatif/tidak bermakna.</div>', unsafe_allow_html=True)

            if wacc_p <= g_term_p:
                st.error("❌ WACC harus lebih besar dari growth terminal!")
            else:
                wacc = wacc_p / 100
                g = g_p / 100
                g_term = g_term_p / 100

                # Perhitungan DCF
                total_pv = 0.0
                data_proyeksi = []
                fcf_n = fcf0

                for n in range(1, tahun + 1):
                    fcf_n = fcf0 * (1 + g) ** n
                    faktor = 1 / (1 + wacc) ** n
                    pv = fcf_n * faktor
                    total_pv += pv
                    data_proyeksi.append({
                        "Tahun": n,
                        "FCF Proyeksi": rp_ringkas(fcf_n),
                        "Faktor Diskon": fmt_indo(faktor, 4),
                        "Present Value": rp_ringkas(pv),
                    })

                st.markdown("#### Proyeksi Arus Kas")
                st.dataframe(pd.DataFrame(data_proyeksi), use_container_width=True)

                # Terminal Value
                terminal_value = fcf_n * (1 + g_term) / (wacc - g_term)
                pv_terminal = terminal_value / (1 + wacc) ** tahun
                enterprise = total_pv + pv_terminal
                equity = enterprise - utang + kas
                harga_wajar = equity / saham

                st.markdown("#### Ringkasan Nilai")
                porsi_tv = pv_terminal / enterprise * 100 if enterprise else 0

                ringkasan_data = {
                    "Keterangan": [
                        f"PV arus kas {tahun} tahun",
                        "Terminal Value",
                        "PV Terminal Value",
                        "Enterprise Value",
                        "(-) Utang berbunga",
                        "(+) Kas",
                        "Equity Value",
                        "Jumlah saham",
                    ],
                    "Nilai": [
                        rp_ringkas(total_pv),
                        rp_ringkas(terminal_value),
                        f"{rp_ringkas(pv_terminal)} ({fmt_indo(porsi_tv)}% dari total)",
                        rp_ringkas(enterprise),
                        rp_ringkas(utang),
                        rp_ringkas(kas),
                        rp_ringkas(equity),
                        f"{fmt_indo(saham, 0)} lembar",
                    ]
                }
                st.dataframe(pd.DataFrame(ringkasan_data), use_container_width=True)

                tampilkan_hasil("Discounted Cash Flow (DCF)", harga_wajar, harga_pasar)

                # Analisis Sensitivitas
                st.markdown("#### Analisis Sensitivitas (harga wajar per lembar)")
                daftar_wacc = [wacc_p - 2, wacc_p, wacc_p + 2]
                daftar_g = [g_p - 2, g_p, g_p + 2]

                sensitivitas = []
                for w_p in daftar_wacc:
                    row = {"WACC %": fmt_indo(w_p, 1)}
                    w = w_p / 100
                    for gg_p in daftar_g:
                        gg = gg_p / 100
                        if w <= g_term or w <= 0:
                            row[f"g={fmt_indo(gg_p, 1)}%"] = "n/a"
                        else:
                            pv_sum = sum(fcf0 * (1 + gg) ** n / (1 + w) ** n for n in range(1, tahun + 1))
                            fcf_akhir = fcf0 * (1 + gg) ** tahun
                            tv = fcf_akhir * (1 + g_term) / (w - g_term)
                            ev = pv_sum + tv / (1 + w) ** tahun
                            nilai = (ev - utang + kas) / saham
                            row[f"g={fmt_indo(gg_p, 1)}%"] = rp(nilai, 0)
                    sensitivitas.append(row)

                st.dataframe(pd.DataFrame(sensitivitas), use_container_width=True)
                st.info("💡 Perhatikan: perubahan kecil pada WACC/growth mengubah hasil cukup jauh. Gunakan dengan margin of safety!")

# ==================== METODE 3: PE & PBV ====================
def metode_pe_pbv():
    st.markdown("# 3️⃣ Metode Rasio PE & PBV (Relative Valuation)")
    st.markdown("""
    **Konsep:** Membandingkan saham dengan rasio acuan (rata-rata historis, industri, atau pesaing)

    **Rumus:**
    - Harga wajar (PE) = EPS × PE acuan
    - Harga wajar (PBV) = BVPS × PBV acuan
    - Harga wajar gabungan = rata-rata berbobot dari keduanya
    """)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📥 INPUT DATA")
        input_mode = st.radio(
            "Pilih cara input data:",
            ["Input Manual", "Ambil dari yfinance"],
            key="pe_mode"
        )

        data_yf = None
        if input_mode == "Ambil dari yfinance":
            ticker = st.text_input("Kode saham (contoh: BBCA.JK, ASII.JK)", key="pe_ticker")
            if ticker:
                with st.spinner(f"Mengambil data {ticker} dari yfinance..."):
                    data_yf = ambil_data_yfinance(ticker)

                if data_yf and data_yf.get('eps') and data_yf.get('book_value'):
                    st.success(f"✓ Data berhasil diambil")
                    st.write(f"**{data_yf['nama']}** ({data_yf['ticker']})")
                    st.metric("EPS", rp(data_yf['eps']))
                    st.metric("BVPS", rp(data_yf['book_value']))
                    eps = data_yf['eps']
                    bvps = data_yf['book_value']
                else:
                    st.error("❌ Data tidak lengkap dari yfinance.")
                    eps = st.number_input("EPS (Rp)", min_value=0.0, step=100.0, key="pe_eps_manual")
                    bvps = st.number_input("BVPS (Rp)", min_value=0.0, step=100.0, key="pe_bvps_manual")
        else:
            eps = st.number_input("EPS - laba per lembar saham (Rp)", min_value=0.0, step=100.0, key="pe_eps")
            bvps = st.number_input("BVPS - nilai buku per lembar saham (Rp)", min_value=0.0, step=100.0, key="pe_bvps")

        pe_acuan = st.number_input("PE acuan / target (x)", min_value=0.1, value=15.0, step=0.5, key="pe_acuan")
        pbv_acuan = st.number_input("PBV acuan / target (x)", min_value=0.1, value=1.5, step=0.1, key="pbv_acuan")
        bobot_pe = st.slider("Bobot untuk metode PE (%)", min_value=0, max_value=100, value=50, step=5, key="bobot_pe")

        harga_pasar = st.number_input("Harga pasar saat ini (Rp, isi 0 untuk melewati)", min_value=0.0, step=100.0, key="pe_pasar")

    with col2:
        st.subheader("🧮 PERHITUNGAN")

        if st.button("Hitung Harga Wajar PE & PBV", key="btn_pe"):
            bobot_pbv = 100 - bobot_pe
            wajar_pe = eps * pe_acuan
            wajar_pbv = bvps * pbv_acuan
            wajar_gabungan = (wajar_pe * bobot_pe + wajar_pbv * bobot_pbv) / 100

            st.markdown("#### Perhitungan")
            st.write(f"**Harga wajar via PE:** {rp(eps)} × {fmt_indo(pe_acuan)} = {rp(wajar_pe)}")
            st.write(f"**Harga wajar via PBV:** {rp(bvps)} × {fmt_indo(pbv_acuan)} = {rp(wajar_pbv)}")
            st.write(f"**Bobot:** PE {bobot_pe}% / PBV {bobot_pbv}%")
            st.write(f"**Harga wajar gabungan:** {rp(wajar_gabungan)}")

            if eps <= 0:
                st.markdown('<div class="warning-box"><strong>⚠️ EPS ≤ 0</strong><br>Valuasi berbasis PE tidak bermakna. Andalkan PBV atau metode lain.</div>', unsafe_allow_html=True)

            if bvps <= 0:
                st.markdown('<div class="warning-box"><strong>⚠️ BVPS ≤ 0</strong><br>Ekuitas negatif, valuasi berbasis PBV tidak bermakna.</div>', unsafe_allow_html=True)

            info_tambahan = {}
            if harga_pasar > 0 and eps != 0:
                info_tambahan["PE pada harga pasar"] = f"{fmt_indo(harga_pasar / eps)}x (acuan {fmt_indo(pe_acuan)}x)"
            if harga_pasar > 0 and bvps != 0:
                info_tambahan["PBV pada harga pasar"] = f"{fmt_indo(harga_pasar / bvps)}x (acuan {fmt_indo(pbv_acuan)}x)"

            tampilkan_hasil(f"Rasio PE & PBV (bobot {bobot_pe}/{bobot_pbv})", wajar_gabungan, harga_pasar, info_tambahan)

# ==================== HALAMAN RINGKASAN ====================
def halaman_riwayat():
    st.markdown("# 📋 Ringkasan Hasil Sesi Ini")

    if not st.session_state.riwayat:
        st.info("Belum ada perhitungan. Jalankan salah satu metode terlebih dahulu.")
    else:
        df_riwayat = pd.DataFrame(st.session_state.riwayat)

        st.markdown("### Daftar Perhitungan")
        st.dataframe(
            df_riwayat.rename(columns={
                'metode': 'Metode',
                'harga_wajar': 'Harga Wajar',
                'harga_pasar': 'Harga Pasar'
            }),
            use_container_width=True
        )

        # Statistik
        nilai = [r['harga_wajar'] for r in st.session_state.riwayat]
        rata = sum(nilai) / len(nilai)

        st.markdown("### Statistik")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Jumlah Metode", len(nilai))
        with col2:
            st.metric("Rata-rata", rp(rata))
        with col3:
            st.metric("Terendah (Konservatif)", rp(min(nilai)))
        with col4:
            st.metric("Tertinggi (Optimistis)", rp(max(nilai)))

        # Perbandingan dengan harga pasar
        pasar = [r['harga_pasar'] for r in st.session_state.riwayat if r['harga_pasar'] > 0]
        if pasar:
            harga_pasar = pasar[-1]
            st.markdown("---")
            st.write(f"**Harga pasar terakhir yang diinput:** {rp(harga_pasar)}")
            murah = sum(1 for v in nilai if v > harga_pasar)
            st.write(f"**{murah} dari {len(nilai)} metode menilai saham ini di bawah nilai wajar (undervalued).**")

        # Saran
        st.info("💡 **Praktik umum:** Gunakan beberapa metode lalu ambil rentang nilainya, bukan satu angka tunggal.")

        if st.button("🗑️ Hapus Riwayat", key="btn_hapus_riwayat"):
            st.session_state.riwayat = []
            st.rerun()

# ==================== HALAMAN PENJELASAN ====================
def halaman_penjelasan():
    st.markdown("# ℹ️ Penjelasan Metode & Istilah")

    with st.expander("1️⃣ Benjamin Graham (Graham Number)", expanded=False):
        st.markdown("""
        **Rumus:** Harga Wajar = √(22,5 × EPS × BVPS)

        **Data yang dibutuhkan:**
        - EPS: laba per lembar saham
        - BVPS: nilai buku per lembar saham

        **Cocok untuk:**
        - Perusahaan mapan dan berlaba stabil
        - Perusahaan dengan aset berwujud besar (bank, manufaktur, consumer goods)

        **Kelemahan:**
        - Terlalu ketat untuk perusahaan bertumbuh cepat
        - Tidak cocok untuk perusahaan aset ringan (teknologi, jasa)
        - Tidak bisa dipakai jika EPS atau BVPS negatif
        """)

    with st.expander("2️⃣ Discounted Cash Flow (DCF)", expanded=False):
        st.markdown("""
        **Konsep:** Nilai perusahaan = seluruh arus kas masa depan yang didiskontokan ke nilai sekarang

        **Data yang dibutuhkan:**
        - FCF: Free Cash Flow terakhir
        - Growth rate: pertumbuhan FCF yang diproyeksikan
        - WACC: Weighted Average Cost of Capital (discount rate)
        - Growth terminal: pertumbuhan perpetual
        - Utang, kas, jumlah saham beredar

        **Cocok untuk:**
        - Perusahaan dengan arus kas positif dan terprediksi

        **Kelemahan:**
        - Sangat sensitif terhadap asumsi
        - Perubahan WACC 1% saja bisa memotong nilai wajar 20%+
        - Hasil sangat bergantung pada proyeksi masa depan

        **Saran:** Selalu gunakan dengan margin of safety dan tabel sensitivitas!
        """)

    with st.expander("3️⃣ Rasio PE & PBV (Relative Valuation)", expanded=False):
        st.markdown("""
        **Rumus:**
        - Harga wajar (PE) = EPS × PE acuan
        - Harga wajar (PBV) = BVPS × PBV acuan

        **Data yang dibutuhkan:**
        - EPS & BVPS perusahaan
        - PE & PBV acuan (rata-rata historis, industri, atau pesaing)

        **Cocok untuk:**
        - Perbandingan cepat antar emiten satu sektor
        - Ketika data historis perusahaan tersedia

        **Kelemahan:**
        - Ikut salah kalau seluruh sektor sedang overvalued
        - Tidak bermakna saat EPS negatif
        - Rentan terhadap manipulasi rasio pasar
        """)

    st.markdown("---")

    with st.expander("📖 Istilah Penting", expanded=False):
        st.markdown("""
        **EPS (Earning Per Share)**
        - Laba bersih perusahaan dibagi jumlah saham beredar
        - Mengukur berapa banyak keuntungan per lembar saham

        **BVPS (Book Value Per Share)**
        - Total ekuitas perusahaan dibagi jumlah saham beredar
        - Mengukur nilai aset bersih per lembar saham

        **FCF (Free Cash Flow)**
        - Arus kas dari operasi dikurangi belanja modal (capex)
        - Uang tunai yang benar-benar bisa digunakan perusahaan

        **WACC (Weighted Average Cost of Capital)**
        - Rata-rata biaya modal berbobot (dari utang dan ekuitas)
        - Digunakan sebagai discount rate dalam DCF
        - Semakin berisiko perusahaan, semakin tinggi WACC

        **MOS (Margin of Safety)**
        - Selisih diskon harga pasar terhadap nilai wajar
        - Benjamin Graham menyarankan minimal 20-30%
        - Contoh: jika nilai wajar Rp 10.000 dan pasar Rp 7.000, MOS = 30%

        **PE Ratio (Price-to-Earning)**
        - Harga saham dibagi EPS
        - Mengukur berapa tahun investor perlu untuk balik modal dari profit

        **PBV Ratio (Price-to-Book Value)**
        - Harga saham dibagi BVPS
        - Membandingkan nilai pasar dengan nilai buku
        """)

    st.markdown("---")

    with st.expander("📚 Sumber Data", expanded=False):
        st.markdown("""
        **Laporan Keuangan Publik:**
        - Situs Bursa Efek Indonesia (IDX): www.idx.co.id
        - Situs investor relations perusahaan
        - Laporan tahunan (annual report)

        **Data yang dapat dicari:**
        - Laba bersih (net income)
        - Total ekuitas (total equity)
        - Arus kas operasi (operating cash flow)
        - Belanja modal / capex (capital expenditure)
        - Total utang (total debt)
        - Kas dan setara kas (cash and equivalents)
        - Jumlah saham beredar (shares outstanding)

        **Platform analisis:**
        - yfinance (untuk data pasar global)
        - Aplikasi trading lokal (Gotrade, Stockbit, dll)
        - Platform riset saham lokal
        """)

    st.markdown("---")

    st.warning("""
    ⚠️ **PERINGATAN PENTING**

    Semua hasil perhitungan hanyalah estimasi berdasarkan asumsi yang Anda masukkan.

    **Program ini adalah alat bantu BELAJAR, BUKAN rekomendasi investasi.**

    Selalu lakukan riset lebih lanjut, konsultasi dengan profesional keuangan,
    dan gunakan margin of safety sebelum membuat keputusan investasi.
    """)

# ==================== SIDEBAR & NAVIGASI ====================
def main():
    st.sidebar.markdown("# 📊 Kalkulator Saham")
    st.sidebar.markdown("Kalkulator harga wajar saham dengan 3 metode")
    st.sidebar.markdown("---")

    halaman = st.sidebar.radio(
        "Pilih Menu:",
        ["🏠 Beranda", "1️⃣ Graham", "2️⃣ DCF", "3️⃣ PE & PBV", "📋 Riwayat", "ℹ️ Penjelasan"],
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    **Tentang Aplikasi**

    Aplikasi ini menggunakan logika dari `kalkulator_saham.py` untuk menghitung:
    1. **Benjamin Graham** - Graham Number
    2. **DCF** - Discounted Cash Flow
    3. **PE & PBV** - Relative Valuation

    *Sumber data: yfinance API*
    """)

    # Render halaman
    if halaman == "🏠 Beranda":
        st.markdown("# 📈 Kalkulator Harga Wajar Saham")
        st.markdown("""
        Selamat datang! Aplikasi ini membantu Anda menghitung estimasi harga wajar saham
        menggunakan **3 metode berbeda**:

        ### 🎯 3 Metode Valuasi

        1. **Benjamin Graham (Graham Number)**
           - Rumus sederhana: √(22,5 × EPS × BVPS)
           - Cocok untuk perusahaan mapan dengan profit stabil
           - **Akses:** Menu 1️⃣ Graham

        2. **Discounted Cash Flow (DCF)**
           - Proyeksikan arus kas masa depan dan diskontokan ke nilai sekarang
           - Cocok untuk perusahaan dengan cashflow positif & terprediksi
           - Lebih sophisticated dan sensitive terhadap asumsi
           - **Akses:** Menu 2️⃣ DCF

        3. **Rasio PE & PBV (Relative Valuation)**
           - Bandingkan dengan rasio acuan industri atau historis
           - Cocok untuk perbandingan antar emiten satu sektor
           - **Akses:** Menu 3️⃣ PE & PBV

        ### 📋 Fitur Utama
        - ✅ **Input Manual** - Masukkan data sendiri
        - ✅ **yfinance Integration** - Ambil data otomatis dari internet
        - ✅ **Margin of Safety** - Analisis risiko investasi
        - ✅ **Sensitivity Analysis** - Lihat perubahan hasil (DCF)
        - ✅ **Riwayat Perhitungan** - Simpan & bandingkan hasil

        ### 🚀 Cara Mulai
        1. Pilih metode di menu sidebar (1️⃣, 2️⃣, atau 3️⃣)
        2. Input data saham (manual atau ambil dari yfinance)
        3. Masukkan asumsi yang sesuai
        4. Klik tombol "Hitung"
        5. Lihat hasil dan analisisnya

        ### ⚠️ Penting!
        - **Ini bukan rekomendasi investasi**, hanya alat bantu belajar
        - Selalu gunakan **margin of safety** (diskon 20-30%)
        - **Jangan andalkan satu metode saja** - gunakan beberapa metode dan ambil rentangnya
        - Cek **sensitivitas asumsi** (terutama untuk DCF)
        - **Riset lebih lanjut** sebelum investasi

        ---

        **Mulai sekarang:** Pilih menu di sidebar → Input data → Hitung!
        """)

        # Sample calculation cards
        st.markdown("### 💡 Contoh Kasus")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.info("""
            **Graham Number**

            Cocok jika Anda punya:
            - Data EPS & BVPS
            - Perusahaan stabil & mapan
            - 5 menit waktu
            """)

        with col2:
            st.info("""
            **DCF**

            Cocok jika Anda punya:
            - Data FCF terbaru
            - Proyeksi pertumbuhan
            - 15 menit waktu
            """)

        with col3:
            st.info("""
            **PE & PBV**

            Cocok jika Anda punya:
            - Data EPS & BVPS
            - Rasio acuan industri
            - 5 menit waktu
            """)

    elif halaman == "1️⃣ Graham":
        metode_graham()
    elif halaman == "2️⃣ DCF":
        metode_dcf()
    elif halaman == "3️⃣ PE & PBV":
        metode_pe_pbv()
    elif halaman == "📋 Riwayat":
        halaman_riwayat()
    elif halaman == "ℹ️ Penjelasan":
        halaman_penjelasan()

if __name__ == "__main__":
    main()
