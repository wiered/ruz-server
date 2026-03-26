"""API tests for lecturers endpoints."""

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
from api import lecturers
from api.security import require_api_key


@pytest_asyncio.fixture
async def client():
    """Create HTTP client with isolated test DB."""
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
    app.dependency_overrides[lecturers.get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.mark.api
class TestLecturersAPI:
    @pytest.mark.asyncio
    async def test_create_lecturer(self, client):
        payload = {
            "id": 5001,
            "guid": str(uuid.uuid4()),
            "full_name": "John Smith",
            "short_name": "J. Smith",
            "rank": "Professor",
        }
        response = await client.post("/api/lecturer/", json=payload)
        assert response.status_code == 201
        body = response.json()
        assert body["id"] == payload["id"]
        assert body["full_name"] == payload["full_name"]

    @pytest.mark.asyncio
    async def test_list_lecturers(self, client):
        await client.post("/api/lecturer/", json={
            "id": 5002,
            "guid": str(uuid.uuid4()),
            "full_name": "Jane Doe",
            "short_name": "J. Doe",
            "rank": "Docent",
        })
        response = await client.get("/api/lecturer/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) >= 1

    @pytest.mark.asyncio
    async def test_get_lecturer_by_id(self, client):
        payload = {
            "id": 5003,
            "guid": str(uuid.uuid4()),
            "full_name": "Alan Turing",
            "short_name": "A. Turing",
            "rank": "Professor",
        }
        await client.post("/api/lecturer/", json=payload)
        response = await client.get("/api/lecturer/5003")
        assert response.status_code == 200
        assert response.json()["id"] == 5003

    @pytest.mark.asyncio
    async def test_get_lecturer_by_guid(self, client):
        lecturer_guid = str(uuid.uuid4())
        payload = {
            "id": 5004,
            "guid": lecturer_guid,
            "full_name": "Ada Lovelace",
            "short_name": "A. Lovelace",
            "rank": "Senior Lecturer",
        }
        await client.post("/api/lecturer/", json=payload)
        response = await client.get(f"/api/lecturer/guid/{lecturer_guid}")
        assert response.status_code == 200
        assert response.json()["guid"] == lecturer_guid

    @pytest.mark.asyncio
    async def test_update_lecturer(self, client):
        payload = {
            "id": 5005,
            "guid": str(uuid.uuid4()),
            "full_name": "Old Name",
            "short_name": "O. Name",
            "rank": "Assistant",
        }
        await client.post("/api/lecturer/", json=payload)
        response = await client.put("/api/lecturer/5005", json={
            "full_name": "New Name",
            "short_name": "N. Name",
            "rank": "Professor",
        })
        assert response.status_code == 200
        assert response.json() is True
        get_response = await client.get("/api/lecturer/5005")
        body = get_response.json()
        assert body["full_name"] == "New Name"
        assert body["rank"] == "Professor"

    @pytest.mark.asyncio
    async def test_delete_lecturer(self, client):
        payload = {
            "id": 5006,
            "guid": str(uuid.uuid4()),
            "full_name": "Delete Me",
            "short_name": "D. Me",
            "rank": "Assistant",
        }
        await client.post("/api/lecturer/", json=payload)
        response = await client.delete("/api/lecturer/5006")
        assert response.status_code == 200
        assert response.json() is True
        get_response = await client.get("/api/lecturer/5006")
        assert get_response.status_code == 404
