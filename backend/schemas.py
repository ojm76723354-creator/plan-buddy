from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    profile_image: Optional[str] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    username: str
    password: str

class NicknameUpdate(BaseModel):
    new_username: str

class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str

# ----------------- #
# Event Schemas     #
# ----------------- #
class EventParticipantResponse(BaseModel):
    user_id: int
    username: str
    status: str
    last_latitude: Optional[float] = None
    last_longitude: Optional[float] = None
    is_sharing_location: bool
    arrival_time: Optional[datetime] = None

    class Config:
        from_attributes = True

class EventChatCreate(BaseModel):
    message: str

class EventChatResponse(BaseModel):
    id: int
    user_id: int
    username: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True

class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius: Optional[float] = 50.0
    start_time: datetime
    end_time: datetime
    visibility: Optional[str] = "PUBLIC"
    invitees: Optional[List[str]] = [] # 초대할 유저이름 목록

class EventResponse(EventCreate):
    id: int
    user_id: int
    participants: List[EventParticipantResponse] = []

    class Config:
        from_attributes = True

class LocationUpdate(BaseModel):
    latitude: float
    longitude: float

class StatusUpdate(BaseModel):
    status: str

# ----------------- #
# Friendship Schemas#
# ----------------- #
class FriendRequest(BaseModel):
    target_username: str

class FriendshipResponse(BaseModel):
    id: int
    user_id_1: int
    user_id_2: int
    status: str
    
    class Config:
        from_attributes = True
