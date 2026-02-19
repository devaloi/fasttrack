import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    resp = await client.post("/api/v1/auth/register", json={
        "email": "new@example.com",
        "password": "newpass123",
        "display_name": "New User",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "new@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user):
    resp = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "testpass123",
    })
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    resp = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user):
    resp = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpass",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    resp = await client.post("/api/v1/auth/login", json={
        "email": "nobody@example.com",
        "password": "whatever",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, test_user):
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123",
    })
    refresh_token = login_resp.json()["refresh_token"]

    resp = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_refresh_token_rotation(client: AsyncClient, test_user):
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123",
    })
    old_refresh = login_resp.json()["refresh_token"]

    await client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})

    # Old refresh token should be revoked
    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, test_user):
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123",
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/auth/logout", headers=headers)
    assert resp.status_code == 204

    # Token should be revoked
    resp = await client.get("/api/v1/users/me", headers=headers)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_invalid_token(client: AsyncClient):
    resp = await client.get(
        "/api/v1/users/me", headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert resp.status_code == 401
