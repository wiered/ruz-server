"""API tests for auditorium endpoints."""

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
from api import auditorium
from api.security import require_api_key


@pytest_asyncio.fixture
async def client():
    """Create TestClient with DB and auth overrides."""
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
    app.dependency_overrides[auditorium.get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.mark.api
class TestAuditoriumAPI:
    @pytest.mark.asyncio
    async def test_create_auditorium(self, client):
        payload = {
            "id": 1001,
            "guid": str(uuid.uuid4()),
            "name": "A-101",
            "building": "Main Building",
        }

        response = await client.post("/api/auditorium/", json=payload)

        assert response.status_code == 201
        body = response.json()
        assert body["id"] == payload["id"]
        assert body["name"] == payload["name"]
        assert body["building"] == payload["building"]

    @pytest.mark.asyncio
    async def test_list_auditoriums(self, client):
        await client.post("/api/auditorium/", json={
            "id": 1002,
            "guid": str(uuid.uuid4()),
            "name": "B-201",
            "building": "Second Building",
        })

        response = await client.get("/api/auditorium/")

        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) >= 1

    @pytest.mark.asyncio
    async def test_get_auditorium_by_id(self, client):
        payload = {
            "id": 1003,
            "guid": str(uuid.uuid4()),
            "name": "C-301",
            "building": "Third Building",
        }
        await client.post("/api/auditorium/", json=payload)

        response = await client.get("/api/auditorium/1003")

        assert response.status_code == 200
        assert response.json()["id"] == 1003

    @pytest.mark.asyncio
    async def test_get_auditorium_by_guid(self, client):
        auditorium_guid = str(uuid.uuid4())
        payload = {
            "id": 1004,
            "guid": auditorium_guid,
            "name": "D-401",
            "building": "Fourth Building",
        }
        await client.post("/api/auditorium/", json=payload)

        response = await client.get(f"/api/auditorium/guid/{auditorium_guid}")

        assert response.status_code == 200
        assert response.json()["guid"] == auditorium_guid

    @pytest.mark.asyncio
    async def test_update_auditorium(self, client):
        payload = {
            "id": 1005,
            "guid": str(uuid.uuid4()),
            "name": "E-501",
            "building": "Old Building",
        }
        await client.post("/api/auditorium/", json=payload)

        response = await client.put("/api/auditorium/1005", json={"name": "E-502", "building": "New Building"})

        assert response.status_code == 200
        assert response.json() is True

        get_response = await client.get("/api/auditorium/1005")
        assert get_response.json()["name"] == "E-502"
        assert get_response.json()["building"] == "New Building"

    @pytest.mark.asyncio
    async def test_delete_auditorium(self, client):
        payload = {
            "id": 1006,
            "guid": str(uuid.uuid4()),
            "name": "F-601",
            "building": "Delete Building",
        }
        await client.post("/api/auditorium/", json=payload)

        response = await client.delete("/api/auditorium/1006")

        assert response.status_code == 200
        assert response.json() is True

        get_response = await client.get("/api/auditorium/1006")
        assert get_response.status_code == 404
