"""API tests for lesson endpoints."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, select

from ruz_server.api import lesson
from ruz_server.api.app import app
from ruz_server.api.security import require_api_key
from ruz_server.models.models import (
    Auditorium,
    Discipline,
    KindOfWork,
    Lecturer,
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
    app.dependency_overrides[lesson.get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as test_client:
        test_client.engine = engine
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
    async def test_create_lesson_autocreates_related_entities(self, client):
        await client.post("/api/lesson/", json=lesson_payload(10011))

        with Session(client.engine) as session:
            assert (
                session.exec(select(Lecturer).where(Lecturer.id == 9001)).first()
                is not None
            )
            assert (
                session.exec(select(KindOfWork).where(KindOfWork.id == 8001)).first()
                is not None
            )
            assert (
                session.exec(select(Discipline).where(Discipline.id == 7001)).first()
                is not None
            )
            assert (
                session.exec(select(Auditorium).where(Auditorium.id == 6001)).first()
                is not None
            )

    @pytest.mark.asyncio
    async def test_create_lesson_sets_has_labs_for_lab(self, client):
        payload = lesson_payload(10012)
        payload["type_of_work"] = "Лабораторная работа"

        response = await client.post("/api/lesson/", json=payload)
        assert response.status_code == 201

        with Session(client.engine) as session:
            discipline = session.exec(
                select(Discipline).where(Discipline.id == 7001)
            ).first()
            assert discipline is not None
            assert discipline.has_labs is True

    @pytest.mark.asyncio
    async def test_create_lesson_sets_examtype_from_unknown(self, client):
        payload = lesson_payload(10013)
        payload["type_of_work"] = "Зачёт"

        response = await client.post("/api/lesson/", json=payload)
        assert response.status_code == 201

        with Session(client.engine) as session:
            discipline = session.exec(
                select(Discipline).where(Discipline.id == 7001)
            ).first()
            assert discipline is not None
            assert discipline.examtype == "Зачёт"

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
        before_update = (await client.get(f"/api/lesson/{lesson_id}")).json()[
            "updated_at"
        ]

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
        assert body["updated_at"] != before_update

    @pytest.mark.asyncio
    async def test_partial_update_keeps_other_fields(self, client):
        await client.post("/api/lesson/", json=lesson_payload(10014))
        lesson_id = (await client.get("/api/lesson/")).json()[0]["id"]
        before = (await client.get(f"/api/lesson/{lesson_id}")).json()

        response = await client.put(f"/api/lesson/{lesson_id}", json={"sub_group": 9})
        assert response.status_code == 200
        after = response.json()

        assert after["sub_group"] == 9
        assert after["discipline_id"] == before["discipline_id"]
        assert after["lecturer_id"] == before["lecturer_id"]
        assert after["kind_of_work_id"] == before["kind_of_work_id"]
        assert after["updated_at"] != before["updated_at"]

    @pytest.mark.asyncio
    async def test_delete_lesson(self, client):
        await client.post("/api/lesson/", json=lesson_payload(10005))
        lesson_id = (await client.get("/api/lesson/")).json()[0]["id"]

        response = await client.delete(f"/api/lesson/{lesson_id}")
        assert response.status_code == 200
        assert response.json() is True

        get_response = await client.get(f"/api/lesson/{lesson_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_lesson_not_found_returns_404(self, client):
        response = await client.get("/api/lesson/999999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_lesson_not_found_returns_404(self, client):
        response = await client.put("/api/lesson/999999", json={"sub_group": 2})
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_lesson_not_found_returns_404(self, client):
        response = await client.delete("/api/lesson/999999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_lesson_invalid_payload_returns_422(self, client):
        response = await client.post("/api/lesson/", json={"id": 1})
        assert response.status_code == 422
