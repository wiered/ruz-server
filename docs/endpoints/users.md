# Users

В этом разделе описаны эндпоинты для управления пользователями: создание, получение списка, обновление и удаление пользователей. Каждый запрос требует передачи API-ключа в заголовке. Все данные передаются и возвращаются в формате JSON.

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

| Поле           | Тип     | Обязательно | Описание                   |
| -------------- | ------- | ----------- | -------------------------- |
| `id`           | integer | Да          | Telegram ID пользователя   |
| `username`     | string  | Да          | Имя пользователя Telegram  |
| `group_oid`    | integer | Да          | ID группы пользователя     |
| `subgroup`     | integer | Нет         | Подгруппа (по умолчанию 0) |
| `group_guid`   | string  | Нет         | GUID группы                |
| `group_name`   | string  | Нет         | Название группы            |
| `faculty_name` | string  | Нет         | Название факультета        |

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
