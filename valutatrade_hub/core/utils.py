import hashlib
import json
import random
import string
from pathlib import Path


def read_json_file(file_path: str):
    path = Path(file_path)
    if not path.exists():
        return [] if "users" in file_path or "portfolios" in file_path else {}

    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json_file(file_path: str, data):
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def hash_password(password: str, salt: str = None) -> tuple:
    if salt is None:
        salt = generate_salt()

    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return hashed, salt


def generate_salt(length: int = 8) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def validate_username(username: str) -> bool:
    return bool(username and username.strip())


def validate_password(password: str) -> bool:
    return len(password) >= 4


def validate_currency_code(currency_code: str) -> bool:
    return bool(currency_code and currency_code.isalpha() and currency_code.isupper())


def validate_amount(amount: float) -> bool:
    return isinstance(amount, (int, float)) and amount > 0


def get_next_user_id() -> int:
    users = read_json_file("data/users.json")
    if not users:
        return 1

    max_id = max(user["user_id"] for user in users)
    return max_id + 1


def get_exchange_rate(from_currency: str, to_currency: str = "USD") -> float:
    rates = read_json_file("data/rates.json")

    # курс к USD
    if to_currency == "USD":
        rate_key = f"{from_currency}_USD"
        if rate_key in rates:
            return rates[rate_key]

    if from_currency == "USD" and to_currency == "EUR":
        return 0.92
    elif from_currency == "EUR" and to_currency == "USD":
        return 1.08
    elif from_currency == "BTC" and to_currency == "USD":
        return 45000.0
    elif from_currency == "USD" and to_currency == "BTC":
        return 1 / 45000.0
    else:
        return 1.0
