# Kind of Work

В этом разделе описаны эндпоинты для управления типами работ: создание, просмотр, обновление и удаление типов работ. Каждый запрос требует передачи API-ключа в заголовке. Все данные передаются и возвращаются в формате JSON.

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
