"""API tests for core app endpoints."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient



from ruz_server.api.app import app
from ruz_server.api.security import require_api_key


@pytest_asyncio.fixture
async def client():
    """Create TestClient with API key dependency override."""
    app.dependency_overrides[require_api_key] = lambda: None
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def client_no_auth():
    """Create client without API key override."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client


@pytest.mark.api
class TestAppAPI:
    @pytest.mark.asyncio
    async def test_root(self, client):
        response = await client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello World"}

    @pytest.mark.asyncio
    async def test_public(self, client):
        response = await client.get("/public")
        assert response.status_code == 200
        assert response.json() == {"message": "public ok"}

    @pytest.mark.asyncio
    async def test_protected(self, client):
        response = await client.get("/protected")
        assert response.status_code == 200
        assert response.json() == {"message": "protected ok"}

    @pytest.mark.asyncio
    async def test_healthz(self, client):
        response = await client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    @pytest.mark.asyncio
    async def test_api_route_requires_api_key(self, client_no_auth):
        response = await client_no_auth.get("/api/group/")
        assert response.status_code == 401
