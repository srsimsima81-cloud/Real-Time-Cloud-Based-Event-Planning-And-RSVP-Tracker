from collections import defaultdict
from fastapi import WebSocket
import asyncio

class ConnectionManager:
    def __init__(self): self.connections = defaultdict(set); self.lock = asyncio.Lock()
    async def connect(self, event_id: int, websocket: WebSocket):
        await websocket.accept()
        async with self.lock: self.connections[event_id].add(websocket)
    async def disconnect(self, event_id: int, websocket: WebSocket):
        async with self.lock:
            self.connections[event_id].discard(websocket)
            if not self.connections[event_id]: self.connections.pop(event_id, None)
    async def broadcast(self, event_id: int, payload: dict):
        async with self.lock: sockets = list(self.connections.get(event_id, set()))
        stale = []
        for ws in sockets:
            try: await ws.send_json(payload)
            except Exception: stale.append(ws)
        for ws in stale: await self.disconnect(event_id, ws)

manager = ConnectionManager()
