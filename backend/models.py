from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone
import enum

class FriendshipStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"

class EventVisibility(str, enum.Enum):
    PUBLIC = "PUBLIC"
    FRIENDS_ONLY = "FRIENDS_ONLY"
    PRIVATE = "PRIVATE"

class ParticipantStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    ARRIVED = "ARRIVED"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    profile_image = Column(String, nullable=True) # 프로필 이미지 경로 저장용
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    events = relationship("Event", back_populates="owner")
    participations = relationship("EventParticipant", back_populates="user")

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    location = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)  # 위도
    longitude = Column(Float, nullable=True) # 경도
    radius = Column(Float, default=50.0)      # 도착 판정 반경 (m)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    visibility = Column(SQLEnum(EventVisibility), default=EventVisibility.PUBLIC)

    owner = relationship("User", back_populates="events")
    participants = relationship("EventParticipant", back_populates="event", cascade="all, delete-orphan")
    messages = relationship("EventChat", back_populates="event", cascade="all, delete-orphan")

class EventParticipant(Base):
    __tablename__ = "event_participants"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(SQLEnum(ParticipantStatus), default=ParticipantStatus.PENDING)
    
    # 위치 정보 (실시간 공유용)
    last_latitude = Column(Float, nullable=True)
    last_longitude = Column(Float, nullable=True)
    is_sharing_location = Column(Boolean, default=False)
    
    arrival_time = Column(DateTime, nullable=True) # 실제 도착 시간
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    event = relationship("Event", back_populates="participants")
    user = relationship("User", back_populates="participations")

class EventChat(Base):
    __tablename__ = "event_chats"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    event = relationship("Event", back_populates="messages")
    user = relationship("User")

class Friendship(Base):
    __tablename__ = "friendships"

    id = Column(Integer, primary_key=True, index=True)
    user_id_1 = Column(Integer, ForeignKey("users.id"))
    user_id_2 = Column(Integer, ForeignKey("users.id"))
    status = Column(SQLEnum(FriendshipStatus), default=FriendshipStatus.PENDING)
