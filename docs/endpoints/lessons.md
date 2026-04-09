# Lessons

В этом разделе описаны эндпоинты для управления занятиями: создание, получение, обновление и удаление занятий. Каждый запрос требует передачи API-ключа в заголовке. Все данные передаются и возвращаются в формате JSON.

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
