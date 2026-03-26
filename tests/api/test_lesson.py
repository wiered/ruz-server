"""API tests for lesson endpoints."""

import datetime
import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from api.app import app
from api import lesson
from api.security import require_api_key
from models.models import Lecturer, KindOfWork, Discipline, Auditorium, Group


@pytest_asyncio.fixture
async def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    # Seed required related entities so create_lesson doesn't hit broken helper path.
    seed_session = Session(engine)
    try:
        seed_session.add(
            Lecturer(
                id=9001,
                guid=uuid.uuid4(),
                full_name="Seed Lecturer",
                short_name="S. Lecturer",
                rank="Professor",
            )
        )
        seed_session.add(
            KindOfWork(
                id=8001,
                type_of_work="Лекция",
                complexity=3,
            )
        )
        seed_session.add(
            Discipline(
                id=7001,
                name="Seed Discipline",
                examtype="Неизв.",
                has_labs=False,
            )
        )
        seed_session.add(
            Auditorium(
                id=6001,
                guid=uuid.uuid4(),
                name="A-101",
                building="Main",
            )
        )
        seed_session.add(
            Group(
                id=5001,
                guid=uuid.uuid4(),
                name="IU8-5001",
                faculty_name="Informatics",
            )
        )
        seed_session.commit()
    finally:
        seed_session.close()

    def override_get_db():
        session = Session(engine)
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[require_api_key] = lambda: None
    app.dependency_overrides[lesson.get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


def lesson_payload(lesson_id: int) -> dict:
    return {
        "id": lesson_id,
        "lecturer_id": 9001,
        "lecturer_guid": str(uuid.uuid4()),
        "lecturer_full_name": "Test Lecturer",
        "lecturer_short_name": "T. Lecturer",
        "lecturer_rank": "Professor",
        "kind_of_work_id": 8001,
        "type_of_work": "Лекция",
        "complexity": 3,
        "discipline_id": 7001,
        "discipline_name": "Math",
        "auditorium_id": 6001,
        "auditorium_guid": str(uuid.uuid4()),
        "auditorium_name": "A-101",
        "auditorium_building": "Main",
        "date": "2025-01-10",
        "begin_lesson": "09:00:00",
        "end_lesson": "10:30:00",
        "group_id": 5001,
        "sub_group": 1,
    }


@pytest.mark.api
class TestLessonAPI:
    @pytest.mark.asyncio
    async def test_create_lesson(self, client):
        response = await client.post("/api/lesson/", json=lesson_payload(10001))
        assert response.status_code == 201
        body = response.json()
        assert body["discipline_id"] == 7001
        assert body["auditorium_id"] == 6001
        assert body["lecturer_id"] == 9001

    @pytest.mark.asyncio
    async def test_list_lessons(self, client):
        await client.post("/api/lesson/", json=lesson_payload(10002))
        response = await client.get("/api/lesson/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_get_lesson_by_id(self, client):
        await client.post("/api/lesson/", json=lesson_payload(10003))
        list_response = await client.get("/api/lesson/")
        lesson_id = list_response.json()[0]["id"]

        response = await client.get(f"/api/lesson/{lesson_id}")
        assert response.status_code == 200
        assert response.json()["id"] == lesson_id

    @pytest.mark.asyncio
    async def test_update_lesson(self, client):
        await client.post("/api/lesson/", json=lesson_payload(10004))
        lesson_id = (await client.get("/api/lesson/")).json()[0]["id"]

        response = await client.put(
            f"/api/lesson/{lesson_id}",
            json={
                "sub_group": 2,
                "date": "2025-01-11",
                "begin_lesson": "11:00:00",
                "end_lesson": "12:30:00",
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["id"] == lesson_id
        assert body["sub_group"] == 2

    @pytest.mark.asyncio
    async def test_delete_lesson(self, client):
        await client.post("/api/lesson/", json=lesson_payload(10005))
        lesson_id = (await client.get("/api/lesson/")).json()[0]["id"]

        response = await client.delete(f"/api/lesson/{lesson_id}")
        assert response.status_code == 200
        assert response.json() is True

        get_response = await client.get(f"/api/lesson/{lesson_id}")
        assert get_response.status_code == 404
