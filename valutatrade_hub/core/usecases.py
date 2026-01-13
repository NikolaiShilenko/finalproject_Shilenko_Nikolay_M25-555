from datetime import datetime
from .models import User, Portfolio
from .currencies import get_currency, CurrencyNotFoundError
from .exceptions import InsufficientFundsError, ApiRequestError
from ..decorators import log_action
from .utils import (
    read_json_file, write_json_file, hash_password,
    get_next_user_id, validate_username, validate_password,
    validate_amount, get_exchange_rate, save_session, load_session
)


class AuthManager:
    def __init__(self):
        self.current_user = None
        self._load_session()

    def _load_session(self):
        user_id = load_session()
        if user_id:
            users = read_json_file("data/users.json")
            for user_data in users:
                if user_data["user_id"] == user_id:
                    self.current_user = User.from_dict(user_data)
                    break

    @log_action("REGISTER")
    def register(self, username, password):
        if not validate_username(username):
            return {"success": False, "message": "Имя пользователя не может быть пустым"}

        if not validate_password(password):
            return {"success": False, "message": "Пароль должен быть не короче 4 символов"}

        users = read_json_file("data/users.json")
        for user in users:
            if user["username"] == username:
                return {"success": False, "message": f"Имя пользователя '{username}' уже занято"}

        user_id = get_next_user_id()
        hashed_password, salt = hash_password(password)

        new_user = User(
            user_id=user_id,
            username=username,
            hashed_password=hashed_password,
            salt=salt,
            registration_date=datetime.now()
        )

        users.append(new_user.to_dict())
        write_json_file("data/users.json", users)

        portfolios = read_json_file("data/portfolios.json")
        new_portfolio = Portfolio(user_id)
        portfolios.append(new_portfolio.to_dict())
        write_json_file("data/portfolios.json", portfolios)

        return {
            "success": True,
            "message": f"Пользователь '{username}' зарегистрирован (id={user_id})",
            "user_id": user_id,
            "username": username
        }

    @log_action("LOGIN")
    def login(self, username, password):
        users = read_json_file("data/users.json")

        user_data = None
        for user in users:
            if user["username"] == username:
                user_data = user
                break

        if not user_data:
            return {"success": False, "message": f"Пользователь '{username}' не найден"}

        user_obj = User.from_dict(user_data)
        if not user_obj.verify_password(password):
            return {"success": False, "message": "Неверный пароль"}

        self.current_user = user_obj
        save_session(user_obj.user_id)

        return {
            "success": True,
            "message": f"Вы вошли как '{username}'",
            "user": user_obj,
            "user_id": user_obj.user_id,
            "username": username
        }

    def logout(self):
        self.current_user = None
        save_session(None)
        return {"success": True, "message": "Вы вышли из системы"}

    def is_authenticated(self):
        return self.current_user is not None


class PortfolioManager:
    def __init__(self, auth_manager):
        self.auth = auth_manager

    def show_portfolio(self, base_currency="USD"):
        if not self.auth.is_authenticated():
            return {"success": False, "message": "Сначала выполните login"}

        portfolios = read_json_file("data/portfolios.json")
        portfolio_data = None

        for portfolio in portfolios:
            if portfolio["user_id"] == self.auth.current_user.user_id:
                portfolio_data = portfolio
                break

        if not portfolio_data:
            return {"success": False, "message": "Портфель не найден"}

        portfolio_obj = Portfolio.from_dict(portfolio_data)

        wallets_info = []
        total_value = 0.0

        for currency_code, wallet in portfolio_obj.wallets.items():
            if currency_code == base_currency:
                value = wallet.balance
            else:
                try:
                    rate = get_exchange_rate(currency_code, base_currency)
                    value = wallet.balance * rate
                except (CurrencyNotFoundError, ApiRequestError):
                    value = 0.0

            wallets_info.append({
                "currency": currency_code,
                "balance": wallet.balance,
                "value": value,
                "value_currency": base_currency
            })
            total_value += value

        return {
            "success": True,
            "username": self.auth.current_user.username,
            "base_currency": base_currency,
            "wallets": wallets_info,
            "total_value": total_value
        }

    @log_action("BUY", verbose=True)
    def buy_currency(self, currency_code, amount):
        if not self.auth.is_authenticated():
            return {"success": False, "message": "Сначала выполните login"}

        if not validate_amount(amount):
            return {"success": False, "message": "'amount' должен быть положительным числом"}

        try:
            currency = get_currency(currency_code)
        except CurrencyNotFoundError as e:
            return {"success": False, "message": str(e)}

        portfolios = read_json_file("data/portfolios.json")
        portfolio_index = -1

        for i, portfolio in enumerate(portfolios):
            if portfolio["user_id"] == self.auth.current_user.user_id:
                portfolio_index = i
                portfolio_data = portfolio
                break

        if portfolio_index == -1:
            return {"success": False, "message": "Портфель не найден"}

        portfolio_obj = Portfolio.from_dict(portfolio_data)

        if currency_code not in portfolio_obj.wallets:
            portfolio_obj.add_currency(currency_code)

        try:
            rate = get_exchange_rate(currency_code, "USD")
        except ApiRequestError as e:
            return {"success": False, "message": str(e)}

        cost_usd = amount * rate

        wallet = portfolio_obj.get_wallet(currency_code)
        old_balance = wallet.balance
        wallet.deposit(amount)

        portfolios[portfolio_index] = portfolio_obj.to_dict()
        write_json_file("data/portfolios.json", portfolios)

        return {
            "success": True,
            "message": f"Покупка выполнена: {amount:.4f} {currency_code}",
            "currency": currency_code,
            "amount": amount,
            "rate": rate,
            "cost_usd": cost_usd,
            "old_balance": old_balance,
            "new_balance": wallet.balance,
            "user_id": self.auth.current_user.user_id,
            "username": self.auth.current_user.username
        }

    @log_action("SELL", verbose=True)
    def sell_currency(self, currency_code, amount):
        if not self.auth.is_authenticated():
            return {"success": False, "message": "Сначала выполните login"}

        if not validate_amount(amount):
            return {"success": False, "message": "'amount' должен быть положительным числом"}

        try:
            currency = get_currency(currency_code)
        except CurrencyNotFoundError as e:
            return {"success": False, "message": str(e)}

        portfolios = read_json_file("data/portfolios.json")
        portfolio_index = -1

        for i, portfolio in enumerate(portfolios):
            if portfolio["user_id"] == self.auth.current_user.user_id:
                portfolio_index = i
                portfolio_data = portfolio
                break

        if portfolio_index == -1:
            return {"success": False, "message": "Портфель не найден"}

        portfolio_obj = Portfolio.from_dict(portfolio_data)

        if currency_code not in portfolio_obj.wallets:
            return {
                "success": False,
                "message": f"У вас нет кошелька '{currency_code}'"
            }

        try:
            rate = get_exchange_rate(currency_code, "USD")
        except ApiRequestError as e:
            return {"success": False, "message": str(e)}

        wallet = portfolio_obj.get_wallet(currency_code)

        try:
            old_balance = wallet.balance
            wallet.withdraw(amount)
        except InsufficientFundsError as e:
            return {"success": False, "message": str(e)}

        revenue_usd = amount * rate

        portfolios[portfolio_index] = portfolio_obj.to_dict()
        write_json_file("data/portfolios.json", portfolios)

        return {
            "success": True,
            "message": f"Продажа выполнена: {amount:.4f} {currency_code}",
            "currency": currency_code,
            "amount": amount,
            "rate": rate,
            "revenue_usd": revenue_usd,
            "old_balance": old_balance,
            "new_balance": wallet.balance,
            "user_id": self.auth.current_user.user_id,
            "username": self.auth.current_user.username
        }


class CurrencyManager:
    def get_rate(self, from_currency, to_currency="USD"):
        try:
            get_currency(from_currency)
            get_currency(to_currency)
        except CurrencyNotFoundError as e:
            return {"success": False, "message": str(e)}

        try:
            rate = get_exchange_rate(from_currency, to_currency)
        except ApiRequestError as e:
            return {"success": False, "message": str(e)}

        reverse_rate = 1 / rate if rate != 0 else 0

        return {
            "success": True,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": rate,
            "reverse_rate": reverse_rate,
            "message": f"Курс {from_currency}→{to_currency}: {rate:.6f}"
        }
