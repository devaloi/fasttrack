import asyncio
import contextlib
import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[int, set[WebSocket]] = {}
        self._heartbeat_tasks: dict[WebSocket, asyncio.Task] = {}  # type: ignore[type-arg]

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        if user_id not in self._connections:
            self._connections[user_id] = set()
        self._connections[user_id].add(websocket)
        task = asyncio.create_task(self._heartbeat(user_id, websocket))
        self._heartbeat_tasks[websocket] = task

    def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        if user_id in self._connections:
            self._connections[user_id].discard(websocket)
            if not self._connections[user_id]:
                del self._connections[user_id]
        task = self._heartbeat_tasks.pop(websocket, None)
        if task:
            task.cancel()

    async def send_to_user(self, user_id: int, message: dict) -> None:
        connections = self._connections.get(user_id, set()).copy()
        for ws in connections:
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(user_id, ws)

    async def broadcast(self, message: dict) -> None:
        for user_id in list(self._connections.keys()):
            await self.send_to_user(user_id, message)

    async def _heartbeat(self, user_id: int, websocket: WebSocket) -> None:
        try:
            while True:
                await asyncio.sleep(30)
                try:
                    await websocket.send_json({"type": "ping"})
                except Exception:
                    self.disconnect(user_id, websocket)
                    break
        except asyncio.CancelledError:
            pass

    async def shutdown(self) -> None:
        for task in self._heartbeat_tasks.values():
            task.cancel()
        self._heartbeat_tasks.clear()
        for _user_id, connections in list(self._connections.items()):
            for ws in connections.copy():
                with contextlib.suppress(Exception):
                    await ws.close()
        self._connections.clear()


manager = ConnectionManager()
