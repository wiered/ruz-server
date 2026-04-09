# RUZ Server

`RUZ Server` это FastAPI-сервис для хранения и выдачи расписания RUZ через PostgreSQL. Приложение синхронизирует справочники и занятия, предоставляет защищённое REST API и публикует служебные эндпоинты для проверки состояния сервиса.

## Возможности

- хранение групп, пользователей, преподавателей, дисциплин, аудиторий, видов работ и занятий в PostgreSQL;
- импорт и обновление расписания из внешнего источника RUZ;
- ежедневное фоновое обновление через APScheduler;
- защита всех маршрутов под `/api` с помощью заголовка `X-API-Key`;
- служебные эндпоинты `/`, `/healthz`, `/version`, `/public` и `/protected`.

## Стек

- Python 3.12
- FastAPI
- SQLModel / SQLAlchemy
- PostgreSQL
- APScheduler
- Uvicorn
- Pytest

## Требования

- рекомендуется Python 3.12 или новее;
- PostgreSQL должен быть доступен до старта приложения;
- для маршрутов под `/api` нужен API-ключ.

## Быстрый старт

### 1. Установка зависимостей

Создайте виртуальное окружение:

```bash
python -m venv .venv
```

Активируйте его:

```powershell
.venv\Scripts\Activate.ps1
```

```bash
source .venv/bin/activate
```

Установите приложение:

```bash
pip install -e .
```

Для разработки и тестов:

```bash
pip install -e ".[test]"
```

### 2. Настройка окружения

Создайте `.env` в корне проекта на основе `.env.example`:

```powershell
Copy-Item .env.example .env
```

```bash
cp .env.example .env
```

Загрузчик настроек нечувствителен к регистру, поэтому переменные можно задавать как в верхнем, так и в нижнем регистре. Основные параметры:

| Переменная | Обязательна | Назначение |
| --- | --- | --- |
| `VALID_API_KEY` | да | API-ключ для `/api/*` и `/protected`. |
| `POSTGRESQL_URI` | да | Строка подключения к PostgreSQL, например `postgresql://user:password@localhost:5432/ruz`. |
| `LOGGING_LEVEL` | да | Уровень логирования приложения, например `INFO`. |
| `LOGGING_FORMAT` | да | Формат логирования. |
| `HOST` | нет | Хост приложения. По умолчанию `0.0.0.0`. |
| `PORT` | нет | Порт приложения. По умолчанию `2201`. |
| `RELOAD` | нет | Включает hot reload для разработки. |
| `WORKERS` | нет | Количество Uvicorn workers в режиме без reload. |
| `ENABLE_DOCS` | нет | Включает `/docs`, `/redoc` и `/openapi.json`. |
| `DOUPDATE` | нет | Если `true`, запускает обновление данных при старте. |
| `REFRESH_HOUR` | нет | Час ежедневного обновления. По умолчанию `2`. |
| `REFRESH_MINUTE` | нет | Минута ежедневного обновления. По умолчанию `0`. |
| `REFRESH_TIMEZONE` | нет | Часовой пояс планировщика. По умолчанию `Europe/Moscow`. |
| `REFRESH_LOCK_FILE` | нет | Путь к lock-файлу, защищающему от параллельного refresh. |

Минимальный пример:

```env
HOST=0.0.0.0
PORT=2201
POSTGRESQL_URI=postgresql://user:password@localhost:5432/ruz
VALID_API_KEY=change-me
LOGGING_LEVEL=INFO
LOGGING_FORMAT=standard
ENABLE_DOCS=true
DOUPDATE=false
```

### 3. Запуск приложения

```bash
python -m ruz_server.main
```

Альтернативная совместимая точка входа:

```bash
python -m ruzserver
```

При старте сервис автоматически создаёт таблицы и запускает планировщик обновлений.

### Обновление схемы

В версиях до поддержки nullable `users.subgroup` колонка `users.subgroup` создавалась как `NOT NULL`. Для уже существующей PostgreSQL-базы перед запуском новой версии ослабьте ограничение вручную:

```sql
ALTER TABLE users ALTER COLUMN subgroup DROP NOT NULL;
```

## Docker

Сборка образа:

```bash
docker build -t ruz-server .
```

Запуск контейнера:

```bash
docker run --rm --env-file .env -p 2201:2201 ruz-server
```

## API

Публичные эндпоинты:

- `GET /`
- `GET /healthz`
- `GET /version`
- `GET /public`

Защищённые эндпоинты:

- `GET /protected`
- все маршруты под `/api/*`

Основные группы маршрутов:

- `/api/user`
- `/api/group`
- `/api/lecturer`
- `/api/kind_of_work`
- `/api/discipline`
- `/api/auditorium`
- `/api/lesson`
- `/api/schedule`
- `/api/search`

Пример запроса к защищённому эндпоинту:

```bash
curl -H "X-API-Key: change-me" http://localhost:2201/api/group/
```

Пример проверки состояния:

```bash
curl http://localhost:2201/healthz
```

Если `ENABLE_DOCS=true`, доступны:

- `/docs`
- `/redoc`
- `/openapi.json`

Подробная документация по API:

- [Общий обзор API](docs/api.md)
- [Users](docs/endpoints/users.md)
- [Groups](docs/endpoints/groups.md)
- [Lessons](docs/endpoints/lessons.md)
- [Lecturers](docs/endpoints/lecturers.md)
- [Disciplines](docs/endpoints/disciplines.md)
- [Auditoriums](docs/endpoints/auditoriums.md)
- [Kind of Work](docs/endpoints/kind_of_work.md)
- [Schedule](docs/endpoints/schedule.md)
- [Search](docs/endpoints/search.md)

## Обновление данных и `healthz`

- Планировщик выполняет ежедневный refresh по параметрам `REFRESH_HOUR`, `REFRESH_MINUTE` и `REFRESH_TIMEZONE`.
- От параллельного запуска защищают in-process lock и lock-файл.
- `GET /healthz` возвращает `200 OK`, если последнее завершённое обновление закончилось со статусом `success` или `skipped`.
- `GET /healthz` возвращает `503`, если обновление ещё ни разу не выполнялось или завершилось ошибкой.

## Тесты

Установка зависимостей для тестов:

```bash
pip install -e ".[test]"
```

Запуск всех тестов:

```bash
make test
```

Если `make` недоступен, используйте напрямую:

```bash
pytest
```

Полезные команды:

- `make test-fast`
- `make test-api`
- `make test-repositories`
- `make test-unit`
- `make test-integration`
- `make test-coverage`

Дополнительно: [tests/README.md](tests/README.md)

## Структура проекта

```text
.
├── docs/                # Документация по API
├── src/ruz_server/      # Основной пакет приложения
├── src/ruzserver/       # Совместимый entrypoint
├── tests/               # Набор тестов
├── Dockerfile
├── Makefile
├── pyproject.toml
└── .env.example
```

## Лицензия

Проект распространяется по лицензии [MIT](LICENSE).
