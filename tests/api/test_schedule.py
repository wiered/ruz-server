"""API tests for user schedule endpoints."""

import datetime
import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session

from ruz_server.api import schedule
from ruz_server.api.app import app
from ruz_server.api.security import require_api_key
from ruz_server.models.models import (
    Auditorium,
    Discipline,
    Group,
    KindOfWork,
    Lecturer,
    Lesson,
    LessonGroup,
    User,
)


@pytest_asyncio.fixture
async def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def override_get_db():
        session = Session(engine)
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[require_api_key] = lambda: None
    app.dependency_overrides[schedule.get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        test_client.engine = engine
        yield test_client
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


def _seed_user_and_lessons(engine, *, user_group_oid: int = 7001, user_subgroup: int = 1):
    with Session(engine) as session:
        group = Group(
            id=user_group_oid,
            guid=uuid.uuid4(),
            name=f"IU8-{user_group_oid}",
            faculty_name="Informatics",
        )
        session.add(group)

        user = User(
            id=123456,
            username="schedule_user",
            group_oid=user_group_oid,
            subgroup=user_subgroup,
        )
        session.add(user)

        lecturer = Lecturer(
            id=9001,
            guid=uuid.uuid4(),
            full_name="Test Lecturer",
            short_name="T. Lecturer",
            rank="Professor",
        )
        kind = KindOfWork(id=8001, type_of_work="Лекция", complexity=2)
        discipline = Discipline(id=7001, name="Math", examtype="Неизв.", has_labs=False)
        auditorium = Auditorium(id=6001, guid=uuid.uuid4(), name="A-101", building="Main")
        session.add(lecturer)
        session.add(kind)
        session.add(discipline)
        session.add(auditorium)

        lessons = [
            Lesson(
                id=1001,
                kind_of_work_id=8001,
                discipline_id=7001,
                auditorium_id=6001,
                lecturer_id=9001,
                date=datetime.date(2025, 1, 13),
                begin_lesson=datetime.time(8, 0),
                end_lesson=datetime.time(9, 30),
                sub_group=0,
            ),
            Lesson(
                id=1002,
                kind_of_work_id=8001,
                discipline_id=7001,
                auditorium_id=6001,
                lecturer_id=9001,
                date=datetime.date(2025, 1, 13),
                begin_lesson=datetime.time(10, 0),
                end_lesson=datetime.time(11, 30),
                sub_group=1,
            ),
            Lesson(
                id=1003,
                kind_of_work_id=8001,
                discipline_id=7001,
                auditorium_id=6001,
                lecturer_id=9001,
                date=datetime.date(2025, 1, 13),
                begin_lesson=datetime.time(12, 0),
                end_lesson=datetime.time(13, 30),
                sub_group=2,
            ),
            Lesson(
                id=1004,
                kind_of_work_id=8001,
                discipline_id=7001,
                auditorium_id=6001,
                lecturer_id=9001,
                date=datetime.date(2025, 1, 15),
                begin_lesson=datetime.time(9, 0),
                end_lesson=datetime.time(10, 30),
                sub_group=1,
            ),
            Lesson(
                id=1005,
                kind_of_work_id=8001,
                discipline_id=7001,
                auditorium_id=6001,
                lecturer_id=9001,
                date=datetime.date(2025, 1, 21),
                begin_lesson=datetime.time(9, 0),
                end_lesson=datetime.time(10, 30),
                sub_group=1,
            ),
        ]
        session.add_all(lessons)
        session.add_all(
            [LessonGroup(lesson_id=lesson.id, group_id=user_group_oid) for lesson in lessons]
        )
        session.commit()


@pytest.mark.api
class TestScheduleAPI:
    @pytest.mark.asyncio
    async def test_day_returns_only_date_and_sorted(self, client):
        _seed_user_and_lessons(client.engine)
        response = await client.get("/api/schedule/user/123456/day", params={"date": "2025-01-13"})
        assert response.status_code == 200
        data = response.json()
        assert [row["lesson_id"] for row in data] == [1001, 1002]
        assert all(row["date"] == "2025-01-13" for row in data)

    @pytest.mark.asyncio
    async def test_week_returns_lessons_in_week_range(self, client):
        _seed_user_and_lessons(client.engine)
        response = await client.get("/api/schedule/user/123456/week", params={"date": "2025-01-14"})
        assert response.status_code == 200
        data = response.json()
        lesson_ids = [row["lesson_id"] for row in data]
        assert 1004 in lesson_ids
        assert 1005 not in lesson_ids

    @pytest.mark.asyncio
    async def test_subgroup_policy_includes_common_and_user_only(self, client):
        _seed_user_and_lessons(client.engine, user_subgroup=1)
        response = await client.get("/api/schedule/user/123456/day", params={"date": "2025-01-13"})
        assert response.status_code == 200
        lesson_ids = [row["lesson_id"] for row in response.json()]
        assert set(lesson_ids) == {1001, 1002}

    @pytest.mark.asyncio
    async def test_user_without_group_returns_400(self, client):
        with Session(client.engine) as session:
            session.add(User(id=200001, username="no_group_user", group_oid=None, subgroup=1))
            session.commit()
        response = await client.get("/api/schedule/user/200001/day", params={"date": "2025-01-13"})
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_user_not_found_returns_404(self, client):
        response = await client.get("/api/schedule/user/999999/day", params={"date": "2025-01-13"})
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_empty_result_returns_empty_list(self, client):
        _seed_user_and_lessons(client.engine)
        response = await client.get("/api/schedule/user/123456/day", params={"date": "2025-02-01"})
        assert response.status_code == 200
        assert response.json() == []
