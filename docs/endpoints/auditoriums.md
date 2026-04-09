# Auditoriums

В этом разделе описаны эндпоинты для управления аудиториями: создание, получение, обновление и удаление аудиторий. Каждый запрос требует передачи API-ключа в заголовке. Все данные передаются и возвращаются в формате JSON.

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
