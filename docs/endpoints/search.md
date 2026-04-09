# Search

В этом разделе описаны эндпоинты для поиска занятий по различным параметрам (например, по преподавателю за день или неделю). Каждый запрос требует передачи API-ключа в заголовке. Все данные передаются и возвращаются в формате JSON.

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
    "lecturer_id": 1,
    "discipline_id": 1,
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
    "lecturer_id": 1,
    "discipline_id": 1,
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
    "lecturer_id": 1,
    "discipline_id": 1,
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
    "lecturer_id": 1,
    "discipline_id": 1,
    "auditorium_name": "101",
    "building": "ГЗ",
    "group_id": 1
  }
]
```
