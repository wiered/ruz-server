"""Pytest configuration and shared fixtures."""

import datetime
import os
import tempfile
from typing import Generator
from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel

import sys
from pathlib import Path

# Добавляем src в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.models import User, Group, Auditorium, Discipline


@pytest.fixture(scope="session")
def test_db_uri() -> str:
    """Create a temporary SQLite database for testing."""
    # Use SQLite for testing to avoid PostgreSQL dependency
    return "sqlite:///:memory:"


@pytest.fixture(scope="session")
def test_engine(test_db_uri: str):
    """Create test database engine."""
    engine = create_engine(test_db_uri, echo=False)
    # Create all tables
    SQLModel.metadata.create_all(engine)
    yield engine
    # Cleanup
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def test_session(test_engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    session = Session(test_engine)
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def clean_test_session(test_engine) -> Generator[Session, None, None]:
    """Create a clean test session with automatic cleanup for integration tests."""
    session = Session(test_engine)
    try:
        yield session
    finally:
        try:
            # Очищаем все таблицы после каждого теста
            for table in reversed(SQLModel.metadata.sorted_tables):
                session.execute(table.delete())
            session.commit()
        except Exception:
            # Если что-то пошло не так, делаем rollback
            session.rollback()
        finally:
            session.close()


@pytest.fixture
def mock_session():
    """Create a mock database session."""
    return MagicMock(spec=Session)


@pytest.fixture
def unique_user_id():
    """Generate unique user ID for each test."""
    import time
    import random
    # Генерируем уникальный ID на основе времени и случайного числа
    return int(time.time() * 1000000) % 1000000000 + random.randint(1000, 9999)


@pytest.fixture
def sample_user_data(unique_user_id):
    """Sample user data for testing with unique ID."""
    return {
        "id": unique_user_id,
        "username": f"test_user_{unique_user_id}",
        "group_oid": 1,
        "subgroup": 1,
        "created_at": datetime.datetime.now(datetime.timezone.utc),
        "last_used_at": datetime.datetime.now(datetime.timezone.utc)
    }


@pytest.fixture
def sample_user_data_static():
    """Static sample user data for unit tests (without unique ID)."""
    return {
        "id": 123456789,
        "username": "test_user",
        "group_oid": 1,
        "subgroup": 1,
        "created_at": datetime.datetime.now(datetime.timezone.utc),
        "last_used_at": datetime.datetime.now(datetime.timezone.utc)
    }


@pytest.fixture
def sample_user(sample_user_data):
    """Create a sample User object with unique ID."""
    return User(**sample_user_data)


@pytest.fixture
def sample_user_static(sample_user_data_static):
    """Create a static sample User object for unit tests."""
    return User(**sample_user_data_static)


@pytest.fixture
def unique_group_id():
    """Generate unique group ID for each test."""
    import time
    import random
    return int(time.time() * 1000) % 100000 + random.randint(100, 999)


@pytest.fixture
def sample_group(unique_group_id):
    """Create a sample Group object with unique ID."""
    import uuid
    return Group(
        id=unique_group_id,
        guid=uuid.uuid4(),
        name=f"Test Group {unique_group_id}",
        faculty_name="Test Faculty"
    )


@pytest.fixture
def sample_group_static():
    """Create a static sample Group object for unit tests."""
    return Group(
        id=1,
        guid="550e8400-e29b-41d4-a716-446655440000",
        name="Test Group",
        faculty_name="Test Faculty"
    )


@pytest.fixture
def unique_auditorium_id():
    """Generate unique auditorium ID for each test."""
    import time
    import random
    return int(time.time() * 1000) % 100000 + random.randint(100, 999)


@pytest.fixture
def sample_auditorium(unique_auditorium_id):
    """Create a sample Auditorium object with unique ID."""
    import uuid
    return Auditorium(
        id=unique_auditorium_id,
        guid=uuid.uuid4(),
        name=f"Auditorium {unique_auditorium_id}",
        building="Main Building"
    )


@pytest.fixture
def sample_auditorium_static():
    """Create a static sample Auditorium object for unit tests."""
    return Auditorium(
        id=1,
        guid="550e8400-e29b-41d4-a716-446655440000",
        name="A-101",
        building="Main Building"
    )


@pytest.fixture
def unique_discipline_id():
    """Generate unique discipline ID for each test."""
    import time
    import random
    return int(time.time() * 1000) % 100000 + random.randint(100, 999)


@pytest.fixture
def sample_discipline(unique_discipline_id):
    """Create a sample Discipline object with unique ID."""
    return Discipline(
        id=unique_discipline_id,
        name=f"Discipline {unique_discipline_id}",
        examtype="exam",
        has_labs=True
    )


@pytest.fixture
def sample_discipline_static():
    """Create a static sample Discipline object for unit tests."""
    return Discipline(
        id=1,
        name="Linear Algebra",
        examtype="exam",
        has_labs=True
    )


@pytest.fixture
def user_with_group(sample_user, sample_group):
    """Create a user with associated group."""
    sample_user.group = sample_group
    return sample_user


@pytest.fixture
def user_with_group_static(sample_user_static, sample_group_static):
    """Create a static user with associated group for unit tests."""
    sample_user_static.group = sample_group_static
    return sample_user_static
