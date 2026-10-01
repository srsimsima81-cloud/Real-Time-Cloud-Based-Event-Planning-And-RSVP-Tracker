from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Notification, RSVP, User

async def create_notification(db: AsyncSession, user_id: int, event_id: int | None, ntype: str, message: str):
    n = Notification(user_id=user_id, event_id=event_id, type=ntype, message=message)
    db.add(n); return n

async def notify_event_rsvpers(db: AsyncSession, event_id: int, ntype: str, message: str):
    ids = (await db.execute(select(RSVP.user_id).where(RSVP.event_id == event_id, RSVP.status.in_(["GOING", "MAYBE"])))).scalars().all()
    for uid in ids: await create_notification(db, uid, event_id, ntype, message)
