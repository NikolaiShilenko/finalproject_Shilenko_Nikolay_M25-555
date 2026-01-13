class InsufficientFundsError(Exception):
    def __init__(self, code, available, required):
        self.code = code
        self.available = available
        self.required = required
        super().__init__(f"Недостаточно средст: доступно {available} {code}, требуется {required} {code}")


class CurrencyNotFoundError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(f"Неизвестная валюта '{code}'")


class ApiRequestError(Exception):
    def __init__(self, reason):
        self.reason = reason
        super().__init__(f"Ошибка при обращении к внешнему API: {reason}")
