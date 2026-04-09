# API Documentation

## Содержание

- [Общая информация](#общая-информация)
- [Аутентификация](#аутентификация)
- [Служебные эндпоинты](#служебные-эндпоинты)
- [Users](endpoints/users.md)
- [Groups](endpoints/groups.md)
- [Lessons](endpoints/lessons.md)
- [Lecturers](endpoints/lecturers.md)
- [Disciplines](endpoints/disciplines.md)
- [Auditoriums](endpoints/auditoriums.md)
- [Kind of Work](endpoints/kind_of_work.md)
- [Schedule](endpoints/schedule.md)
- [Search](endpoints/search.md)
- [Общие ошибки](#общие-ошибки)

## Общая информация

**Корень сервиса** (без префикса): `http://localhost:8000` — служебные проверки (`/`, `/healthz`, `/version`, `/public`) доступны без ключа.

**Базовый URL REST API**: `http://localhost:8000/api` — все маршруты под `/api` требуют заголовок `X-API-Key`.

**Документация OpenAPI** (если в настройках включено `enable_docs`): интерактивная схема по адресам `/docs`, `/redoc`, спецификация `/openapi.json`.

**Content-Type** для JSON: `application/json`.

## Аутентификация

Эндпоинты с префиксом `/api` и служебный `GET /protected` требуют API-ключ в заголовке `X-API-Key`. Значение ключа задаётся переменной окружения `VALID_API_KEY`.

### Ошибки аутентификации

**Response 401** — отсутствует или неверный API-ключ

```json
{
  "detail": "Unauthorized"
}
```

## Служебные эндпоинты

Маршруты ниже объявлены на корне приложения (не под `/api`).

### GET `/`

Проверка, что сервис отвечает.

**Response 200**

```json
{
  "message": "Hello World"
}
```

### GET `/healthz`

Проверка готовности сервиса с учётом последнего фона обновления данных (расписание и связанные сущности). Использует состояние последнего refresh-job.

**Response 200** — «здорово», если последнее завершённое обновление не в состоянии `never` и не `error` (то есть `success` или `skipped`)

```json
{
  "status": "ok",
  "last_refresh_at": "2026-04-10T12:00:00+03:00",
  "last_refresh_status": "success"
}
```

Поле `last_refresh_at` может быть `null`, если время ещё не зафиксировано.

**Response 503** — обновление никогда не выполнялось или последний завершённый запуск завершился с ошибкой

```json
{
  "status": "degraded",
  "last_refresh_at": null,
  "last_refresh_status": "never"
}
```

Возможные значения `last_refresh_status`: `never`, `success`, `error`, `skipped`. Код **503** возвращается только для `never` и `error`.

### GET `/version`

Версия установленного пакета `ruz-server`.

**Response 200**

```json
{
  "version": "1.0.0"
}
```

### GET `/public`

Публичная проверка без ключа.

**Response 200**

```json
{
  "message": "public ok"
}
```

### GET `/protected`

Проверка валидности API-ключа (тот же механизм, что и для `/api`).

**Response 200**

```json
{
  "message": "protected ok"
}
```

## Общие ошибки

Раздел зарезервирован под типовые коды и форматы ошибок, общие для эндпоинтов под `/api` (см. отдельные страницы в [endpoints](endpoints/)).
