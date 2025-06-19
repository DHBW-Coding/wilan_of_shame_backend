import asyncio
from typing import Set
from fastapi import WebSocket

class WebSocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.queue = asyncio.Queue()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast_from_queue(self):
        while True:
            data = await self.queue.get()
            await self.broadcast(data)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)

    async def send_to_queue(self, message: str):
        await self.queue.put(message)

# Singleton instance
ws_manager = WebSocketManager()