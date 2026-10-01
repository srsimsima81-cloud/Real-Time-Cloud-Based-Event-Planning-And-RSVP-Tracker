from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.models import RSVP, User
from app.schemas.schemas import RSVPOut

router = APIRouter(prefix="/api/rsvps", tags=["RSVP"])

@router.get("/me", response_model=list[RSVPOut])
async def my_rsvps(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return (await db.execute(select(RSVP).where(RSVP.user_id == user.id).order_by(RSVP.updated_at.desc()))).scalars().all()
