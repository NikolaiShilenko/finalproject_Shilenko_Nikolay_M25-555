import json
from pathlib import Path


class SettingsLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._config = {
            "data_path": "data",
            "rates_ttl_seconds": 300,
            "default_base_currency": "USD",
            "log_path": "logs",
            "log_level": "INFO",
            "supported_currencies": ["USD", "EUR", "RUB", "BTC", "ETH", "LTC"]
        }

        self._load_config()
        self._initialized = True

    def _load_config(self):
        config_file = Path("config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    self._config.update(user_config)
            except Exception:
                pass

    def get(self, key, default=None):
        return self._config.get(key, default)

    def reload(self):
        self._load_config()

    def __getitem__(self, key):
        return self._config[key]

    def __contains__(self, key):
        return key in self._config


# глобальный экземпляр
settings = SettingsLoader()
