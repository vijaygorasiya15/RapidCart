from app.core.dependencies import get_current_user_ws
from app.db.database import SessionLocal
from app.services.websocket import manager
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, WebSocketException
from sqlalchemy.orm import Session

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/orders")
async def orders_websocket(websocket: WebSocket):
    db: Session = SessionLocal()
    try:
        user = await get_current_user_ws(websocket, db)
    except WebSocketException:
        await websocket.close(code=1008)
        db.close()
        return

    await manager.connect(user.id, websocket)
    db.close()

    try:
        while True:
            await websocket.receive_text()  # keeps connection alive; we don't act on client messages
    except WebSocketDisconnect:
        manager.disconnect(user.id)