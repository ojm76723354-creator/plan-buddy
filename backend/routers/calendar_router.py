from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from database import get_db
from models import Event, User, EventParticipant, ParticipantStatus, EventVisibility, Friendship, FriendshipStatus
from schemas import EventCreate, EventResponse
from security import get_current_user

calendar_router = APIRouter()


def _build_event_dict(event: Event) -> dict:
    return {
        "id": event.id,
        "user_id": event.user_id,
        "title": event.title,
        "description": event.description,
        "location": event.location,
        "latitude": event.latitude,
        "longitude": event.longitude,
        "radius": event.radius,
        "start_time": event.start_time,
        "end_time": event.end_time,
        "visibility": event.visibility.value if hasattr(event.visibility, "value") else event.visibility,
        "participants": [
            {
                "user_id": p.user_id,
                "username": p.user.username,
                "status": p.status.value if hasattr(p.status, "value") else p.status,
                "last_latitude": p.last_latitude,
                "last_longitude": p.last_longitude,
                "is_sharing_location": p.is_sharing_location or False,
                "arrival_time": p.arrival_time,
            }
            for p in event.participants
        ],
    }


@calendar_router.get("/", response_model=List[EventResponse])
def get_events(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    owned = (
        db.query(Event)
        .options(joinedload(Event.participants).joinedload(EventParticipant.user))
        .filter(Event.user_id == current_user.id)
        .all()
    )

    participating_ids = {
        row.event_id
        for row in db.query(EventParticipant.event_id)
        .filter(
            EventParticipant.user_id == current_user.id,
            EventParticipant.status != ParticipantStatus.REJECTED,
            EventParticipant.event_id.notin_([e.id for e in owned]),
        )
        .all()
    }

    invited = []
    if participating_ids:
        invited = (
            db.query(Event)
            .options(joinedload(Event.participants).joinedload(EventParticipant.user))
            .filter(Event.id.in_(participating_ids))
            .all()
        )

    return [_build_event_dict(e) for e in owned + invited]


@calendar_router.post("/", response_model=EventResponse)
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_event = Event(
        user_id=current_user.id,
        title=event.title,
        description=event.description,
        location=event.location,
        latitude=event.latitude,
        longitude=event.longitude,
        radius=event.radius or 50.0,
        start_time=event.start_time,
        end_time=event.end_time,
        visibility=event.visibility or EventVisibility.PUBLIC,
    )
    db.add(new_event)
    db.flush()

    db.add(EventParticipant(
        event_id=new_event.id,
        user_id=current_user.id,
        status=ParticipantStatus.ACCEPTED,
    ))

    if event.invitees:
        for username in event.invitees:
            invitee = db.query(User).filter(User.username == username).first()
            if invitee and invitee.id != current_user.id:
                db.add(EventParticipant(
                    event_id=new_event.id,
                    user_id=invitee.id,
                    status=ParticipantStatus.PENDING,
                ))

    db.commit()

    saved = (
        db.query(Event)
        .options(joinedload(Event.participants).joinedload(EventParticipant.user))
        .filter(Event.id == new_event.id)
        .one()
    )
    return _build_event_dict(saved)


@calendar_router.get("/friends/{username}", response_model=List[EventResponse])
def get_friend_events(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target = db.query(User).filter(User.username == username).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    friendship = db.query(Friendship).filter(
        ((Friendship.user_id_1 == current_user.id) & (Friendship.user_id_2 == target.id)) |
        ((Friendship.user_id_1 == target.id) & (Friendship.user_id_2 == current_user.id)),
        Friendship.status == FriendshipStatus.ACCEPTED,
    ).first()
    is_friend = friendship is not None

    allowed_visibilities = [EventVisibility.PUBLIC]
    if is_friend:
        allowed_visibilities.append(EventVisibility.FRIENDS_ONLY)

    events = (
        db.query(Event)
        .options(joinedload(Event.participants).joinedload(EventParticipant.user))
        .filter(Event.user_id == target.id, Event.visibility.in_(allowed_visibilities))
        .all()
    )
    return [_build_event_dict(e) for e in events]


@calendar_router.get("/{event_id}", response_model=EventResponse)
def get_event_detail(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = (
        db.query(Event)
        .options(joinedload(Event.participants).joinedload(EventParticipant.user))
        .filter(Event.id == event_id)
        .first()
    )
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return _build_event_dict(event)
