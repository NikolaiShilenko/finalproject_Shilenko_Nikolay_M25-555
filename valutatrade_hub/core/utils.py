import hashlib
import json
import random
import string
from pathlib import Path

from .currencies import CurrencyNotFoundError, get_currency
from .exceptions import ApiRequestError


def read_json_file(file_path):
    path = Path(file_path)
    if not path.exists():
        return [] if "users" in file_path or "portfolios" in file_path else {}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return [] if "users" in file_path or "portfolios" in file_path else {}


def write_json_file(file_path, data):
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def hash_password(password, salt=None):
    if salt is None:
        salt = generate_salt()

    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return hashed, salt


def generate_salt(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def validate_username(username):
    return bool(username and username.strip())


def validate_password(password):
    return len(password) >= 4


def validate_currency_code(currency_code):
    try:
        get_currency(currency_code)
        return True
    except CurrencyNotFoundError:
        return False


def validate_amount(amount):
    return isinstance(amount, (int, float)) and amount > 0


def get_next_user_id():
    users = read_json_file("data/users.json")
    if not users:
        return 1

    max_id = max(user["user_id"] for user in users)
    return max_id + 1


def get_exchange_rate(from_currency, to_currency="USD"):
    if from_currency == to_currency:
        return 1.0

    # Сначала пробуем получить из кэша rates.json
    rates_data = read_json_file("data/rates.json")

    if "pairs" in rates_data:
        pairs = rates_data["pairs"]

        # прямой курс
        direct_key = f"{from_currency}_{to_currency}"
        if direct_key in pairs:
            return pairs[direct_key]["rate"]

        # обратный курс
        reverse_key = f"{to_currency}_{from_currency}"
        if reverse_key in pairs:
            rate = pairs[reverse_key]["rate"]
            return 1.0 / rate if rate != 0 else 0

    try:
        get_currency(from_currency)
        get_currency(to_currency)
    except CurrencyNotFoundError as e:
        raise CurrencyNotFoundError(e.code) from e

    rates = read_json_file("data/rates.json")

    rate_key = f"{from_currency}_{to_currency}"
    if rate_key in rates:
        rate = rates[rate_key]
        return float(rate) if isinstance(rate, (int, float)) else rate

    reverse_key = f"{to_currency}_{from_currency}"
    if reverse_key in rates:
        rate = rates[reverse_key]
        reverse_rate = float(rate) if isinstance(rate, (int, float)) else rate
        return 1.0 / reverse_rate

    raise ApiRequestError(f"Курс {from_currency}→{to_currency} не найден")

def save_session(user_id=None):
    session_data = {"current_user_id": user_id}
    write_json_file("data/session.json", session_data)


def load_session():
    session_data = read_json_file("data/session.json")
    return session_data.get("current_user_id")
