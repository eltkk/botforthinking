# ThinkBot

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![aiogram](https://img.shields.io/badge/aiogram-3.7-green)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-asyncio-orange)
![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)
![CI](https://github.com/eltkk/botforthinking/actions/workflows/ci.yml/badge.svg)

Telegram-бот с AI на базе [OpenRouter](https://openrouter.ai/). Поддерживает историю диалога, дневной лимит запросов и команды для администратора.

## Возможности

- Общение с AI (модель `google/gemini-2.0-flash-exp:free`)
- История диалога — бот помнит контекст разговора
- Дневной лимит запросов на пользователя (сбрасывается каждый день)
- Блокировка пользователей администратором
- Рассылка сообщений всем пользователям
- Поддержка SQLite (разработка) и PostgreSQL (production)
- Docker + docker-compose для быстрого запуска
- Автоматические тесты (pytest) и CI/CD (GitHub Actions)
- Миграции базы данных (Alembic)

## Требования

- Python 3.11+
- Docker Desktop (опционально, для запуска через docker-compose)
- Аккаунт на [openrouter.ai](https://openrouter.ai/) для получения API ключа
- Telegram-бот (создаётся через [@BotFather](https://t.me/BotFather))

## Как получить токены

### BOT_TOKEN
1. Открой Telegram, найди [@BotFather](https://t.me/BotFather)
2. Отправь `/newbot` и следуй инструкциям
3. Скопируй полученный токен

### OPENROUTER_API_KEY
1. Зарегистрируйся на [openrouter.ai](https://openrouter.ai/)
2. Перейди в раздел **Keys** и создай новый ключ
3. Скопируй ключ (модель `google/gemini-2.0-flash-exp` — бесплатная)

### ADMIN_ID (твой Telegram ID)
1. Найди в Telegram бота [@userinfobot](https://t.me/userinfobot)
2. Отправь ему любое сообщение
3. Скопируй число после `Id:`

## Быстрый старт

### Вариант 1 — Локально (без Docker)

```bash
# 1. Клонировать репозиторий
git clone https://github.com/eltkk/botforthinking.git
cd botforthinking

# 2. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Настроить .env
cp .env.example .env
# Открыть .env и заполнить BOT_TOKEN, OPENROUTER_API_KEY, ADMIN_ID

# 5. Создать папку для базы данных
mkdir data

# 6. Запустить
python main.py
```

### Вариант 2 — Docker (рекомендуется)

```bash
# 1. Клонировать репозиторий
git clone https://github.com/eltkk/botforthinking.git
cd botforthinking

# 2. Настроить .env
cp .env.example .env
# Открыть .env и заполнить BOT_TOKEN, OPENROUTER_API_KEY, ADMIN_ID

# 3. Запустить (Docker сам создаст папки и базу данных)
docker-compose up -d

# Посмотреть логи
docker-compose logs -f bot
```

## Настройка .env

```env
BOT_TOKEN=токен_от_BotFather
OPENROUTER_API_KEY=ключ_с_openrouter.ai
ADMIN_ID=ваш_telegram_id # узнать у @userinfobot
DAILY_LIMIT=10 # лимит запросов в день на пользователя

# SQLite (по умолчанию, для локальной разработки):
DB_URL=sqlite+aiosqlite:///data/thinkbot.db

# PostgreSQL (для production с Docker):
# DB_URL=postgresql+asyncpg://thinkbot:thinkbot@db:5432/thinkbot
```

> **Важно:** Файл `.env` никогда не попадает в Git — он добавлен в `.gitignore`.

## Команды бота

### Для пользователей
| Команда | Описание |
|---------|----------|
| `/start` | Начать работу с ботом |
| `/help` | Список команд |
| `/reset` | Очистить историю чата |
| `/limit` | Посмотреть оставшийся лимит запросов |

### Для администратора
> Работают только если `ADMIN_ID` задан в `.env`

| Команда | Описание |
|---------|----------|
| `/stats` | Статистика: пользователи, запросы, сообщения |
| `/ban <telegram_id>` | Заблокировать пользователя |
| `/unban <telegram_id>` | Разблокировать пользователя |
| `/broadcast <текст>` | Рассылка сообщения всем пользователям |

## Запуск тестов

```bash
pytest tests/ -v
```

Тесты используют SQLite в памяти — не затрагивают реальную базу данных.

## Миграции базы данных (Alembic)

```bash
# Применить все миграции
alembic upgrade head

# Создать новую миграцию после изменения models.py
alembic revision --autogenerate -m "описание изменений"

# Откатить последнюю миграцию
alembic downgrade -1
```

## Архитектура

```
botforthinking/
├── main.py # Точка входа, запуск бота
├── models.py # Модели БД (User, Message)
├── database.py # Функции работы с БД
├── handlers/
│   ├── start.py # Команды /start, /help, /reset, /limit
│   ├── chat.py # Обработчик сообщений и вызов AI
│   └── admin.py # Admin-команды (/stats, /ban, /unban, /broadcast)
├── middlewares/
│   └── limit.py # Проверка лимита и бана перед каждым запросом
├── alembic/ # Миграции БД
│   └── versions/
│       └── 001_initial.py # Начальная миграция
├── tests/
│   └── test_database.py # Тесты функций базы данных
├── .github/
│   └── workflows/
│       └── ci.yml # GitHub Actions — автозапуск тестов
├── .env.example # Шаблон переменных окружения
├── Dockerfile # Сборка Docker-образа
├── docker-compose.yml # Запуск бота + PostgreSQL
├── pytest.ini # Настройки pytest
└── requirements.txt # Зависимости
```

## Технологии

| Технология | Назначение |
|------------|-----------|
| [aiogram 3](https://docs.aiogram.dev/) | Telegram Bot framework |
| [SQLAlchemy (async)](https://docs.sqlalchemy.org/) | ORM для работы с БД |
| [Alembic](https://alembic.sqlalchemy.org/) | Миграции базы данных |
| [aiohttp](https://docs.aiohttp.org/) | HTTP-клиент для OpenRouter API |
| [pytest](https://pytest.org/) | Автоматические тесты |
| [Docker](https://docker.com/) | Контейнеризация |
| [OpenRouter](https://openrouter.ai/) | Доступ к AI моделям |
