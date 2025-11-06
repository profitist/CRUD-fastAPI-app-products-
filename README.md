# FastAPI Интернет-магазин

API для интернет-магазина, построенное на FastAPI с использованием PostgreSQL и асинхронной работы с базой данных.

## Описание

Проект представляет собой RESTful API для интернет-магазина с функционалом:
- Регистрация и аутентификация пользователей (JWT)
- Управление категориями товаров
- CRUD операции с товарами
- Система отзывов и рейтингов
- Разделение прав доступа (покупатели, продавцы, администраторы)

## Технологический стек

- **FastAPI** - веб-фреймворк
- **SQLAlchemy 2.0** - ORM с асинхронной поддержкой
- **PostgreSQL** - база данных
- **Alembic** - миграции базы данных
- **Pydantic** - валидация данных
- **JWT** - аутентификация
- **Bcrypt** - хеширование паролей
- **Docker & Docker Compose** - контейнеризация
- **Loguru** - логирование

## Структура проекта

```
CourseProj/
├── app/
│   ├── models/          # SQLAlchemy модели
│   │   ├── users.py
│   │   ├── categories.py
│   │   ├── products.py
│   │   └── reviews.py
│   ├── routers/         # API эндпоинты
│   │   ├── users.py
│   │   ├── categories.py
│   │   ├── products.py
│   │   └── reviews.py
│   ├── migrations/      # Alembic миграции
│   ├── auth.py          # Аутентификация и авторизация
│   ├── config.py        # Конфигурация
│   ├── database.py      # Настройка БД
│   ├── schemas.py       # Pydantic схемы
│   ├── db_depends.py    # Зависимости для БД
│   └── main.py          # Точка входа приложения
├── nginx/               # Конфигурация Nginx
├── docker-compose.yml
├── docker-compose.prod.yml
├── requirements.txt
├── alembic.ini
└── .env
```

## Требования

- Python 3.11+
- Docker и Docker Compose
- PostgreSQL 15

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd CourseProj
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
SECRET_KEY=your_secret_key_here
```

### 3. Запуск через Docker Compose

```bash
# Запуск в режиме разработки
docker-compose up --build

# Запуск в фоновом режиме
docker-compose up -d
```

Приложение будет доступно по адресу: `http://localhost:8000`

### 4. Локальная установка (без Docker)

```bash
# Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # На Windows: .venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt

# Запуск миграций
alembic upgrade head

# Запуск приложения
uvicorn app.main:app --reload
```

## API Документация

После запуска приложения документация доступна по адресам:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Основные эндпоинты

### Пользователи (`/users`)

- `POST /users/` - Регистрация нового пользователя
- `POST /users/token` - Получение access и refresh токенов
- `POST /users/refresh-token` - Обновление access токена

### Категории (`/categories`)

- `GET /categories/` - Получить все активные категории
- `POST /categories/` - Создать новую категорию
- `PUT /categories/{category_id}` - Обновить категорию
- `DELETE /categories/{category_id}` - Деактивировать категорию

### Товары (`/products`)

- `GET /products/` - Получить все активные товары
- `GET /products/{product_id}` - Получить конкретный товар
- `GET /products/categories/{category_id}` - Товары по категории
- `POST /products/` - Создать товар (только продавцы)
- `PUT /products/{product_id}` - Обновить товар (только владелец)
- `DELETE /products/{product_id}` - Удалить товар (только владелец)
- `GET /products/{product_id}/reviews` - Получить отзывы о товаре

### Отзывы (`/reviews`)

- `GET /reviews/` - Получить все отзывы
- `POST /reviews/` - Создать отзыв (только покупатели)

## Роли пользователей

- **buyer** - покупатель (может оставлять отзывы)
- **seller** - продавец (может создавать и редактировать товары)
- **admin** - администратор (полный доступ)

## Аутентификация

Приложение использует JWT токены для аутентификации:

1. Зарегистрируйте пользователя через `POST /users/`
2. Получите токены через `POST /users/token`
3. Используйте `access_token` в заголовке: `Authorization: Bearer <token>`

**Время жизни токенов:**
- Access token: 30 минут
- Refresh token: 7 дней

## Миграции базы данных

```bash
# Создание новой миграции
alembic revision --autogenerate -m "описание изменений"

# Применение миграций
alembic upgrade head

# Откат последней миграции
alembic downgrade -1
```

## Разработка



### Логирование

Логи записываются в файл `info.log` с использованием библиотеки Loguru. Каждый запрос получает уникальный `log_id` для отслеживания.

## Production

Для запуска в production используйте:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Структура базы данных

### Таблица `users`
- id, email, hashed_password, is_active, role

### Таблица `categories`
- id, name, is_active, parent_id (древовидная структура)

### Таблица `products`
- id, name, description, price, image_url, stock, is_active, rating, category_id, seller_id

### Таблица `reviews`
- id, user_id, product_id, comment, comment_date, grade (1-5), is_active

## Особенности

- **Асинхронная работа** с базой данных через SQLAlchemy + asyncpg
- **Автоматический расчет рейтинга** товара при добавлении отзыва
- **Soft delete** - объекты помечаются как неактивные вместо удаления
- **Валидация данных** через Pydantic
- **Middleware для логирования** всех HTTP запросов
- **Разделение прав доступа** на уровне роутеров

## Автор

profitist (Иван Михайлов) - Учебный проект
