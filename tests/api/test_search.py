"""API tests for search endpoints."""

import datetime
import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel

from ruz_server.api import search
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
    app.dependency_overrides[search.get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as test_client:
        test_client.engine = engine
        yield test_client
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


def _seed_search_data(engine):
    with Session(engine) as session:
        session.add(
            Group(
                id=7001, guid=uuid.uuid4(), name="IU8-7001", faculty_name="Informatics"
            )
        )
        session.add(
            Group(
                id=7002, guid=uuid.uuid4(), name="IU8-7002", faculty_name="Informatics"
            )
        )

        session.add(
            Lecturer(
                id=9001,
                guid=uuid.uuid4(),
                full_name="Lecturer One",
                short_name="L. One",
                rank="Professor",
            )
        )
        session.add(
            Lecturer(
                id=9002,
                guid=uuid.uuid4(),
                full_name="Lecturer Two",
                short_name="L. Two",
                rank="Associate Professor",
            )
        )
        session.add(KindOfWork(id=8001, type_of_work="Лекция", complexity=2))
        session.add(
            Discipline(id=7101, name="Algebra", examtype="Неизв.", has_labs=False)
        )
        session.add(
            Discipline(id=7102, name="Physics", examtype="Неизв.", has_labs=False)
        )
        session.add(
            Auditorium(id=6001, guid=uuid.uuid4(), name="A-101", building="Main")
        )

        lessons = [
            Lesson(
                id=1101,
                kind_of_work_id=8001,
                discipline_id=7101,
                auditorium_id=6001,
                lecturer_id=9001,
                date=datetime.date(2025, 1, 13),
                begin_lesson=datetime.time(9, 0),
                end_lesson=datetime.time(10, 30),
                sub_group=1,
            ),
            Lesson(
                id=1102,
                kind_of_work_id=8001,
                discipline_id=7102,
                auditorium_id=6001,
                lecturer_id=9001,
                date=datetime.date(2025, 1, 15),
                begin_lesson=datetime.time(11, 0),
                end_lesson=datetime.time(12, 30),
                sub_group=2,
            ),
            Lesson(
                id=1103,
                kind_of_work_id=8001,
                discipline_id=7101,
                auditorium_id=6001,
                lecturer_id=9002,
                date=datetime.date(2025, 1, 13),
                begin_lesson=datetime.time(13, 0),
                end_lesson=datetime.time(14, 30),
                sub_group=1,
            ),
            Lesson(
                id=1104,
                kind_of_work_id=8001,
                discipline_id=7101,
                auditorium_id=6001,
                lecturer_id=9001,
                date=datetime.date(2025, 1, 20),
                begin_lesson=datetime.time(9, 0),
                end_lesson=datetime.time(10, 30),
                sub_group=1,
            ),
        ]
        session.add_all(lessons)
        session.add_all(
            [
                LessonGroup(lesson_id=1101, group_id=7001),
                LessonGroup(lesson_id=1102, group_id=7002),
                LessonGroup(lesson_id=1103, group_id=7001),
                LessonGroup(lesson_id=1104, group_id=7001),
            ]
        )
        session.commit()


@pytest.mark.api
class TestSearchAPI:
    @pytest.mark.asyncio
    async def test_lecturer_day(self, client):
        _seed_search_data(client.engine)
        response = await client.get(
            "/api/search/lecturer/day",
            params={"lecturer_id": 9001, "date": "2025-01-13"},
        )
        assert response.status_code == 200
        assert [row["lesson_id"] for row in response.json()] == [1101]

    @pytest.mark.asyncio
    async def test_lecturer_week(self, client):
        _seed_search_data(client.engine)
        response = await client.get(
            "/api/search/lecturer/week",
            params={"lecturer_id": 9001, "date": "2025-01-14"},
        )
        assert response.status_code == 200
        data = response.json()
        lesson_ids = [row["lesson_id"] for row in data]
        assert lesson_ids == [1101, 1102]
        assert 1101 in lesson_ids and 1102 in lesson_ids
        assert 1104 not in lesson_ids
        expected_keys = {
            "lesson_id",
            "date",
            "begin_lesson",
            "end_lesson",
            "sub_group",
            "discipline_name",
            "kind_of_work",
            "lecturer_short_name",
            "lecturer_id",
            "discipline_id",
            "auditorium_name",
            "building",
            "group_id",
        }
        assert set(data[0].keys()) == expected_keys

    @pytest.mark.asyncio
    async def test_discipline_day(self, client):
        _seed_search_data(client.engine)
        response = await client.get(
            "/api/search/discipline/day",
            params={"discipline_id": 7101, "date": "2025-01-13"},
        )
        assert response.status_code == 200
        assert [row["lesson_id"] for row in response.json()] == [1101, 1103]

    @pytest.mark.asyncio
    async def test_discipline_week(self, client):
        _seed_search_data(client.engine)
        response = await client.get(
            "/api/search/discipline/week",
            params={"discipline_id": 7101, "date": "2025-01-14"},
        )
        assert response.status_code == 200
        lesson_ids = [row["lesson_id"] for row in response.json()]
        assert 1101 in lesson_ids and 1103 in lesson_ids
        assert 1104 not in lesson_ids

    @pytest.mark.asyncio
    async def test_filter_by_group_id(self, client):
        _seed_search_data(client.engine)
        response = await client.get(
            "/api/search/lecturer/week",
            params={"lecturer_id": 9001, "date": "2025-01-14", "group_id": 7001},
        )
        assert response.status_code == 200
        assert [row["lesson_id"] for row in response.json()] == [1101]

    @pytest.mark.asyncio
    async def test_filter_by_sub_group(self, client):
        _seed_search_data(client.engine)
        response = await client.get(
            "/api/search/lecturer/week",
            params={"lecturer_id": 9001, "date": "2025-01-14", "sub_group": 2},
        )
        assert response.status_code == 200
        assert [row["lesson_id"] for row in response.json()] == [1102]

    @pytest.mark.asyncio
    async def test_filter_by_group_and_sub_group(self, client):
        _seed_search_data(client.engine)
        response = await client.get(
            "/api/search/lecturer/week",
            params={
                "lecturer_id": 9001,
                "date": "2025-01-14",
                "group_id": 7002,
                "sub_group": 2,
            },
        )
        assert response.status_code == 200
        assert [row["lesson_id"] for row in response.json()] == [1102]

    @pytest.mark.asyncio
    async def test_empty_result(self, client):
        _seed_search_data(client.engine)
        response = await client.get(
            "/api/search/lecturer/day",
            params={"lecturer_id": 9999, "date": "2025-01-13"},
        )
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_invalid_date_returns_422(self, client):
        response = await client.get(
            "/api/search/lecturer/day",
            params={"lecturer_id": 9001, "date": "2025-13-99"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_search_week_boundary_excludes_next_week(self, client):
        _seed_search_data(client.engine)
        response = await client.get(
            "/api/search/discipline/week",
            params={"discipline_id": 7101, "date": "2025-01-19"},
        )
        assert response.status_code == 200
        lesson_ids = [row["lesson_id"] for row in response.json()]
        assert 1104 not in lesson_ids
