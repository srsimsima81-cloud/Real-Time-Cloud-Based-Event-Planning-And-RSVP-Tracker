from datetime import datetime
from enum import Enum
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, Time, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class UserRole(str, Enum):
    ATTENDEE = "ATTENDEE"
    ORGANIZER = "ORGANIZER"
    ADMIN = "ADMIN"

class EventStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    FULL = "FULL"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class RSVPStatus(str, Enum):
    GOING = "GOING"
    MAYBE = "MAYBE"
    NOT_GOING = "NOT_GOING"
    WAITLISTED = "WAITLISTED"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(String(20), default=UserRole.ATTENDEE, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    events: Mapped[list["Event"]] = relationship(back_populates="organizer")
    rsvps: Mapped[list["RSVP"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organizer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    event_name: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    event_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    start_time: Mapped[datetime] = mapped_column(Time, nullable=False)
    end_time: Mapped[datetime] = mapped_column(Time, nullable=False)
    venue: Mapped[str] = mapped_column(String(200), nullable=False)
    online_link: Mapped[str | None] = mapped_column(String(500))
    maximum_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    registration_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[EventStatus] = mapped_column(String(20), default=EventStatus.DRAFT, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    organizer: Mapped[User] = relationship(back_populates="events")
    rsvps: Mapped[list["RSVP"]] = relationship(back_populates="event", cascade="all, delete-orphan")
    announcements: Mapped[list["Announcement"]] = relationship(back_populates="event", cascade="all, delete-orphan")
    waitlist_entries: Mapped[list["WaitlistEntry"]] = relationship(back_populates="event", cascade="all, delete-orphan")
    __table_args__ = (Index("ix_events_date_status", "event_date", "status"),)

class RSVP(Base):
    __tablename__ = "rsvps"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[RSVPStatus] = mapped_column(String(20), nullable=False)
    responded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    event: Mapped[Event] = relationship(back_populates="rsvps")
    user: Mapped[User] = relationship(back_populates="rsvps")
    __table_args__ = (UniqueConstraint("event_id", "user_id", name="uq_rsvp_event_user"), Index("ix_rsvps_event_status", "event_id", "status"))

class WaitlistEntry(Base):
    __tablename__ = "waitlist"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="WAITING", nullable=False)
    event: Mapped[Event] = relationship(back_populates="waitlist_entries")
    __table_args__ = (UniqueConstraint("event_id", "user_id", name="uq_waitlist_event_user"), Index("ix_waitlist_event_status_joined", "event_id", "status", "joined_at"))

class Announcement(Base):
    __tablename__ = "announcements"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    event: Mapped[Event] = relationship(back_populates="announcements")

class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id: Mapped[int | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"))
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    user: Mapped[User] = relationship(back_populates="notifications")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    entity: Mapped[str] = mapped_column(String(80), nullable=False)
    entity_id: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
