"""Tests for SQLModel entities defined in models.py."""

import datetime
import uuid
import pytest


from ruz_server.models.models import (
    SQLModel,
    LessonGroup,
    Group,
    User,
    Lecturer,
    KindOfWork,
    Discipline,
    Auditorium,
    Lesson,
)


@pytest.mark.unit
@pytest.mark.models
class TestModels:
    def test_sqlmodel_metadata_contains_expected_tables(self):
        table_names = set(SQLModel.metadata.tables.keys())
        assert "lesson_group" in table_names
        assert "groups" in table_names
        assert "users" in table_names
        assert "lecturer" in table_names
        assert "kind_of_work" in table_names
        assert "discipline" in table_names
        assert "auditorium" in table_names
        assert "lesson" in table_names

    def test_group_model_creation(self):
        entity = Group(
            id=1,
            guid=uuid.uuid4(),
            name="IU8-31",
            faculty_name="Informatics",
        )
        assert entity.id == 1
        assert entity.name == "IU8-31"
        assert entity.faculty_name == "Informatics"

    def test_user_model_defaults(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        entity = User(
            id=123456,
            username="tester",
            group_oid=1,
        )
        assert entity.subgroup is None
        assert isinstance(entity.created_at, datetime.datetime)
        assert isinstance(entity.last_used_at, datetime.datetime)
        assert entity.created_at.tzinfo is not None
        assert entity.last_used_at.tzinfo is not None
        assert entity.created_at <= now + datetime.timedelta(seconds=1)

    def test_lecturer_model_creation(self):
        entity = Lecturer(
            id=10,
            guid=uuid.uuid4(),
            full_name="John Smith",
            short_name="J. Smith",
            rank="Professor",
        )
        assert entity.full_name == "John Smith"
        assert entity.short_name == "J. Smith"
        assert entity.rank == "Professor"

    def test_kind_of_work_model_creation(self):
        entity = KindOfWork(
            id=20,
            type_of_work="Lecture",
            complexity=3,
        )
        assert entity.type_of_work == "Lecture"
        assert entity.complexity == 3

    def test_discipline_model_defaults(self):
        entity = Discipline(
            id=30,
            name="Math",
            examtype="Exam",
        )
        assert entity.name == "Math"
        assert entity.examtype == "Exam"
        assert entity.has_labs is False

    def test_auditorium_model_creation(self):
        entity = Auditorium(
            id=40,
            guid=uuid.uuid4(),
            name="A-101",
            building="Main",
        )
        assert entity.name == "A-101"
        assert entity.building == "Main"

    def test_lesson_model_defaults(self):
        entity = Lesson(
            id=50,
            kind_of_work_id=20,
            discipline_id=30,
            auditorium_id=40,
            lecturer_id=10,
            begin_lesson=datetime.time(9, 0),
            end_lesson=datetime.time(10, 30),
        )
        assert entity.sub_group == 0
        assert isinstance(entity.date, datetime.date)
        assert isinstance(entity.updated_at, datetime.datetime)
        assert entity.begin_lesson == datetime.time(9, 0)
        assert entity.end_lesson == datetime.time(10, 30)

    def test_lesson_group_composite_keys(self):
        entity = LessonGroup(lesson_id=50, group_id=1)
        assert entity.lesson_id == 50
        assert entity.group_id == 1

    def test_relationship_attributes_exist(self):
        # Regression guard: repository methods rely on these attributes in selectinload.
        assert hasattr(LessonGroup, "lesson")
        assert hasattr(LessonGroup, "group")
        assert hasattr(Lesson, "lesson_groups")
        assert hasattr(Group, "lesson_groups")
