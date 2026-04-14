from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Event, User, Friendship, FriendshipStatus, EventVisibility
from schemas import EventCreate, EventResponse
from security import get_current_user
from datetime import datetime

calendar_router = APIRouter()

@calendar_router.get("/", response_model=List[EventResponse])
def get_events(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    events = db.query(Event).filter(Event.user_id == current_user.id).all()
    # In a real app we'd also return friends' public/friends_only events here
    return events

@calendar_router.post("/", response_model=EventResponse)
def create_event(event: EventCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_event = Event(
        user_id=current_user.id,
        title=event.title,
        description=event.description,
        location=event.location,
        start_time=event.start_time,
        end_time=event.end_time,
        visibility=event.visibility
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event

@calendar_router.get("/friends/{username}", response_model=List[EventResponse])
def get_friend_events(username: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    friend = db.query(User).filter(User.username == username).first()
    if not friend:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check friendship status
    friendship = db.query(Friendship).filter(
        ((Friendship.user_id_1 == current_user.id) & (Friendship.user_id_2 == friend.id) & (Friendship.status == FriendshipStatus.ACCEPTED)) |
        ((Friendship.user_id_1 == friend.id) & (Friendship.user_id_2 == current_user.id) & (Friendship.status == FriendshipStatus.ACCEPTED))
    ).first()
    
    if not friendship:
        raise HTTPException(status_code=403, detail="You are not friends with this user")
        
    # Get events that are not PRIVATE
    events = db.query(Event).filter(
        (Event.user_id == friend.id) & (Event.visibility != EventVisibility.PRIVATE)
    ).all()
    return events
