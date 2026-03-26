"""API tests for groups endpoints."""

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
from api import groups
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
    app.dependency_overrides[groups.get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.mark.api
class TestGroupsAPI:
    @pytest.mark.asyncio
    async def test_create_group(self, client):
        payload = {
            "id": 3001,
            "guid": str(uuid.uuid4()),
            "name": "IU8-11",
            "faculty_name": "Informatics",
        }
        response = await client.post("/api/group/", json=payload)
        assert response.status_code == 201
        body = response.json()
        assert body["id"] == payload["id"]
        assert body["name"] == payload["name"]

    @pytest.mark.asyncio
    async def test_list_groups(self, client):
        await client.post("/api/group/", json={
            "id": 3002,
            "guid": str(uuid.uuid4()),
            "name": "IU8-12",
            "faculty_name": "Informatics",
        })
        response = await client.get("/api/group/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) >= 1

    @pytest.mark.asyncio
    async def test_get_group_by_id(self, client):
        payload = {
            "id": 3003,
            "guid": str(uuid.uuid4()),
            "name": "IU8-13",
            "faculty_name": "Informatics",
        }
        await client.post("/api/group/", json=payload)
        response = await client.get("/api/group/3003")
        assert response.status_code == 200
        assert response.json()["id"] == 3003

    @pytest.mark.asyncio
    async def test_get_group_by_guid(self, client):
        group_guid = str(uuid.uuid4())
        payload = {
            "id": 3004,
            "guid": group_guid,
            "name": "IU8-14",
            "faculty_name": "Informatics",
        }
        await client.post("/api/group/", json=payload)
        response = await client.get(f"/api/group/guid/{group_guid}")
        assert response.status_code == 200
        assert response.json()["guid"] == group_guid

    @pytest.mark.asyncio
    async def test_update_group(self, client):
        payload = {
            "id": 3005,
            "guid": str(uuid.uuid4()),
            "name": "IU8-15",
            "faculty_name": "Old Faculty",
        }
        await client.post("/api/group/", json=payload)
        response = await client.put("/api/group/3005", json={
            "name": "IU8-15-Updated",
            "faculty_name": "New Faculty",
        })
        assert response.status_code == 200
        assert response.json() is True
        get_response = await client.get("/api/group/3005")
        assert get_response.json()["name"] == "IU8-15-Updated"
        assert get_response.json()["faculty_name"] == "New Faculty"

    @pytest.mark.asyncio
    async def test_delete_group(self, client):
        payload = {
            "id": 3006,
            "guid": str(uuid.uuid4()),
            "name": "IU8-16",
            "faculty_name": "Faculty",
        }
        await client.post("/api/group/", json=payload)
        response = await client.delete("/api/group/3006")
        assert response.status_code == 200
        assert response.json() is True
        get_response = await client.get("/api/group/3006")
        assert get_response.status_code == 404
