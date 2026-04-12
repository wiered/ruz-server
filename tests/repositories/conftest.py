"""Repository-specific test fixtures."""

import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError


from ruz_server.repositories.user_repository import UserRepository  # noqa: F401
from ruz_server.repositories.group_repository import GroupRepository  # noqa: F401
from ruz_server.repositories.auditorium_repository import AuditoriumRepository  # noqa: F401
from ruz_server.repositories.discipline_repository import DisciplineRepository  # noqa: F401
from ruz_server.repositories.kind_of_work_repository import KindOfWorkRepository  # noqa: F401
from ruz_server.repositories.lecturer_repository import LecturerRepository  # noqa: F401
from ruz_server.repositories.lesson_group_repository import LessonGroupRepository  # noqa: F401
from ruz_server.repositories.lesson_repository import LessonRepository  # noqa: F401
from ruz_server.models.models import (
    User,
    Group,
    Auditorium,
    Discipline,
    KindOfWork,
    Lecturer,
    LessonGroup,
    Lesson,
)  # noqa: F401


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
def kind_of_work_repository(mock_session):
    """Create KindOfWorkRepository instance with mocked session."""
    return KindOfWorkRepository(mock_session)


@pytest.fixture
def kind_of_work_repository_with_real_session(test_session):
    """Create KindOfWorkRepository instance with real test session."""
    return KindOfWorkRepository(test_session)


@pytest.fixture
def kind_of_work_repository_clean(clean_test_session):
    """Create KindOfWorkRepository instance with clean session for integration tests."""
    return KindOfWorkRepository(clean_test_session)


@pytest.fixture
def lecturer_repository(mock_session):
    """Create LecturerRepository instance with mocked session."""
    return LecturerRepository(mock_session)


@pytest.fixture
def lecturer_repository_with_real_session(test_session):
    """Create LecturerRepository instance with real test session."""
    return LecturerRepository(test_session)


@pytest.fixture
def lecturer_repository_clean(clean_test_session):
    """Create LecturerRepository instance with clean session for integration tests."""
    return LecturerRepository(clean_test_session)


@pytest.fixture
def lesson_group_repository(mock_session):
    """Create LessonGroupRepository instance with mocked session."""
    return LessonGroupRepository(mock_session)


@pytest.fixture
def lesson_group_repository_with_real_session(test_session):
    """Create LessonGroupRepository instance with real test session."""
    return LessonGroupRepository(test_session)


@pytest.fixture
def lesson_group_repository_clean(clean_test_session):
    """Create LessonGroupRepository instance with clean session for integration tests."""
    return LessonGroupRepository(clean_test_session)


@pytest.fixture
def lesson_repository(mock_session):
    """Create LessonRepository instance with mocked session."""
    return LessonRepository(mock_session)


@pytest.fixture
def lesson_repository_with_real_session(test_session):
    """Create LessonRepository instance with real test session."""
    return LessonRepository(test_session)


@pytest.fixture
def lesson_repository_clean(clean_test_session):
    """Create LessonRepository instance with clean session for integration tests."""
    return LessonRepository(clean_test_session)


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
            subgroup=i,
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
            faculty_name=f"Faculty {i + 1}",
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
            building=f"Building {i + 1}",
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
            has_labs=i % 2 == 0,
        )
        disciplines.append(discipline)
    return disciplines


@pytest.fixture
def multiple_kinds_of_work(unique_kind_of_work_id):
    """Create multiple kind-of-work objects for testing with unique IDs."""
    kinds = []
    for i in range(3):
        kind = KindOfWork(
            id=unique_kind_of_work_id + i,
            type_of_work=f"Type {unique_kind_of_work_id + i}",
            complexity=i + 1,
        )
        kinds.append(kind)
    return kinds


@pytest.fixture
def multiple_lecturers(unique_lecturer_id):
    """Create multiple lecturer objects for testing with unique IDs."""
    import uuid

    lecturers = []
    for i in range(3):
        lecturer = Lecturer(
            id=unique_lecturer_id + i,
            guid=uuid.uuid4(),
            full_name=f"Lecturer {unique_lecturer_id + i}",
            short_name=f"L{unique_lecturer_id + i}",
            rank=f"Rank {i + 1}",
        )
        lecturers.append(lecturer)
    return lecturers


@pytest.fixture
def multiple_lesson_groups():
    """Create multiple lesson-group association objects for testing."""
    return [
        LessonGroup(lesson_id=1, group_id=1),
        LessonGroup(lesson_id=1, group_id=2),
        LessonGroup(lesson_id=2, group_id=1),
    ]


@pytest.fixture
def multiple_lessons(unique_lesson_id):
    """Create multiple lesson objects for testing with unique IDs."""
    import datetime

    return [
        Lesson(
            id=unique_lesson_id,
            kind_of_work_id=1,
            discipline_id=1,
            auditorium_id=1,
            lecturer_id=1,
            date=datetime.date(2025, 1, 1),
            begin_lesson=datetime.time(9, 0),
            end_lesson=datetime.time(10, 30),
            sub_group=1,
        ),
        Lesson(
            id=unique_lesson_id + 1,
            kind_of_work_id=2,
            discipline_id=2,
            auditorium_id=2,
            lecturer_id=2,
            date=datetime.date(2025, 1, 2),
            begin_lesson=datetime.time(11, 0),
            end_lesson=datetime.time(12, 30),
            sub_group=2,
        ),
        Lesson(
            id=unique_lesson_id + 2,
            kind_of_work_id=1,
            discipline_id=2,
            auditorium_id=1,
            lecturer_id=1,
            date=datetime.date(2025, 1, 3),
            begin_lesson=datetime.time(13, 0),
            end_lesson=datetime.time(14, 30),
            sub_group=1,
        ),
    ]
