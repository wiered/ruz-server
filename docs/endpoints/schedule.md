# Schedule

В этом разделе описаны эндпоинты для получения расписания пользователя. Используйте эти методы для получения расписания на конкретный день или неделю. Каждый запрос требует передачи API-ключа в заголовке. Все данные отправляются и возвращаются в формате JSON.

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
    "lecturer_id": 1,
    "discipline_id": 1,
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
    "lecturer_id": 1,
    "discipline_id": 1,
    "auditorium_name": "101",
    "building": "ГЗ",
    "group_id": 1
  }
]
```
