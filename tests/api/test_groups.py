"""API tests for groups endpoints."""

import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session


from ruz_server.api.app import app
from ruz_server.api import groups
from ruz_server.api.security import require_api_key
from ruz_server.ruz_api.api import RuzAPI


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
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as test_client:
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
        await client.post(
            "/api/group/",
            json={
                "id": 3002,
                "guid": str(uuid.uuid4()),
                "name": "IU8-12",
                "faculty_name": "Informatics",
            },
        )
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
        response = await client.put(
            "/api/group/3005",
            json={
                "name": "IU8-15-Updated",
                "faculty_name": "New Faculty",
            },
        )
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

    @pytest.mark.asyncio
    async def test_create_group_duplicate_id_returns_409(self, client):
        payload = {
            "id": 3010,
            "guid": str(uuid.uuid4()),
            "name": "IU8-DUP-1",
            "faculty_name": "Informatics",
        }
        await client.post("/api/group/", json=payload)
        response = await client.post("/api/group/", json=payload)
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_create_group_duplicate_name_returns_409(self, client):
        payload1 = {
            "id": 3011,
            "guid": str(uuid.uuid4()),
            "name": "IU8-DUP-2",
            "faculty_name": "Informatics",
        }
        payload2 = {
            "id": 3012,
            "guid": str(uuid.uuid4()),
            "name": "IU8-DUP-2",
            "faculty_name": "Informatics",
        }
        await client.post("/api/group/", json=payload1)
        response = await client.post("/api/group/", json=payload2)
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_get_group_not_found_returns_404(self, client):
        response = await client.get("/api/group/999999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_group_not_found_returns_404(self, client):
        response = await client.put(
            "/api/group/999999", json={"name": "X", "faculty_name": "Y"}
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_group_not_found_returns_404(self, client):
        response = await client.delete("/api/group/999999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_group_invalid_payload_returns_422(self, client):
        response = await client.post("/api/group/", json={"id": 1})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_search_groups_ruz_only(self, client, monkeypatch):
        gid_a = uuid.UUID("c72c7026-7e2d-4a76-af57-f1247a6d2e25")
        gid_b = uuid.UUID("f07651c5-4709-4190-b82a-269c7078e6b7")

        async def fake_get_group(self, group_name: str):
            assert group_name == "ИС22"
            return [
                {
                    "type": "group",
                    "id": "841",
                    "label": "ИС221",
                    "description": "4",
                    "guid": str(gid_a),
                },
                {
                    "type": "group",
                    "id": "839",
                    "label": "БИС221",
                    "description": "4",
                    "guid": str(gid_b),
                },
            ]

        monkeypatch.setattr(RuzAPI, "getGroup", fake_get_group)

        response = await client.get("/api/group/search", params={"q": "ИС22"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0] == {
            "oid": 841,
            "name": "ИС221",
            "guid": str(gid_a),
            "faculty_name": None,
        }
        assert data[1] == {
            "oid": 839,
            "name": "БИС221",
            "guid": str(gid_b),
            "faculty_name": None,
        }

    @pytest.mark.asyncio
    async def test_search_groups_db_then_ruz_skips_duplicate_oid(
        self, client, monkeypatch
    ):
        gid_a = uuid.UUID("c72c7026-7e2d-4a76-af57-f1247a6d2e25")
        gid_b = uuid.UUID("f07651c5-4709-4190-b82a-269c7078e6b7")

        await client.post(
            "/api/group/",
            json={
                "id": 841,
                "guid": str(gid_a),
                "name": "ИС221",
                "faculty_name": "Факультет 4",
            },
        )

        async def fake_get_group(self, group_name: str):
            assert group_name == "ИС221"
            return [
                {
                    "type": "group",
                    "id": "841",
                    "label": "ИС221",
                    "description": "4",
                    "guid": str(gid_a),
                },
                {
                    "type": "group",
                    "id": "839",
                    "label": "БИС221",
                    "description": "4",
                    "guid": str(gid_b),
                },
            ]

        monkeypatch.setattr(RuzAPI, "getGroup", fake_get_group)

        response = await client.get("/api/group/search", params={"q": "ИС221"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["oid"] == 841
        assert data[0]["faculty_name"] == "Факультет 4"
        assert data[1]["oid"] == 839
        assert data[1]["faculty_name"] is None
