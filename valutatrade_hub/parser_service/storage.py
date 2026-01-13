import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class RatesStorage:
    def __init__(self, config):
        self.config = config
        self.history_file = Path(config.HISTORY_FILE_PATH)
        self.rates_file = Path(config.RATES_FILE_PATH)

        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.rates_file.parent.mkdir(parents=True, exist_ok=True)

    def save_to_history(self, rate_data: Dict[str, Any]):
        try:
            history = self._load_history()

            rate_data["id"] = self._generate_id(rate_data)
            rate_data["timestamp"] = datetime.utcnow().isoformat() + "Z"

            history.append(rate_data)

            temp_file = self.history_file.with_suffix(".tmp")
            with open(temp_file, "w") as f:
                json.dump(history, f, indent=2)

            temp_file.replace(self.history_file)
            logger.debug(f"Saved to history: {rate_data['id']}")

        except Exception as e:
            logger.error(f"History save error: {e}")

    def update_current_rates(self, rates: Dict[str, float], source: str):
        try:
            current_data = self._load_current_rates()

            timestamp = datetime.utcnow().isoformat() + "Z"

            if "pairs" not in current_data:
                current_data["pairs"] = {}

            updated_count = 0
            for pair, rate in rates.items():
                if not isinstance(rate, (int, float)):
                    continue

                current_data["pairs"][pair] = {
                    "rate": float(rate),
                    "updated_at": timestamp,
                    "source": source
                }
                updated_count += 1

            current_data["last_refresh"] = timestamp

            temp_file = self.rates_file.with_suffix(".tmp")
            with open(temp_file, "w") as f:
                json.dump(current_data, f, indent=2)

            temp_file.replace(self.rates_file)
            logger.info(f"Updated {updated_count} rates in cache")

            return updated_count

        except Exception as e:
            logger.error(f"Current rates update error: {e}")
            return 0

    def _load_history(self) -> List[Dict]:
        if not self.history_file.exists():
            return []

        try:
            with open(self.history_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def _load_current_rates(self) -> Dict:
        if not self.rates_file.exists():
            return {"pairs": {}, "last_refresh": None}

        try:
            with open(self.rates_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"pairs": {}, "last_refresh": None}

    def _generate_id(self, rate_data: Dict) -> str:
        from_curr = rate_data["from_currency"]
        to_curr = rate_data["to_currency"]
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        return f"{from_curr}_{to_curr}_{timestamp}"
