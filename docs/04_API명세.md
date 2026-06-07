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
  "latitude": 37.5665,
  "longitude": 126.9780,
  "radius": 50,
  "start_time": "2026-05-12T10:00:00",
  "end_time": "2026-05-12T12:00:00",
  "visibility": "PUBLIC",
  "invitees": ["friend1", "friend2"]
}
```

**`visibility` 값**: `PUBLIC` | `FRIENDS_ONLY` | `PRIVATE`

---

## 3. 위치 및 실시간 API (`/location`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `POST` | `/location/{event_id}/status` | 참여 상태 변경 (수락/거절) |
| `POST` | `/location/{event_id}/location` | 내 위치 업데이트 및 자동 체크인 확인 |
| `GET` | `/location/{event_id}/participants`| 참여자 실시간 위치 목록 조회 |
| `POST` | `/location/{event_id}/chat` | 임시 채팅 메시지 발송 |
| `GET` | `/location/{event_id}/chat` | 임시 채팅 내역 조회 |
| `GET` | `/location/stats/{username}` | 유저 정시 도착 통계 조회 |

---

## 4. 장소 검색 API (`/places`)

> ⚠️ 인증 필요. 백엔드에 `NAVER_CLIENT_ID` / `NAVER_CLIENT_SECRET` 환경 변수 설정 필요.

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `GET` | `/places/search` | 키워드로 장소 검색 (Naver Local Search API 프록시) |

### GET /places/search — 장소 검색

**Query Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `q` | string | ✅ | 검색 키워드 (예: "스타벅스 강남", "도서관") |

**Response** `200 OK`
```json
{
  "items": [
    {
      "title": "스타벅스 강남역점",
      "category": "카페,음료,스타벅스",
      "address": "서울특별시 강남구 강남대로 390",
      "roadAddress": "서울특별시 강남구 강남대로 390",
      "lat": 37.4979,
      "lng": 127.0276
    }
  ]
}
```

**Error Responses**
| 코드 | 설명 |
|------|------|
| `503` | 서버에 Naver API 자격증명이 설정되지 않은 경우 |
| `502` | Naver API 호출 오류 |
| `504` | Naver API 응답 시간 초과 |

> **설정 방법**: `backend/.env` 파일에 `NAVER_CLIENT_ID`와 `NAVER_CLIENT_SECRET`을 추가하세요.  
> Naver Open API 자격증명은 [https://developers.naver.com/apps/](https://developers.naver.com/apps/) 에서 앱 등록 후 "검색" API를 활성화하면 발급됩니다.

---

## 5. 친구 API (`/friends`)

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
