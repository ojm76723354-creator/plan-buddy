from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Event, User, Friendship, FriendshipStatus, EventVisibility, EventParticipant, ParticipantStatus
from schemas import EventCreate, EventResponse
from security import get_current_user
from datetime import datetime

calendar_router = APIRouter()

@calendar_router.get("/", response_model=List[EventResponse])
def get_events(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 내가 소유한 이벤트 또는 수락된 참여자로 등록된 이벤트 조회
    owned_events = db.query(Event).filter(Event.user_id == current_user.id).all()
    participating_events = db.query(Event).join(EventParticipant).filter(
        (EventParticipant.user_id == current_user.id) & 
        (EventParticipant.status != ParticipantStatus.REJECTED)
    ).all()
    
    all_events = list(set(owned_events + participating_events))
    
    # 맵핑 (username 등을 포함하기 위함)
    results = []
    for event in all_events:
        event_dict = event.__dict__
        event_dict["participants"] = [
            {
                "user_id": p.user_id,
                "username": p.user.username,
                "status": p.status,
                "last_latitude": p.last_latitude,
                "last_longitude": p.last_longitude,
                "is_sharing_location": p.is_sharing_location,
                "arrival_time": p.arrival_time
            } for p in event.participants
        ]
        results.append(event_dict)
    return results

@calendar_router.post("/", response_model=EventResponse)
def create_event(event: EventCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_event = Event(
        user_id=current_user.id,
        title=event.title,
        description=event.description,
        location=event.location,
        latitude=event.latitude,
        longitude=event.longitude,
        radius=event.radius,
        start_time=event.start_time,
        end_time=event.end_time,
        visibility=event.visibility
    )
    db.add(new_event)
    db.flush() # ID를 얻기 위해 (초대에 필요)

    # 작성자 본인을 참여자로 자동 등록 (ACCEPTED 상태)
    creator_participant = EventParticipant(
        event_id=new_event.id,
        user_id=current_user.id,
        status=ParticipantStatus.ACCEPTED
    )
    db.add(creator_participant)

    # 초대받은 유저들 처리
    if event.invitees:
        for username in event.invitees:
            invitee = db.query(User).filter(User.username == username).first()
            if invitee and invitee.id != current_user.id:
                new_participant = EventParticipant(
                    event_id=new_event.id,
                    user_id=invitee.id,
                    status=ParticipantStatus.PENDING
                )
                db.add(new_participant)
    
    db.commit()
    db.refresh(new_event)
    
    # 리턴 데이터 가공
    result = new_event.__dict__
    result["participants"] = [
        {
            "user_id": p.user_id,
            "username": p.user.username,
            "status": p.status,
            "last_latitude": p.last_latitude,
            "last_longitude": p.last_longitude,
            "is_sharing_location": p.is_sharing_location,
            "arrival_time": p.arrival_time
        } for p in new_event.participants
    ]
    return result

@calendar_router.get("/{event_id}", response_model=EventResponse)
def get_event_detail(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # 가공
    result = event.__dict__
    result["participants"] = [
        {
            "user_id": p.user_id,
            "username": p.user.username,
            "status": p.status,
            "last_latitude": p.last_latitude,
            "last_longitude": p.last_longitude,
            "is_sharing_location": p.is_sharing_location,
            "arrival_time": p.arrival_time
        } for p in event.participants
    ]
    return result
