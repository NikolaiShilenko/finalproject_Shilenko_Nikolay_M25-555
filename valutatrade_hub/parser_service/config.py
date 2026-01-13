from dataclasses import dataclass, field


@dataclass
class ParserConfig:
    EXCHANGERATE_API_KEY: str = "f297542a83c299171bddbf3b"

    COINGECKO_URL: str = "https://api.coingecko.com/api/v3/simple/price"
    EXCHANGERATE_API_URL: str = "https://v6.exchangerate-api.com/v6"

    BASE_CURRENCY: str = "USD"
    FIAT_CURRENCIES: tuple = field(default_factory=lambda: ("EUR", "GBP", "RUB", "JPY", "CNY"))
    CRYPTO_CURRENCIES: tuple = field(default_factory=lambda: ("BTC", "ETH", "SOL", "LTC", "ADA"))

    CRYPTO_ID_MAP: dict = field(default_factory=lambda: {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "LTC": "litecoin",
        "ADA": "cardano"
    })

    RATES_FILE_PATH: str = "data/rates.json"
    HISTORY_FILE_PATH: str = "data/exchange_rates.json"
    REQUEST_TIMEOUT: int = 10
    UPDATE_INTERVAL_MINUTES: int = 60
