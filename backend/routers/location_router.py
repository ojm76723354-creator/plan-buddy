from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models
from models import Event, User, EventParticipant, EventChat, ParticipantStatus
import schemas
from security import get_current_user
from datetime import datetime, timezone, timedelta
import math

location_router = APIRouter()

# 1. 참여 상태 변경 (수락/거절)
@location_router.post("/{event_id}/status")
def update_participation_status(
    event_id: int, 
    status_update: schemas.StatusUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    participant = db.query(EventParticipant).filter(
        EventParticipant.event_id == event_id,
        EventParticipant.user_id == current_user.id
    ).first()
    
    if not participant:
        raise HTTPException(status_code=404, detail="Participation record not found")
    
    participant.status = status_update.status
    db.commit()
    return {"message": f"Status updated to {status_update.status}"}

# 2. 실시간 위치 업데이트 및 자동 체크인 확인
@location_router.post("/{event_id}/location")
def update_location(
    event_id: int, 
    location: schemas.LocationUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    participant = db.query(EventParticipant).filter(
        EventParticipant.event_id == event_id,
        EventParticipant.user_id == current_user.id
    ).first()
    
    if not participant:
        raise HTTPException(status_code=403, detail="You are not a participant of this event")

    # 약속 시간 전후로만 공유 가능하도록 설정 (예: 2시간 전 ~ 종료 후 1시간)
    now = datetime.now(timezone.utc)
    # models.py에서 start_time/end_time이 naive datetime이면 timezone.utc 처리가 필요할 수 있음
    # 여기서는 단순 비교를 위해 naive 처리 (db 데이터가 naive라고 가정)
    now_naive = datetime.now() 
    
    # 위치 정보 업데이트
    participant.last_latitude = location.latitude
    participant.last_longitude = location.longitude
    participant.is_sharing_location = True
    participant.updated_at = now_naive

    # 자동 체크인 로직 (장소 좌표가 설정되어 있고 아직 도착 전인 경우)
    if event.latitude and event.longitude and participant.status != ParticipantStatus.ARRIVED:
        # Haversine 공식으로 거리 계산
        R = 6371e3 # 지구 반지름 (m)
        phi1 = math.radians(event.latitude)
        phi2 = math.radians(location.latitude)
        delta_phi = math.radians(location.latitude - event.latitude)
        delta_lambda = math.radians(location.longitude - event.longitude)
        
        a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        if distance <= event.radius:
            participant.status = ParticipantStatus.ARRIVED
            participant.arrival_time = now_naive
            participant.is_sharing_location = False # 도착 후 공유 중단

    db.commit()
    return {"status": participant.status, "distance": distance if 'distance' in locals() else None}

# 3. 참여자들 위치 현황 조회
@location_router.get("/{event_id}/participants", response_model=List[schemas.EventParticipantResponse])
def get_participants_locations(
    event_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    participants = db.query(EventParticipant).filter(EventParticipant.event_id == event_id).all()
    
    results = []
    for p in participants:
        results.append({
            "user_id": p.user_id,
            "username": p.user.username,
            "status": p.status,
            "last_latitude": p.last_latitude if p.is_sharing_location else None,
            "last_longitude": p.last_longitude if p.is_sharing_location else None,
            "is_sharing_location": p.is_sharing_location,
            "arrival_time": p.arrival_time
        })
    return results

# 4. 임시 채팅 메시지 발송
@location_router.post("/{event_id}/chat", response_model=schemas.EventChatResponse)
def send_chat_message(
    event_id: int, 
    chat: schemas.EventChatCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # 참여 여부 확인
    participant = db.query(EventParticipant).filter(
        EventParticipant.event_id == event_id,
        EventParticipant.user_id == current_user.id
    ).first()
    
    if not participant:
        raise HTTPException(status_code=403, detail="Not a participant")

    new_msg = models.EventChat(
        event_id=event_id,
        user_id=current_user.id,
        message=chat.message
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    
    return {
        "id": new_msg.id,
        "user_id": new_msg.user_id,
        "username": current_user.username,
        "message": new_msg.message,
        "created_at": new_msg.created_at
    }

# 5. 채팅 내역 조회
@location_router.get("/{event_id}/chat", response_model=List[schemas.EventChatResponse])
def get_chat_messages(
    event_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    msgs = db.query(models.EventChat).filter(models.EventChat.event_id == event_id).order_by(models.EventChat.created_at.asc()).all()
    results = []
    for m in msgs:
        results.append({
            "id": m.id,
            "user_id": m.user_id,
            "username": m.user.username,
            "message": m.message,
            "created_at": m.created_at
        })
    return results

# 6. 유저 도착 통계 조회
@location_router.get("/stats/{username}")
def get_user_arrival_stats(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    participations = db.query(EventParticipant).filter(
        EventParticipant.user_id == user.id,
        EventParticipant.status == ParticipantStatus.ARRIVED
    ).all()
    
    total_arrived = len(participations)
    on_time_count = 0
    
    for p in participations:
        event = p.event
        if p.arrival_time and p.arrival_time <= event.start_time:
            on_time_count += 1
            
    return {
        "username": username,
        "total_arrivals": total_arrived,
        "on_time_arrivals": on_time_count,
        "punctuality_rate": (on_time_count / total_arrived * 100) if total_arrived > 0 else 0
    }
