"""API tests for users endpoints."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel

from ruz_server.api import users
from ruz_server.api.app import app
from ruz_server.api.security import require_api_key


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
    app.dependency_overrides[users.get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


def user_payload(user_id: int, group_id: int = 6001) -> dict:
    return {
        "id": user_id,
        "username": f"user_{user_id}",
        "group_oid": group_id,
        "subgroup": 1,
        "group_guid": str(uuid.uuid4()),
        "group_name": f"IU8-{group_id}",
        "faculty_name": "Informatics",
    }


@pytest.mark.api
class TestUsersAPI:
    @pytest.mark.asyncio
    async def test_create_user(self, client):
        response = await client.post("/api/user/", json=user_payload(7001))
        assert response.status_code == 201
        body = response.json()
        assert body["id"] == 7001
        assert body["username"] == "user_7001"
        assert body["group_oid"] == 6001

    @pytest.mark.asyncio
    async def test_create_user_with_null_subgroup(self, client):
        payload = user_payload(7014)
        payload["subgroup"] = None
        response = await client.post("/api/user/", json=payload)

        assert response.status_code == 201
        assert response.json()["subgroup"] is None

    @pytest.mark.asyncio
    async def test_create_user_without_subgroup_defaults_to_null(self, client):
        payload = user_payload(7015)
        payload.pop("subgroup")
        response = await client.post("/api/user/", json=payload)

        assert response.status_code == 201
        assert response.json()["subgroup"] is None

    @pytest.mark.asyncio
    async def test_list_users(self, client):
        await client.post("/api/user/", json=user_payload(7002))
        response = await client.get("/api/user/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, client):
        await client.post("/api/user/", json=user_payload(7003))
        response = await client.get("/api/user/7003")
        assert response.status_code == 200
        assert response.json()["id"] == 7003

    @pytest.mark.asyncio
    async def test_update_user(self, client):
        await client.post("/api/user/", json=user_payload(7004))
        response = await client.put(
            "/api/user/7004",
            json={
                "username": "updated_user",
                "group_oid": 6002,
                "subgroup": 2,
                "group_guid": str(uuid.uuid4()),
                "group_name": "IU8-6002",
                "faculty_name": "Updated Faculty",
            },
        )
        assert response.status_code == 200
        updated_body = response.json()
        assert updated_body["id"] == 7004
        assert updated_body["username"] == "updated_user"
        assert updated_body["group_oid"] == 6002
        assert updated_body["subgroup"] == 2

        get_response = await client.get("/api/user/7004")
        body = get_response.json()
        assert body["username"] == "updated_user"
        assert body["group_oid"] == 6002
        assert body["subgroup"] == 2

    @pytest.mark.asyncio
    async def test_update_user_invalid_subgroup_returns_400(self, client):
        await client.post("/api/user/", json=user_payload(7011))
        response = await client.put("/api/user/7011", json={"subgroup": 3})
        assert response.status_code == 400
        assert response.json()["detail"] == "invalid subgroup"

    @pytest.mark.asyncio
    async def test_update_user_can_clear_group_and_subgroup_together(self, client):
        await client.post("/api/user/", json=user_payload(7016))
        response = await client.put(
            "/api/user/7016",
            json={
                "group_oid": None,
                "subgroup": None,
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert body["group_oid"] is None
        assert body["subgroup"] is None

    @pytest.mark.asyncio
    async def test_update_user_rejects_null_subgroup_without_null_group(self, client):
        await client.post("/api/user/", json=user_payload(7017))
        response = await client.put(
            "/api/user/7017",
            json={
                "subgroup": None,
            },
        )

        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "subgroup can be null only when group_oid is null"
        )

    @pytest.mark.asyncio
    async def test_update_user_autocreates_missing_group(self, client):
        await client.post("/api/user/", json=user_payload(7012, group_id=6101))
        new_group_guid = str(uuid.uuid4())
        response = await client.put(
            "/api/user/7012",
            json={
                "group_oid": 6102,
                "subgroup": 1,
                "group_guid": new_group_guid,
                "group_name": "IU8-6102",
                "faculty_name": "Informatics",
            },
        )
        assert response.status_code == 200
        updated_body = response.json()
        assert updated_body["id"] == 7012
        assert updated_body["group_oid"] == 6102
        assert updated_body["subgroup"] == 1

    @pytest.mark.asyncio
    async def test_delete_user(self, client):
        await client.post("/api/user/", json=user_payload(7005))
        response = await client.delete("/api/user/7005")
        assert response.status_code == 200
        assert response.json() is True

        get_response = await client.get("/api/user/7005")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_user_duplicate_returns_409(self, client):
        payload = user_payload(7010)
        await client.post("/api/user/", json=payload)
        response = await client.post("/api/user/", json=payload)
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_create_user_invalid_subgroup_returns_400(self, client):
        payload = user_payload(7013)
        payload["subgroup"] = -1
        response = await client.post("/api/user/", json=payload)
        assert response.status_code == 400
        assert response.json()["detail"] == "invalid subgroup"

    @pytest.mark.asyncio
    async def test_get_user_not_found_returns_404(self, client):
        response = await client.get("/api/user/999999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_user_not_found_returns_404(self, client):
        response = await client.put("/api/user/999999", json={"username": "x"})
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_user_not_found_returns_404(self, client):
        response = await client.delete("/api/user/999999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_user_invalid_payload_returns_422(self, client):
        response = await client.post("/api/user/", json={"id": 1})
        assert response.status_code == 422
