import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from prettytable import PrettyTable

from ..core.currencies import get_all_currencies
from ..core.usecases import AuthManager, CurrencyManager, PortfolioManager
from ..parser_service.config import ParserConfig
from ..parser_service.updater import RatesUpdater


class CLI:
    def __init__(self):
        self.auth_manager = AuthManager()
        self.portfolio_manager = PortfolioManager(self.auth_manager)
        self.currency_manager = CurrencyManager()
        self.parser = self._create_parser()

    def _create_parser(self):
        parser = argparse.ArgumentParser(
            description="Валютный Кошелек",
            prog="project"
        )

        subparsers = parser.add_subparsers(dest="command")

        register_parser = subparsers.add_parser("register", help="Регистрация")
        register_parser.add_argument("--username", required=True)
        register_parser.add_argument("--password", required=True)

        login_parser = subparsers.add_parser("login", help="Вход")
        login_parser.add_argument("--username", required=True)
        login_parser.add_argument("--password", required=True)

        portfolio_parser = subparsers.add_parser("show-portfolio", help="Портфель")
        portfolio_parser.add_argument("--base", default="USD")

        buy_parser = subparsers.add_parser("buy", help="Купить")
        buy_parser.add_argument("--currency", required=True)
        buy_parser.add_argument("--amount", type=float, required=True)

        sell_parser = subparsers.add_parser("sell", help="Продать")
        sell_parser.add_argument("--currency", required=True)
        sell_parser.add_argument("--amount", type=float, required=True)

        rate_parser = subparsers.add_parser("get-rate", help="Курс")
        rate_parser.add_argument("--from", dest="from_currency", required=True)
        rate_parser.add_argument("--to", default="USD")

        update_parser = subparsers.add_parser("update-rates", help="Обновить курсы")
        update_parser.add_argument("--source", choices=["coingecko", "exchangerate"], help="Источник данных")

        show_rates_parser = subparsers.add_parser("show-rates", help="Показать курсы из кэша")
        show_rates_parser.add_argument("--currency", help="Фильтр по валюте")
        show_rates_parser.add_argument("--top", type=int, help="Топ N валют")
        show_rates_parser.add_argument("--base", default="USD", help="Базовая валюта")

        subparsers.add_parser("list-currencies", help="Список валют")

        subparsers.add_parser("logout", help="Выход")
        subparsers.add_parser("help", help="Справка")

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
        elif parsed_args.command == "update-rates":
            self.handle_update_rates(parsed_args)
        elif parsed_args.command == "show-rates":
            self.handle_show_rates(parsed_args)
        elif parsed_args.command == "logout":
            self.handle_logout()
        elif parsed_args.command == "list-currencies":
            self.handle_list_currencies()
        elif parsed_args.command == "help":
            self.print_help()
        else:
            print("Неизвестная команда. Используйте 'help'")

    def print_welcome(self):
        print("\n" + "=" * 50)
        print("     Валютный Кошелек")
        print("=" * 50)
        print("\nКоманды:")
        print("  register         - Регистрация")
        print("  login            - Вход")
        print("  show-portfolio   - Портфель")
        print("  buy              - Купить валюту")
        print("  sell             - Продать валюту")
        print("  get-rate         - Курс валюты")
        print("  update-rates     - Обновить курсы")
        print("  show-rates       - Показать курсы из кэша")
        print("  list-currencies  - Список валют")
        print("  logout           - Выход")
        print("  help             - Справка")
        print("\nПример: project register --username user --password pass")
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
            print(f"Ошибка: {result['message']}")
            if "Неизвестная валюта" in result["message"]:
                print("Используйте 'list-currencies' для списка валют")
            elif "API" in result["message"]:
                print("Повторите попытку позже")
            return

        print(f"\n{result['message']}")
        print(f"Курс: {result['rate']:.2f} USD/{args.currency}")
        print(f"Стоимость: {result['cost_usd']:.2f} USD")
        print(f"Баланс: {result['old_balance']:.4f} → {result['new_balance']:.4f}\n")

    def handle_sell(self, args):
        result = self.portfolio_manager.sell_currency(args.currency, args.amount)

        if not result["success"]:
            print(f"Ошибка: {result['message']}")
            if "Недостаточно средств" in result["message"]:
                print("Проверьте баланс")
            elif "Неизвестная валюта" in result["message"]:
                print("Используйте 'list-currencies' для списка валют")
            elif "API" in result["message"]:
                print("Повторите попытку позже")
            return

        print(f"\n{result['message']}")
        print(f"Курс: {result['rate']:.2f} USD/{args.currency}")
        print(f"Выручка: {result['revenue_usd']:.2f} USD")
        print(f"Баланс: {result['old_balance']:.4f} → {result['new_balance']:.4f}\n")

    def handle_get_rate(self, args):
        result = self.currency_manager.get_rate(args.from_currency, args.to)

        if not result["success"]:
            print(f"Ошибка: {result['message']}")
            if "Неизвестная валюта" in result["message"]:
                print("Используйте 'list-currencies' для списка валют")
            return

        print(f"\nКурс {result['from_currency']}→{result['to_currency']}: {result['rate']:.6f}")
        print(f"Обратный курс: {result['reverse_rate']:.6f}")
        print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    def handle_update_rates(self, args):
        try:
            config = ParserConfig()
            if not config.EXCHANGERATE_API_KEY:
                print("Внимание: API ключ для ExchangeRate-API не установлен.")
                print("Установите переменную окружения EXCHANGERATE_API_KEY")
                print("Или добавьте ключ в config.py")

            updater = RatesUpdater(config)
            result = updater.run_update(args.source)

            if result["errors"]:
                print("Обновление завершено с ошибками:")
                for error in result["errors"]:
                    print(f"  - {error}")
                print("Проверьте logs/parser.log для деталей")
            else:
                print(f"Обновление успешно. Обновлено курсов: {result['total_updated']}")
                print(f"Время обновления: {result['timestamp']}")

        except Exception as e:
            print(f"Ошибка при обновлении курсов: {e}")

    def handle_show_rates(self, args):
        rates_file = Path("data/rates.json")
        if not rates_file.exists():
            print("Локальный кеш курсов пуст.")
            print("Выполните 'update-rates', чтобы загрузить данные.")
            return

        try:
            with open(rates_file, "r") as f:
                data = json.load(f)

            if "pairs" not in data or not data["pairs"]:
                print("Локальный кеш курсов пуст.")
                print("Выполните 'update-rates', чтобы загрузить данные.")
                return

            pairs = data["pairs"]

            if args.currency:
                currency = args.currency.upper()
                filtered = {k: v for k, v in pairs.items()
                            if currency in k}
                if not filtered:
                    print(f"Курс для '{args.currency}' не найден в кеше.")
                    return
                pairs = filtered

            sorted_pairs = sorted(pairs.items(),
                                  key=lambda x: x[1]["rate"],
                                  reverse=True)

            if args.top:
                sorted_pairs = sorted_pairs[:args.top]

            table = PrettyTable()
            table.field_names = ["Пара", "Курс", "Обновлен", "Источник"]

            for pair, info in sorted_pairs:
                table.add_row([
                    pair,
                    f"{info['rate']:.6f}",
                    info["updated_at"][:19],
                    info["source"]
                ])

            print(f"Курсы из кэша (обновлено: {data.get('last_refresh', 'N/A')}):")
            print(table)

        except Exception as e:
            print(f"Ошибка при чтении кэша: {e}")

    def handle_logout(self):
        result = self.auth_manager.logout()
        print(result["message"])

    def handle_list_currencies(self):
        currencies = get_all_currencies()

        print("\nДоступные валюты:")
        print("-" * 60)

        table = PrettyTable()
        table.field_names = ["Тип", "Код", "Название", "Доп. информация"]

        for code, currency in currencies.items():
            info = currency.get_display_info()
            parts = info.split(" — ")
            if len(parts) >= 2:
                type_code = parts[0]
                name_desc = parts[1]
                table.add_row([type_code, code, name_desc[:30], ""])

        print(table)
        print("-" * 60 + "\n")


def main():
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()
