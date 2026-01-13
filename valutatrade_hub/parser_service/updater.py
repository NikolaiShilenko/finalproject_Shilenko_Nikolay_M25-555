import logging
from datetime import datetime
from typing import Dict

from .api_clients import CoinGeckoClient, ExchangeRateApiClient
from .config import ParserConfig
from .storage import RatesStorage

logger = logging.getLogger(__name__)


class RatesUpdater:
    def __init__(self, config: ParserConfig = None):
        self.config = config or ParserConfig()
        self.storage = RatesStorage(self.config)

        self.clients = []
        if self.config.CRYPTO_CURRENCIES:
            self.clients.append(("CoinGecko", CoinGeckoClient(self.config)))

        if self.config.FIAT_CURRENCIES and self.config.EXCHANGERATE_API_KEY:
            try:
                self.clients.append(("ExchangeRate-API", ExchangeRateApiClient(self.config)))
            except ValueError as e:
                logger.warning(f"ExchangeRate-API client not created: {e}")

    def run_update(self, source: str = None) -> Dict:
        logger.info("Starting rates update...")

        all_rates = {}
        results = {
            "total_updated": 0,
            "sources": {},
            "errors": []
        }

        for client_name, client in self.clients:
            if source and client_name.lower() != source.lower():
                continue

            try:
                logger.info(f"Fetching from {client_name}...")
                rates = client.fetch_rates()

                if rates:
                    updated = self.storage.update_current_rates(rates, client_name)
                    all_rates.update(rates)

                    results["sources"][client_name] = {
                        "rates_count": len(rates),
                        "updated": updated
                    }
                    results["total_updated"] += updated

                    for pair, rate in rates.items():
                        from_curr, to_curr = pair.split("_")
                        self._save_to_history(from_curr, to_curr, rate, client_name)

                    logger.info(f"{client_name}: OK ({len(rates)} rates)")
                else:
                    logger.warning(f"{client_name}: No rates received")

            except Exception as e:
                error_msg = f"{client_name}: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)

        if all_rates:
            logger.info(f"Update completed. Total rates: {len(all_rates)}")
        else:
            logger.warning("No rates were updated")

        results["timestamp"] = datetime.utcnow().isoformat() + "Z"
        return results

    def _save_to_history(self, from_curr: str, to_curr: str, rate: float, source: str):
        rate_data = {
            "from_currency": from_curr,
            "to_currency": to_curr,
            "rate": float(rate),
            "source": source,
            "meta": {
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
        self.storage.save_to_history(rate_data)
