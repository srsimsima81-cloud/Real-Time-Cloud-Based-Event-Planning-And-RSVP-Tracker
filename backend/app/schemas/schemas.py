from datetime import date, datetime, time
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from app.models.models import EventStatus, RSVPStatus, UserRole

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.ATTENDEE

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; name: str; email: EmailStr; role: UserRole

class TokenResponse(BaseModel):
    access_token: str; token_type: str = "bearer"; user: UserOut

class EventCreate(BaseModel):
    event_name: str = Field(min_length=3, max_length=180)
    description: str = Field(min_length=10)
    event_type: str = Field(min_length=2, max_length=80)
    event_date: date
    start_time: time
    end_time: time
    venue: str = Field(min_length=2, max_length=200)
    online_link: Optional[str] = None
    maximum_capacity: int = Field(gt=0, le=1_000_000)
    registration_deadline: datetime
    status: EventStatus = EventStatus.PUBLISHED

    @field_validator("end_time")
    @classmethod
    def valid_time(cls, v, info):
        start = info.data.get("start_time")
        if start and v <= start: raise ValueError("end_time must be after start_time")
        return v

class EventOut(EventCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int; organizer_id: int; created_at: datetime; updated_at: datetime

class RSVPRequest(BaseModel):
    status: RSVPStatus

class RSVPOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; event_id: int; user_id: int; status: RSVPStatus; responded_at: datetime; updated_at: datetime

class AnnouncementCreate(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    message: str = Field(min_length=2, max_length=5000)

class AnnouncementOut(AnnouncementCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int; event_id: int; created_at: datetime

class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; user_id: int; event_id: Optional[int]; type: str; message: str; read: bool; created_at: datetime

class AnalyticsOut(BaseModel):
    total_responses: int; going: int; maybe: int; not_going: int; waitlisted: int; capacity: int; available_seats: int; response_rate: float; capacity_utilization: float

class MessageOut(BaseModel):
    message: str
