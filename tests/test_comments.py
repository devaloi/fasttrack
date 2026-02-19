import pytest
from httpx import AsyncClient


async def _setup_task(client: AsyncClient, headers: dict) -> int:
    proj_resp = await client.post(
        "/api/v1/projects", headers=headers, json={"name": "Comment Project"}
    )
    project_id = proj_resp.json()["id"]
    task_resp = await client.post(
        f"/api/v1/projects/{project_id}/tasks",
        headers=headers,
        json={"title": "Comment Task"},
    )
    return task_resp.json()["id"]


@pytest.mark.asyncio
async def test_create_comment(client: AsyncClient, test_user, auth_headers):
    task_id = await _setup_task(client, auth_headers)
    resp = await client.post(
        f"/api/v1/tasks/{task_id}/comments",
        headers=auth_headers,
        json={"body": "This is a comment"},
    )
    assert resp.status_code == 201
    assert resp.json()["body"] == "This is a comment"


@pytest.mark.asyncio
async def test_list_comments(client: AsyncClient, test_user, auth_headers):
    task_id = await _setup_task(client, auth_headers)
    for i in range(3):
        await client.post(
            f"/api/v1/tasks/{task_id}/comments",
            headers=auth_headers,
            json={"body": f"Comment {i}"},
        )
    resp = await client.get(f"/api/v1/tasks/{task_id}/comments", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 3


@pytest.mark.asyncio
async def test_delete_own_comment(client: AsyncClient, test_user, auth_headers):
    task_id = await _setup_task(client, auth_headers)
    create_resp = await client.post(
        f"/api/v1/tasks/{task_id}/comments",
        headers=auth_headers,
        json={"body": "Delete me"},
    )
    comment_id = create_resp.json()["id"]
    resp = await client.delete(f"/api/v1/comments/{comment_id}", headers=auth_headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_cannot_delete_others_comment(
    client: AsyncClient, test_user, admin_user, auth_headers, admin_headers
):
    task_id = await _setup_task(client, admin_headers)

    create_resp = await client.post(
        f"/api/v1/tasks/{task_id}/comments",
        headers=admin_headers,
        json={"body": "Admin comment"},
    )
    comment_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/v1/comments/{comment_id}", headers=auth_headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_delete_any_comment(
    client: AsyncClient, test_user, admin_user, auth_headers, admin_headers
):
    task_id = await _setup_task(client, auth_headers)
    create_resp = await client.post(
        f"/api/v1/tasks/{task_id}/comments",
        headers=auth_headers,
        json={"body": "User comment"},
    )
    comment_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/v1/comments/{comment_id}", headers=admin_headers)
    assert resp.status_code == 204
