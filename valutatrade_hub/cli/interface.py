import argparse
import sys
from datetime import datetime

from prettytable import PrettyTable

from ..core.usecases import AuthManager, CurrencyManager, PortfolioManager


class CLI:

    def __init__(self):
        self.auth_manager = AuthManager()
        self.portfolio_manager = PortfolioManager(self.auth_manager)
        self.currency_manager = CurrencyManager()
        self.parser = self._create_parser()

    def _create_parser(self):
        parser = argparse.ArgumentParser(
            description="Валютный Кошелек - управление мультивалютным портфелем",
            prog="project"
        )

        subparsers = parser.add_subparsers(dest="command", help="Команды")

        register_parser = subparsers.add_parser("register", help="Регистрация нового пользователя")
        register_parser.add_argument("--username", required=True, help="Имя пользователя")
        register_parser.add_argument("--password", required=True, help="Пароль")

        login_parser = subparsers.add_parser("login", help="Вход в систему")
        login_parser.add_argument("--username", required=True, help="Имя пользователя")
        login_parser.add_argument("--password", required=True, help="Пароль")

        portfolio_parser = subparsers.add_parser("show-portfolio", help="Показать портфель")
        portfolio_parser.add_argument("--base", default="USD", help="Базовая валюта (по умолчанию USD)")

        buy_parser = subparsers.add_parser("buy", help="Купить валюту")
        buy_parser.add_argument("--currency", required=True, help="Код покупаемой валюты")
        buy_parser.add_argument("--amount", type=float, required=True, help="Количество")

        sell_parser = subparsers.add_parser("sell", help="Продать валюту")
        sell_parser.add_argument("--currency", required=True, help="Код продаваемой валюты")
        sell_parser.add_argument("--amount", type=float, required=True, help="Количество")

        rate_parser = subparsers.add_parser("get-rate", help="Получить курс валюты")
        rate_parser.add_argument("--from", dest="from_currency", required=True, help="Исходная валюта")
        rate_parser.add_argument("--to", default="USD", help="Целевая валюта (по умолчанию USD)")

        subparsers.add_parser("logout", help="Выход из системы")

        subparsers.add_parser("help", help="Показать справку")

        return parser

    def run(self, args=None):
        if args is None:
            args = sys.argv[1:]

        if not args:
            self.print_welcome()
            return

        parsed_args = self.parser.parse_args(args)

        if parsed_args.command == "register":
            self.handle_register(parsed_args)
        elif parsed_args.command == "login":
            self.handle_login(parsed_args)
        elif parsed_args.command == "show-portfolio":
            self.handle_show_portfolio(parsed_args)
        elif parsed_args.command == "buy":
            self.handle_buy(parsed_args)
        elif parsed_args.command == "sell":
            self.handle_sell(parsed_args)
        elif parsed_args.command == "get-rate":
            self.handle_get_rate(parsed_args)
        elif parsed_args.command == "logout":
            self.handle_logout()
        elif parsed_args.command == "help":
            self.print_help()
        else:
            print("Неизвестная команда. Используйте 'help' для справки.")

    def print_welcome(self):
        print("\n" + "=" * 50)
        print("     Добро пожаловать в Валютный Кошелек!")
        print("=" * 50)
        print("\nДоступные команды:")
        print("  register    - Регистрация нового пользователя")
        print("  login       - Вход в систему")
        print("  show-portfolio - Показать портфель")
        print("  buy         - Купить валюту")
        print("  sell        - Продать валюту")
        print("  get-rate    - Получить курс валюты")
        print("  logout      - Выход из системы")
        print("  help        - Показать справку")
        print("\nПример: project register --username alice --password 1234")
        print("=" * 50 + "\n")

    def print_help(self):
        self.parser.print_help()

    def handle_register(self, args):
        result = self.auth_manager.register(args.username, args.password)
        print(result["message"])

    def handle_login(self, args):
        result = self.auth_manager.login(args.username, args.password)
        print(result["message"])

    def handle_show_portfolio(self, args):
        result = self.portfolio_manager.show_portfolio(args.base)

        if not result["success"]:
            print(result["message"])
            return

        print(f"\nПортфель пользователя '{result['username']}' (база: {result['base_currency']}):")
        print("-" * 50)

        table = PrettyTable()
        table.field_names = ["Валюта", "Баланс", f"Стоимость ({result['base_currency']})"]

        for wallet in result["wallets"]:
            table.add_row([
                wallet["currency"],
                f"{wallet['balance']:.4f}",
                f"{wallet['value']:.2f}"
            ])

        print(table)
        print("-" * 50)
        print(f"ИТОГО: {result['total_value']:.2f} {result['base_currency']}\n")

    def handle_buy(self, args):
        result = self.portfolio_manager.buy_currency(args.currency, args.amount)

        if not result["success"]:
            print(result["message"])
            return

        print(f"\n{result['message']} по курсу {result['rate']:.2f} USD/{args.currency}")
        print(f"Оценочная стоимость покупки: {result['cost_usd']:.2f} USD")
        print("Изменения в портфеле:")
        print(f"  - {args.currency}: было {result['old_balance']:.4f} → стало {result['new_balance']:.4f}\n")

    def handle_sell(self, args):
        result = self.portfolio_manager.sell_currency(args.currency, args.amount)

        if not result["success"]:
            print(result["message"])
            return

        print(f"\n{result['message']} по курсу {result['rate']:.2f} USD/{args.currency}")
        print(f"Оценочная выручка: {result['revenue_usd']:.2f} USD")
        print("Изменения в портфеле:")
        print(f"  - {args.currency}: было {result['old_balance']:.4f} → стало {result['new_balance']:.4f}\n")

    def handle_get_rate(self, args):
        result = self.currency_manager.get_rate(args.from_currency, args.to)

        if not result["success"]:
            print(result["message"])
            return

        print(f"\nКурс {result['from_currency']}→{result['to_currency']}: {result['rate']:.6f}")
        print(f"Обратный курс {result['to_currency']}→{result['from_currency']}: {result['reverse_rate']:.6f}")
        print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    def handle_logout(self):
        result = self.auth_manager.logout()
        print(result["message"])


def main():
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()
