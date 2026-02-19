import pytest
from httpx import AsyncClient


async def _create_project(client: AsyncClient, headers: dict) -> int:
    resp = await client.post(
        "/api/v1/projects",
        headers=headers,
        json={"name": "Task Test Project"},
    )
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient, test_user, auth_headers):
    project_id = await _create_project(client, auth_headers)
    resp = await client.post(
        f"/api/v1/projects/{project_id}/tasks",
        headers=auth_headers,
        json={"title": "My Task", "description": "Do something"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "My Task"
    assert data["status"] == "todo"
    assert data["priority"] == "medium"


@pytest.mark.asyncio
async def test_list_tasks(client: AsyncClient, test_user, auth_headers):
    project_id = await _create_project(client, auth_headers)
    for i in range(3):
        await client.post(
            f"/api/v1/projects/{project_id}/tasks",
            headers=auth_headers,
            json={"title": f"Task {i}"},
        )
    resp = await client.get(f"/api/v1/projects/{project_id}/tasks", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 3


@pytest.mark.asyncio
async def test_get_task(client: AsyncClient, test_user, auth_headers):
    project_id = await _create_project(client, auth_headers)
    create_resp = await client.post(
        f"/api/v1/projects/{project_id}/tasks",
        headers=auth_headers,
        json={"title": "Get Test"},
    )
    task_id = create_resp.json()["id"]
    resp = await client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Get Test"


@pytest.mark.asyncio
async def test_update_task(client: AsyncClient, test_user, auth_headers):
    project_id = await _create_project(client, auth_headers)
    create_resp = await client.post(
        f"/api/v1/projects/{project_id}/tasks",
        headers=auth_headers,
        json={"title": "Update Test"},
    )
    task_id = create_resp.json()["id"]
    resp = await client.patch(
        f"/api/v1/tasks/{task_id}",
        headers=auth_headers,
        json={"status": "in_progress", "priority": "high"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"
    assert resp.json()["priority"] == "high"


@pytest.mark.asyncio
async def test_delete_task(client: AsyncClient, test_user, auth_headers):
    project_id = await _create_project(client, auth_headers)
    create_resp = await client.post(
        f"/api/v1/projects/{project_id}/tasks",
        headers=auth_headers,
        json={"title": "Delete Test"},
    )
    task_id = create_resp.json()["id"]
    resp = await client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_task_filter_by_status(client: AsyncClient, test_user, auth_headers):
    project_id = await _create_project(client, auth_headers)
    create_resp = await client.post(
        f"/api/v1/projects/{project_id}/tasks",
        headers=auth_headers,
        json={"title": "Todo Task"},
    )
    task_id = create_resp.json()["id"]
    await client.patch(
        f"/api/v1/tasks/{task_id}",
        headers=auth_headers,
        json={"status": "done"},
    )
    await client.post(
        f"/api/v1/projects/{project_id}/tasks",
        headers=auth_headers,
        json={"title": "Still Todo"},
    )
    resp = await client.get(
        f"/api/v1/projects/{project_id}/tasks?task_status=todo",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert all(t["status"] == "todo" for t in items)


@pytest.mark.asyncio
async def test_task_not_found(client: AsyncClient, test_user, auth_headers):
    resp = await client.get("/api/v1/tasks/99999", headers=auth_headers)
    assert resp.status_code == 404
