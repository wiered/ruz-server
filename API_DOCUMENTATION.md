# API Documentation - Ruz Server

## Обзор проекта

Проект представляет собой REST API для управления расписанием университета, построенный на FastAPI с использованием SQLModel/SQLAlchemy. API обеспечивает полный CRUD функционал для всех основных сущностей системы.

## Архитектура

- **Backend**: FastAPI
- **ORM**: SQLModel (на основе SQLAlchemy)
- **База данных**: PostgreSQL
- **Аутентификация**: API Key
- **Структура**: Repository pattern + API endpoints

## Таблицы базы данных

### 1. Users (Пользователи)

**Таблица**: `users`
**Описание**: Хранит информацию о пользователях Telegram бота

| Поле         | Тип        | Описание                                |
| ------------ | ---------- | --------------------------------------- |
| id           | BigInteger | Telegram ID пользователя (PK)           |
| group_oid    | int        | ID группы пользователя (FK → groups.id) |
| subgroup     | int        | Подгруппа (по умолчанию 0)              |
| username     | str        | Имя пользователя Telegram               |
| created_at   | datetime   | Дата создания                           |
| last_used_at | datetime   | Последнее использование                 |

**Связи**:

- `group_oid` → `groups.id` (Many-to-One)

### 2. Groups (Группы)

**Таблица**: `groups`
**Описание**: Учебные группы университета

| Поле         | Тип  | Описание                     |
| ------------ | ---- | ---------------------------- |
| id           | int  | ID группы (PK)               |
| guid         | UUID | GUID группы                  |
| name         | str  | Название группы (уникальное) |
| faculty_name | str  | Название факультета          |

**Связи**:

- One-to-Many с `users`
- Many-to-Many с `lessons` через `lesson_group`

### 3. Lesson (Занятия)

**Таблица**: `lesson`
**Описание**: Основная таблица расписания

| Поле            | Тип      | Описание                          |
| --------------- | -------- | --------------------------------- |
| id              | int      | ID занятия (PK)                   |
| kind_of_work_id | int      | Тип работы (FK → kind_of_work.id) |
| discipline_id   | int      | Дисциплина (FK → discipline.id)   |
| auditorium_id   | int      | Аудитория (FK → auditorium.id)    |
| lecturer_id     | int      | Преподаватель (FK → lecturer.id)  |
| date            | date     | Дата занятия                      |
| begin_lesson    | time     | Время начала                      |
| end_lesson      | time     | Время окончания                   |
| updated_at      | datetime | Время обновления                  |
| sub_group       | int      | Подгруппа (по умолчанию 0)        |

**Связи**:

- Many-to-One с `kind_of_work`, `discipline`, `auditorium`, `lecturer`
- Many-to-Many с `groups` через `lesson_group`

### 4. Lecturer (Преподаватели)

**Таблица**: `lecturer`
**Описание**: Информация о преподавателях

| Поле       | Тип  | Описание              |
| ---------- | ---- | --------------------- |
| id         | int  | ID преподавателя (PK) |
| guid       | UUID | GUID преподавателя    |
| full_name  | str  | Полное имя            |
| short_name | str  | Краткое имя           |
| rank       | str  | Должность/звание      |

**Связи**:

- One-to-Many с `lessons`

### 5. Discipline (Дисциплины)

**Таблица**: `discipline`
**Описание**: Учебные дисциплины

| Поле     | Тип  | Описание                     |
| -------- | ---- | ---------------------------- |
| id       | int  | ID дисциплины (PK)           |
| name     | str  | Название дисциплины          |
| examtype | str  | Тип экзамена (Зачёт/Экзамен) |
| has_labs | bool | Есть ли лабораторные работы  |

**Связи**:

- One-to-Many с `lessons`

### 6. Auditorium (Аудитории)

**Таблица**: `auditorium`
**Описание**: Учебные аудитории

| Поле     | Тип  | Описание           |
| -------- | ---- | ------------------ |
| id       | int  | ID аудитории (PK)  |
| guid     | UUID | GUID аудитории     |
| name     | str  | Название аудитории |
| building | str  | Корпус             |

**Связи**:

- One-to-Many с `lessons`

### 7. KindOfWork (Типы работ)

**Таблица**: `kind_of_work`
**Описание**: Типы учебных занятий

| Поле         | Тип | Описание             |
| ------------ | --- | -------------------- |
| id           | int | ID типа работы (PK)  |
| type_of_work | str | Название типа работы |
| complexity   | int | Сложность            |

**Связи**:

- One-to-Many с `lessons`

### 8. LessonGroup (Связь занятий и групп)

**Таблица**: `lesson_group`
**Описание**: Промежуточная таблица для связи Many-to-Many между занятиями и группами

| Поле      | Тип | Описание                        |
| --------- | --- | ------------------------------- |
| lesson_id | int | ID занятия (PK, FK → lesson.id) |
| group_id  | int | ID группы (PK, FK → groups.id)  |

## API Endpoints

### Аутентификация

Все эндпоинты требуют API ключ в заголовке `X-API-Key`.

### 1. Users API (`/api/user`)

#### `POST /api/user/`

**Описание**: Создать нового пользователя
**Тело запроса**:

```json
{
  "id": 123456789,
  "username": "user123",
  "group_oid": 1,
  "subgroup": 0,
  "group_guid": "uuid",
  "group_name": "ИУ5-11",
  "faculty_name": "Факультет"
}
```

#### `GET /api/user/`

**Описание**: Получить список всех пользователей
**Ответ**: Массив объектов UserRead

#### `GET /api/user/{user_id}`

**Описание**: Получить пользователя по ID
**Параметры**: `user_id` (int) - ID пользователя

#### `GET /api/user/guid/{username}`

**Описание**: Получить пользователя по username
**Параметры**: `username` (str) - Имя пользователя

#### `PUT /api/user/{user_id}`

**Описание**: Обновить пользователя
**Тело запроса**: UserUpdate (все поля опциональны)

#### `PUT /api/user/last_used_at/{user_id}`

**Описание**: Обновить время последнего использования

#### `DELETE /api/user/{user_id}`

**Описание**: Удалить пользователя

### 2. Groups API (`/api/group`)

#### `POST /api/group/`

**Описание**: Создать новую группу
**Тело запроса**:

```json
{
  "id": 1,
  "guid": "uuid",
  "name": "ИУ5-11",
  "faculty_name": "Факультет"
}
```

#### `GET /api/group/`

**Описание**: Получить список всех групп

#### `GET /api/group/{group_id}`

**Описание**: Получить группу по ID

#### `GET /api/group/guid/{group_guid}`

**Описание**: Получить группу по GUID

#### `PUT /api/group/{group_id}`

**Описание**: Обновить группу

#### `DELETE /api/group/{group_id}`

**Описание**: Удалить группу

### 3. Lessons API (`/api/lesson`)

#### `POST /api/lesson/`

**Описание**: Создать новое занятие
**Тело запроса**:

```json
{
  "id": 1,
  "lecturer_id": 1,
  "lecturer_guid": "uuid",
  "lecturer_full_name": "Иванов И.И.",
  "lecturer_short_name": "Иванов",
  "lecturer_rank": "Доцент",
  "kind_of_work_id": 1,
  "type_of_work": "Лекция",
  "complexity": 1,
  "discipline_id": 1,
  "discipline_name": "Математика",
  "auditorium_id": 1,
  "auditorium_guid": "uuid",
  "auditorium_name": "101",
  "auditorium_building": "ГЗ",
  "date": "2024-01-15",
  "begin_lesson": "09:00:00",
  "end_lesson": "10:30:00",
  "group_id": 1,
  "sub_group": 0
}
```

#### `PUT /api/lesson/parse`

**Описание**: Парсинг расписания из внешнего API

#### `GET /api/lesson/`

**Описание**: Получить список всех занятий

#### `GET /api/lesson/{lesson_id}`

**Описание**: Получить занятие по ID

#### `PUT /api/lesson/{lesson_id}`

**Описание**: Обновить занятие

#### `DELETE /api/lesson/{lesson_id}`

**Описание**: Удалить занятие

### 4. Lecturers API (`/api/lecturer`)

#### `POST /api/lecturer/`

**Описание**: Создать нового преподавателя
**Тело запроса**:

```json
{
  "id": 1,
  "guid": "uuid",
  "full_name": "Иванов Иван Иванович",
  "short_name": "Иванов И.И.",
  "rank": "Доцент"
}
```

#### `GET /api/lecturer/`

**Описание**: Получить список всех преподавателей

#### `GET /api/lecturer/{lecturer_id}`

**Описание**: Получить преподавателя по ID

#### `GET /api/lecturer/guid/{lecturer_guid}`

**Описание**: Получить преподавателя по GUID

#### `PUT /api/lecturer/{lecturer_id}`

**Описание**: Обновить преподавателя

#### `DELETE /api/lecturer/{lecturer_id}`

**Описание**: Удалить преподавателя

### 5. Disciplines API (`/api/discipline`)

#### `POST /api/discipline/`

**Описание**: Создать новую дисциплину
**Тело запроса**:

```json
{
  "id": 1,
  "name": "Математика",
  "examtype": "Экзамен",
  "has_labs": true
}
```

#### `GET /api/discipline/`

**Описание**: Получить список всех дисциплин

#### `GET /api/discipline/{discipline_id}`

**Описание**: Получить дисциплину по ID

#### `PUT /api/discipline/{discipline_id}`

**Описание**: Обновить дисциплину

#### `DELETE /api/discipline/{discipline_id}`

**Описание**: Удалить дисциплину

### 6. Auditoriums API (`/api/auditorium`)

#### `POST /api/auditorium/`

**Описание**: Создать новую аудиторию
**Тело запроса**:

```json
{
  "id": 1,
  "guid": "uuid",
  "name": "101",
  "building": "ГЗ"
}
```

#### `GET /api/auditorium/`

**Описание**: Получить список всех аудиторий

#### `GET /api/auditorium/{auditorium_id}`

**Описание**: Получить аудиторию по ID

#### `GET /api/auditorium/guid/{auditorium_guid}`

**Описание**: Получить аудиторию по GUID

#### `PUT /api/auditorium/{auditorium_id}`

**Описание**: Обновить аудиторию

#### `DELETE /api/auditorium/{auditorium_id}`

**Описание**: Удалить аудиторию

### 7. Kind of Work API (`/api/kind_of_work`)

#### `POST /api/kind_of_work/`

**Описание**: Создать новый тип работы
**Тело запроса**:

```json
{
  "id": 1,
  "type_of_work": "Лекция",
  "complexity": 1
}
```

#### `GET /api/kind_of_work/`

**Описание**: Получить список всех типов работ

#### `GET /api/kind_of_work/{id}`

**Описание**: Получить тип работы по ID

#### `PUT /api/kind_of_work/{id}`

**Описание**: Обновить тип работы

#### `DELETE /api/kind_of_work/{id}`

**Описание**: Удалить тип работы

## Статус готовности CRUD операций

### ✅ Полностью готовые сущности:

- **Users** - полный CRUD + дополнительные методы
- **Groups** - полный CRUD
- **Lessons** - полный CRUD + парсинг
- **Lecturers** - полный CRUD
- **Disciplines** - полный CRUD
- **Auditoriums** - полный CRUD
- **Kind of Work** - полный CRUD

### 📊 Статистика:

- **Таблиц**: 8
- **Репозиториев**: 8 (100% покрытие)
- **API эндпоинтов**: 8 (100% покрытие)
- **CRUD операций**: Полный набор для всех сущностей

### 🔧 Дополнительные возможности:

- **Аутентификация**: API Key для всех эндпоинтов
- **Валидация**: Pydantic схемы для всех операций
- **Обработка ошибок**: Централизованная через helpers
- **Логирование**: Подробное логирование всех операций
- **Связи**: Автоматическое создание связанных сущностей
- **Парсинг**: Интеграция с внешним API для получения расписания

## Заключение

Проект полностью готов для использования. Все таблицы имеют соответствующие репозитории и API эндпоинты с полным CRUD функционалом. Архитектура следует лучшим практикам с разделением на слои (модели, репозитории, API) и обеспечивает надежную работу с данными.
