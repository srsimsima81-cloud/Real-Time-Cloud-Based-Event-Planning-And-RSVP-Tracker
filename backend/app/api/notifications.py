from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.models import Notification
from app.schemas.schemas import NotificationOut

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])
@router.get("", response_model=list[NotificationOut])
async def notifications(user=Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    return (await db.execute(select(Notification).where(Notification.user_id==user.id).order_by(Notification.created_at.desc()).limit(100))).scalars().all()
@router.put("/{notification_id}/read", response_model=NotificationOut)
async def mark_read(notification_id:int, user=Depends(get_current_user), db:AsyncSession=Depends(get_db)):
    n=await db.get(Notification, notification_id)
    if not n or n.user_id != user.id: raise HTTPException(404,"Notification not found")
    n.read=True; await db.commit(); await db.refresh(n); return n
