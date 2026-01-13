import hashlib
from datetime import datetime

from .exceptions import InsufficientFundsError


class User:
    def __init__(self, user_id, username, hashed_password, salt, registration_date):
        self._user_id = user_id
        self._username = username
        self._hashed_password = hashed_password
        self._salt = salt
        self._registration_date = registration_date

    @property
    def user_id(self):
        return self._user_id

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        if not value:
            raise ValueError("Имя пользователя не может быть пустым")
        self._username = value

    @property
    def hashed_password(self):
        return self._hashed_password

    @hashed_password.setter
    def hashed_password(self, value):
        if len(value) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов")
        self._hashed_password = value

    def get_user_info(self):
        return {
            "user_id": self._user_id,
            "username": self._username,
            "registration_date": self._registration_date.isoformat()
        }

    def change_password(self, new_password):
        if len(new_password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов")

        new_salt = self._generate_salt()
        self._salt = new_salt
        self._hashed_password = self._hash_password(new_password, new_salt)

    def verify_password(self, password):
        test_hash = self._hash_password(password, self._salt)
        return test_hash == self._hashed_password

    def _hash_password(self, password, salt):
        return hashlib.sha256((password + salt).encode()).hexdigest()

    def _generate_salt(self):
        import random
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    def to_dict(self):
        return {
            "user_id": self._user_id,
            "username": self._username,
            "hashed_password": self._hashed_password,
            "salt": self._salt,
            "registration_date": self._registration_date.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            user_id=data["user_id"],
            username=data["username"],
            hashed_password=data["hashed_password"],
            salt=data["salt"],
            registration_date=datetime.fromisoformat(data["registration_date"])
        )


class Wallet:
    def __init__(self, currency_code, balance=0.0):
        self.currency_code = currency_code
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("Баланс должен быть числом")
        if value < 0:
            raise ValueError("Баланс не может быть отрицательным")
        self._balance = float(value)

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        self.balance += amount

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной")

        if amount > self._balance:
            raise InsufficientFundsError(
                self.currency_code,
                self._balance,
                amount
            )

        self.balance -= amount

    def get_balance_info(self):
        return {
            "currency_code": self.currency_code,
            "balance": self._balance
        }

    def to_dict(self):
        return {
            "currency_code": self.currency_code,
            "balance": self._balance
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            currency_code=data["currency_code"],
            balance=data["balance"]
        )


class Portfolio:
    def __init__(self, user_id, wallets=None):
        self._user_id = user_id
        self._wallets = wallets or {}

    @property
    def user_id(self):
        return self._user_id

    @property
    def wallets(self):
        return self._wallets.copy()

    def add_currency(self, currency_code):
        if currency_code in self._wallets:
            raise ValueError(f"Валюта {currency_code} уже есть в портфеле")
        self._wallets[currency_code] = Wallet(currency_code)

    def get_wallet(self, currency_code):
        return self._wallets.get(currency_code)

    def get_total_value(self, base_currency="USD"):
        total = 0.0
        for wallet in self._wallets.values():
            total += wallet.balance
        return total

    def to_dict(self):
        wallets_dict = {}
        for currency_code, wallet in self._wallets.items():
            wallets_dict[currency_code] = wallet.to_dict()

        return {
            "user_id": self._user_id,
            "wallets": wallets_dict
        }

    @classmethod
    def from_dict(cls, data):
        wallets = {}
        for currency_code, wallet_data in data["wallets"].items():
            wallets[currency_code] = Wallet.from_dict(wallet_data)

        return cls(
            user_id=data["user_id"],
            wallets=wallets
        )
