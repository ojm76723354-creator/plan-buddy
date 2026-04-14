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
class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: datetime
    end_time: datetime
    visibility: Optional[str] = "PUBLIC"

class EventResponse(EventCreate):
    id: int
    user_id: int

    class Config:
        from_attributes = True

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
