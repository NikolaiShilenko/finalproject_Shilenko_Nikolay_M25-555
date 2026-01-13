from datetime import datetime

from .models import Portfolio, User
from .utils import (
    get_exchange_rate,
    get_next_user_id,
    hash_password,
    read_json_file,
    validate_amount,
    validate_currency_code,
    validate_password,
    validate_username,
    write_json_file,
)


class AuthManager:

    def __init__(self):
        self.current_user = None

    def register(self, username: str, password: str) -> dict:
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
            "message": f"Пользователь '{username}' зарегистрирован (id={user_id}). "
                       f"Войдите: login --username {username} --password ****",
            "user_id": user_id
        }

    def login(self, username: str, password: str) -> dict:
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
        return {
            "success": True,
            "message": f"Вы вошли как '{username}'",
            "user": user_obj
        }

    def logout(self):
        self.current_user = None
        return {"success": True, "message": "Вы вышли из системы"}

    def is_authenticated(self) -> bool:
        return self.current_user is not None


class PortfolioManager:

    def __init__(self, auth_manager: AuthManager):
        self.auth = auth_manager

    def show_portfolio(self, base_currency: str = "USD") -> dict:
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

        # расчет стоимости
        wallets_info = []
        total_value = 0.0

        for currency_code, wallet in portfolio_obj.wallets.items():
            if currency_code == base_currency:
                value = wallet.balance
            else:
                rate = get_exchange_rate(currency_code, base_currency)
                value = wallet.balance * rate

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

    def buy_currency(self, currency_code: str, amount: float) -> dict:
        if not self.auth.is_authenticated():
            return {"success": False, "message": "Сначала выполните login"}

        if not validate_currency_code(currency_code):
            return {"success": False, "message": "Неверный код валюты"}

        if not validate_amount(amount):
            return {"success": False, "message": "'amount' должен быть положительным числом"}

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

        rate = get_exchange_rate(currency_code, "USD")
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
            "new_balance": wallet.balance
        }

    def sell_currency(self, currency_code: str, amount: float) -> dict:
        if not self.auth.is_authenticated():
            return {"success": False, "message": "Сначала выполните login"}

        if not validate_currency_code(currency_code):
            return {"success": False, "message": "Неверный код валюты"}

        if not validate_amount(amount):
            return {"success": False, "message": "'amount' должен быть положительным числом"}

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
                "message": f"У вас нет кошелька '{currency_code}'. "
                           f"Добавьте валюту: она создаётся автоматически при первой покупке."
            }

        wallet = portfolio_obj.get_wallet(currency_code)
        if amount > wallet.balance:
            return {
                "success": False,
                "message": f"Недостаточно средств: доступно {wallet.balance:.4f} {currency_code}, "
                           f"требуется {amount:.4f}"
            }

        # получение курса
        rate = get_exchange_rate(currency_code, "USD")
        revenue_usd = amount * rate

        # обновление баланса
        old_balance = wallet.balance
        wallet.withdraw(amount)

        # сохранение
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
            "new_balance": wallet.balance
        }


class CurrencyManager:

    def get_rate(self, from_currency: str, to_currency: str = "USD") -> dict:
        if not validate_currency_code(from_currency) or not validate_currency_code(to_currency):
            return {"success": False, "message": "Неверный код валюты"}

        rate = get_exchange_rate(from_currency, to_currency)

        if rate is None:
            return {
                "success": False,
                "message": f"Курс {from_currency}→{to_currency} недоступен. Повторите попытку позже."
            }

        # расчитуем обратный курс
        reverse_rate = 1 / rate if rate != 0 else 0

        return {
            "success": True,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": rate,
            "reverse_rate": reverse_rate,
            "message": f"Курс {from_currency}→{to_currency}: {rate:.6f}"
        }
