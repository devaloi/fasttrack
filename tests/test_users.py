import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, test_user, auth_headers):
    resp = await client.get("/api/v1/users/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "test@example.com"
    assert data["display_name"] == "Test User"


@pytest.mark.asyncio
async def test_update_me(client: AsyncClient, test_user, auth_headers):
    resp = await client.patch(
        "/api/v1/users/me",
        headers=auth_headers,
        json={"display_name": "Updated Name"},
    )
    assert resp.status_code == 200
    assert resp.json()["display_name"] == "Updated Name"


@pytest.mark.asyncio
async def test_list_users_admin(client: AsyncClient, admin_user, admin_headers, test_user):
    resp = await client.get("/api/v1/users", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) >= 2


@pytest.mark.asyncio
async def test_list_users_forbidden(client: AsyncClient, test_user, auth_headers):
    resp = await client.get("/api/v1/users", headers=auth_headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_update_user(client: AsyncClient, admin_user, admin_headers, test_user):
    resp = await client.patch(
        f"/api/v1/users/{test_user.id}",
        headers=admin_headers,
        json={"display_name": "Admin Changed"},
    )
    assert resp.status_code == 200
    assert resp.json()["display_name"] == "Admin Changed"


@pytest.mark.asyncio
async def test_get_user_by_id_admin(client: AsyncClient, admin_user, admin_headers, test_user):
    resp = await client.get(f"/api/v1/users/{test_user.id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"
