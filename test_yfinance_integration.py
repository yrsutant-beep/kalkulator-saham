#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script untuk verifikasi integrasi yfinance pada kalkulator_saham.py
"""

import sys
sys.path.insert(0, '.')

from kalkulator_saham import ambil_data_yfinance, tampilkan_data_yfinance, fmt, rp_ringkas

def test_yfinance():
    """Test pengambilan data dari yfinance untuk beberapa saham"""

    print("\n" + "="*70)
    print("TEST INTEGRASI YFINANCE - KALKULATOR SAHAM")
    print("="*70)

    # Test beberapa saham populer
    ticker_list = ["BBCA.JK", "ASII.JK", "UNVR.JK"]

    for ticker in ticker_list:
        print(f"\n[TEST] Mengambil data untuk {ticker}...")
        print("-" * 70)

        data = ambil_data_yfinance(ticker)

        if data:
            print(f"✓ Berhasil mengambil data untuk {ticker}")
            print(f"  Nama: {data.get('nama', 'N/A')}")

            # Cek data penting
            if data.get('eps') is not None:
                print(f"  ✓ EPS: {rp_ringkas(data['eps'])}")
            else:
                print(f"  ✗ EPS: tidak tersedia")

            if data.get('book_value') is not None:
                print(f"  ✓ Book Value: {rp_ringkas(data['book_value'])}")
            else:
                print(f"  ✗ Book Value: tidak tersedia")

            if data.get('price') is not None:
                print(f"  ✓ Harga pasar: {rp_ringkas(data['price'])}")
            else:
                print(f"  ✗ Harga pasar: tidak tersedia")

            if data.get('fcf') is not None:
                print(f"  ✓ FCF: {rp_ringkas(data['fcf'])}")
            else:
                print(f"  ✗ FCF: tidak tersedia")

            # Test Graham Number jika EPS dan BVPS ada
            if data.get('eps') and data.get('book_value') and \
               data['eps'] > 0 and data['book_value'] > 0:
                graham = (22.5 * data['eps'] * data['book_value']) ** 0.5
                print(f"\n  Simulasi Graham Number:")
                print(f"    EPS = {rp_ringkas(data['eps'])}")
                print(f"    BVPS = {rp_ringkas(data['book_value'])}")
                print(f"    Graham Number = {rp_ringkas(graham)}")
        else:
            print(f"✗ Gagal mengambil data untuk {ticker}")

    print("\n" + "="*70)
    print("TEST SELESAI")
    print("="*70)
    print("\nHasil:")
    print("- Jika semua test ✓: Integrasi yfinance berfungsi dengan baik")
    print("- Jika ada ✗: Kemungkinan ticker tidak ditemukan atau data tidak lengkap")
    print("\nAnda sekarang bisa menjalankan: python kalkulator_saham.py")
    print("dan memilih opsi untuk mengambil data dari yfinance pada setiap metode.\n")

if __name__ == "__main__":
    test_yfinance()
