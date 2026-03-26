"""API tests for discipline endpoints."""

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
from api import discipline
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
    app.dependency_overrides[discipline.get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.mark.api
class TestDisciplineAPI:
    @pytest.mark.asyncio
    async def test_create_discipline(self, client):
        payload = {
            "id": 2001,
            "name": "Linear Algebra",
            "examtype": "exam",
            "has_labs": True,
        }

        response = await client.post("/api/discipline/", json=payload)

        assert response.status_code == 201
        body = response.json()
        assert body["id"] == payload["id"]
        assert body["name"] == payload["name"]
        assert body["examtype"] == payload["examtype"]
        assert body["has_labs"] is True

    @pytest.mark.asyncio
    async def test_list_disciplines(self, client):
        await client.post("/api/discipline/", json={
            "id": 2002,
            "name": "Physics",
            "examtype": "credit",
            "has_labs": False,
        })

        response = await client.get("/api/discipline/")

        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) >= 1

    @pytest.mark.asyncio
    async def test_get_discipline_by_id(self, client):
        payload = {
            "id": 2003,
            "name": "Programming",
            "examtype": "exam",
            "has_labs": True,
        }
        await client.post("/api/discipline/", json=payload)

        response = await client.get("/api/discipline/2003")

        assert response.status_code == 200
        assert response.json()["id"] == 2003

    @pytest.mark.asyncio
    async def test_update_discipline(self, client):
        payload = {
            "id": 2004,
            "name": "History",
            "examtype": "credit",
            "has_labs": False,
        }
        await client.post("/api/discipline/", json=payload)

        response = await client.put("/api/discipline/2004", json={
            "name": "World History",
            "examtype": "exam",
            "has_labs": True,
        })

        assert response.status_code == 200
        assert response.json() is True

        get_response = await client.get("/api/discipline/2004")
        body = get_response.json()
        assert body["name"] == "World History"
        assert body["examtype"] == "exam"
        assert body["has_labs"] is True

    @pytest.mark.asyncio
    async def test_delete_discipline(self, client):
        payload = {
            "id": 2005,
            "name": "Chemistry",
            "examtype": "exam",
            "has_labs": True,
        }
        await client.post("/api/discipline/", json=payload)

        response = await client.delete("/api/discipline/2005")

        assert response.status_code == 200
        assert response.json() is True

        get_response = await client.get("/api/discipline/2005")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_discipline_duplicate_returns_409(self, client):
        payload = {
            "id": 2010,
            "name": "Duplicate",
            "examtype": "exam",
            "has_labs": True,
        }
        await client.post("/api/discipline/", json=payload)
        response = await client.post("/api/discipline/", json=payload)
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_get_discipline_not_found_returns_404(self, client):
        response = await client.get("/api/discipline/999999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_discipline_not_found_returns_404(self, client):
        response = await client.put("/api/discipline/999999", json={"name": "X"})
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_discipline_not_found_returns_404(self, client):
        response = await client.delete("/api/discipline/999999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_discipline_invalid_payload_returns_422(self, client):
        response = await client.post("/api/discipline/", json={"id": 1})
        assert response.status_code == 422
