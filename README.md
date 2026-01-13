## 📋 О проекте
Консольное приложение для управления мультивалютным портфелем с поддержкой криптовалют (через CoinGecko API) и фиатных валют (через ExchangeRate-API). Проект реализован как полноценный с использованием Poetry и имеет модульную архитектуру.
### 🎯 Ключевые бизнес-возможности:

**📈 Анализ и мониторинг рынка:**
- **Мультиплатформенные котировки** — агрегация данных с ведущих финансовых API (CoinGecko для криптовалют, ExchangeRate-API для фиатных валют)
- **Интеллектуальное кэширование** — локальное хранение курсов с системой TTL для оптимизации запросов и работы в условиях нестабильного интернет-соединения
- **Историческая аналитика** — ведение полного архива курсов в `exchange_rates.json` для последующего анализа динамики рынка

**💼 Управление инвестиционным портфелем:**
- **Диверсификация активов** — одновременная работа с 10+ валютами (BTC, ETH, SOL, EUR, GBP, JPY и другие)
- **Автоматический пересчет стоимости** — мгновенный расчет общей стоимости портфеля в любой выбранной валюте (USD, EUR и др.)
- **Детализированная отчетность** — структурированный вывод информации о балансах, стоимости активов и их доле в портфеле

**🔄 Операционная деятельность:**
- **Безопасные транзакции** — проведение операций покупки/продажи с валидацией сумм и проверкой достаточности средств
- **Автоматизированное ведение учета** — логирование всех операций с timestamp в `actions.log` для аудита и отчетности
- **Интеграция с внешними системами** — модульная архитектура позволяет легко добавлять новые источники данных и платежные шлюзы

**🔐 Управление доступом и безопасность:**
- **Многоуровневая аутентификация** — регистрация пользователей с хешированием паролей по алгоритму SHA-256 с уникальной солью
- **Изоляция данных** — каждый пользователь работает только со своим портфелем, полное разделение данных
- **Резервное копирование** — автоматическое сохранение состояния в JSON-формате для возможности восстановления

**🏗️ Технологическая платформа для масштабирования:**
- **Микросервисная архитектура** — разделение на Core Service (бизнес-логика) и Parser Service (работа с API)
- **Производственная готовность** — поддержка синглтонов, декораторов, пользовательских исключений, системы логирования
- **CLI-first подход** — возможность интеграции в автоматизированные pipeline и скрипты для институциональных клиентов

### Предварительные требования

**Установка Python:**
```bash
# Windows: скачайте с python.org
# Linux (Ubuntu/Debian):
sudo apt update
sudo apt install python3 python3-pip

# Linux (CentOS/RHEL):
sudo yum install python3 python3-pip

# macOS:
brew install python
```
**Установка Poetry:**
```bash
# Windows/Linux/macOS:
curl -sSL https://install.python-poetry.org | python3 -

# Добавьте Poetry в PATH (может потребоваться перезапуск терминала):
export PATH="$HOME/.local/bin:$PATH"
```
**Установка Make:**
```bash
# Windows: установите Chocolatey, затем:
choco install make

# Linux (Ubuntu/Debian):
sudo apt install make

# Linux (CentOS/RHEL):
sudo yum install make

# macOS:
brew install make
```

## 🚀 Быстрый старт

### Установка и запуск:
```bash
# Клонирование репозитория
git clone https://github.com/NikolaiShilenko/finalproject_Shilenko_Nikolay_M25-555.git
cd finalproject_Shilenko_Nikolay_M25-555

# Установка Poetry (если не установлен)
# Windows:
pip install poetry
# Linux/Mac:
curl -sSL https://install.python-poetry.org | python3 -

# Установка зависимостей проекта
make install

# Запуск приложения
make project
# или
poetry run project
```

### 📁 Структура проекта

    finalproject_Shilenko_Nikolay_M25-555/
    ├── data/                          # Данные приложения
    │   ├── users.json                # Пользователи (с хешированными паролями)
    │   ├── portfolios.json           # Портфели пользователей
    │   ├── rates.json               # Кэш текущих курсов валют
    │   └── exchange_rates.json      # Полная история всех курсов
    ├── valutatrade_hub/              # Основной пакет приложения
    │   ├── core/                    # Бизнес-логика (модели, usecases)
    │   ├── infra/                   # Инфраструктура (настройки, БД)
    │   ├── parser_service/          # Сервис обновления курсов валют
    │   ├── cli/                     # Командный интерфейс
    │   ├── logging_config.py        # Настройка логирования
    │   └── decorators.py            # Декораторы для логирования операций
    ├── logs/                        # Логи приложения
    ├── main.py                      # Точка входа
    ├── pyproject.toml              # Конфигурация Poetry и зависимости
    ├── Makefile                    # Автоматизация команд
    └── README.md                   # Документация


### 💻 Основные команды CLI
#### Регистрация нового пользователя
```bash
poetry run project register --username alice --password 1234
```
#### Вход в систему
```bash
poetry run project login --username alice --password 1234
```
#### Выход из системы
```bash
poetry run project logout
```
#### Покупка валюты
```bash
poetry run project buy --currency BTC --amount 0.01
poetry run project buy --currency EUR --amount 100
```
#### Продажа валюты
```bash
poetry run project sell --currency BTC --amount 0.005
```
#### Просмотр портфеля
```bash
poetry run project show-portfolio
poetry run project show-portfolio --base EUR  # в другой базовой валюте
```
#### Получение текущего курса
```bash
poetry run project get-rate --from USD --to EUR
poetry run project get-rate --from BTC --to USD
```
#### Список всех поддерживаемых валют
```bash
poetry run project list-currencies
```
#### Обновление всех курсов (крипто + фиат)
```bash
poetry run project update-rates
```
#### Обновление только из конкретного источника
```bash
poetry run project update-rates --source coingecko
poetry run project update-rates --source exchangerate
```
#### Просмотр кэшированных курсов
```bash
poetry run project show-rates
poetry run project show-rates --top 5      # топ-5 самых дорогих валют
poetry run project show-rates --currency BTC  # только для конкретной валюты
poetry run project show-rates --base EUR   # в другой базовой валюте
```

## 🔧 Настройка API ключей
Для полноценной работы с фиатными валютами нужен API ключ от ExchangeRate-API:

Зарегистрируйтесь на ExchangeRate-API (бесплатно, 1500 запросов/месяц)

Получите API ключ

Добавьте его в файл valutatrade_hub/parser_service/config.py:


EXCHANGERATE_API_KEY: str = "ваш_ключ_здесь"
Примечание: Без API ключа будут работать только криптовалюты через CoinGecko.

## 📊 Полный пример использования

### 1. Установка и запуск
```bash
git clone https://github.com/NikolaiShilenko/finalproject_Shilenko_Nikolay_M25-555.git
cd finalproject_Shilenko_Nikolay_M25-555
make install
```
### 2. Регистрация пользователя
```bash
poetry run project register --username trader --password Trade123!
poetry run project login --username trader --password Trade123!
```
### 3. Обновление курсов валют
```bash
poetry run project update-rates
```
### 4. Покупка активов
```bash
poetry run project buy --currency BTC --amount 0.05
poetry run project buy --currency EUR --amount 500
poetry run project buy --currency ETH --amount 0.5
```
### 5. Мониторинг портфеля
```bash
poetry run project show-portfolio
poetry run project get-rate --from BTC --to EUR
```
###  6. Продажа части активов
```bash
poetry run project sell --currency BTC --amount 0.02
```
###  7. Итоговый портфель
```bash
poetry run project show-portfolio --base EUR
```

## ⚙️ Команды Makefile

### Установка зависимостей
```bash
make install
```
###  Запуск приложения
```bash
make project
```
###  Проверка стиля кода (PEP8 через Ruff)
```bash
make lint
```
###  Автоматическое исправление стиля
```bash
poetry run ruff check --fix .
```
###  Сборка Python-пакета
```bash
make build
```
###  Тестовая публикация (dry-run)
```bash
make publish
```
###  Установка собранного пакета
```bash
make package-install
```

## 📹 Демонстрация:
[![Демонстрация работы ValutaTrade Hub](https://asciinema.org/a/BVZweg3HFTlz8Y8f.svg)](https://asciinema.org/a/BVZweg3HFTlz8Y8f)

## 📄 Лицензия
Учебный проект, созданный в рамках экзамена по программированию на Python. Весь код открыт для изучения и может использоваться в образовательных целях.
