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
  "group_oid": 1,
  "subgroup": null
}
```

| Поле           | Тип     | Обязательно | Описание                   |
| -------------- | ------- | ----------- | -------------------------- |
| `id`           | integer | Да          | Telegram ID пользователя   |
| `username`     | string  | Да          | Имя пользователя Telegram  |
| `group_oid`    | integer | Да          | ID группы пользователя     |
| `subgroup`     | integer \| null | Нет | Подгруппа. Допустимые значения: `null`, `0`, `1`, `2`. Если поле не передано, сервер сохраняет `null` |
| `group_guid`   | string  | Нет         | GUID группы                |
| `group_name`   | string  | Нет         | Название группы            |
| `faculty_name` | string  | Нет         | Название факультета        |

Если `subgroup` не передан, сервер сохраняет `null`. Значение `0` означает "без ограничения по подгруппе". Значение `null` означает, что подгруппа у пользователя не задана, и для такого пользователя нельзя получить расписание через `/api/schedule/user/*`. Значения, отличные от `null`, `0`, `1`, `2`, отклоняются с ошибкой `400`.

**Response 201**

```json
{
  "id": 123456789,
  "group_oid": 1,
  "subgroup": null,
  "username": "user123",
  "created_at": "2024-01-15T10:30:00Z",
  "last_used_at": "2024-01-15T10:30:00Z"
}
```

**Response 400**

```json
{
  "detail": "invalid subgroup"
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
    "subgroup": null,
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
  "subgroup": null,
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
  "subgroup": null,
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
  "group_oid": null,
  "subgroup": null
}
```

Все поля опциональны. Для `subgroup`, если поле передано, допустимы только значения `null`, `0`, `1`, `2`. Если поле не передано, текущее значение пользователя сохраняется.

`subgroup: null` разрешён только вместе с `group_oid: null` в этом же запросе. Если нужно просто снять группу, можно передать только `group_oid: null`; текущее значение `subgroup` при этом сохранится.

**Response 200** - Успешное обновление

```json
{
  "id": 123456789,
  "group_oid": null,
  "subgroup": null,
  "username": "new_username",
  "created_at": "2024-01-15T10:30:00Z",
  "last_used_at": "2024-01-15T10:30:00Z"
}
```

**Response 400**

```json
{
  "detail": "invalid subgroup"
}
```

```json
{
  "detail": "subgroup can be null only when group_oid is null"
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
true
```
