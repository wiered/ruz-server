"""API tests for kind_of_work endpoints."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel

from ruz_server.api import kind_of_work
from ruz_server.api.app import app
from ruz_server.api.security import require_api_key


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
    app.dependency_overrides[kind_of_work.get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.mark.api
class TestKindOfWorkAPI:
    @pytest.mark.asyncio
    async def test_create_kind_of_work(self, client):
        payload = {"id": 4001, "type_of_work": "Lecture", "complexity": 3}
        response = await client.post("/api/kind_of_work/", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["id"] == payload["id"]
        assert body["type_of_work"] == payload["type_of_work"]

    @pytest.mark.asyncio
    async def test_list_kind_of_work(self, client):
        await client.post(
            "/api/kind_of_work/",
            json={"id": 4002, "type_of_work": "Seminar", "complexity": 2},
        )
        response = await client.get("/api/kind_of_work/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) >= 1

    @pytest.mark.asyncio
    async def test_get_kind_of_work_by_id(self, client):
        await client.post(
            "/api/kind_of_work/",
            json={"id": 4003, "type_of_work": "Lab", "complexity": 5},
        )
        response = await client.get("/api/kind_of_work/4003")
        assert response.status_code == 200
        assert response.json()["id"] == 4003

    @pytest.mark.asyncio
    async def test_update_kind_of_work(self, client):
        await client.post(
            "/api/kind_of_work/",
            json={"id": 4004, "type_of_work": "Practice", "complexity": 1},
        )
        response = await client.put(
            "/api/kind_of_work/4004", json={"type_of_work": "Workshop", "complexity": 4}
        )
        assert response.status_code == 200
        assert response.json() is True
        get_response = await client.get("/api/kind_of_work/4004")
        body = get_response.json()
        assert body["type_of_work"] == "Workshop"
        assert body["complexity"] == 4

    @pytest.mark.asyncio
    async def test_delete_kind_of_work(self, client):
        await client.post(
            "/api/kind_of_work/",
            json={"id": 4005, "type_of_work": "Colloquium", "complexity": 2},
        )
        response = await client.delete("/api/kind_of_work/4005")
        assert response.status_code == 200
        assert response.json() is True
        get_response = await client.get("/api/kind_of_work/4005")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_kind_of_work_duplicate_returns_409(self, client):
        payload = {"id": 4010, "type_of_work": "Duplicate", "complexity": 1}
        await client.post("/api/kind_of_work/", json=payload)
        response = await client.post("/api/kind_of_work/", json=payload)
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_get_kind_of_work_not_found_returns_404(self, client):
        response = await client.get("/api/kind_of_work/999999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_kind_of_work_not_found_returns_404(self, client):
        response = await client.put(
            "/api/kind_of_work/999999", json={"type_of_work": "X"}
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_kind_of_work_not_found_returns_404(self, client):
        response = await client.delete("/api/kind_of_work/999999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_kind_of_work_invalid_payload_returns_422(self, client):
        response = await client.post("/api/kind_of_work/", json={"id": 1})
        assert response.status_code == 422
