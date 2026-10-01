from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import RSVP, RSVPStatus, WaitlistEntry

async def event_analytics(db: AsyncSession, event_id: int, capacity: int, invitee_count: int | None = None):
    rows = (await db.execute(select(RSVP.status, func.count(RSVP.id)).where(RSVP.event_id == event_id).group_by(RSVP.status))).all()
    counts = {str(status): count for status, count in rows}
    going = counts.get(RSVPStatus.GOING.value, 0); maybe = counts.get(RSVPStatus.MAYBE.value, 0); not_going = counts.get(RSVPStatus.NOT_GOING.value, 0)
    waitlisted = await db.scalar(select(func.count(WaitlistEntry.id)).where(WaitlistEntry.event_id == event_id, WaitlistEntry.status == "WAITING")) or 0
    total = going + maybe + not_going
    denominator = invitee_count if invitee_count is not None and invitee_count > 0 else total
    return {"total_responses": total, "going": going, "maybe": maybe, "not_going": not_going, "waitlisted": waitlisted, "capacity": capacity, "available_seats": max(capacity-going, 0), "response_rate": round(total / denominator * 100, 2) if denominator else 0.0, "capacity_utilization": round(going / capacity * 100, 2) if capacity else 0.0}
