"""Repository tests for user/search date-range filters."""

import datetime
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session

from ruz_server.models.models import (
    Auditorium,
    Discipline,
    Group,
    KindOfWork,
    Lecturer,
    Lesson,
    LessonGroup,
)
from ruz_server.repositories.lesson_repository import LessonRepository


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


def _seed_entities(session: Session):
    session.add(Group(id=7001, guid=uuid.uuid4(), name="IU8-31", faculty_name="Informatics"))
    session.add(Lecturer(id=9001, guid=uuid.uuid4(), full_name="Lecturer", short_name="Lec", rank="Prof"))
    session.add(KindOfWork(id=8001, type_of_work="Лекция", complexity=2))
    session.add(Discipline(id=7101, name="Math", examtype="Неизв.", has_labs=False))
    session.add(Auditorium(id=6001, guid=uuid.uuid4(), name="A-101", building="Main"))
    session.commit()


def _lesson(lesson_id: int, *, sub_group: int, day: int, begin_hour: int) -> Lesson:
    return Lesson(
        id=lesson_id,
        kind_of_work_id=8001,
        discipline_id=7101,
        auditorium_id=6001,
        lecturer_id=9001,
        date=datetime.date(2025, 1, day),
        begin_lesson=datetime.time(begin_hour, 0),
        end_lesson=datetime.time(begin_hour + 1, 30),
        sub_group=sub_group,
    )


@pytest.mark.repositories
def test_list_for_user_by_date_range_applies_subgroup_policy_and_order(session: Session):
    _seed_entities(session)
    lessons = [
        _lesson(1003, sub_group=2, day=13, begin_hour=12),
        _lesson(1001, sub_group=0, day=13, begin_hour=8),
        _lesson(1002, sub_group=1, day=13, begin_hour=10),
        _lesson(1004, sub_group=1, day=14, begin_hour=9),
    ]
    session.add_all(lessons)
    session.add_all([LessonGroup(lesson_id=lesson.id, group_id=7001) for lesson in lessons])
    session.commit()

    repo = LessonRepository(session)
    result = repo.ListForUserByDateRange(
        group_id=7001,
        subgroup=1,
        start=datetime.date(2025, 1, 13),
        end=datetime.date(2025, 1, 14),
    )

    assert [lesson.id for lesson in result] == [1001, 1002, 1004]


@pytest.mark.repositories
def test_list_for_user_by_date_range_subgroup_zero_returns_all_sub_groups(session: Session):
    _seed_entities(session)
    lessons = [
        _lesson(1003, sub_group=2, day=13, begin_hour=12),
        _lesson(1001, sub_group=0, day=13, begin_hour=8),
        _lesson(1002, sub_group=1, day=13, begin_hour=10),
        _lesson(1004, sub_group=1, day=14, begin_hour=9),
    ]
    session.add_all(lessons)
    session.add_all([LessonGroup(lesson_id=lesson.id, group_id=7001) for lesson in lessons])
    session.commit()

    repo = LessonRepository(session)
    result = repo.ListForUserByDateRange(
        group_id=7001,
        subgroup=0,
        start=datetime.date(2025, 1, 13),
        end=datetime.date(2025, 1, 14),
    )

    assert [lesson.id for lesson in result] == [1001, 1002, 1003, 1004]


@pytest.mark.repositories
def test_list_by_lecturer_and_date_range_applies_filters_and_sorting(session: Session):
    _seed_entities(session)
    lessons = [
        _lesson(2002, sub_group=2, day=13, begin_hour=11),
        _lesson(2001, sub_group=1, day=13, begin_hour=9),
        _lesson(2003, sub_group=1, day=14, begin_hour=8),
    ]
    session.add_all(lessons)
    session.add_all(
        [
            LessonGroup(lesson_id=2001, group_id=7001),
            LessonGroup(lesson_id=2002, group_id=7001),
            LessonGroup(lesson_id=2003, group_id=7001),
        ]
    )
    session.commit()

    repo = LessonRepository(session)
    result = repo.ListByLecturerAndDateRange(
        lecturer_id=9001,
        start=datetime.date(2025, 1, 13),
        end=datetime.date(2025, 1, 14),
        group_id=7001,
        sub_group=1,
    )

    assert [lesson.id for lesson in result] == [2001, 2003]


@pytest.mark.repositories
def test_list_by_lecturer_and_date_range_sub_group_zero_returns_all(session: Session):
    _seed_entities(session)
    lessons = [
        _lesson(2002, sub_group=2, day=13, begin_hour=11),
        _lesson(2001, sub_group=1, day=13, begin_hour=9),
        _lesson(2003, sub_group=1, day=14, begin_hour=8),
    ]
    session.add_all(lessons)
    session.add_all(
        [
            LessonGroup(lesson_id=2001, group_id=7001),
            LessonGroup(lesson_id=2002, group_id=7001),
            LessonGroup(lesson_id=2003, group_id=7001),
        ]
    )
    session.commit()

    repo = LessonRepository(session)
    result = repo.ListByLecturerAndDateRange(
        lecturer_id=9001,
        start=datetime.date(2025, 1, 13),
        end=datetime.date(2025, 1, 14),
        group_id=7001,
        sub_group=0,
    )

    assert [lesson.id for lesson in result] == [2001, 2002, 2003]


@pytest.mark.repositories
def test_list_by_lecturer_and_date_range_includes_common_sub_group_zero_lessons(session: Session):
    _seed_entities(session)
    lessons = [
        _lesson(3001, sub_group=0, day=13, begin_hour=8),
        _lesson(3002, sub_group=2, day=13, begin_hour=11),
    ]
    session.add_all(lessons)
    session.add_all(
        [
            LessonGroup(lesson_id=3001, group_id=7001),
            LessonGroup(lesson_id=3002, group_id=7001),
        ]
    )
    session.commit()

    repo = LessonRepository(session)
    result = repo.ListByLecturerAndDateRange(
        lecturer_id=9001,
        start=datetime.date(2025, 1, 13),
        end=datetime.date(2025, 1, 13),
        group_id=7001,
        sub_group=2,
    )

    assert [lesson.id for lesson in result] == [3001, 3002]


@pytest.mark.repositories
def test_list_by_discipline_and_date_range_sub_group_zero_returns_all(session: Session):
    _seed_entities(session)
    lessons = [
        _lesson(4002, sub_group=2, day=13, begin_hour=11),
        _lesson(4001, sub_group=1, day=13, begin_hour=9),
    ]
    session.add_all(lessons)
    session.add_all(
        [
            LessonGroup(lesson_id=4001, group_id=7001),
            LessonGroup(lesson_id=4002, group_id=7001),
        ]
    )
    session.commit()

    repo = LessonRepository(session)
    result = repo.ListByDisciplineAndDateRange(
        discipline_id=7101,
        start=datetime.date(2025, 1, 13),
        end=datetime.date(2025, 1, 13),
        group_id=7001,
        sub_group=0,
    )

    assert [lesson.id for lesson in result] == [4001, 4002]


@pytest.mark.repositories
def test_list_by_discipline_and_date_range_includes_common_sub_group_zero_lessons(session: Session):
    _seed_entities(session)
    lessons = [
        _lesson(5001, sub_group=0, day=13, begin_hour=8),
        _lesson(5002, sub_group=2, day=13, begin_hour=11),
    ]
    session.add_all(lessons)
    session.add_all(
        [
            LessonGroup(lesson_id=5001, group_id=7001),
            LessonGroup(lesson_id=5002, group_id=7001),
        ]
    )
    session.commit()

    repo = LessonRepository(session)
    result = repo.ListByDisciplineAndDateRange(
        discipline_id=7101,
        start=datetime.date(2025, 1, 13),
        end=datetime.date(2025, 1, 13),
        group_id=7001,
        sub_group=2,
    )

    assert [lesson.id for lesson in result] == [5001, 5002]
