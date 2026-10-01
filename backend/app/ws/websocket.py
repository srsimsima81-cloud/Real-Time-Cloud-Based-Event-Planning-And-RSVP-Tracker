from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.realtime import manager

router = APIRouter()
@router.websocket("/ws/events/{event_id}")
async def event_socket(websocket: WebSocket, event_id: int):
    await manager.connect(event_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(event_id, websocket)
    except Exception:
        await manager.disconnect(event_id, websocket)
