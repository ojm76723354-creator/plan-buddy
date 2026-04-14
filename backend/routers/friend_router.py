from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Friendship, User, FriendshipStatus
from schemas import FriendRequest, FriendshipResponse, UserResponse
from security import get_current_user

friend_router = APIRouter()

@friend_router.post("/request", response_model=FriendshipResponse)
def send_friend_request(req: FriendRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    target_user = db.query(User).filter(User.username == req.target_username).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    if target_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send friend request to yourself")
    
    # Check existing
    existing = db.query(Friendship).filter(
        ((Friendship.user_id_1 == current_user.id) & (Friendship.user_id_2 == target_user.id)) |
        ((Friendship.user_id_1 == target_user.id) & (Friendship.user_id_2 == current_user.id))
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Friendship already exists or pending")
        
    new_friendship = Friendship(
        user_id_1=current_user.id,
        user_id_2=target_user.id,
        status=FriendshipStatus.PENDING
    )
    db.add(new_friendship)
    db.commit()
    db.refresh(new_friendship)
    return new_friendship

@friend_router.get("/list", response_model=List[dict])
def get_friends(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Returns a list of friends with their statuses and usernames
    friendships = db.query(Friendship).filter(
        (Friendship.user_id_1 == current_user.id) | (Friendship.user_id_2 == current_user.id)
    ).all()
    
    result = []
    for f in friendships:
        friend_id = f.user_id_2 if f.user_id_1 == current_user.id else f.user_id_1
        friend_user = db.query(User).filter(User.id == friend_id).first()
        if friend_user:
            result.append({
                "id": f.id,
                "friend_username": friend_user.username,
                "status": f.status.value,
                "is_sender": f.user_id_1 == current_user.id,
                "profile_image": friend_user.profile_image # 프로필 이미지 필드 추가
            })
    return result

@friend_router.post("/{friendship_id}/accept", response_model=FriendshipResponse)
def accept_friend_request(friendship_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    friendship = db.query(Friendship).filter(Friendship.id == friendship_id).first()
    if not friendship:
        raise HTTPException(status_code=404, detail="Friendship request not found")
    
    if friendship.user_id_2 != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to accept this request")
    
    if friendship.status != FriendshipStatus.PENDING:
        raise HTTPException(status_code=400, detail="Friendship is already accepted or not in pending status")
    
    friendship.status = FriendshipStatus.ACCEPTED
    db.commit()
    db.refresh(friendship)
    return friendship
