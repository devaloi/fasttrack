import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient, test_user, auth_headers):
    resp = await client.post(
        "/api/v1/projects",
        headers=auth_headers,
        json={"name": "My Project", "description": "A test project"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "My Project"
    assert data["owner_id"] == test_user.id


@pytest.mark.asyncio
async def test_list_projects(client: AsyncClient, test_user, auth_headers):
    await client.post(
        "/api/v1/projects",
        headers=auth_headers,
        json={"name": "Project 1"},
    )
    await client.post(
        "/api/v1/projects",
        headers=auth_headers,
        json={"name": "Project 2"},
    )
    resp = await client.get("/api/v1/projects", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) >= 2


@pytest.mark.asyncio
async def test_get_project(client: AsyncClient, test_user, auth_headers):
    create_resp = await client.post(
        "/api/v1/projects",
        headers=auth_headers,
        json={"name": "Get Test"},
    )
    project_id = create_resp.json()["id"]
    resp = await client.get(f"/api/v1/projects/{project_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Get Test"


@pytest.mark.asyncio
async def test_update_project(client: AsyncClient, test_user, auth_headers):
    create_resp = await client.post(
        "/api/v1/projects",
        headers=auth_headers,
        json={"name": "Update Test"},
    )
    project_id = create_resp.json()["id"]
    resp = await client.patch(
        f"/api/v1/projects/{project_id}",
        headers=auth_headers,
        json={"name": "Updated Name"},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_delete_project(client: AsyncClient, test_user, auth_headers):
    create_resp = await client.post(
        "/api/v1/projects",
        headers=auth_headers,
        json={"name": "Delete Test"},
    )
    project_id = create_resp.json()["id"]
    resp = await client.delete(f"/api/v1/projects/{project_id}", headers=auth_headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_project_not_found(client: AsyncClient, test_user, auth_headers):
    resp = await client.get("/api/v1/projects/99999", headers=auth_headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_project_ownership(client: AsyncClient, test_user, admin_user, admin_headers):
    # Admin creates a project
    create_resp = await client.post(
        "/api/v1/projects",
        headers=admin_headers,
        json={"name": "Admin Project"},
    )
    project_id = create_resp.json()["id"]

    # Regular user tries to access it
    from fasttrack.auth.jwt import create_access_token

    user_token = create_access_token(test_user.id, test_user.role)
    user_headers = {"Authorization": f"Bearer {user_token}"}
    resp = await client.get(f"/api/v1/projects/{project_id}", headers=user_headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_project_pagination(client: AsyncClient, test_user, auth_headers):
    for i in range(5):
        await client.post(
            "/api/v1/projects",
            headers=auth_headers,
            json={"name": f"Paginated {i}"},
        )
    resp = await client.get("/api/v1/projects?limit=2", headers=auth_headers)
    data = resp.json()
    assert len(data["items"]) == 2
    assert data["has_more"] is True
    assert data["next_cursor"] is not None

    resp2 = await client.get(
        f"/api/v1/projects?limit=2&cursor={data['next_cursor']}", headers=auth_headers
    )
    data2 = resp2.json()
    assert len(data2["items"]) == 2
