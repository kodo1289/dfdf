# Movies API

Асинхронный REST API для ведения каталога фильмов. Приложение позволяет создавать, просматривать, фильтровать, сортировать, изменять и удалять записи. Данные хранятся в SQLite.

## Основные возможности

- Полный CRUD для фильмов.
- Фильтрация по названию, жанру, рейтингу и диапазону годов.
- Сортировка по ID, названию, жанру, рейтингу или году.
- Пагинация списка с помощью `offset` и `limit`.
- Валидация данных при создании и обновлении.
- Управление схемой базы данных через миграции Alembic.
- Интерактивная документация OpenAPI/Swagger.

## Технологический стек

- Python 3.10+
- FastAPI и Uvicorn
- SQLAlchemy 2.x с асинхронным драйвером `aiosqlite`
- SQLite
- Pydantic 2
- Alembic
- pytest, pytest-asyncio и HTTPX

## Структура проекта

```text
movies-api/
├── alembic/
│   ├── versions/
│   │   └── 0001_create_movies.py
│   ├── env.py
│   └── script.py.mako
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   └── movie.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── movies.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── movies.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── movie.py
│   ├── database.py
│   └── main.py
├── tests/
│   ├── conftest.py
│   └── test_movies.py
├── .gitignore
├── alembic.ini
├── pytest.ini
├── README.md
└── requirements.txt
```

## Быстрый старт

### Клонирование репозитория

После публикации проекта замените `<username>` на имя пользователя GitHub:

```powershell
git clone https://github.com/<username>/movies-api.git
cd movies-api
```

### Установка зависимостей

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Применение миграций и запуск

```powershell
python -m alembic upgrade head
python -m uvicorn src.main:app --reload
```

По умолчанию SQLite-файл `movies.db` создаётся в текущем каталоге. При необходимости URL базы задаётся переменной окружения `DATABASE_URL`, например:

```powershell
$env:DATABASE_URL = "sqlite+aiosqlite:///./movies.db"
```

После запуска:

- API: <http://127.0.0.1:8000>
- Swagger UI: <http://127.0.0.1:8000/docs>
- OpenAPI JSON: <http://127.0.0.1:8000/openapi.json>

## Основные эндпоинты

| Метод | Путь | Описание | Успешный ответ |
|---|---|---|---|
| `GET` | `/` | Проверка готовности API | `200 OK` |
| `POST` | `/movies/` | Создать фильм | `201 Created` |
| `GET` | `/movies/` | Получить список фильмов | `200 OK` |
| `GET` | `/movies/{movie_id}` | Получить фильм по ID | `200 OK` |
| `PUT` | `/movies/{movie_id}` | Полностью заменить фильм | `200 OK` |
| `PATCH` | `/movies/{movie_id}` | Обновить переданные поля | `200 OK` |
| `DELETE` | `/movies/{movie_id}` | Удалить фильм | `204 No Content` |

Если фильм с указанным ID не найден, API возвращает `404 Not Found`. Некорректные данные или параметры запроса возвращают `422 Unprocessable Entity`.

Пример тела запроса для создания или полной замены фильма:

```json
{
  "title": "The Matrix",
  "genre": "Sci-Fi",
  "rating": 8.7,
  "year": 1999
}
```

## Фильтрация и сортировка

Параметры можно комбинировать. Фильтрация применяется до сортировки и пагинации.

| Параметр | Значение |
|---|---|
| `title` | Поиск по части названия, без учёта регистра |
| `genre` | Жанр, точное совпадение без учёта регистра |
| `min_rating` | Нижняя граница рейтинга включительно (`0`–`10`) |
| `max_rating` | Верхняя граница рейтинга включительно (`0`–`10`) |
| `year_from` | Нижняя граница года включительно |
| `year_to` | Верхняя граница года включительно |
| `sort_by` | Поле сортировки: `id`, `title`, `genre`, `rating` или `year` |
| `order` | Направление сортировки: `asc` или `desc` |
| `offset` | Число пропускаемых записей (по умолчанию `0`) |
| `limit` | Число записей на странице: от `1` до `100` (по умолчанию `100`) |

Пример: найти фильмы жанра Sci-Fi с рейтингом не ниже 8 и начиная с 1990 года, отсортировать по рейтингу от большего к меньшему:

```text
GET /movies/?genre=Sci-Fi&min_rating=8&year_from=1990&sort_by=rating&order=desc
```

Поиск по части названия:

```text
GET /movies/?title=matrix
```

При одинаковом значении поля сортировки результаты дополнительно упорядочиваются по ID для стабильного порядка. Некорректное поле/направление сортировки, диапазон рейтинга или диапазон годов приводят к `422`.

## Модель данных

Таблица `movies` содержит:

| Поле | Тип | Ограничения |
|---|---|---|
| `id` | Integer | Первичный ключ, индекс |
| `title` | String(200) | Обязательное; Pydantic: от 2 до 200 символов |
| `genre` | String(100) | Обязательное; Pydantic: от 2 до 100 символов |
| `rating` | Float | Обязательное; от 0 до 10 |
| `year` | Integer | Обязательное; от 1888 до текущего года при проверке API |

В ответе API также присутствует `id`; при создании передавать его не нужно.

## Ограничения базы данных

На уровне SQLite определены:

- `PRIMARY KEY` для `id`;
- `NOT NULL` для `title`, `genre`, `rating` и `year`;
- `CHECK (rating >= 0 AND rating <= 10)`;
- `CHECK (year >= 1888)`;
- индексы для `id` и `title`.

Верхняя граница года и ограничения длины строк проверяются схемами Pydantic на уровне API. Миграции применяются командой `python -m alembic upgrade head`; для возврата к предыдущей версии используйте `python -m alembic downgrade -1`.

## Тесты

```powershell
python -m pytest
```

Тесты используют отдельную временную SQLite-базу и не изменяют рабочую `movies.db`.

## Публикация на GitHub

1. Создайте на GitHub **публичный** репозиторий `movies-api` без автоматически созданных README и лицензии.
2. В корне проекта выполните:

```powershell
git init
git add .
git commit -m "Add Movies API project"
git branch -M main
git remote add origin https://github.com/<username>/movies-api.git
git push -u origin main
```

3. Проверьте в настройках репозитория GitHub, что его видимость — **Public**.
4. Ссылка для отправки преподавателю: `https://github.com/<username>/movies-api`.
#   m o v i e s - a p i  
 