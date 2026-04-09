# Disciplines

В этом разделе описаны эндпоинты для управления дисциплинами: создание, получение, обновление и удаление дисциплин. Каждый запрос требует передачи API-ключа в заголовке. Все данные передаются и возвращаются в формате JSON.

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
