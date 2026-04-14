from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
import os

# 1. DB 및 모델 불러오기 (테이블 자동 생성)
from database import engine, Base
from models import * # models/__init__.py 덕분에 모두 불러옵니다.

Base.metadata.create_all(bind=engine)

# 2. 라우터 불러오기
from routers import auth_router, calendar_router, mypage_router

app = FastAPI()

# 3. CORS 설정 (배포 주소 허용)
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:5173"], # 로컬과 배포 주소 모두 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for profile images
UPLOAD_DIR = "static/profiles"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 4. 세션 설정 (자바의 HttpSession 역할)
app.add_middleware(SessionMiddleware, secret_key="my_secret_key")

# 5. 프로필 폴더 자동 생성 (기존 경로 유지하되 내부 경로 우대)
# os.makedirs("C:/loginproject_stable/profile/", exist_ok=True)

# 6. 라우터 등록
app.include_router(auth_router, tags=["Auth"])
app.include_router(calendar_router, prefix="/calendar", tags=["Calendar"])
app.include_router(mypage_router, prefix="/mypage", tags=["MyPage"])

from routers.friend_router import friend_router
app.include_router(friend_router, prefix="/friends", tags=["Friends"])

@app.get("/")
def home():
    return {"message": "서버가 정상적으로 실행 중입니다!"}