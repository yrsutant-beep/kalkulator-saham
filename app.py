"""
Kalkulator Harga Wajar Saham
============================

Program terminal interaktif untuk menghitung estimasi harga wajar (nilai
intrinsik) sebuah saham dengan 3 metode:

  1. Benjamin Graham  -> Graham Number dari EPS & BVPS
  2. Discounted Cash Flow (DCF) -> Free Cash Flow, WACC, Growth Rate
  3. Relative Valuation -> Rasio PE dan PBV

Semua data dimasukkan manual oleh pengguna lewat input terminal.

Catatan: hasil perhitungan adalah estimasi berbasis asumsi yang Anda
masukkan, BUKAN rekomendasi jual/beli.
"""

import re
import logging
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

riwayat = []  # kumpulan hasil perhitungan selama sesi berjalan


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

    sub(f"DATA DARI YFINANCE: {data['ticker']} ({data['nama']})")
    if data.get('eps') is not None:
        print(f"  EPS                  : {rp(data['eps'])}")
    if data.get('book_value') is not None:
        print(f"  Book Value per share : {rp(data['book_value'])}")
    if data.get('price') is not None:
        print(f"  Harga pasar saat ini  : {rp(data['price'])}")
    if data.get('fcf') is not None:
        print(f"  Free Cash Flow       : {rp_ringkas(data['fcf'])}")
    if data.get('utang') is not None:
        print(f"  Total Utang          : {rp_ringkas(data['utang'])}")
    if data.get('kas') is not None:
        print(f"  Kas & Setara         : {rp_ringkas(data['kas'])}")
    if data.get('saham_beredar') is not None:
        print(f"  Saham Beredar        : {fmt(data['saham_beredar'], 0)} lembar")


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


def minta_float(label, minimum=None, maksimum=None, default=None, param_name=None):
    """Baca satu bilangan dari terminal sampai valid.

    Args:
        label: Label pertanyaan untuk user
        minimum: Nilai minimum yang diterima
        maksimum: Nilai maksimum yang diterima
        default: Nilai default jika user tidak input
        param_name: Nama parameter untuk validasi khusus (wacc, growth_rate, pe_ratio, pbv_ratio)
    """
    petunjuk = f" [{fmt_default(default)}]" if default is not None else ""
    while True:
        try:
            mentah = input(f"  {label}{petunjuk}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nInput dibatalkan. Program berhenti.")
            raise SystemExit(0)

        if not mentah:
            if default is not None:
                return float(default)
            print("  ! Nilai tidak boleh kosong.")
            continue

        try:
            nilai = float(normalisasi_angka(mentah))
        except ValueError:
            print("  ! Bukan angka yang valid. Contoh: 1250  atau  1.250,75")
            continue

        if nilai != nilai or nilai in (float("inf"), float("-inf")):
            print("  ! Angka tidak valid.")
            continue

        # Gunakan validation module jika tersedia dan param_name diberikan
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

        # Fallback ke manual range checking
        if minimum is not None and nilai < minimum:
            print(f"  ! Nilai minimal {fmt(minimum)}.")
            continue
        if maksimum is not None and nilai > maksimum:
            print(f"  ! Nilai maksimal {fmt(maksimum)}.")
            continue
        if POLA_RIBUAN.match(mentah.replace(" ", "").replace("_", "")):
            print(f"  -> dibaca sebagai {fmt(nilai, 0)}"
                  f" (titik dianggap pemisah ribuan; pakai koma untuk desimal)")
        return nilai


def minta_int(label, minimum=None, maksimum=None, default=None):
    while True:
        nilai = minta_float(label, minimum, maksimum, default)
        if abs(nilai - round(nilai)) > 1e-9:
            print("  ! Harus bilangan bulat.")
            continue
        return int(round(nilai))


def minta_pilihan(label, pilihan_valid):
    while True:
        try:
            jawab = input(f"{label} ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nInput dibatalkan. Program berhenti.")
            raise SystemExit(0)
        if jawab in pilihan_valid:
            return jawab
        print(f"  ! Pilihan tidak dikenal. Pilih salah satu: {', '.join(pilihan_valid)}")


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
    print("\n" + "=" * 62)
    print(teks.center(62))
    print("=" * 62)


def sub(teks):
    print(f"\n-- {teks} " + "-" * max(0, 58 - len(teks)))


# ---------------------------------------------------------------------------
# Kesimpulan & margin of safety
# ---------------------------------------------------------------------------

def minta_harga_pasar():
    return minta_float(
        "Harga pasar saat ini per lembar (isi 0 untuk melewati)",
        minimum=0, default=0,
    )


def tampilkan_kesimpulan(metode, harga_wajar, harga_pasar):
    sub("HASIL")
    print(f"  Metode            : {metode}")
    print(f"  Harga wajar/lembar: {rp(harga_wajar)}")

    if harga_wajar <= 0:
        print("\n  Harga wajar <= 0. Berdasarkan asumsi yang dimasukkan, saham ini")
        print("  tidak punya nilai wajar positif (cek kembali data/asumsi Anda).")
        riwayat.append((metode, harga_wajar, harga_pasar))
        return

    harga_beli_ideal = harga_wajar * (1 - MOS_DEFAULT / 100)
    print(f"  Harga beli ideal  : {rp(harga_beli_ideal)}  (MOS {fmt(MOS_DEFAULT, 0)}%)")

    if harga_pasar > 0:
        mos = (harga_wajar - harga_pasar) / harga_wajar * 100
        upside = (harga_wajar - harga_pasar) / harga_pasar * 100
        print(f"  Harga pasar       : {rp(harga_pasar)}")
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
    else:
        print("  Harga pasar       : (tidak diisi, perbandingan dilewati)")

    riwayat.append((metode, harga_wajar, harga_pasar))


# ---------------------------------------------------------------------------
# Metode 1: Benjamin Graham
# ---------------------------------------------------------------------------

def metode_graham():
    judul("METODE 1: BENJAMIN GRAHAM (GRAHAM NUMBER)")
    print("""
  Rumus : Harga Wajar = akar( 22,5 x EPS x BVPS )

  Angka 22,5 berasal dari batas konservatif Graham: PER maksimal 15
  dan PBV maksimal 1,5  (15 x 1,5 = 22,5).

  EPS  = Earning Per Share  = laba bersih / jumlah saham beredar
  BVPS = Book Value / Share = total ekuitas / jumlah saham beredar

  Syarat: EPS dan BVPS harus positif (perusahaan untung & ekuitas positif).
""")
    sub("INPUT DATA")

    pilihan_mode = ["1", "2", "3"] if yf else ["1", "2"]
    print("  Pilihan input data:")
    print("    1. Input langsung EPS & BVPS")
    print("    2. Hitung dari laba / ekuitas / saham beredar")
    if yf:
        print("    3. Ambil data otomatis dari yfinance (BBCA.JK, ASII.JK, dll)")

    cara = minta_pilihan("  Pilih opsi (1-3):", pilihan_mode)

    if cara == "1":
        eps = minta_float("EPS - laba per lembar saham (Rp)")
        bvps = minta_float("BVPS - nilai buku per lembar saham (Rp)")
    elif cara == "2":
        pengali_l, _ = pilih_satuan("laba bersih & total ekuitas")
        laba = minta_float("Laba bersih setahun") * pengali_l
        ekuitas = minta_float("Total ekuitas (book value)") * pengali_l
        saham = minta_float("Jumlah saham beredar (lembar)", minimum=1)
        eps = laba / saham
        bvps = ekuitas / saham
        print(f"\n  EPS  = {rp_ringkas(laba)} / {fmt(saham, 0)} lembar = {rp(eps)}")
        print(f"  BVPS = {rp_ringkas(ekuitas)} / {fmt(saham, 0)} lembar = {rp(bvps)}")
    else:  # cara == "3", ambil dari yfinance
        while True:
            try:
                ticker_input = input("  Kode saham (contoh: BBCA.JK, ASII.JK): ").strip()
                if VALIDATION_AVAILABLE:
                    ticker = validate_ticker(ticker_input)
                else:
                    ticker = ticker_input.upper()
                break
            except ValueError as e:
                print(f"  ! {e}")
                continue
        data_yf = ambil_data_yfinance(ticker)

        if not data_yf or data_yf.get('eps') is None or data_yf.get('book_value') is None:
            print(f"\n  ! Data tidak lengkap dari yfinance untuk {ticker}.")
            print("  Lanjut dengan input manual.")
            eps = minta_float("EPS - laba per lembar saham (Rp)")
            bvps = minta_float("BVPS - nilai buku per lembar saham (Rp)")
        else:
            tampilkan_data_yfinance(data_yf)
            eps = data_yf['eps']
            bvps = data_yf['book_value']
            print(f"\n  ! Data EPS dan BVPS sudah diambil dari yfinance.")

    harga_pasar = minta_harga_pasar()

    if eps <= 0 or bvps <= 0:
        sub("HASIL")
        print("  Graham Number tidak bisa dihitung.")
        if eps <= 0:
            print(f"  - EPS = {rp(eps)} (perusahaan rugi / tidak untung).")
        if bvps <= 0:
            print(f"  - BVPS = {rp(bvps)} (ekuitas negatif).")
        print("\n  Metode Graham hanya berlaku untuk perusahaan yang profitabel")
        print("  dengan ekuitas positif. Coba metode lain atau perbaiki data.")
        return

    graham = (22.5 * eps * bvps) ** 0.5
    print(f"\n  Perhitungan: akar(22,5 x {fmt(eps)} x {fmt(bvps)}) = {rp(graham)}")

    tampilkan_kesimpulan("Benjamin Graham (Graham Number)", graham, harga_pasar)

    sub("INFO TAMBAHAN")
    print(f"  PER pada harga wajar : {fmt(graham / eps)}x")
    print(f"  PBV pada harga wajar : {fmt(graham / bvps)}x")
    if harga_pasar > 0:
        print(f"  PER pada harga pasar : {fmt(harga_pasar / eps)}x")
        print(f"  PBV pada harga pasar : {fmt(harga_pasar / bvps)}x")


# ---------------------------------------------------------------------------
# Metode 2: Discounted Cash Flow
# ---------------------------------------------------------------------------

def metode_dcf():
    judul("METODE 2: DISCOUNTED CASH FLOW (DCF)")
    print("""
  Ide dasar: nilai perusahaan = seluruh arus kas masa depan yang
  didiskontokan ke nilai sekarang (present value).

    FCF tahun ke-n   = FCF0 x (1 + g)^n
    PV               = FCF tahun ke-n / (1 + WACC)^n
    Terminal Value   = FCF tahun akhir x (1 + g_term) / (WACC - g_term)
    Enterprise Value = sigma PV + PV(Terminal Value)
    Equity Value     = Enterprise Value - utang berbunga + kas
    Harga wajar      = Equity Value / jumlah saham beredar

  Syarat: WACC harus lebih besar dari growth terminal.
""")
    sub("INPUT DATA")

    pilihan_mode = ["1", "2"] if yf else ["1"]
    print("  Pilihan input data:")
    print("    1. Input manual semua data")
    if yf:
        print("    2. Ambil FCF, utang, kas, saham dari yfinance (WACC & growth manual)")

    cara = minta_pilihan("  Pilih opsi (1-2):", pilihan_mode)

    data_yf = None
    if cara == "2":
        while True:
            try:
                ticker_input = input("  Kode saham (contoh: BBCA.JK, ASII.JK): ").strip()
                if VALIDATION_AVAILABLE:
                    ticker = validate_ticker(ticker_input)
                else:
                    ticker = ticker_input.upper()
                break
            except ValueError as e:
                print(f"  ! {e}")
                continue
        data_yf = ambil_data_yfinance(ticker)

        if data_yf and (data_yf.get('fcf') or data_yf.get('kas') or data_yf.get('saham_beredar')):
            tampilkan_data_yfinance(data_yf)
        else:
            print(f"\n  ! Data dari yfinance untuk {ticker} tidak lengkap.")
            data_yf = None

    pengali, nama_satuan = pilih_satuan("Free Cash Flow, utang, dan kas")

    if data_yf and data_yf.get('fcf'):
        fcf0 = data_yf['fcf'] / pengali
        print(f"  Free Cash Flow (dari yfinance): {fmt(fcf0)} {nama_satuan}")
    else:
        fcf0 = minta_float(f"Free Cash Flow tahun terakhir (dalam {nama_satuan})") * pengali
    if fcf0 <= 0:
        print("\n  ! Catatan: FCF Anda <= 0. DCF akan menghasilkan nilai negatif.")
        print("    Metode DCF sebaiknya dipakai saat FCF positif dan relatif stabil.")

    tahun = minta_int("Periode proyeksi (tahun)", minimum=1, maksimum=30, default=5)
    wacc_p = minta_float(
        "WACC / discount rate (% per tahun)", minimum=0.01, maksimum=100, default=10,
        param_name="wacc"
    )
    g_p = minta_float(
        "Growth rate FCF selama proyeksi (% per tahun)", minimum=-100, maksimum=200, default=5,
        param_name="growth_rate"
    )
    g_term_p = minta_float(
        "Growth terminal / perpetual (% per tahun)",
        minimum=-10, maksimum=wacc_p - 0.01, default=min(3.0, wacc_p - 0.01),
    )
    if data_yf and data_yf.get('utang'):
        utang = data_yf['utang'] / pengali
        print(f"  Total utang (dari yfinance): {fmt(utang)} {nama_satuan}")
    else:
        utang = minta_float(f"Total utang berbunga (dalam {nama_satuan}, 0 bila tidak ada)",
                            minimum=0, default=0) * pengali

    if data_yf and data_yf.get('kas'):
        kas = data_yf['kas'] / pengali
        print(f"  Kas & setara (dari yfinance): {fmt(kas)} {nama_satuan}")
    else:
        kas = minta_float(f"Kas & setara kas (dalam {nama_satuan}, 0 bila tidak ada)",
                          minimum=0, default=0) * pengali

    if data_yf and data_yf.get('saham_beredar'):
        saham = data_yf['saham_beredar']
        print(f"  Saham beredar (dari yfinance): {fmt(saham, 0)} lembar")
    else:
        saham = minta_float("Jumlah saham beredar (lembar)", minimum=1)

    harga_pasar = minta_harga_pasar()

    wacc, g, g_term = wacc_p / 100, g_p / 100, g_term_p / 100

    sub("PROYEKSI ARUS KAS")
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

    terminal_value = fcf_n * (1 + g_term) / (wacc - g_term)
    pv_terminal = terminal_value / (1 + wacc) ** tahun
    enterprise = total_pv + pv_terminal
    equity = enterprise - utang + kas
    harga_wajar = equity / saham

    sub("RINGKASAN NILAI")
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

    tampilkan_kesimpulan("Discounted Cash Flow (DCF)", harga_wajar, harga_pasar)

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


# ---------------------------------------------------------------------------
# Metode 3: Rasio PE & PBV
# ---------------------------------------------------------------------------

def metode_pe_pbv():
    judul("METODE 3: RASIO PE DAN PBV (RELATIVE VALUATION)")
    print("""
  Membandingkan saham dengan rasio acuan (rata-rata historis emiten,
  rata-rata industri, atau rasio pesaing).

    Harga wajar (PE)  = EPS  x PE acuan
    Harga wajar (PBV) = BVPS x PBV acuan
    Harga wajar gabungan = rata-rata berbobot dari keduanya

  PE  = Price to Earning Ratio (harga dibanding laba per saham)
  PBV = Price to Book Value    (harga dibanding nilai buku per saham)
""")
    sub("INPUT DATA")

    pilihan_mode = ["1", "2"] if yf else ["1"]
    print("  Pilihan input data:")
    print("    1. Input manual EPS & BVPS")
    if yf:
        print("    2. Ambil data otomatis dari yfinance")

    cara = minta_pilihan("  Pilih opsi (1-2):", pilihan_mode)

    if cara == "1":
        eps = minta_float("EPS - laba per lembar saham (Rp)")
        bvps = minta_float("BVPS - nilai buku per lembar saham (Rp)")
    else:  # cara == "2", ambil dari yfinance
        while True:
            try:
                ticker_input = input("  Kode saham (contoh: BBCA.JK, ASII.JK): ").strip()
                if VALIDATION_AVAILABLE:
                    ticker = validate_ticker(ticker_input)
                else:
                    ticker = ticker_input.upper()
                break
            except ValueError as e:
                print(f"  ! {e}")
                continue
        data_yf = ambil_data_yfinance(ticker)

        if not data_yf or data_yf.get('eps') is None or data_yf.get('book_value') is None:
            print(f"\n  ! Data tidak lengkap dari yfinance untuk {ticker}.")
            print("  Lanjut dengan input manual.")
            eps = minta_float("EPS - laba per lembar saham (Rp)")
            bvps = minta_float("BVPS - nilai buku per lembar saham (Rp)")
        else:
            tampilkan_data_yfinance(data_yf)
            eps = data_yf['eps']
            bvps = data_yf['book_value']
            print(f"\n  ! Data EPS dan BVPS sudah diambil dari yfinance.")
    pe_acuan = minta_float("PE acuan / target (x)", minimum=0, default=15,
                           param_name="pe_ratio")
    pbv_acuan = minta_float("PBV acuan / target (x)", minimum=0, default=1.5,
                            param_name="pbv_ratio")
    bobot_pe = minta_float("Bobot untuk metode PE (%)", minimum=0, maksimum=100, default=50)
    harga_pasar = minta_harga_pasar()

    bobot_pbv = 100 - bobot_pe
    wajar_pe = eps * pe_acuan
    wajar_pbv = bvps * pbv_acuan
    wajar_gabungan = (wajar_pe * bobot_pe + wajar_pbv * bobot_pbv) / 100

    sub("PERHITUNGAN")
    print(f"  Harga wajar via PE  : {rp(eps)} x {fmt(pe_acuan)} = {rp(wajar_pe)}")
    print(f"  Harga wajar via PBV : {rp(bvps)} x {fmt(pbv_acuan)} = {rp(wajar_pbv)}")
    print(f"  Bobot               : PE {fmt(bobot_pe, 0)}% / PBV {fmt(bobot_pbv, 0)}%")

    if eps <= 0:
        print("\n  ! EPS <= 0, sehingga valuasi berbasis PE tidak bermakna.")
        print("    Untuk emiten rugi, andalkan PBV atau metode lain.")
    if bvps <= 0:
        print("\n  ! BVPS <= 0 (ekuitas negatif), valuasi berbasis PBV tidak bermakna.")

    tampilkan_kesimpulan(
        f"Rasio PE & PBV (bobot {fmt(bobot_pe, 0)}/{fmt(bobot_pbv, 0)})",
        wajar_gabungan, harga_pasar,
    )

    if harga_pasar > 0:
        sub("RASIO PADA HARGA PASAR SEKARANG")
        if eps != 0:
            print(f"  PE  sekarang : {fmt(harga_pasar / eps)}x  (acuan {fmt(pe_acuan)}x)")
        else:
            print("  PE  sekarang : tidak terdefinisi (EPS = 0)")
        if bvps != 0:
            print(f"  PBV sekarang : {fmt(harga_pasar / bvps)}x  (acuan {fmt(pbv_acuan)}x)")
        else:
            print("  PBV sekarang : tidak terdefinisi (BVPS = 0)")


# ---------------------------------------------------------------------------
# Ringkasan & penjelasan
# ---------------------------------------------------------------------------

def tampilkan_riwayat():
    judul("RINGKASAN HASIL SESI INI")
    if not riwayat:
        print("\n  Belum ada perhitungan. Jalankan menu 1, 2, atau 3 dulu.")
        return

    print(f"\n  {'Metode':<40}{'Harga Wajar':>18}")
    print("  " + "-" * 58)
    for metode, wajar, _ in riwayat:
        print(f"  {metode[:40]:<40}{rp(wajar):>18}")

    nilai = [w for _, w, _ in riwayat]
    rata = sum(nilai) / len(nilai)
    print("  " + "-" * 58)
    print(f"  {'Rata-rata semua metode':<40}{rp(rata):>18}")
    print(f"  {'Terendah (paling konservatif)':<40}{rp(min(nilai)):>18}")
    print(f"  {'Tertinggi (paling optimistis)':<40}{rp(max(nilai)):>18}")

    pasar = [p for _, _, p in riwayat if p > 0]
    if pasar:
        harga_pasar = pasar[-1]
        print(f"\n  Harga pasar terakhir yang diinput: {rp(harga_pasar)}")
        murah = sum(1 for v in nilai if v > harga_pasar)
        print(f"  {murah} dari {len(nilai)} metode menilai saham ini di bawah nilai wajar.")
    print("\n  Praktik umum: pakai beberapa metode lalu ambil rentang nilainya,")
    print("  bukan satu angka tunggal.")


def tampilkan_penjelasan():
    judul("PENJELASAN SINGKAT KETIGA METODE")
    print("""
  1. BENJAMIN GRAHAM (GRAHAM NUMBER)
     Rumus  : akar(22,5 x EPS x BVPS)
     Data   : EPS, BVPS
     Cocok  : perusahaan mapan, berlaba stabil, aset berwujud besar
              (bank, manufaktur, consumer goods).
     Lemah  : terlalu ketat untuk perusahaan bertumbuh cepat atau
              perusahaan aset ringan (teknologi, jasa), dan tidak bisa
              dipakai bila EPS atau BVPS negatif.

  2. DISCOUNTED CASH FLOW (DCF)
     Rumus  : jumlahkan PV dari FCF proyeksi + PV terminal value,
              lalu sesuaikan dengan utang & kas, bagi jumlah saham.
     Data   : FCF terakhir, growth, WACC, growth terminal, utang, kas, saham
     Cocok  : perusahaan dengan arus kas positif dan cukup terprediksi.
     Lemah  : sangat sensitif terhadap asumsi. WACC naik 1% saja bisa
              memotong nilai wajar dua digit persen. Karena itu program ini
              menampilkan tabel sensitivitas.

  3. RASIO PE DAN PBV
     Rumus  : EPS x PE acuan, dan BVPS x PBV acuan
     Data   : EPS, BVPS, PE & PBV acuan (historis emiten / industri)
     Cocok  : perbandingan cepat antar emiten satu sektor.
     Lemah  : ikut salah kalau seluruh sektor sedang overvalued, dan
              tidak bermakna saat EPS negatif.

  ISTILAH PENTING
     EPS   : laba bersih dibagi jumlah saham beredar.
     BVPS  : total ekuitas dibagi jumlah saham beredar.
     FCF   : arus kas operasi dikurangi belanja modal (capex).
     WACC  : rata-rata biaya modal berbobot; dipakai sebagai discount rate.
             Semakin berisiko perusahaan, semakin tinggi WACC.
     MOS   : Margin of Safety, selisih diskon harga pasar terhadap nilai
             wajar. Graham menyarankan minimal 20-30%.

  DI MANA MENCARI DATANYA
     Laporan keuangan / laporan tahunan emiten (situs IDX atau situs
     perusahaan): laba bersih, ekuitas, arus kas operasi, capex, utang,
     kas, jumlah saham beredar.

  PERINGATAN
     Semua hasil hanyalah estimasi dari asumsi yang Anda masukkan.
     Program ini alat bantu belajar, bukan rekomendasi investasi.
""")


# ---------------------------------------------------------------------------
# Menu utama
# ---------------------------------------------------------------------------

MENU = """
==============================================================
            KALKULATOR HARGA WAJAR SAHAM
==============================================================
  1. Metode Benjamin Graham       (EPS, BVPS)
  2. Metode Discounted Cash Flow  (FCF, WACC, Growth)
  3. Metode Rasio PE dan PBV      (EPS, BVPS, PE, PBV)
  4. Ringkasan hasil sesi ini
  5. Penjelasan metode & istilah
  0. Keluar
==============================================================
"""


def main():
    print("\nSelamat datang di Kalkulator Harga Wajar Saham.")
    print("Penulisan angka: desimal pakai koma (1.250,75 atau 1250,75).")
    print("Titik berkelompok 3 angka dianggap pemisah ribuan (1.500 = seribu lima ratus).")

    if yf is None:
        print("\n⚠ CATATAN: yfinance tidak terinstall.")
        print("  Untuk menggunakan fitur pengambilan data otomatis dari internet,")
        print("  jalankan: pip install yfinance")
        print("  Anda masih bisa menggunakan kalkulator dengan input manual.")
    else:
        print("\n✓ yfinance tersedia. Anda bisa memilih mengambil data dari internet")

    # Display security validation status
    if VALIDATION_AVAILABLE:
        print("\n✓ Security validation AKTIF")
        print("  - Ticker format validation (format: KODE.JK)")
        print("  - WACC range validation (0.5% - 20%)")
        print("  - Growth rate range validation (-10% - 30%)")
        print("  - PE/PBV ratio validation (1x - 100x, 0.1x - 10x)")
    else:
        print("\n⚠ Security validation tidak aktif")
        print("  - Pastikan input_validation.py ada di folder yang sama")
        print("  - atau install dependencies yang diperlukan")

    aksi = {
        "1": metode_graham,
        "2": metode_dcf,
        "3": metode_pe_pbv,
        "4": tampilkan_riwayat,
        "5": tampilkan_penjelasan,
    }

    while True:
        print(MENU)
        pilihan = minta_pilihan("Pilih menu (0-5):", list(aksi) + ["0"])
        if pilihan == "0":
            if riwayat:
                tampilkan_riwayat()
            print("\nTerima kasih. Selamat berinvestasi dengan bijak!\n")
            return
        aksi[pilihan]()
        try:
            input("\n  [Enter] untuk kembali ke menu utama...")
        except (EOFError, KeyboardInterrupt):
            print("\n\nProgram berhenti.")
            return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram dihentikan oleh pengguna.\n")
