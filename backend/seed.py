
import asyncio
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import select

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.models import (
    User,
    Event,
    RSVP,
    Announcement,
    Notification,
    UserRole,
    RSVPStatus,
    EventStatus,
)
from app.core.security import hash_password


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as db:
        # Prevent duplicate seed data
        if await db.scalar(
            select(User).where(
                User.email == "sophie.bennett@example.com"
            )
        ):
            print("Sample data already exists.")
            return

        # Sample users
        org = User(
            name="Sophie Bennett",
            email="sophie.bennett@example.com",
            password_hash=hash_password("Organizer@123"),
            role=UserRole.ORGANIZER,
        )

        a = User(
            name="Liam Carter",
            email="liam.carter@example.com",
            password_hash=hash_password("Attendee@123"),
            role=UserRole.ATTENDEE,
        )

        b = User(
            name="Emma Wilson",
            email="emma.wilson@example.com",
            password_hash=hash_password("Attendee@123"),
            role=UserRole.ATTENDEE,
        )

        c = User(
            name="Oliver Smith",
            email="oliver.smith@example.com",
            password_hash=hash_password("Attendee@123"),
            role=UserRole.ATTENDEE,
        )

        db.add_all([org, a, b, c])
        await db.flush()

        # Sample events
        workshop_date = date.today() + timedelta(days=7)

        event = Event(
            organizer_id=org.id,
            event_name="Cloud Computing Workshop",
            description=(
                "A fictional hands-on workshop covering cloud architecture, "
                "REST APIs, managed databases and real-time systems."
            ),
            event_type="Workshop",
            event_date=workshop_date,
            start_time=time(10, 0),
            end_time=time(13, 0),
            venue="Skyline Learning Hub",
            maximum_capacity=100,
            registration_deadline=datetime.combine(
                workshop_date,
                time(9, 0),
                tzinfo=timezone.utc,
            ),
            status=EventStatus.PUBLISHED,
        )

        hackathon_date = date.today() + timedelta(days=21)

        event2 = Event(
            organizer_id=org.id,
            event_name="Campus Tech Hackathon",
            description=(
                "A fictional weekend hackathon for building scalable "
                "student applications."
            ),
            event_type="Hackathon",
            event_date=hackathon_date,
            start_time=time(9, 0),
            end_time=time(18, 0),
            venue="Innovation Hall",
            maximum_capacity=50,
            registration_deadline=datetime.combine(
                date.today() + timedelta(days=20),
                time(18, 0),
                tzinfo=timezone.utc,
            ),
            status=EventStatus.PUBLISHED,
        )

        db.add_all([event, event2])
        await db.flush()

        # Sample RSVPs, announcement and notification
        db.add_all(
            [
                RSVP(
                    event_id=event.id,
                    user_id=a.id,
                    status=RSVPStatus.GOING,
                ),
                RSVP(
                    event_id=event.id,
                    user_id=b.id,
                    status=RSVPStatus.MAYBE,
                ),
                RSVP(
                    event_id=event.id,
                    user_id=c.id,
                    status=RSVPStatus.NOT_GOING,
                ),
                Announcement(
                    event_id=event.id,
                    title="Welcome",
                    message="Bring a laptop for the practical session.",
                ),
                Notification(
                    user_id=a.id,
                    event_id=event.id,
                    type="RSVP_CONFIRMATION",
                    message="Your RSVP is GOING.",
                ),
            ]
        )

        await db.commit()

        print(
            "Seeded sample users, events, RSVPs, "
            "announcement and notification."
        )


if __name__ == "__main__":
    asyncio.run(seed())

