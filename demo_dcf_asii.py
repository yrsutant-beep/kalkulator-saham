#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Demo script: Menjalankan kalkulasi DCF dengan ASII.JK menggunakan yfinance
"""

import sys
sys.path.insert(0, '.')

from kalkulator_saham import (
    ambil_data_yfinance, tampilkan_data_yfinance,
    fmt, rp, rp_ringkas, judul, sub, MOS_DEFAULT
)

def demo_dcf_asii():
    """Demo: Kalkulasi DCF untuk ASII.JK menggunakan yfinance"""

    judul("DEMO: METODE DCF DENGAN ASII.JK")

    print("\n[SIMULASI] Pengguna memilih metode 2 (DCF)")
    print("[SIMULASI] Pengguna memilih opsi 2: Ambil data dari yfinance")
    print("[SIMULASI] Pengguna memasukkan: ASII.JK\n")

    # Ambil data dari yfinance
    ticker = "ASII.JK"
    print(f"Mengambil data untuk {ticker}...")
    data = ambil_data_yfinance(ticker)

    if not data:
        print("✗ Error: Tidak bisa mengambil data")
        return

    # Tampilkan data yang diambil
    tampilkan_data_yfinance(data)

    # Ekstrak data dari yfinance
    print("\n[SIMULASI] Data diambil dari yfinance:")

    # Satuan: Miliar (untuk yang lebih mudah dibaca)
    pengali = 1_000_000_000.0  # 10^9

    fcf0 = data.get('fcf', 0)  # Free Cash Flow dalam IDR
    utang = data.get('utang', 0)  # Total debt dalam IDR
    kas = data.get('kas', 0)  # Cash dalam IDR
    saham = data.get('saham_beredar', 1)  # Shares outstanding

    # Konversi ke miliar
    fcf0_display = fcf0 / pengali if fcf0 else 0
    utang_display = utang / pengali if utang else 0
    kas_display = kas / pengali if kas else 0

    print(f"  - FCF: Rp {fmt(fcf0_display)} M")
    print(f"  - Total Utang: Rp {fmt(utang_display)} M")
    print(f"  - Kas: Rp {fmt(kas_display)} M")
    print(f"  - Saham Beredar: {fmt(saham, 0)} lembar")

    print("\n[SIMULASI] Input asumsi DCF (simulasi nilai konservatif):")

    # Asumsi DCF - nilai konservatif untuk manufaktur
    tahun = 5
    wacc_p = 8.5  # 8.5% WACC untuk perusahaan besar yang mapan
    g_p = 6.0     # 6% growth rate untuk FCF
    g_term_p = 3.0  # 3% perpetual growth (sesuai growth GDP)

    print(f"  - Periode proyeksi: {tahun} tahun")
    print(f"  - WACC: {fmt(wacc_p, 1)}%")
    print(f"  - Growth rate FCF: {fmt(g_p, 1)}%")
    print(f"  - Growth terminal: {fmt(g_term_p, 1)}%")

    # Validasi FCF
    if fcf0 <= 0:
        print("\n  ! Catatan: FCF Anda <= 0. DCF akan menghasilkan nilai negatif.")
        print("    Metode DCF sebaiknya dipakai saat FCF positif dan relatif stabil.")
        return

    wacc, g, g_term = wacc_p / 100, g_p / 100, g_term_p / 100

    sub("PROYEKSI ARUS KAS (5 TAHUN)")
    print(f"  {'Thn':>4} {'FCF Proyeksi':>18} {'Faktor Diskon':>15} {'Present Value':>18}")
    print("  " + "-" * 57)

    total_pv = 0.0
    fcf_n = fcf0
    for n in range(1, tahun + 1):
        fcf_n = fcf0 * (1 + g) ** n
        faktor = 1 / (1 + wacc) ** n
        pv = fcf_n * faktor
        total_pv += pv
        print(f"  {n:>4} {rp_ringkas(fcf_n):>18} {fmt(faktor, 4):>15} {rp_ringkas(pv):>18}")

    sub("TERMINAL VALUE")
    terminal_value = fcf_n * (1 + g_term) / (wacc - g_term)
    pv_terminal = terminal_value / (1 + wacc) ** tahun

    print(f"  FCF tahun ke-5: {rp_ringkas(fcf_n)}")
    print(f"  Terminal Value: {rp_ringkas(terminal_value)}")
    print(f"  PV Terminal Value: {rp_ringkas(pv_terminal)}")

    sub("RINGKASAN NILAI")
    enterprise = total_pv + pv_terminal
    equity = enterprise - utang + kas
    harga_wajar = equity / saham

    porsi_tv = pv_terminal / enterprise * 100 if enterprise else 0

    baris_nilai = [
        (f"PV arus kas {tahun} tahun", rp_ringkas(total_pv)),
        ("Terminal Value", rp_ringkas(terminal_value)),
        ("PV Terminal Value", f"{rp_ringkas(pv_terminal)}  ({fmt(porsi_tv)}% dari total)"),
        ("Enterprise Value", rp_ringkas(enterprise)),
        ("(-) Utang berbunga", rp_ringkas(utang)),
        ("(+) Kas", rp_ringkas(kas)),
        ("Equity Value", rp_ringkas(equity)),
        ("Jumlah saham", f"{fmt(saham, 0)} lembar"),
    ]
    lebar = max(len(label) for label, _ in baris_nilai)
    for label, nilai_teks in baris_nilai:
        print(f"  {label:<{lebar}} : {nilai_teks}")

    sub("HASIL DCF")
    print(f"  Metode                 : Discounted Cash Flow (DCF)")
    print(f"  Kode Saham             : {ticker}")
    print(f"  Nama Perusahaan        : {data.get('nama', 'N/A')}")
    print(f"  Harga wajar per lembar : {rp(harga_wajar)}")

    # Harga beli ideal dengan MOS
    harga_beli_ideal = harga_wajar * (1 - MOS_DEFAULT / 100)
    print(f"  Harga beli ideal       : {rp(harga_beli_ideal)}  (MOS {fmt(MOS_DEFAULT, 0)}%)")

    # Bandingkan dengan harga pasar
    harga_pasar = data.get('price')
    if harga_pasar:
        print(f"\n  Harga pasar            : {rp(harga_pasar)}")
        mos = (harga_wajar - harga_pasar) / harga_wajar * 100
        upside = (harga_wajar - harga_pasar) / harga_pasar * 100
        print(f"  Margin of safety       : {fmt(mos)}%")
        print(f"  Potensi upside         : {fmt(upside)}%")

        if mos >= MOS_DEFAULT:
            status = "UNDERVALUED - diskon cukup besar terhadap nilai wajar"
        elif mos > 0:
            status = "SEDIKIT DI BAWAH nilai wajar - margin of safety masih tipis"
        elif mos > -10:
            status = "WAJAR / FAIRLY VALUED - harga mendekati nilai wajar"
        else:
            status = "OVERVALUED - harga di atas nilai wajar"
        print(f"  Kesimpulan             : {status}")

    sub("ANALISIS SENSITIVITAS (harga wajar per lembar)")
    daftar_wacc = [wacc_p - 2, wacc_p, wacc_p + 2]
    daftar_g = [g_p - 2, g_p, g_p + 2]
    print("  " + "WACC \\ g".ljust(12) + "".join(f"{fmt(x, 1) + '%':>16}" for x in daftar_g))
    for w_p in daftar_wacc:
        w = w_p / 100
        baris = f"  {fmt(w_p, 1) + '%':<12}"
        for gg_p in daftar_g:
            gg = gg_p / 100
            if w <= g_term or w <= 0:
                baris += f"{'n/a':>16}"
                continue
            pv_sum = sum(fcf0 * (1 + gg) ** n / (1 + w) ** n for n in range(1, tahun + 1))
            fcf_akhir = fcf0 * (1 + gg) ** tahun
            tv = fcf_akhir * (1 + g_term) / (w - g_term)
            ev = pv_sum + tv / (1 + w) ** tahun
            nilai = (ev - utang + kas) / saham
            baris += f"{rp(nilai, 0):>16}"
        print(baris)

    print("\n  Perhatikan: perubahan kecil pada WACC/growth mengubah hasil cukup jauh.")
    print("  Itu sebabnya DCF selalu dipakai bersama margin of safety.")

    print("\n" + "="*70)
    print("PENJELASAN HASIL:")
    print("="*70)
    print(f"""
DCF untuk {ticker} dengan asumsi konservatif menghasilkan harga wajar:
{rp(harga_wajar)} per lembar

Asumsi yang digunakan:
- WACC: {fmt(wacc_p, 1)}% (discount rate)
- Growth rate FCF: {fmt(g_p, 1)}% selama proyeksi 5 tahun
- Growth terminal: {fmt(g_term_p, 1)}% (perpetual growth)

Komponen nilai:
- PV arus kas 5 tahun: {rp_ringkas(total_pv)} ({fmt(100 - porsi_tv)}% dari total)
- PV Terminal Value: {rp_ringkas(pv_terminal)} ({fmt(porsi_tv)}% dari total)
- Enterprise Value: {rp_ringkas(enterprise)}
- Setelah sesuaikan utang & kas → Equity Value: {rp_ringkas(equity)}
- Dibagi {fmt(saham, 0)} saham → Harga per lembar: {rp(harga_wajar)}

Harga yang aman dengan MOS 30%: {rp(harga_beli_ideal)}
""")

    if harga_pasar:
        if harga_wajar > harga_pasar:
            selisih = ((harga_wajar - harga_pasar) / harga_pasar * 100)
            print(f"Harga pasar saat ini ({rp(harga_pasar)}) lebih MURAH {fmt(selisih)}%")
            print(f"Ini menunjukkan peluang jika asumsi DCF Anda akurat.")
        else:
            selisih = ((harga_pasar - harga_wajar) / harga_wajar * 100)
            print(f"Harga pasar saat ini ({rp(harga_pasar)}) lebih MAHAL {fmt(selisih)}%")
            print(f"Kurang menarik jika asumsi DCF Anda konservatif.")

    print(f"""
Catatan PENTING:
- Hasil sangat sensitif terhadap asumsi WACC dan growth rate
- Lihat tabel sensitivitas di atas untuk melihat range kemungkinan
- Verifikasi asumsi dengan kondisi bisnis & industri sebelum keputusan
- DCF adalah alat proyeksi, bukan prediksi pasti
- Selalu gunakan margin of safety {fmt(MOS_DEFAULT, 0)}% atau lebih
""")

if __name__ == "__main__":
    demo_dcf_asii()
