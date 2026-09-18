#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Demo script: Menjalankan kalkulasi dengan BBCA.JK menggunakan yfinance
"""

import sys
sys.path.insert(0, '.')

from kalkulator_saham import (
    ambil_data_yfinance, tampilkan_data_yfinance,
    fmt, rp, rp_ringkas, judul, sub, MOS_DEFAULT
)

def demo_graham_bbca():
    """Demo: Kalkulasi Graham Number untuk BBCA.JK menggunakan yfinance"""

    judul("DEMO: METODE GRAHAM DENGAN BBCA.JK")

    print("\n[SIMULASI] Pengguna memilih opsi 3: Ambil dari yfinance")
    print("[SIMULASI] Pengguna memasukkan: BBCA.JK\n")

    # Ambil data dari yfinance
    ticker = "BBCA.JK"
    print(f"Mengambil data untuk {ticker}...")
    data = ambil_data_yfinance(ticker)

    if not data:
        print("✗ Error: Tidak bisa mengambil data")
        return

    # Tampilkan data yang diambil
    tampilkan_data_yfinance(data)

    # Validasi data
    eps = data.get('eps')
    bvps = data.get('book_value')

    if not eps or not bvps or eps <= 0 or bvps <= 0:
        sub("HASIL")
        print("Graham Number tidak bisa dihitung.")
        if eps and eps <= 0:
            print(f"- EPS = {rp(eps)} (perusahaan rugi / tidak untung).")
        if bvps and bvps <= 0:
            print(f"- BVPS = {rp(bvps)} (ekuitas negatif).")
        return

    # Hitung Graham Number
    sub("PERHITUNGAN")
    graham = (22.5 * eps * bvps) ** 0.5
    print(f"  Rumus Graham Number: akar(22,5 × EPS × BVPS)")
    print(f"  = akar(22,5 × {fmt(eps)} × {fmt(bvps)})")
    print(f"  = akar({fmt(22.5 * eps * bvps)})")
    print(f"  = {rp(graham)}")

    # Tampilkan hasil
    sub("HASIL")
    print(f"  Metode            : Benjamin Graham (Graham Number)")
    print(f"  Kode Saham        : {ticker}")
    print(f"  Nama Perusahaan   : {data.get('nama', 'N/A')}")
    print(f"  EPS (dari yfinance): {rp(eps)}")
    print(f"  BVPS (dari yfinance): {rp(bvps)}")
    print(f"  Harga wajar/lembar: {rp(graham)}")

    # Harga beli ideal dengan MOS
    harga_beli_ideal = graham * (1 - MOS_DEFAULT / 100)
    print(f"  Harga beli ideal  : {rp(harga_beli_ideal)}  (MOS {fmt(MOS_DEFAULT, 0)}%)")

    # Bandingkan dengan harga pasar
    harga_pasar = data.get('price')
    if harga_pasar:
        print(f"\n  Harga pasar       : {rp(harga_pasar)}")
        mos = (graham - harga_pasar) / graham * 100
        upside = (graham - harga_pasar) / harga_pasar * 100
        print(f"  Margin of safety  : {fmt(mos)}%")
        print(f"  Potensi upside    : {fmt(upside)}%")

        if mos >= MOS_DEFAULT:
            status = "UNDERVALUED - diskon cukup besar terhadap nilai wajar"
        elif mos > 0:
            status = "SEDIKIT DI BAWAH nilai wajar - margin of safety masih tipis"
        elif mos > -10:
            status = "WAJAR / FAIRLY VALUED - harga mendekati nilai wajar"
        else:
            status = "OVERVALUED - harga di atas nilai wajar"
        print(f"  Kesimpulan        : {status}")

    # Info tambahan
    sub("INFO TAMBAHAN")
    print(f"  PER pada harga wajar : {fmt(graham / eps)}x")
    print(f"  PBV pada harga wajar : {fmt(graham / bvps)}x")
    if harga_pasar:
        print(f"  PER pada harga pasar : {fmt(harga_pasar / eps)}x")
        print(f"  PBV pada harga pasar : {fmt(harga_pasar / bvps)}x")

    print("\n" + "="*70)
    print("PENJELASAN HASIL:")
    print("="*70)
    print(f"""
Graham Number untuk {ticker} adalah {rp(graham)} per lembar.

Ini berarti:
- Nilai intrinsik saham {ticker} diperkirakan {rp(graham)} per lembar
- Harga yang aman untuk membeli (dengan {fmt(MOS_DEFAULT, 0)}% margin of safety) adalah {rp(harga_beli_ideal)}
""")

    if harga_pasar:
        if graham > harga_pasar:
            selisih = ((graham - harga_pasar) / harga_pasar * 100)
            print(f"- Harga pasar saat ini ({rp(harga_pasar)}) masih LEBIH MURAH dari nilai wajar")
            print(f"  sebesar {fmt(selisih)}%, menunjukkan peluang")
        else:
            selisih = ((harga_pasar - graham) / graham * 100)
            print(f"- Harga pasar saat ini ({rp(harga_pasar)}) sudah LEBIH MAHAL dari nilai wajar")
            print(f"  sebesar {fmt(selisih)}%, kurang menarik untuk dibeli")

    print(f"\nCatatan: Hasil ini adalah estimasi berdasarkan EPS dan BVPS dari yfinance.")
    print("Pastikan untuk verifikasi data dengan laporan keuangan resmi sebelum keputusan investasi.")
    print()

if __name__ == "__main__":
    demo_graham_bbca()
