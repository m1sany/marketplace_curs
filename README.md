# Marketplace Coursework

Небольшой демонстрационный маркетплейс на FastAPI с рендерингом HTML-шаблонов через Jinja2.

## Краткое описание

Проект предоставляет простую веб-страницу маркетплейса и API-роуты для регистрации, входа, управления товарами, заказами и комиссионными. Шаблоны находятся в папке `templates`, маршруты — в паке `routers`.

## Технологии

- Python 3.11+ (рекомендуется)
- FastAPI
- Uvicorn
- SQLAlchemy (async)
- Jinja2

## Зависимости

Зависимости перечислены в `requirements.txt`. Основные пакеты:

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
aiosqlite==0.19.0
jinja2==3.1.2
greenlet>=3.0.0
email-validator>=2.0.0
```

## Быстрый старт (локально)

1. Клонируйте репозиторий и перейдите в папку проекта:

```bash
cd /path/to/marketplace_coursework
```

2. Создайте виртуальное окружение и активируйте его (zsh):

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Установите зависимости:

```bash
pip install -r requirements.txt
```

4. Запустите приложение (в режиме разработки):

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

После запуска откройте в браузере `http://127.0.0.1:8000/`.

## База данных

По умолчанию используется SQLite-файл `marketplace.db` (см. `database.py`). Если хотите использовать другую СУБД, измените `DATABASE_URL` в `database.py` или адаптируйте код для чтения URL из переменных окружения.

Пример настройки для PostgreSQL (требуется установить async драйвер):

```
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"
```

В текущей реализации нет готовой конфигурации Alembic-миграций; Alembic установлен в зависимостях и может быть добавлен при необходимости.

## Структура проекта

- `main.py` — точка входа, инициализация приложения и маршрутов
- `database.py` — подключение SQLAlchemy (async)
- `routers/` — маршруты: `auth.py`, `products.py`, `orders.py`, `commissions.py`
- `templates/` — Jinja2 HTML-шаблоны
- `models.py`, `schemas.py` — модели и схемы
- `auth.py` — логика аутентификации (JWT и т.д.)

## Роуты и страницы

Приложение рендерит HTML-страницы для:
- `/` — главная
- `/login` — страница входа
- `/register` — регистрация
- `/products` — каталог товаров
- `/my-products` — мои товары
- `/orders` — заказы
- `/commissions` — комиссия продавцов

API-эндпойнты находятся в соответствующих файлах в папке `routers`.

## Разработка и вклад

1. Создавайте ветки фич от `main`.
2. Открывайте PR с описанием изменений.

## Контакты

Если нужно помочь с запуском или дописать документацию — откройте issue или напишите автору репозитория.

---

_README сгенерирован автоматически. При желании могу дополнить его инструкциями по миграциям Alembic, CI/CD или сделать англоязычную версию._
