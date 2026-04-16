# Schedule

В этом разделе описаны эндпоинты для получения расписания пользователя и недельного расписания группы целиком. Используйте эти методы для получения расписания на конкретный день или неделю. Каждый запрос требует передачи API-ключа в заголовке. Все данные отправляются и возвращаются в формате JSON.

### GET `/api/schedule/user/{user_id}/day`

Получение расписания пользователя за указанный день.

Если у пользователя `group_oid = null`, сервер возвращает `400`. Если у пользователя `subgroup = null`, сервер тоже возвращает `400`: расписание для такого пользователя недоступно, пока подгруппа не задана.

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

**Response 400**

```json
{
  "detail": "User has no group assigned"
}
```

```json
{
  "detail": "User has no subgroup assigned"
}
```

### GET `/api/schedule/user/{user_id}/week`

Получение расписания пользователя за неделю (с понедельника по воскресенье), привязанную к дате `date`.

Если у пользователя `group_oid = null`, сервер возвращает `400`. Если у пользователя `subgroup = null`, сервер тоже возвращает `400`: расписание для такого пользователя недоступно, пока подгруппа не задана.

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

**Response 400**

```json
{
  "detail": "User has no group assigned"
}
```

```json
{
  "detail": "User has no subgroup assigned"
}
```

### GET `/api/schedule/group/{group_id}/week`

Расписание группы за календарную неделю (понедельник–воскресенье), **со всеми подгруппами**: в ответ попадают все занятия, привязанные к этой группе в БД, без фильтра по `Lesson.sub_group`.

Если группы с таким `group_id` нет, сервер возвращает `404`.

**Path Parameters**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `group_id` | integer | ID группы (`Group.id` / groupOid) |

**Query Parameters**

| Параметр | Тип | Обязательно | Описание |
|----------|-----|-------------|----------|
| `date` | string (YYYY-MM-DD) | Да | Анкерная дата внутри недели |

**Response 200** — тот же формат массива объектов, что у `/api/schedule/user/{user_id}/week`.

**Response 404**

```json
{
  "detail": "Error: Not Found"
}
```
