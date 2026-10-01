from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user, require_roles
from app.db.session import get_db
from app.models.models import (
    Event,
    EventStatus,
    RSVP,
    RSVPStatus,
    User,
    UserRole,
    WaitlistEntry,
)
from app.schemas.schemas import AnalyticsOut, RSVPOut, RSVPRequest
from app.services.analytics import event_analytics
from app.services.notifications import create_notification
from app.services.realtime import manager


router = APIRouter(prefix="/api/events", tags=["RSVP"])


def counts_payload(event_id, analytics):
    return {
        "type": "rsvp.updated",
        "event_id": event_id,
        "analytics": analytics,
    }


@router.post("/{event_id}/rsvp", response_model=RSVPOut)
async def create_or_update_rsvp(
    event_id: int,
    data: RSVPRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # get_current_user() performs a database query, which may already
    # have started a transaction on this SQLAlchemy session.
    # End that read transaction before starting our explicit
    # transaction for the RSVP operation.
    user_id = user.id
    await db.rollback()

    async with db.begin():
        # Lock the event row so concurrent RSVP requests for the
        # same event cannot simultaneously modify its capacity.
        event = (
            await db.execute(
                select(Event)
                .where(Event.id == event_id)
                .with_for_update()
            )
        ).scalar_one_or_none()

        if not event:
            raise HTTPException(404, "Event not found")

        if event.status not in [
            EventStatus.PUBLISHED,
            EventStatus.FULL,
        ]:
            raise HTTPException(
                409,
                "Event is not accepting RSVPs",
            )

        if datetime.now(timezone.utc) > event.registration_deadline:
            raise HTTPException(
                409,
                "Registration deadline has passed",
            )

        # Lock this user's RSVP if one already exists.
        rsvp = (
            await db.execute(
                select(RSVP)
                .where(
                    RSVP.event_id == event_id,
                    RSVP.user_id == user_id,
                )
                .with_for_update()
            )
        ).scalar_one_or_none()

        current_going = (
            await db.scalar(
                select(func.count(RSVP.id)).where(
                    RSVP.event_id == event_id,
                    RSVP.status == RSVPStatus.GOING,
                )
            )
            or 0
        )

        old_status = rsvp.status if rsvp else None
        target = data.status

        # ---------------------------------------------------------
        # EVENT IS FULL -> ADD ATTENDEE TO WAITLIST
        # ---------------------------------------------------------
        if (
            target == RSVPStatus.GOING
            and old_status != RSVPStatus.GOING
            and current_going >= event.maximum_capacity
        ):
            existing_wait = await db.scalar(
                select(WaitlistEntry).where(
                    WaitlistEntry.event_id == event_id,
                    WaitlistEntry.user_id == user_id,
                    WaitlistEntry.status == "WAITING",
                )
            )

            if not existing_wait:
                db.add(
                    WaitlistEntry(
                        event_id=event_id,
                        user_id=user_id,
                    )
                )

            if rsvp:
                rsvp.status = RSVPStatus.WAITLISTED
            else:
                rsvp = RSVP(
                    event_id=event_id,
                    user_id=user_id,
                    status=RSVPStatus.WAITLISTED,
                )
                db.add(rsvp)

            event.status = EventStatus.FULL

            await create_notification(
                db,
                user_id,
                event_id,
                "WAITLISTED",
                (
                    f"{event.event_name} is full. "
                    "You were added to the waitlist."
                ),
            )

        # ---------------------------------------------------------
        # NORMAL RSVP CREATE / UPDATE
        # ---------------------------------------------------------
        else:
            if not rsvp:
                rsvp = RSVP(
                    event_id=event_id,
                    user_id=user_id,
                    status=target,
                )
                db.add(rsvp)
            else:
                rsvp.status = target

            # Update event capacity status.
            if target == RSVPStatus.GOING:
                new_going_count = current_going

                if old_status != RSVPStatus.GOING:
                    new_going_count += 1

                if new_going_count >= event.maximum_capacity:
                    event.status = EventStatus.FULL
                else:
                    event.status = EventStatus.PUBLISHED

            elif event.status == EventStatus.FULL:
                event.status = EventStatus.PUBLISHED

            await create_notification(
                db,
                user_id,
                event_id,
                "RSVP_CONFIRMATION",
                (
                    f"Your RSVP for {event.event_name} is "
                    f"{target.value.replace('_', ' ').title()}."
                ),
            )

        # Make sure pending inserts/updates are visible to the
        # analytics query before calculating the live values.
        await db.flush()

        analytics = await event_analytics(
            db,
            event_id,
            event.maximum_capacity,
        )

    # The transaction has successfully committed at this point.
    # Only then broadcast the realtime update.
    await manager.broadcast(
        event_id,
        counts_payload(event_id, analytics),
    )

    return rsvp


@router.put("/{event_id}/rsvp", response_model=RSVPOut)
async def update_rsvp(
    event_id: int,
    data: RSVPRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_or_update_rsvp(
        event_id,
        data,
        user,
        db,
    )


@router.delete("/{event_id}/rsvp")
async def cancel_rsvp(
    event_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # get_current_user() already used this session.
    # Reset that transaction before starting our explicit one.
    user_id = user.id
    await db.rollback()

    async with db.begin():
        # Lock event row to safely handle capacity changes and
        # waitlist promotion.
        event = (
            await db.execute(
                select(Event)
                .where(Event.id == event_id)
                .with_for_update()
            )
        ).scalar_one_or_none()

        if not event:
            raise HTTPException(404, "Event not found")

        rsvp = (
            await db.execute(
                select(RSVP)
                .where(
                    RSVP.event_id == event_id,
                    RSVP.user_id == user_id,
                )
                .with_for_update()
            )
        ).scalar_one_or_none()

        if not rsvp:
            raise HTTPException(
                404,
                "RSVP not found",
            )

        was_going = rsvp.status == RSVPStatus.GOING

        rsvp.status = RSVPStatus.NOT_GOING

        # ---------------------------------------------------------
        # PROMOTE FIRST WAITLISTED ATTENDEE
        # ---------------------------------------------------------
        if was_going:
            candidate = (
                await db.execute(
                    select(WaitlistEntry)
                    .where(
                        WaitlistEntry.event_id == event_id,
                        WaitlistEntry.status == "WAITING",
                    )
                    .order_by(WaitlistEntry.joined_at)
                    .with_for_update(skip_locked=True)
                )
            ).scalars().first()

            if candidate:
                promoted = (
                    await db.execute(
                        select(RSVP)
                        .where(
                            RSVP.event_id == event_id,
                            RSVP.user_id == candidate.user_id,
                        )
                        .with_for_update()
                    )
                ).scalar_one_or_none()

                if promoted:
                    promoted.status = RSVPStatus.GOING
                else:
                    promoted = RSVP(
                        event_id=event_id,
                        user_id=candidate.user_id,
                        status=RSVPStatus.GOING,
                    )
                    db.add(promoted)

                candidate.status = "PROMOTED"

                await create_notification(
                    db,
                    candidate.user_id,
                    event_id,
                    "WAITLIST_PROMOTION",
                    (
                        f"A seat opened for {event.event_name}. "
                        "Your waitlist entry was promoted to GOING."
                    ),
                )

            event.status = EventStatus.PUBLISHED

        await db.flush()

        analytics = await event_analytics(
            db,
            event_id,
            event.maximum_capacity,
        )

    await manager.broadcast(
        event_id,
        counts_payload(event_id, analytics),
    )

    return {
        "message": "RSVP cancelled",
    }


@router.get(
    "/{event_id}/rsvps",
    response_model=list[RSVPOut],
)
async def event_rsvps(
    event_id: int,
    user: User = Depends(
        require_roles(
            UserRole.ORGANIZER,
            UserRole.ADMIN,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    event = await db.get(Event, event_id)

    if not event:
        raise HTTPException(
            404,
            "Event not found",
        )

    if (
        user.role != UserRole.ADMIN
        and event.organizer_id != user.id
    ):
        raise HTTPException(
            403,
            "Not your event",
        )

    result = await db.execute(
        select(RSVP)
        .where(RSVP.event_id == event_id)
        .order_by(RSVP.updated_at.desc())
    )

    return result.scalars().all()


@router.get(
    "/{event_id}/analytics",
    response_model=AnalyticsOut,
)
async def analytics(
    event_id: int,
    user: User = Depends(
        require_roles(
            UserRole.ORGANIZER,
            UserRole.ADMIN,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    event = await db.get(Event, event_id)

    if not event:
        raise HTTPException(
            404,
            "Event not found",
        )

    if (
        user.role != UserRole.ADMIN
        and event.organizer_id != user.id
    ):
        raise HTTPException(
            403,
            "Not your event",
        )

    return await event_analytics(
        db,
        event_id,
        event.maximum_capacity,
    )

