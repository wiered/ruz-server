# Тесты для RUZ Server

Этот каталог содержит unit тесты для проекта RUZ Server, организованные по компонентам для удобного раздельного запуска.

## Структура

```
tests/
├── __init__.py
├── conftest.py              # Общие фикстуры и конфигурация
├── pytest.ini              # Конфигурация pytest
├── repositories/            # Тесты для репозиториев
│   ├── __init__.py
│   ├── conftest.py         # Фикстуры для репозиториев
│   └── test_user_repository.py
├── api/                     # Тесты для API (будущие)
├── helpers/                 # Тесты для хелперов (будущие)
└── README.md               # Этот файл
```

## Запуск тестов

### Установка зависимостей

```bash
# Установить тестовые зависимости
make install-test-deps
# или
pip install -e ".[test]"
```

### Запуск всех тестов

```bash
make test
# или
pytest
```

### Запуск тестов по компонентам

```bash
# Только тесты репозиториев
make test-repositories
pytest -m repositories

# Только unit тесты
make test-unit
pytest -m unit

# Только integration тесты
make test-integration
pytest -m integration

# Только быстрые тесты (исключить медленные)
make test-fast
pytest -m "not slow"
```

### Запуск с покрытием кода

```bash
make test-coverage
pytest --cov=src --cov-report=html --cov-report=term
```

## Маркеры тестов

- `repositories` - тесты для слоя репозиториев
- `api` - тесты для API слоя
- `helpers` - тесты для вспомогательных функций
- `unit` - unit тесты
- `integration` - интеграционные тесты
- `slow` - медленные тесты

## Добавление новых тестов

### Для репозиториев

1. Создайте файл `tests/repositories/test_<repository_name>.py`
2. Используйте маркер `@pytest.mark.repositories`
3. Для unit тестов добавьте `@pytest.mark.unit`
4. Для integration тестов добавьте `@pytest.mark.integration`

### Для API

1. Создайте файл `tests/api/test_<api_module>.py`
2. Используйте маркер `@pytest.mark.api`

### Для хелперов

1. Создайте файл `tests/helpers/test_<helper_module>.py`
2. Используйте маркер `@pytest.mark.helpers`

## Фикстуры

### Общие фикстуры (conftest.py)

- `test_session` - тестовая сессия базы данных
- `mock_session` - мок сессии для unit тестов
- `sample_user_data` - тестовые данные пользователя
- `sample_user` - объект User для тестов
- `sample_group` - объект Group для тестов

### Фикстуры репозиториев (repositories/conftest.py)

- `user_repository` - UserRepository с мок сессией
- `user_repository_with_real_session` - UserRepository с реальной сессией
- `multiple_users` - несколько пользователей для тестов

## Примеры тестов

### Unit тест с моками

```python
@pytest.mark.repositories
@pytest.mark.unit
def test_create_success(self, user_repository, sample_user, mock_session):
    """Test successful user creation."""
    # Setup
    mock_session.add.return_value = None
    mock_session.commit.return_value = None

    # Execute
    result = user_repository.Create(sample_user)

    # Assert
    assert result == sample_user
    mock_session.add.assert_called_once_with(sample_user)
    mock_session.commit.assert_called_once()
```

### Integration тест с реальной БД

```python
@pytest.mark.repositories
@pytest.mark.integration
def test_create_and_retrieve_user(self, user_repository_with_real_session, sample_user):
    """Test creating and retrieving a user with real database."""
    # Execute
    created_user = user_repository_with_real_session.Create(sample_user)
    retrieved_user = user_repository_with_real_session.GetById(sample_user.id)

    # Assert
    assert created_user.id == sample_user.id
    assert retrieved_user is not None
    assert retrieved_user.username == sample_user.username
```

## База данных для тестов

Тесты используют SQLite в памяти для быстрого выполнения и изоляции. Интеграционные тесты могут использовать реальную PostgreSQL базу при необходимости.

## Логирование

Тесты настроены на отключение предупреждений для чистого вывода. Логирование ошибок в тестах отключено по умолчанию.
