#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Input Validation Module - Keamanan & Validasi Input Data
"""

import re
import logging
from typing import Union, Optional

logger = logging.getLogger(__name__)

# ========================================
# KONFIGURASI VALIDASI
# ========================================

TICKER_PATTERN = r'^[A-Z]{1,5}\.JK$'
TICKER_MIN_LEN = 3
TICKER_MAX_LEN = 10

NUMERIC_RANGES = {
    'wacc': {'min': 0.5, 'max': 20.0, 'unit': '%'},
    'growth_rate': {'min': -10.0, 'max': 30.0, 'unit': '%'},
    'pe_ratio': {'min': 1.0, 'max': 100.0},
    'pbv_ratio': {'min': 0.1, 'max': 10.0},
}


# ========================================
# VALIDASI TICKER SAHAM
# ========================================

def validate_ticker(ticker_input: str) -> str:
    """
    Validasi format ticker saham Indonesia

    Args:
        ticker_input: Input dari user (contoh: "BBCA.JK")

    Returns:
        str: Ticker yang sudah divalidasi

    Raises:
        ValueError: Jika format tidak valid

    Contoh:
        >>> validate_ticker("BBCA.JK")
        'BBCA.JK'
        >>> validate_ticker("bbca")
        ValueError: Format ticker tidak valid
    """
    if not ticker_input:
        raise ValueError("Ticker tidak boleh kosong")

    # 1. Pembersihan
    clean = str(ticker_input).strip().upper()

    # 2. Validasi panjang
    if len(clean) < TICKER_MIN_LEN or len(clean) > TICKER_MAX_LEN:
        raise ValueError(
            f"Panjang ticker harus {TICKER_MIN_LEN}-{TICKER_MAX_LEN} karakter"
        )

    # 3. Validasi format dengan regex
    if not re.match(TICKER_PATTERN, clean):
        raise ValueError(
            f"Format ticker tidak valid. Gunakan format: KODE.JK "
            f"(contoh: BBCA.JK, ASII.JK)"
        )

    logger.info(f"Ticker '{clean}' valid")
    return clean


# ========================================
# VALIDASI INPUT NUMERIK
# ========================================

def validate_percentage(
    value: Union[str, float],
    param_name: str,
    min_val: float = None,
    max_val: float = None
) -> float:
    """
    Validasi input persentase dengan range check

    Args:
        value: Input nilai (string atau float)
        param_name: Nama parameter untuk error message
        min_val: Nilai minimum (opsional)
        max_val: Nilai maximum (opsional)

    Returns:
        float: Nilai yang sudah divalidasi

    Raises:
        ValueError: Jika nilai tidak valid
    """
    try:
        num = float(value)
    except (ValueError, TypeError):
        raise ValueError(f"{param_name} harus berupa angka, dapat '{value}'")

    # Gunakan default range jika tersedia di NUMERIC_RANGES
    if param_name.lower() in NUMERIC_RANGES:
        ranges = NUMERIC_RANGES[param_name.lower()]
        min_val = min_val or ranges.get('min')
        max_val = max_val or ranges.get('max')

    if min_val is not None and num < min_val:
        raise ValueError(
            f"{param_name} {num} lebih kecil dari minimum {min_val}"
        )

    if max_val is not None and num > max_val:
        raise ValueError(
            f"{param_name} {num} lebih besar dari maksimum {max_val}"
        )

    logger.info(f"{param_name}: {num} valid")
    return num


def validate_wacc(wacc_input: Union[str, float]) -> float:
    """Validasi WACC (Weighted Average Cost of Capital)"""
    return validate_percentage(wacc_input, "WACC", 0.5, 20.0)


def validate_growth_rate(growth_input: Union[str, float]) -> float:
    """Validasi growth rate"""
    return validate_percentage(growth_input, "Growth Rate", -10.0, 30.0)


def validate_pe_ratio(pe_input: Union[str, float]) -> float:
    """Validasi P/E ratio"""
    return validate_percentage(pe_input, "PE Ratio", 1.0, 100.0)


def validate_pbv_ratio(pbv_input: Union[str, float]) -> float:
    """Validasi P/BV ratio"""
    return validate_percentage(pbv_input, "PBV Ratio", 0.1, 10.0)


# ========================================
# VALIDASI STRING & TEXT
# ========================================

def sanitize_text(text_input: str, max_length: int = 255) -> str:
    """
    Pembersihan & sanitasi text input

    Args:
        text_input: String yang akan dibersihkan
        max_length: Panjang maksimal string

    Returns:
        str: String yang sudah dibersihkan

    Raises:
        ValueError: Jika terlalu panjang atau kosong
    """
    if not text_input:
        raise ValueError("Input tidak boleh kosong")

    # 1. Strip whitespace
    clean = str(text_input).strip()

    # 2. Batasi panjang
    if len(clean) > max_length:
        raise ValueError(f"Input terlalu panjang (max {max_length} karakter)")

    # 3. Cegah injeksi dasar
    dangerous_chars = ['<', '>', '"', "'", ';', '&', '|', '`', '$']
    for char in dangerous_chars:
        if char in clean:
            raise ValueError(f"Karakter '{char}' tidak diperbolehkan")

    logger.info(f"Text '{clean[:50]}...' sanitized")
    return clean


# ========================================
# VALIDASI FILE
# ========================================

def validate_filename(filename: str) -> str:
    """
    Validasi dan sanitasi nama file

    Args:
        filename: Nama file dari user

    Returns:
        str: Nama file yang aman

    Raises:
        ValueError: Jika filename tidak aman
    """
    ALLOWED_EXTENSIONS = ['.py', '.json', '.md', '.txt', '.csv', '.xlsx']
    BLOCKED_EXTENSIONS = ['.exe', '.bat', '.sh', '.cmd', '.ps1', '.dll']

    if not filename:
        raise ValueError("Nama file tidak boleh kosong")

    # Cegah path traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        raise ValueError("Path traversal tidak diperbolehkan")

    # Check extension
    _, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
    ext = '.' + ext.lower() if ext else ''

    if ext in BLOCKED_EXTENSIONS:
        raise ValueError(f"Ekstensi {ext} tidak diperbolehkan")

    if ext and ext not in ALLOWED_EXTENSIONS:
        logger.warning(f"File extension {ext} tidak di-whitelist")

    logger.info(f"Filename '{filename}' valid")
    return filename


def validate_file_size(file_size_bytes: int, max_size_mb: int = 100) -> bool:
    """
    Validasi ukuran file

    Args:
        file_size_bytes: Ukuran file dalam bytes
        max_size_mb: Ukuran maksimal dalam MB

    Returns:
        bool: True jika valid

    Raises:
        ValueError: Jika file terlalu besar
    """
    max_size_bytes = max_size_mb * 1_000_000

    if file_size_bytes > max_size_bytes:
        raise ValueError(
            f"File terlalu besar ({file_size_bytes/1_000_000:.1f}MB). "
            f"Maksimal {max_size_mb}MB"
        )

    return True


# ========================================
# BATCH VALIDATION
# ========================================

def validate_dcf_inputs(
    wacc: Union[str, float],
    growth: Union[str, float],
    fcf: Union[str, float]
) -> dict:
    """
    Validasi semua input untuk DCF method

    Args:
        wacc: WACC input
        growth: Growth rate input
        fcf: Free cash flow input

    Returns:
        dict: Dictionary berisi nilai-nilai yang sudah divalidasi

    Raises:
        ValueError: Jika ada input yang tidak valid
    """
    try:
        return {
            'wacc': validate_wacc(wacc),
            'growth': validate_growth_rate(growth),
            'fcf': float(fcf),
        }
    except ValueError as e:
        logger.error(f"DCF validation error: {e}")
        raise


def validate_graham_inputs(eps: Union[str, float], bvps: Union[str, float]) -> dict:
    """Validasi input untuk Graham Number method"""
    try:
        eps_val = float(eps)
        bvps_val = float(bvps)

        if eps_val <= 0 or bvps_val <= 0:
            raise ValueError("EPS dan BVPS harus positif")

        return {'eps': eps_val, 'bvps': bvps_val}
    except ValueError as e:
        logger.error(f"Graham validation error: {e}")
        raise


# ========================================
# ERROR HANDLING
# ========================================

class ValidationError(Exception):
    """Custom exception untuk validation errors"""
    pass


def safe_validate(validation_func, value, *args, **kwargs) -> Optional[any]:
    """
    Wrapper yang aman untuk validation functions

    Menangkap exception dan mengembalikan None jika invalid
    """
    try:
        return validation_func(value, *args, **kwargs)
    except ValueError as e:
        logger.warning(f"Validation failed: {e}")
        return None


# ========================================
# TEST VALIDATION FUNCTIONS
# ========================================

if __name__ == "__main__":
    print("="*50)
    print("Testing Input Validation")
    print("="*50)

    # Test ticker validation
    print("\n1. Testing Ticker Validation:")
    test_tickers = [
        ("BBCA.JK", True),
        ("ASII.JK", True),
        ("bbca", False),
        ("BBCA", False),
        ("BBCAA.JK", False),
    ]

    for ticker, should_pass in test_tickers:
        try:
            result = validate_ticker(ticker)
            status = "✅ PASS" if should_pass else "❌ FAIL (should error)"
            print(f"  {status}: {ticker} → {result}")
        except ValueError as e:
            status = "✅ PASS" if not should_pass else "❌ FAIL (should pass)"
            print(f"  {status}: {ticker} → Error: {e}")

    # Test percentage validation
    print("\n2. Testing WACC Validation:")
    test_waccs = [
        (0.5, True),
        (8.5, True),
        (20.0, True),
        (0.1, False),
        (25.0, False),
    ]

    for wacc, should_pass in test_waccs:
        try:
            result = validate_wacc(wacc)
            status = "✅ PASS" if should_pass else "❌ FAIL"
            print(f"  {status}: {wacc}% → {result}%")
        except ValueError as e:
            status = "✅ PASS" if not should_pass else "❌ FAIL"
            print(f"  {status}: {wacc}% → Error")

    # Test text sanitization
    print("\n3. Testing Text Sanitization:")
    test_texts = [
        ("Nilai wajar", True),
        ("Input<script>", False),
        ("Normal text 123", True),
    ]

    for text, should_pass in test_texts:
        try:
            result = sanitize_text(text)
            status = "✅ PASS" if should_pass else "❌ FAIL"
            print(f"  {status}: {text[:30]}")
        except ValueError:
            status = "✅ PASS" if not should_pass else "❌ FAIL"
            print(f"  {status}: {text[:30]} (blocked)")

    print("\n" + "="*50)
    print("Validation tests completed!")
    print("="*50)
