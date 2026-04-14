from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
import shutil
import uuid
import os
from database import get_db
from models import User
from schemas import UserResponse, NicknameUpdate, PasswordUpdate
from security import get_current_user, get_password_hash, verify_password

mypage_router = APIRouter()

@mypage_router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@mypage_router.post("/upload-profile", response_model=UserResponse)
def upload_profile(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    os.makedirs("static/profiles", exist_ok=True)
    
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = f"static/profiles/{filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    current_user.profile_image = f"/static/profiles/{filename}"
    db.commit()
    db.refresh(current_user)
    return current_user

@mypage_router.put("/update-username", response_model=UserResponse)
def update_username(
    req: NicknameUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    existing = db.query(User).filter(User.username == req.new_username).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 사용 중인 닉네임입니다.")
    
    current_user.username = req.new_username
    db.commit()
    db.refresh(current_user)
    return current_user

@mypage_router.put("/update-password")
def update_password(
    req: PasswordUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if not verify_password(req.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="현재 비밀번호가 일치하지 않습니다.")
    
    current_user.hashed_password = get_password_hash(req.new_password)
    db.commit()
    return {"message": "비밀번호가 성공적으로 변경되었습니다."}
