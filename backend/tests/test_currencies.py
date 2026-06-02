"""Unit tests for the currency formatting logic."""

from decimal import Decimal

from app.core.currencies import format_amount, get_currency, is_supported_currency


def test_chf_uses_apostrophe_thousands_and_suffix_symbol():
    assert format_amount(Decimal("1234.56"), "CHF") == "1'234.56 CHF"


def test_eur_uses_dot_thousands_and_comma_decimals():
    assert format_amount(Decimal("1234.56"), "EUR") == "1.234,56 €"


def test_usd_prefixes_symbol():
    assert format_amount(Decimal("1234.56"), "USD") == "$1,234.56"


def test_thb_is_supported():
    assert is_supported_currency("THB")
    assert get_currency("thb").symbol == "฿"


def test_jpy_has_no_decimals():
    assert format_amount(Decimal("5000"), "JPY") == "¥5,000"


def test_unknown_currency_falls_back_to_plain_format():
    assert format_amount(Decimal("10.50"), "XXX") == "10.50 XXX"
