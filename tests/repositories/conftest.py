"""Repository-specific test fixtures."""

import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError

import sys
from pathlib import Path

# Добавляем src в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from repositories.user_repository import UserRepository # noqa: F401
from repositories.group_repository import GroupRepository # noqa: F401
from repositories.auditorium_repository import AuditoriumRepository # noqa: F401
from repositories.discipline_repository import DisciplineRepository # noqa: F401
from models.models import User, Group, Auditorium, Discipline # noqa: F401


@pytest.fixture
def user_repository(mock_session):
    """Create UserRepository instance with mocked session."""
    return UserRepository(mock_session)


@pytest.fixture
def user_repository_with_real_session(test_session):
    """Create UserRepository instance with real test session."""
    return UserRepository(test_session)


@pytest.fixture
def user_repository_clean(clean_test_session):
    """Create UserRepository instance with clean session for integration tests."""
    return UserRepository(clean_test_session)


@pytest.fixture
def group_repository(mock_session):
    """Create GroupRepository instance with mocked session."""
    return GroupRepository(mock_session)


@pytest.fixture
def group_repository_with_real_session(test_session):
    """Create GroupRepository instance with real test session."""
    return GroupRepository(test_session)


@pytest.fixture
def group_repository_clean(clean_test_session):
    """Create GroupRepository instance with clean session for integration tests."""
    return GroupRepository(clean_test_session)


@pytest.fixture
def auditorium_repository(mock_session):
    """Create AuditoriumRepository instance with mocked session."""
    return AuditoriumRepository(mock_session)


@pytest.fixture
def auditorium_repository_with_real_session(test_session):
    """Create AuditoriumRepository instance with real test session."""
    return AuditoriumRepository(test_session)


@pytest.fixture
def auditorium_repository_clean(clean_test_session):
    """Create AuditoriumRepository instance with clean session for integration tests."""
    return AuditoriumRepository(clean_test_session)


@pytest.fixture
def discipline_repository(mock_session):
    """Create DisciplineRepository instance with mocked session."""
    return DisciplineRepository(mock_session)


@pytest.fixture
def discipline_repository_with_real_session(test_session):
    """Create DisciplineRepository instance with real test session."""
    return DisciplineRepository(test_session)


@pytest.fixture
def discipline_repository_clean(clean_test_session):
    """Create DisciplineRepository instance with clean session for integration tests."""
    return DisciplineRepository(clean_test_session)


@pytest.fixture
def mock_sqlalchemy_error():
    """Mock SQLAlchemy error for testing error handling."""
    return SQLAlchemyError("Database error")


@pytest.fixture
def multiple_users(unique_user_id):
    """Create multiple user objects for testing with unique IDs."""
    users = []
    for i in range(3):
        user = User(
            id=unique_user_id + i,
            username=f"user_{unique_user_id}_{i}",
            group_oid=i + 1,
            subgroup=i
        )
        users.append(user)
    return users


@pytest.fixture
def multiple_groups(unique_group_id):
    """Create multiple group objects for testing with unique IDs."""
    import uuid
    groups = []
    for i in range(3):
        group = Group(
            id=unique_group_id + i,
            guid=uuid.uuid4(),
            name=f"Group {unique_group_id + i}",
            faculty_name=f"Faculty {i + 1}"
        )
        groups.append(group)
    return groups


@pytest.fixture
def multiple_auditoriums(unique_auditorium_id):
    """Create multiple auditorium objects for testing with unique IDs."""
    import uuid
    auditoriums = []
    for i in range(3):
        auditorium = Auditorium(
            id=unique_auditorium_id + i,
            guid=uuid.uuid4(),
            name=f"Auditorium {unique_auditorium_id + i}",
            building=f"Building {i + 1}"
        )
        auditoriums.append(auditorium)
    return auditoriums


@pytest.fixture
def multiple_disciplines(unique_discipline_id):
    """Create multiple discipline objects for testing with unique IDs."""
    disciplines = []
    examtypes = ["exam", "credit", "exam"]
    for i in range(3):
        discipline = Discipline(
            id=unique_discipline_id + i,
            name=f"Discipline {unique_discipline_id + i}",
            examtype=examtypes[i],
            has_labs=i % 2 == 0
        )
        disciplines.append(discipline)
    return disciplines
