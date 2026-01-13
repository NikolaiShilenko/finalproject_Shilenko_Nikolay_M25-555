from abc import ABC, abstractmethod
from .exceptions import CurrencyNotFoundError


class Currency(ABC):
    def __init__(self, name, code):
        if not name or not isinstance(name, str):
            raise ValueError("Название валюты не может быть пустым")

        if not code or not isinstance(code, str):
            raise ValueError("Код валюты не может быть пустым")

        code = code.upper().strip()
        if not 2 <= len(code) <= 5:
            raise ValueError("Код валюты должен быть 2-5 символов")

        if ' ' in code:
            raise ValueError("Код валюты не может содержать пробелы")

        self.name = name
        self.code = code

    @abstractmethod
    def get_display_info(self) -> str:
        pass

    def __str__(self):
        return self.get_display_info()


class FiatCurrency(Currency):
    def __init__(self, name, code, issuing_country):
        super().__init__(name, code)
        self.issuing_country = issuing_country

    def get_display_info(self):
        return f"[FIAT] {self.code} — {self.name} (Issuing: {self.issuing_country})"


class CryptoCurrency(Currency):
    def __init__(self, name, code, algorithm, market_cap=0.0):
        super().__init__(name, code)
        self.algorithm = algorithm
        self.market_cap = market_cap

    def get_display_info(self):
        mcap_str = f"{self.market_cap:.2e}" if self.market_cap > 1e6 else str(self.market_cap)
        return f"[CRYPTO] {self.code} — {self.name} (Algo: {self.algorithm}, MCAP: {mcap_str})"


# реестр валют
_currencies = {}


def register_currency(currency_obj):
    _currencies[currency_obj.code] = currency_obj


def get_currency(code):
    code = code.upper()
    if code not in _currencies:
        raise CurrencyNotFoundError(code)
    return _currencies[code]


def get_all_currencies():
    return _currencies.copy()


def init_default_currencies():
    register_currency(FiatCurrency("US Dollar", "USD", "United States"))
    register_currency(FiatCurrency("Euro", "EUR", "Eurozone"))
    register_currency(FiatCurrency("Russian Ruble", "RUB", "Russia"))

    register_currency(CryptoCurrency("Bitcoin", "BTC", "SHA-256", 1_120_000_000_000))
    register_currency(CryptoCurrency("Ethereum", "ETH", "Ethash", 372_000_000_000))
    register_currency(CryptoCurrency("Litecoin", "LTC", "Scrypt", 5_800_000_000))


# Автоматическая инициализация
init_default_currencies()
