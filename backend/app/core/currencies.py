"""
Currency Management System
Supports multiple currencies with symbols and formatting
"""

from typing import Dict, Optional
from decimal import Decimal


class Currency:
    def __init__(
        self,
        code: str,
        name: str,
        symbol: str,
        decimal_places: int = 2,
        symbol_position: str = "before",  # "before" or "after"
        thousands_separator: str = ",",
        decimal_separator: str = "."
    ):
        self.code = code
        self.name = name
        self.symbol = symbol
        self.decimal_places = decimal_places
        self.symbol_position = symbol_position
        self.thousands_separator = thousands_separator
        self.decimal_separator = decimal_separator

    def format(self, amount: Decimal) -> str:
        """Format amount with currency symbol"""
        # Format number with separators
        amount_str = f"{amount:,.{self.decimal_places}f}"
        
        # Replace separators if needed
        if self.thousands_separator != ",":
            amount_str = amount_str.replace(",", self.thousands_separator)
        if self.decimal_separator != ".":
            amount_str = amount_str.replace(".", self.decimal_separator)
        
        # Add symbol
        if self.symbol_position == "before":
            return f"{self.symbol}{amount_str}"
        else:
            return f"{amount_str} {self.symbol}"


# Supported Currencies
CURRENCIES: Dict[str, Currency] = {
    "CHF": Currency(
        code="CHF",
        name="Schweizer Franken",
        symbol="CHF",
        decimal_places=2,
        symbol_position="after",
        thousands_separator="'",  # Swiss uses apostrophe
        decimal_separator="."
    ),
    "EUR": Currency(
        code="EUR",
        name="Euro",
        symbol="€",
        decimal_places=2,
        symbol_position="after",
        thousands_separator=".",
        decimal_separator=","
    ),
    "USD": Currency(
        code="USD",
        name="US Dollar",
        symbol="$",
        decimal_places=2,
        symbol_position="before",
        thousands_separator=",",
        decimal_separator="."
    ),
    "THB": Currency(
        code="THB",
        name="Thai Baht",
        symbol="฿",
        decimal_places=2,
        symbol_position="before",
        thousands_separator=",",
        decimal_separator="."
    ),
    "GBP": Currency(
        code="GBP",
        name="British Pound",
        symbol="£",
        decimal_places=2,
        symbol_position="before",
        thousands_separator=",",
        decimal_separator="."
    ),
    "JPY": Currency(
        code="JPY",
        name="Japanese Yen",
        symbol="¥",
        decimal_places=0,  # Yen has no decimals
        symbol_position="before",
        thousands_separator=",",
        decimal_separator=""
    ),
    "CNY": Currency(
        code="CNY",
        name="Chinese Yuan",
        symbol="¥",
        decimal_places=2,
        symbol_position="before",
        thousands_separator=",",
        decimal_separator="."
    ),
    "AUD": Currency(
        code="AUD",
        name="Australian Dollar",
        symbol="A$",
        decimal_places=2,
        symbol_position="before",
        thousands_separator=",",
        decimal_separator="."
    ),
    "CAD": Currency(
        code="CAD",
        name="Canadian Dollar",
        symbol="C$",
        decimal_places=2,
        symbol_position="before",
        thousands_separator=",",
        decimal_separator="."
    ),
    "SGD": Currency(
        code="SGD",
        name="Singapore Dollar",
        symbol="S$",
        decimal_places=2,
        symbol_position="before",
        thousands_separator=",",
        decimal_separator="."
    ),
    "INR": Currency(
        code="INR",
        name="Indian Rupee",
        symbol="₹",
        decimal_places=2,
        symbol_position="before",
        thousands_separator=",",
        decimal_separator="."
    ),
    "BRL": Currency(
        code="BRL",
        name="Brazilian Real",
        symbol="R$",
        decimal_places=2,
        symbol_position="before",
        thousands_separator=".",
        decimal_separator=","
    ),
    "ZAR": Currency(
        code="ZAR",
        name="South African Rand",
        symbol="R",
        decimal_places=2,
        symbol_position="before",
        thousands_separator=",",
        decimal_separator="."
    ),
    # Crypto (experimental)
    "BTC": Currency(
        code="BTC",
        name="Bitcoin",
        symbol="₿",
        decimal_places=8,
        symbol_position="before",
        thousands_separator=",",
        decimal_separator="."
    ),
    "ETH": Currency(
        code="ETH",
        name="Ethereum",
        symbol="Ξ",
        decimal_places=18,
        symbol_position="before",
        thousands_separator=",",
        decimal_separator="."
    ),
}


def get_currency(code: str) -> Optional[Currency]:
    """Get currency by code"""
    return CURRENCIES.get(code.upper())


def format_amount(amount: Decimal, currency_code: str) -> str:
    """Format amount with currency"""
    currency = get_currency(currency_code)
    if not currency:
        return f"{amount:.2f} {currency_code}"
    return currency.format(amount)


def get_all_currencies() -> Dict[str, Dict[str, str]]:
    """Get all currencies as dict for API response"""
    return {
        code: {
            "code": curr.code,
            "name": curr.name,
            "symbol": curr.symbol,
            "decimal_places": curr.decimal_places
        }
        for code, curr in CURRENCIES.items()
    }


def is_supported_currency(code: str) -> bool:
    """Check if currency is supported"""
    return code.upper() in CURRENCIES


# Examples:
if __name__ == "__main__":
    # Swiss Francs
    chf = get_currency("CHF")
    print(chf.format(Decimal("1234.56")))  # 1'234.56 CHF
    
    # Thai Baht
    thb = get_currency("THB")
    print(thb.format(Decimal("50000.00")))  # ฿50,000.00
    
    # Euros
    eur = get_currency("EUR")
    print(eur.format(Decimal("1234.56")))  # 1.234,56 €
    
    # US Dollars
    usd = get_currency("USD")
    print(usd.format(Decimal("1234.56")))  # $1,234.56
    
    # Bitcoin
    btc = get_currency("BTC")
    print(btc.format(Decimal("0.12345678")))  # ₿0.12345678
