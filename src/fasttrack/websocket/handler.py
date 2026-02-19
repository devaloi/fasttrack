import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from fasttrack.auth.jwt import decode_token
from fasttrack.websocket.manager import manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str | None = None) -> None:
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return

    try:
        payload = decode_token(token)
    except ValueError:
        await websocket.close(code=4001, reason="Invalid token")
        return

    if payload.get("type") != "access":
        await websocket.close(code=4001, reason="Invalid token type")
        return

    user_id = int(payload["sub"])
    await manager.connect(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "pong":
                continue
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
    except Exception:
        manager.disconnect(user_id, websocket)
