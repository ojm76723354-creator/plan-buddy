# API 명세

> ⚠️ **인증이 필요한 API**는 모두 `Authorization: Bearer <token>` 헤더가 필요합니다.

---

## Base URL

| 환경 | Base URL |
|------|----------|
| 개발 | `http://localhost:8000` |
| 운영 | `https://plan-buddy-zlpu.onrender.com` |
| Swagger UI | `http://localhost:8000/docs` |

---

## 1. 인증 API

| 메서드 | 경로 | 인증 | 설명 |
|--------|------|------|------|
| `POST` | `/register` | ❌ | 회원가입 |
| `POST` | `/login` | ❌ | 로그인 (JWT 발급) |

### POST /register
```json
// Request
{ "username": "홍길동", "email": "hong@example.com", "password": "securepassword" }

// Response 200
{ "id": 1, "username": "홍길동", "email": "hong@example.com" }
```

### POST /login
```json
// Request
{ "username": "홍길동", "password": "securepassword" }

// Response 200
{ "access_token": "eyJhbGci...", "token_type": "bearer" }
```

---

## 2. 캘린더 API (`/calendar`)

> ⚠️ 모든 캘린더 API는 인증 필요

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `GET` | `/calendar/` | 내 이벤트 목록 조회 (초대받은 일정 포함) |
| `POST` | `/calendar/` | 이벤트 생성 |
| `GET` | `/calendar/friends/{username}` | 친구의 이벤트 목록 조회 (공개 범위 필터 적용) |
| `GET` | `/calendar/{event_id}` | 특정 이벤트 상세 조회 |

### GET /calendar/ — 내 이벤트 목록
내가 만든 이벤트와 초대받아 PENDING/ACCEPTED 상태인 이벤트를 합쳐서 반환합니다.

**Response** `200 OK`
```json
[
  {
    "id": 1,
    "user_id": 3,
    "title": "GPS 약속 - 강남역 만남",
    "description": "같이 점심 먹자!",
    "location": "강남역 2번 출구",
    "latitude": 37.4981,
    "longitude": 127.0276,
    "radius": 80.0,
    "start_time": "2026-06-20T12:00:00",
    "end_time": "2026-06-20T13:00:00",
    "visibility": "FRIENDS_ONLY",
    "participants": [
      { "user_id": 3, "username": "testuser_a", "status": "ACCEPTED", "arrival_time": null, "is_sharing_location": false }
    ]
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
  "start_time": "2026-06-15T10:00:00",
  "end_time": "2026-06-15T12:00:00",
  "visibility": "PUBLIC",
  "invitees": ["friend_username"]
}
```

- `latitude`, `longitude`, `radius`, `invitees` 는 GPS 약속 사용 시에만 필요 (선택)
- `visibility` 값: `PUBLIC` | `FRIENDS_ONLY` | `PRIVATE`

### GET /calendar/friends/{username} — 친구 캘린더 조회
공개 범위 필터:
- 친구 관계인 경우: `PUBLIC` + `FRIENDS_ONLY` 이벤트 반환
- 친구 관계가 아닌 경우: `PUBLIC` 이벤트만 반환
- `PRIVATE` 이벤트는 항상 제외

---

## 3. 위치 및 실시간 API (`/location`)

| 메서드 | 경로 | 인증 | 설명 |
|--------|------|------|------|
| `POST` | `/location/{event_id}/status` | ✅ | 참여 상태 변경 (수락/거절) |
| `POST` | `/location/{event_id}/location` | ✅ | 내 위치 업데이트 + 자동 체크인 |
| `GET` | `/location/{event_id}/participants` | ✅ | 참여자 실시간 위치 목록 |
| `POST` | `/location/{event_id}/chat` | ✅ | 채팅 메시지 전송 |
| `GET` | `/location/{event_id}/chat` | ✅ | 채팅 내역 조회 |
| `GET` | `/location/stats/{username}` | ❌ | 유저 도착 통계 조회 |

### POST /location/{event_id}/location — 위치 업데이트

**Request Body**
```json
{ "latitude": 37.4981, "longitude": 127.0276 }
```

**Response** `200 OK`
```json
{ "status": "ARRIVED", "distance": 0.0 }
```

약속 장소 반경 이내 진입 시 `status`가 자동으로 `ARRIVED`로 변경되고 `arrival_time`이 기록됩니다.

### GET /location/stats/{username} — 도착 통계

**Response** `200 OK`
```json
{
  "username": "testuser_a",
  "total_arrivals": 5,
  "on_time_arrivals": 4,
  "punctuality_rate": 80.0
}
```

정시 기준: `arrival_time ≤ event.start_time`

### POST /location/{event_id}/chat — 채팅 전송

**Request Body**
```json
{ "message": "나 거의 다 왔어!" }
```

**Response** `200 OK`
```json
{
  "id": 1,
  "user_id": 3,
  "username": "testuser_a",
  "message": "나 거의 다 왔어!",
  "created_at": "2026-06-08T18:53:00"
}
```

---

## 4. 장소 검색 API (`/places`)

> 백엔드에 `NAVER_CLIENT_ID` / `NAVER_CLIENT_SECRET` 환경 변수가 없으면 503을 반환합니다.  
> 현재 프론트엔드는 이 엔드포인트 대신 **OpenStreetMap Nominatim API**를 직접 호출하여 인증 없이 장소 검색을 수행합니다.

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `GET` | `/places/search?q=검색어` | Naver Local Search API 프록시 |

**Response** `200 OK`
```json
{
  "items": [
    { "title": "강남역", "category": "지하철역", "address": "서울 강남구 강남대로", "lat": 37.4981, "lng": 127.0276 }
  ]
}
```

---

## 5. 친구 API (`/friends`)

| 메서드 | 경로 | 인증 | 설명 |
|--------|------|------|------|
| `POST` | `/friends/request` | ✅ | 친구 요청 보내기 |
| `GET` | `/friends/list` | ✅ | 친구 목록 및 상태 조회 (PENDING 포함) |
| `POST` | `/friends/{friendship_id}/accept` | ✅ | 친구 요청 수락 |
| `GET` | `/friends/pending-count` | ✅ | 미수락 요청 건수 조회 |

### POST /friends/request
```json
// Request
{ "target_username": "상대방_아이디" }
```

### GET /friends/list
```json
// Response 200
[
  { "id": 2, "friend_username": "testuser_b", "status": "ACCEPTED", "is_sender": true, "profile_image": null }
]
```
- `status`: `PENDING` (대기 중) | `ACCEPTED` (수락됨)
- `is_sender`: 내가 요청을 보낸 쪽이면 `true`

### POST /friends/{friendship_id}/accept
친구 요청을 받은 사람(is_sender=false)만 호출 가능합니다. Request body 불필요.

### GET /friends/pending-count
```json
{ "count": 2 }
```

---

## 6. 마이페이지 API (`/mypage`)

| 메서드 | 경로 | 인증 | 설명 |
|--------|------|------|------|
| `GET` | `/mypage/me` | ✅ | 내 프로필 조회 |
| `POST` | `/mypage/update-username` | ✅ | 닉네임 변경 |
| `POST` | `/mypage/update-password` | ✅ | 비밀번호 변경 |
| `POST` | `/mypage/upload-profile-image` | ✅ | 프로필 사진 업로드 |

---

## 인증 방식 요약

- **방식**: JWT Bearer Token
- **토큰 유효 기간**: 7일
- **알고리즘**: HS256
- **헤더 형식**: `Authorization: Bearer <access_token>`
- **저장 위치**: `localStorage` (`token` 키 = JWT, `username` 키 = 로그인한 사용자명)
