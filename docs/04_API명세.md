# API 명세

> ⚠️ **인증이 필요한 API**는 모두 `Authorization: Bearer <token>` 헤더가 필요합니다.

---

## Base URL

| 환경 | Base URL |
|------|----------|
| 개발 | `http://localhost:8000` |
| Swagger UI | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |

---

## 1. 인증 API (`/`)

| 메서드 | 경로 | 인증 | 설명 |
|--------|------|------|------|
| `POST` | `/register` | ❌ | 회원가입 |
| `POST` | `/login` | ❌ | 로그인 (JWT 발급) |

### POST /register — 회원가입

**Request Body**
```json
{
  "username": "홍길동",
  "email": "hong@example.com",
  "password": "securepassword"
}
```

**Response** `200 OK`
```json
{
  "id": 1,
  "username": "홍길동",
  "email": "hong@example.com"
}
```

### POST /login — 로그인

**Request Body**
```json
{
  "email": "hong@example.com",
  "password": "securepassword"
}
```

**Response** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## 2. 캘린더 API (`/calendar`)

> ⚠️ 모든 캘린더 API는 인증 필요

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `GET` | `/calendar/` | 내 이벤트 목록 조회 |
| `POST` | `/calendar/` | 이벤트 생성 |

### GET /calendar/ — 이벤트 목록 조회

**Response** `200 OK`
```json
[
  {
    "id": 1,
    "title": "스터디 모임",
    "description": "알고리즘 스터디",
    "location": "도서관",
    "start_time": "2026-05-12T10:00:00",
    "end_time": "2026-05-12T12:00:00",
    "visibility": "PUBLIC"
  }
]
```

### POST /calendar/ — 이벤트 생성

**Request Body**
```json
{
  "title": "스터디 모임",
  "description": "알고리즘 스터디",
  "location": "도서관",
  "start_time": "2026-05-12T10:00:00",
  "end_time": "2026-05-12T12:00:00",
  "visibility": "PUBLIC"
}
```

**`visibility` 값**: `PUBLIC` | `FRIENDS_ONLY` | `PRIVATE`

---

## 3. 친구 API (`/friends`)

> ⚠️ 모든 친구 API는 인증 필요

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `POST` | `/friends/request` | 친구 요청 보내기 |
| `GET` | `/friends/list` | 친구 목록 및 상태 조회 |

### POST /friends/request — 친구 요청

**Request Body**
```json
{
  "username": "상대방_아이디"
}
```

### GET /friends/list — 친구 목록 조회

**Response** `200 OK`
```json
[
  {
    "id": 1,
    "friend_username": "친구이름",
    "status": "ACCEPTED"
  },
  {
    "id": 2,
    "friend_username": "다른친구",
    "status": "PENDING"
  }
]
```

**`status` 값**: `PENDING` (대기 중) | `ACCEPTED` (수락됨)

---

## 인증 방식 요약

- **방식**: JWT Bearer Token
- **토큰 유효 기간**: 7일
- **알고리즘**: HS256
- **헤더 형식**: `Authorization: Bearer <access_token>`
