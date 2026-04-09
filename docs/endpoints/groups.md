# Groups

В этом разделе описаны эндпоинты для управления группами: создание, получение, обновление и удаление групп. Каждый запрос требует передачи API-ключа в заголовке. Все данные передаются и возвращаются в формате JSON.

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
