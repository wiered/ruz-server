# API Documentation

## Содержание

- [Общая информация](#общая-информация)
- [Аутентификация](#аутентификация)
- [Users](#users)
- [Groups](#groups)
- [Lessons](#lessons)
- [Lecturers](#lecturers)
- [Disciplines](#disciplines)
- [Auditoriums](#auditoriums)
- [Kind of Work](#kind-of-work)
- [Schedule](#schedule)
- [Search](#search)
- [Общие ошибки](#общие-ошибки)

## Общая информация

**Base URL**: `http://localhost:8000/api`

**Аутентификация**: API Key в заголовке `X-API-Key`

**Content-Type**: `application/json`

## Аутентификация

Все эндпоинты требуют API ключ в заголовке `X-API-Key`. Ключ берется из переменной окружения `VALID_API_KEY`.

### Ошибки аутентификации

**Response 401** - Отсутствует или неверный API ключ

```json
{
  "detail": "Unauthorized"
}
```

## Users

### POST `/api/user/`

Создание нового пользователя.

**Headers**
| Заголовок | Значение |
|-----------|----------|
| `X-API-Key` | string | Да | API ключ для аутентификации |
| `Content-Type` | `application/json` | Да | Тип контента |

**Request Body**

```json
{
  "id": 123456789,
  "username": "user123",
  "group_oid": 1
}
```

| Поле           | Тип           | Обязательно | Описание                   |
| -------------- | ------------- | ----------- | -------------------------- |
| `id`           | integer       | Да          | Telegram ID пользователя   |
| `username`     | string        | Да          | Имя пользователя Telegram  |
| `group_oid`    | integer       | Да          | ID группы пользователя     |
| `subgroup`     | integer       | Нет         | Подгруппа (по умолчанию 0) |
| `group_guid`   | string        | Нет         | GUID группы                |
| `group_name`   | string        | Нет         | Название группы            |
| `faculty_name` | string        | Нет         | Название факультета        |

**Response 201**

```json
{
  "id": 123456789,
  "subgroup": 1,
  "username": "user123",
  "created_at": "2024-01-15T10:30:00Z",
  "last_used_at": "2024-01-15T10:30:00Z"
}
```

### GET `/api/user/`

Получение списка всех пользователей.

**Response 200**

```json
[
  {
    "id": 123456789,
    "group_oid": 1,
    "subgroup": 0,
    "username": "user123",
    "created_at": "2024-01-15T10:30:00Z",
    "last_used_at": "2024-01-15T10:30:00Z"
  }
]
```

### GET `/api/user/{user_id}`

Получение пользователя по ID.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `user_id` | integer | ID пользователя |

**Response 200**

```json
{
  "id": 123456789,
  "group_oid": 1,
  "subgroup": 0,
  "username": "user123",
  "created_at": "2024-01-15T10:30:00Z",
  "last_used_at": "2024-01-15T10:30:00Z"
}
```

**Response 404**

```json
{
  "detail": "Error: Not Found"
}
```

### GET `/api/user/guid/{user_guid}`

Получение пользователя по GUID (в URL). Поиск выполняется по query-параметру `username`.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `user_guid` | string (UUID) | GUID пользователя |

**Query Parameters**
| Параметр | Тип | Обязательно | Описание |
|----------|-----|-------------|----------|
| `username` | string | Да | Имя пользователя Telegram |

**Response 200**

```json
{
  "id": 123456789,
  "group_oid": 1,
  "subgroup": 0,
  "username": "user123",
  "created_at": "2024-01-15T10:30:00Z",
  "last_used_at": "2024-01-15T10:30:00Z"
}
```

### PUT `/api/user/{user_id}`

Обновление пользователя.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `user_id` | integer | ID пользователя |

**Request Body**

```json
{
  "username": "new_username",
  "group_oid": 2,
  "subgroup": 1,
  "group_guid": "550e8400-e29b-41d4-a716-446655440001",
  "group_name": "ИУ5-12",
  "faculty_name": "Новый факультет"
}
```

Все поля опциональны.

**Response 200** - Успешное обновление

```json
{
  "success": true
}
```

### PUT `/api/user/last_used_at/{user_guid}`

Обновление времени последнего использования пользователя.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `user_guid` | string (UUID) | GUID пользователя |

**Query Parameters**
| Параметр | Тип | Обязательно | Описание |
|----------|-----|-------------|----------|
| `user_id` | integer | Да | ID пользователя |

**Response 200**

```json
true
```

### DELETE `/api/user/{user_id}`

Удаление пользователя.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `user_id` | integer | ID пользователя |

**Response 200**

```json
{
  "success": true
}
```

## Groups

### POST `/api/group/`

Создание новой группы.

**Request Body**

```json
{
  "id": 1,
  "guid": "550e8400-e29b-41d4-a716-446655440000",
  "name": "ИУ5-11",
  "faculty_name": "Факультет"
}
```

| Поле           | Тип           | Обязательно | Описание            |
| -------------- | ------------- | ----------- | ------------------- |
| `id`           | integer       | Да          | ID группы           |
| `guid`         | string (UUID) | Да          | GUID группы         |
| `name`         | string        | Да          | Название группы     |
| `faculty_name` | string        | Да          | Название факультета |

**Response 201**

```json
{
  "id": 1,
  "guid": "550e8400-e29b-41d4-a716-446655440000",
  "name": "ИУ5-11",
  "faculty_name": "Факультет"
}
```

### GET `/api/group/`

Получение списка всех групп.

**Response 200**

```json
[
  {
    "id": 1,
    "guid": "550e8400-e29b-41d4-a716-446655440000",
    "name": "ИУ5-11",
    "faculty_name": "Факультет"
  }
]
```

### GET `/api/group/{group_id}`

Получение группы по ID.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `group_id` | integer | ID группы |

**Response 200**

```json
{
  "id": 1,
  "guid": "550e8400-e29b-41d4-a716-446655440000",
  "name": "ИУ5-11",
  "faculty_name": "Факультет"
}
```

### GET `/api/group/guid/{group_guid}`

Получение группы по GUID.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `group_guid` | string (UUID) | GUID группы |

**Response 200**

```json
{
  "id": 1,
  "guid": "550e8400-e29b-41d4-a716-446655440000",
  "name": "ИУ5-11",
  "faculty_name": "Факультет"
}
```

### PUT `/api/group/{group_id}`

Обновление группы.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `group_id` | integer | ID группы |

**Request Body**

```json
{
  "name": "ИУ5-12",
  "faculty_name": "Новый факультет"
}
```

**Response 200**

```json
{
  "success": true
}
```

### DELETE `/api/group/{group_id}`

Удаление группы.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `group_id` | integer | ID группы |

**Response 200**

```json
{
  "success": true
}
```

## Lessons

### POST `/api/lesson/`

Создание нового занятия.

**Request Body**

```json
{
  "id": 1,
  "lecturer_id": 1,
  "lecturer_guid": "550e8400-e29b-41d4-a716-446655440000",
  "lecturer_full_name": "Иванов И.И.",
  "lecturer_short_name": "Иванов",
  "lecturer_rank": "Доцент",
  "kind_of_work_id": 1,
  "type_of_work": "Лекция",
  "complexity": 1,
  "discipline_id": 1,
  "discipline_name": "Математика",
  "auditorium_id": 1,
  "auditorium_guid": "550e8400-e29b-41d4-a716-446655440001",
  "auditorium_name": "101",
  "auditorium_building": "ГЗ",
  "date": "2024-01-15",
  "begin_lesson": "09:00:00",
  "end_lesson": "10:30:00",
  "group_id": 1,
  "sub_group": 0
}
```

| Поле                  | Тип           | Обязательно | Описание                   |
| --------------------- | ------------- | ----------- | -------------------------- |
| `id`                  | integer       | Да          | ID занятия                 |
| `lecturer_id`         | integer       | Да          | ID преподавателя           |
| `lecturer_guid`       | string (UUID) | Да          | GUID преподавателя         |
| `lecturer_full_name`  | string        | Да          | Полное имя преподавателя   |
| `lecturer_short_name` | string        | Да          | Краткое имя преподавателя  |
| `lecturer_rank`       | string        | Да          | Должность преподавателя    |
| `kind_of_work_id`     | integer       | Да          | ID типа работы             |
| `type_of_work`        | string        | Да          | Название типа работы       |
| `complexity`          | integer       | Да          | Сложность                  |
| `discipline_id`       | integer       | Да          | ID дисциплины              |
| `discipline_name`     | string        | Да          | Название дисциплины        |
| `auditorium_id`       | integer       | Да          | ID аудитории               |
| `auditorium_guid`     | string (UUID) | Да          | GUID аудитории             |
| `auditorium_name`     | string        | Да          | Название аудитории         |
| `auditorium_building` | string        | Да          | Корпус                     |
| `date`                | string (date) | Да          | Дата занятия (YYYY-MM-DD)  |
| `begin_lesson`        | string (time) | Да          | Время начала (HH:MM:SS)    |
| `end_lesson`          | string (time) | Да          | Время окончания (HH:MM:SS) |
| `group_id`            | integer       | Да          | ID группы                  |
| `sub_group`           | integer       | Нет         | Подгруппа (по умолчанию 0) |

**Response 201**

```json
{
  "id": 1,
  "kind_of_work_id": 1,
  "discipline_id": 1,
  "auditorium_id": 1,
  "lecturer_id": 1,
  "date": "2024-01-15",
  "begin_lesson": "09:00:00",
  "end_lesson": "10:30:00",
  "updated_at": "2024-01-15T10:30:00Z",
  "sub_group": 0
}
```

### PUT `/api/lesson/parse`

Парсинг расписания из внешнего API.

**Response 200**

```json
{
  "message": "Parsing completed"
}
```

### GET `/api/lesson/`

Получение списка всех занятий.

**Response 200**

```json
[
  {
    "id": 1,
    "kind_of_work_id": 1,
    "discipline_id": 1,
    "auditorium_id": 1,
    "lecturer_id": 1,
    "date": "2024-01-15",
    "begin_lesson": "09:00:00",
    "end_lesson": "10:30:00",
    "updated_at": "2024-01-15T10:30:00Z",
    "sub_group": 0
  }
]
```

### GET `/api/lesson/{lesson_id}`

Получение занятия по ID.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `lesson_id` | integer | ID занятия |

**Response 200**

```json
{
  "id": 1,
  "kind_of_work_id": 1,
  "discipline_id": 1,
  "auditorium_id": 1,
  "lecturer_id": 1,
  "date": "2024-01-15",
  "begin_lesson": "09:00:00",
  "end_lesson": "10:30:00",
  "updated_at": "2024-01-15T10:30:00Z",
  "sub_group": 0
}
```

### PUT `/api/lesson/{lesson_id}`

Обновление занятия.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `lesson_id` | integer | ID занятия |

**Request Body**

```json
{
  "kind_of_work_id": 2,
  "discipline_id": 2,
  "auditorium_id": 2,
  "lecturer_id": 2,
  "date": "2024-01-16",
  "begin_lesson": "10:00:00",
  "end_lesson": "11:30:00",
  "sub_group": 1
}
```

Все поля опциональны.

**Response 200**

```json
{
  "success": true
}
```

### DELETE `/api/lesson/{lesson_id}`

Удаление занятия.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `lesson_id` | integer | ID занятия |

**Response 200**

```json
{
  "success": true
}
```

## Lecturers

### POST `/api/lecturer/`

Создание нового преподавателя.

**Request Body**

```json
{
  "id": 1,
  "guid": "550e8400-e29b-41d4-a716-446655440000",
  "full_name": "Иванов Иван Иванович",
  "short_name": "Иванов И.И.",
  "rank": "Доцент"
}
```

| Поле         | Тип           | Обязательно | Описание           |
| ------------ | ------------- | ----------- | ------------------ |
| `id`         | integer       | Да          | ID преподавателя   |
| `guid`       | string (UUID) | Да          | GUID преподавателя |
| `full_name`  | string        | Да          | Полное имя         |
| `short_name` | string        | Да          | Краткое имя        |
| `rank`       | string        | Да          | Должность/звание   |

**Response 201**

```json
{
  "id": 1,
  "guid": "550e8400-e29b-41d4-a716-446655440000",
  "full_name": "Иванов Иван Иванович",
  "short_name": "Иванов И.И.",
  "rank": "Доцент"
}
```

### GET `/api/lecturer/`

Получение списка всех преподавателей.

**Response 200**

```json
[
  {
    "id": 1,
    "guid": "550e8400-e29b-41d4-a716-446655440000",
    "full_name": "Иванов Иван Иванович",
    "short_name": "Иванов И.И.",
    "rank": "Доцент"
  }
]
```

### GET `/api/lecturer/{lecturer_id}`

Получение преподавателя по ID.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `lecturer_id` | integer | ID преподавателя |

**Response 200**

```json
{
  "id": 1,
  "guid": "550e8400-e29b-41d4-a716-446655440000",
  "full_name": "Иванов Иван Иванович",
  "short_name": "Иванов И.И.",
  "rank": "Доцент"
}
```

### GET `/api/lecturer/guid/{lecturer_guid}`

Получение преподавателя по GUID.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `lecturer_guid` | string (UUID) | GUID преподавателя |

**Response 200**

```json
{
  "id": 1,
  "guid": "550e8400-e29b-41d4-a716-446655440000",
  "full_name": "Иванов Иван Иванович",
  "short_name": "Иванов И.И.",
  "rank": "Доцент"
}
```

### PUT `/api/lecturer/{lecturer_id}`

Обновление преподавателя.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `lecturer_id` | integer | ID преподавателя |

**Request Body**

```json
{
  "full_name": "Петров Петр Петрович",
  "short_name": "Петров П.П.",
  "rank": "Профессор"
}
```

Все поля опциональны.

**Response 200**

```json
{
  "success": true
}
```

### DELETE `/api/lecturer/{lecturer_id}`

Удаление преподавателя.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `lecturer_id` | integer | ID преподавателя |

**Response 200**

```json
{
  "success": true
}
```

## Disciplines

### POST `/api/discipline/`

Создание новой дисциплины.

**Request Body**

```json
{
  "id": 1,
  "name": "Математика",
  "examtype": "Экзамен",
  "has_labs": true
}
```

| Поле       | Тип     | Обязательно | Описание                     |
| ---------- | ------- | ----------- | ---------------------------- |
| `id`       | integer | Да          | ID дисциплины                |
| `name`     | string  | Да          | Название дисциплины          |
| `examtype` | string  | Нет         | Тип экзамена (Зачёт/Экзамен) |
| `has_labs` | boolean | Нет         | Есть ли лабораторные работы  |

**Response 201**

```json
{
  "id": 1,
  "name": "Математика",
  "examtype": "Экзамен",
  "has_labs": true
}
```

### GET `/api/discipline/`

Получение списка всех дисциплин.

**Response 200**

```json
[
  {
    "id": 1,
    "name": "Математика",
    "examtype": "Экзамен",
    "has_labs": true
  }
]
```

### GET `/api/discipline/{discipline_id}`

Получение дисциплины по ID.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `discipline_id` | integer | ID дисциплины |

**Response 200**

```json
{
  "id": 1,
  "name": "Математика",
  "examtype": "Экзамен",
  "has_labs": true
}
```

### PUT `/api/discipline/{discipline_id}`

Обновление дисциплины.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `discipline_id` | integer | ID дисциплины |

**Request Body**

```json
{
  "name": "Высшая математика",
  "examtype": "Зачёт",
  "has_labs": false
}
```

Все поля опциональны.

**Response 200**

```json
{
  "success": true
}
```

### DELETE `/api/discipline/{discipline_id}`

Удаление дисциплины.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `discipline_id` | integer | ID дисциплины |

**Response 200**

```json
{
  "success": true
}
```

## Auditoriums

### POST `/api/auditorium/`

Создание новой аудитории.

**Request Body**

```json
{
  "id": 1,
  "guid": "550e8400-e29b-41d4-a716-446655440000",
  "name": "101",
  "building": "ГЗ"
}
```

| Поле       | Тип           | Обязательно | Описание           |
| ---------- | ------------- | ----------- | ------------------ |
| `id`       | integer       | Да          | ID аудитории       |
| `guid`     | string (UUID) | Да          | GUID аудитории     |
| `name`     | string        | Да          | Название аудитории |
| `building` | string        | Да          | Корпус             |

**Response 201**

```json
{
  "id": 1,
  "guid": "550e8400-e29b-41d4-a716-446655440000",
  "name": "101",
  "building": "ГЗ"
}
```

### GET `/api/auditorium/`

Получение списка всех аудиторий.

**Response 200**

```json
[
  {
    "id": 1,
    "guid": "550e8400-e29b-41d4-a716-446655440000",
    "name": "101",
    "building": "ГЗ"
  }
]
```

### GET `/api/auditorium/{auditorium_id}`

Получение аудитории по ID.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `auditorium_id` | integer | ID аудитории |

**Response 200**

```json
{
  "id": 1,
  "guid": "550e8400-e29b-41d4-a716-446655440000",
  "name": "101",
  "building": "ГЗ"
}
```

### GET `/api/auditorium/guid/{auditorium_guid}`

Получение аудитории по GUID.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `auditorium_guid` | string (UUID) | GUID аудитории |

**Response 200**

```json
{
  "id": 1,
  "guid": "550e8400-e29b-41d4-a716-446655440000",
  "name": "101",
  "building": "ГЗ"
}
```

### PUT `/api/auditorium/{auditorium_id}`

Обновление аудитории.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `auditorium_id` | integer | ID аудитории |

**Request Body**

```json
{
  "name": "102",
  "building": "Новый корпус"
}
```

Все поля опциональны.

**Response 200**

```json
{
  "success": true
}
```

### DELETE `/api/auditorium/{auditorium_id}`

Удаление аудитории.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `auditorium_id` | integer | ID аудитории |

**Response 200**

```json
{
  "success": true
}
```

## Kind of Work

### POST `/api/kind_of_work/`

Создание нового типа работы.

**Request Body**

```json
{
  "id": 1,
  "type_of_work": "Лекция",
  "complexity": 1
}
```

| Поле           | Тип     | Обязательно | Описание             |
| -------------- | ------- | ----------- | -------------------- |
| `id`           | integer | Да          | ID типа работы       |
| `type_of_work` | string  | Да          | Название типа работы |
| `complexity`   | integer | Да          | Сложность            |

**Response 201**

```json
{
  "id": 1,
  "type_of_work": "Лекция",
  "complexity": 1
}
```

### GET `/api/kind_of_work/`

Получение списка всех типов работ.

**Response 200**

```json
[
  {
    "id": 1,
    "type_of_work": "Лекция",
    "complexity": 1
  }
]
```

### GET `/api/kind_of_work/{id}`

Получение типа работы по ID.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `id` | integer | ID типа работы |

**Response 200**

```json
{
  "id": 1,
  "type_of_work": "Лекция",
  "complexity": 1
}
```

### PUT `/api/kind_of_work/{id}`

Обновление типа работы.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `id` | integer | ID типа работы |

**Request Body**

```json
{
  "type_of_work": "Практика",
  "complexity": 2
}
```

Все поля опциональны.

**Response 200**

```json
{
  "success": true
}
```

### DELETE `/api/kind_of_work/{id}`

Удаление типа работы.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `id` | integer | ID типа работы |

**Response 200**

```json
{
  "success": true
}
```

## Schedule
### GET `/api/schedule/user/{user_id}/day`

Получение расписания пользователя за указанный день.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `user_id` | integer | ID пользователя |

**Query Parameters**
| Параметр | Тип | Обязательно | Описание |
|----------|-----|-------------|----------|
| `date` | string (YYYY-MM-DD) | Да | Дата для выборки |

**Response 200**
```json
[
  {
    "lesson_id": 1,
    "date": "2026-03-26",
    "begin_lesson": "08:30:00",
    "end_lesson": "09:50:00",
    "sub_group": 0,
    "discipline_name": "Математика",
    "kind_of_work": "Лекция",
    "lecturer_short_name": "Иванов",
    "auditorium_name": "101",
    "building": "ГЗ",
    "group_id": 1
  }
]
```

### GET `/api/schedule/user/{user_id}/week`

Получение расписания пользователя за неделю (с понедельника по воскресенье), привязанную к дате `date`.

**Path Parameters**
| Параметр | Тип | Описание |
|----------|-----|----------|
| `user_id` | integer | ID пользователя |

**Query Parameters**
| Параметр | Тип | Обязательно | Описание |
|----------|-----|-------------|----------|
| `date` | string (YYYY-MM-DD) | Да | Анкерная дата внутри недели |

**Response 200**
```json
[
  {
    "lesson_id": 1,
    "date": "2026-03-24",
    "begin_lesson": "08:30:00",
    "end_lesson": "09:50:00",
    "sub_group": 0,
    "discipline_name": "Математика",
    "kind_of_work": "Лекция",
    "lecturer_short_name": "Иванов",
    "auditorium_name": "101",
    "building": "ГЗ",
    "group_id": 1
  }
]
```

## Search
### GET `/api/search/lecturer/day`

Поиск занятий по преподавателю за указанный день.

**Query Parameters**
| Параметр | Тип | Обязательно | Описание |
|----------|-----|-------------|----------|
| `lecturer_id` | integer | Да | ID преподавателя |
| `date` | string (YYYY-MM-DD) | Да | Дата для выборки |
| `group_id` | integer | Нет | Фильтр по группе |
| `sub_group` | integer | Нет | Фильтр по подгруппе |

**Response 200**
```json
[
  {
    "lesson_id": 1,
    "date": "2026-03-26",
    "begin_lesson": "08:30:00",
    "end_lesson": "09:50:00",
    "sub_group": 0,
    "discipline_name": "Математика",
    "kind_of_work": "Лекция",
    "lecturer_short_name": "Иванов",
    "auditorium_name": "101",
    "building": "ГЗ",
    "group_id": 1
  }
]
```

### GET `/api/search/lecturer/week`

Поиск занятий по преподавателю за неделю (с понедельника по воскресенье), привязанную к дате `date`.

**Query Parameters**
| Параметр | Тип | Обязательно | Описание |
|----------|-----|-------------|----------|
| `lecturer_id` | integer | Да | ID преподавателя |
| `date` | string (YYYY-MM-DD) | Да | Анкерная дата внутри недели |
| `group_id` | integer | Нет | Фильтр по группе |
| `sub_group` | integer | Нет | Фильтр по подгруппе |

**Response 200**
```json
[
  {
    "lesson_id": 1,
    "date": "2026-03-24",
    "begin_lesson": "08:30:00",
    "end_lesson": "09:50:00",
    "sub_group": 0,
    "discipline_name": "Математика",
    "kind_of_work": "Лекция",
    "lecturer_short_name": "Иванов",
    "auditorium_name": "101",
    "building": "ГЗ",
    "group_id": 1
  }
]
```

### GET `/api/search/discipline/day`

Поиск занятий по дисциплине за указанный день.

**Query Parameters**
| Параметр | Тип | Обязательно | Описание |
|----------|-----|-------------|----------|
| `discipline_id` | integer | Да | ID дисциплины |
| `date` | string (YYYY-MM-DD) | Да | Дата для выборки |
| `group_id` | integer | Нет | Фильтр по группе |
| `sub_group` | integer | Нет | Фильтр по подгруппе |

**Response 200**
```json
[
  {
    "lesson_id": 1,
    "date": "2026-03-26",
    "begin_lesson": "08:30:00",
    "end_lesson": "09:50:00",
    "sub_group": 0,
    "discipline_name": "Математика",
    "kind_of_work": "Лекция",
    "lecturer_short_name": "Иванов",
    "auditorium_name": "101",
    "building": "ГЗ",
    "group_id": 1
  }
]
```

### GET `/api/search/discipline/week`

Поиск занятий по дисциплине за неделю (с понедельника по воскресенье), привязанную к дате `date`.

**Query Parameters**
| Параметр | Тип | Обязательно | Описание |
|----------|-----|-------------|----------|
| `discipline_id` | integer | Да | ID дисциплины |
| `date` | string (YYYY-MM-DD) | Да | Анкерная дата внутри недели |
| `group_id` | integer | Нет | Фильтр по группе |
| `sub_group` | integer | Нет | Фильтр по подгруппе |

**Response 200**
```json
[
  {
    "lesson_id": 1,
    "date": "2026-03-24",
    "begin_lesson": "08:30:00",
    "end_lesson": "09:50:00",
    "sub_group": 0,
    "discipline_name": "Математика",
    "kind_of_work": "Лекция",
    "lecturer_short_name": "Иванов",
    "auditorium_name": "101",
    "building": "ГЗ",
    "group_id": 1
  }
]
```

## Общие ошибки

### GET `/`
Root
**Response 200**

### GET `/healthz`
Healthz
**Response 200**

### GET `/protected`
Protected
**Response 200**

### GET `/public`
Public
**Response 200**
