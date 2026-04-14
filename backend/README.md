# 📅 Campus Calendar — 백엔드

FastAPI 기반의 협업 캘린더 서비스 백엔드입니다.  
JWT 인증, 이벤트 관리, 친구 시스템을 제공합니다.

---

## 🛠 기술 스택

| 항목 | 내용 |
|------|------|
| 언어 | Python 3.14+ |
| 프레임워크 | FastAPI 0.135+ |
| ORM | SQLAlchemy 2.0 |
| 데이터베이스 | SQLite (개발) / PostgreSQL (운영) |
| 인증 | JWT (PyJWT + bcrypt) |
| 패키지 매니저 | uv |
| 서버 | Uvicorn |

---

## 📁 프로젝트 구조

```
backend/
├── main.py              # 앱 진입점, 미들웨어 및 라우터 등록
├── database.py          # DB 엔진 및 세션 설정
├── models.py            # SQLAlchemy ORM 모델 (User, Event, Friendship)
├── schemas.py           # Pydantic 요청/응답 스키마
├── security.py          # JWT 생성/검증, 비밀번호 해시, 현재 사용자 의존성
├── pyproject.toml       # 프로젝트 메타데이터 및 의존성
└── routers/
    ├── __init__.py
    ├── auth_router.py       # 회원가입 / 로그인
    ├── calendar_router.py   # 이벤트 CRUD
    ├── friend_router.py     # 친구 요청 / 목록 조회
    └── mypage_router.py     # 마이페이지
```

---

## ⚙️ 시작하기

### 1. 사전 요구사항

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) 설치

```bash
# uv 설치 (없는 경우)
pip install uv
```

### 2. 의존성 설치

```bash
cd backend
uv sync
```

### 3. 개발 서버 실행

```bash
uv run uvicorn main:app --reload
```

서버가 실행되면 아래 주소에서 접근 가능합니다.

| 항목 | URL |
|------|-----|
| API 서버 | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

---

## 🗄️ 데이터베이스 설정

기본값은 SQLite(`sql_app.db`)를 사용합니다.  
PostgreSQL 등으로 변경하려면 `.env` 파일을 생성하세요.

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/campus_calendar
```

서버 시작 시 `Base.metadata.create_all()` 로 테이블이 **자동 생성**됩니다.

---

## 🗂️ 데이터 모델

### User (사용자)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | Integer (PK) | 기본키 |
| username | String (unique) | 사용자 이름 |
| email | String (unique) | 이메일 |
| hashed_password | String | bcrypt 해시된 비밀번호 |
| created_at | DateTime | 생성 일시 (UTC) |

### Event (이벤트)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | Integer (PK) | 기본키 |
| user_id | Integer (FK) | 소유자 (User.id) |
| title | String | 제목 |
| description | String (nullable) | 상세 설명 |
| location | String (nullable) | 장소 |
| start_time | DateTime | 시작 시각 |
| end_time | DateTime | 종료 시각 |
| visibility | Enum | 공개 범위 (`PUBLIC` / `FRIENDS_ONLY` / `PRIVATE`) |

### Friendship (친구 관계)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | Integer (PK) | 기본키 |
| user_id_1 | Integer (FK) | 요청자 |
| user_id_2 | Integer (FK) | 수신자 |
| status | Enum | 상태 (`PENDING` / `ACCEPTED`) |

---

## 🔌 API 엔드포인트

### 인증 (`/`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `POST` | `/register` | 회원가입 |
| `POST` | `/login` | 로그인 (JWT 발급) |

### 캘린더 (`/calendar`)

> ⚠️ 모든 캘린더 API는 `Authorization: Bearer <token>` 헤더가 필요합니다.

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `GET` | `/calendar/` | 내 이벤트 목록 조회 |
| `POST` | `/calendar/` | 이벤트 생성 |

### 친구 (`/friends`)

> ⚠️ 인증 필요

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `POST` | `/friends/request` | 친구 요청 보내기 |
| `GET` | `/friends/list` | 친구 목록 및 상태 조회 |

---

## 🔐 인증 방식

- **JWT Bearer Token** 방식 사용
- 토큰 유효 기간: **7일**
- 알고리즘: `HS256`
- 비밀번호는 **bcrypt**로 해시 저장

> 운영 환경에서는 반드시 `SECRET_KEY`를 환경 변수로 분리하세요.

---

## 🌍 CORS 설정

현재 개발 편의상 모든 오리진(`*`)을 허용하고 있습니다.  
운영 환경에서는 `allow_origins`를 프론트엔드 도메인으로 제한하세요.

```python
# main.py
allow_origins=["https://your-domain.com"]
```

---

## 📦 주요 의존성

| 패키지 | 버전 | 용도 |
|--------|------|------|
| fastapi | ≥0.135.1 | 웹 프레임워크 |
| uvicorn | ≥0.41.0 | ASGI 서버 |
| sqlalchemy | ≥2.0.49 | ORM |
| pyjwt | ≥2.12.1 | JWT 처리 |
| bcrypt | ≥5.0.0 | 비밀번호 해시 |
| python-dotenv | ≥1.2.2 | 환경 변수 로드 |
| psycopg2-binary | ≥2.9.11 | PostgreSQL 드라이버 |
| email-validator | ≥2.3.0 | 이메일 유효성 검사 |
