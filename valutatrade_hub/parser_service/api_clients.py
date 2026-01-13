import logging
from abc import ABC, abstractmethod

import requests

from valutatrade_hub.core.exceptions import ApiRequestError

from .config import ParserConfig

logger = logging.getLogger(__name__)


class BaseApiClient(ABC):
    @abstractmethod
    def fetch_rates(self) -> dict:
        pass


class CoinGeckoClient(BaseApiClient):
    def __init__(self, config: ParserConfig):
        self.config = config
        self.url = config.COINGECKO_URL

    def fetch_rates(self) -> dict:
        try:
            crypto_ids = [self.config.CRYPTO_ID_MAP[code] for code in self.config.CRYPTO_CURRENCIES]
            ids_param = ",".join(crypto_ids)

            params = {
                "ids": ids_param,
                "vs_currencies": self.config.BASE_CURRENCY.lower()
            }

            response = requests.get(
                self.url,
                params=params,
                timeout=self.config.REQUEST_TIMEOUT
            )
            response.raise_for_status()

            data = response.json()
            rates = {}

            for code in self.config.CRYPTO_CURRENCIES:
                coin_id = self.config.CRYPTO_ID_MAP[code]
                if coin_id in data and self.config.BASE_CURRENCY.lower() in data[coin_id]:
                    rate = data[coin_id][self.config.BASE_CURRENCY.lower()]
                    key = f"{code}_{self.config.BASE_CURRENCY}"
                    rates[key] = rate

            logger.info(f"CoinGecko: получено {len(rates)} курсов")
            return rates

        except requests.exceptions.RequestException as e:
            logger.error(f"CoinGecko error: {e}")
            raise ApiRequestError(f"CoinGecko: {e}") from e
        except Exception as e:
            logger.error(f"CoinGecko parsing error: {e}")
            raise ApiRequestError("CoinGecko parsing failed") from e


class ExchangeRateApiClient(BaseApiClient):
    def __init__(self, config: ParserConfig):
        self.config = config
        if not config.EXCHANGERATE_API_KEY:
            raise ValueError("API key for ExchangeRate-API not set")

        self.url = f"{config.EXCHANGERATE_API_URL}/{config.EXCHANGERATE_API_KEY}/latest/{config.BASE_CURRENCY}"

    def fetch_rates(self) -> dict:
        try:
            response = requests.get(
                self.url,
                timeout=self.config.REQUEST_TIMEOUT
            )
            response.raise_for_status()

            data = response.json()

            if data.get("result") != "success":
                raise ApiRequestError(f"ExchangeRate-API error: {data.get('error-type', 'Unknown')}")

            rates = {}
            for currency in self.config.FIAT_CURRENCIES:
                if currency in data.get("conversion_rates", {}):
                    rate = data["conversion_rates"][currency]
                    key = f"{currency}_{self.config.BASE_CURRENCY}"
                    rates[key] = rate

            logger.info(f"ExchangeRate-API: получено {len(rates)} курсов")
            return rates

        except requests.exceptions.RequestException as e:
            logger.error(f"ExchangeRate-API error: {e}")
            raise ApiRequestError(f"ExchangeRate-API: {e}") from e
        except Exception as e:
            logger.error(f"ExchangeRate-API parsing error: {e}")
            raise ApiRequestError("ExchangeRate-API parsing failed") from e
