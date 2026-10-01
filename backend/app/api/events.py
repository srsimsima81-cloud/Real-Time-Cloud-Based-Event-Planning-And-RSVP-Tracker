from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user, require_roles
from app.db.session import get_db
from app.models.models import Announcement, Event, EventStatus, User, UserRole
from app.schemas.schemas import AnnouncementCreate, AnnouncementOut, EventCreate, EventOut
from app.services.notifications import notify_event_rsvpers

router = APIRouter(prefix="/api/events", tags=["Events"])

async def get_owned_event(event_id: int, user: User, db: AsyncSession):
    event = await db.get(Event, event_id)
    if not event: raise HTTPException(404, "Event not found")
    if user.role != UserRole.ADMIN and event.organizer_id != user.id: raise HTTPException(403, "You can manage only your own events")
    return event

@router.post("", response_model=EventOut, status_code=201)
async def create_event(data: EventCreate, user: User = Depends(require_roles(UserRole.ORGANIZER, UserRole.ADMIN)), db: AsyncSession = Depends(get_db)):
    if data.registration_deadline.tzinfo is None: deadline = data.registration_deadline.replace(tzinfo=timezone.utc)
    else: deadline = data.registration_deadline
    if deadline > datetime.combine(data.event_date, data.end_time, tzinfo=timezone.utc): raise HTTPException(422, "Registration deadline must be on or before event end")
    event = Event(**data.model_dump(), organizer_id=user.id, registration_deadline=deadline)
    db.add(event); await db.commit(); await db.refresh(event); return event

@router.get("", response_model=list[EventOut])
async def list_events(db: AsyncSession = Depends(get_db)):
    return (await db.execute(select(Event).where(Event.status.in_([EventStatus.PUBLISHED, EventStatus.FULL])).order_by(Event.event_date, Event.start_time))).scalars().all()

@router.get("/upcoming", response_model=list[EventOut])
async def upcoming(db: AsyncSession = Depends(get_db)):
    today = datetime.now(timezone.utc).date()
    return (await db.execute(select(Event).where(Event.event_date >= today, Event.status.in_([EventStatus.PUBLISHED, EventStatus.FULL])).order_by(Event.event_date, Event.start_time))).scalars().all()

@router.get("/{event_id}", response_model=EventOut)
async def get_event(event_id: int, db: AsyncSession = Depends(get_db)):
    event = await db.get(Event, event_id)
    if not event: raise HTTPException(404, "Event not found")
    return event

@router.put("/{event_id}", response_model=EventOut)
async def update_event(event_id: int, data: EventCreate, user: User = Depends(require_roles(UserRole.ORGANIZER, UserRole.ADMIN)), db: AsyncSession = Depends(get_db)):
    event = await get_owned_event(event_id, user, db)
    for key, value in data.model_dump().items(): setattr(event, key, value)
    await db.commit(); await db.refresh(event); return event

@router.delete("/{event_id}")
async def delete_event(event_id: int, user: User = Depends(require_roles(UserRole.ORGANIZER, UserRole.ADMIN)), db: AsyncSession = Depends(get_db)):
    event = await get_owned_event(event_id, user, db)
    await db.delete(event); await db.commit(); return {"message": "Event deleted"}

@router.post("/{event_id}/cancel")
async def cancel_event(event_id: int, user: User = Depends(require_roles(UserRole.ORGANIZER, UserRole.ADMIN)), db: AsyncSession = Depends(get_db)):
    event = await get_owned_event(event_id, user, db); event.status = EventStatus.CANCELLED
    await notify_event_rsvpers(db, event_id, "EVENT_CANCELLED", f"{event.event_name} has been cancelled.")
    await db.commit(); return {"message": "Event cancelled"}

@router.post("/{event_id}/announcements", response_model=AnnouncementOut, status_code=201)
async def create_announcement(event_id: int, data: AnnouncementCreate, user: User = Depends(require_roles(UserRole.ORGANIZER, UserRole.ADMIN)), db: AsyncSession = Depends(get_db)):
    event = await get_owned_event(event_id, user, db)
    ann = Announcement(event_id=event.id, **data.model_dump()); db.add(ann)
    await notify_event_rsvpers(db, event_id, "ANNOUNCEMENT", f"{data.title}: {data.message}")
    await db.commit(); await db.refresh(ann); return ann

@router.get("/{event_id}/announcements", response_model=list[AnnouncementOut])
async def announcements(event_id: int, db: AsyncSession = Depends(get_db)):
    return (await db.execute(select(Announcement).where(Announcement.event_id == event_id).order_by(Announcement.created_at.desc()))).scalars().all()
