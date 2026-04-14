# 📅 Campus Calendar — 프론트엔드

Vue 3 기반의 협업 캘린더 서비스 프론트엔드입니다.  
월별/주별 캘린더 뷰, 다크 모드, 친구 관리 기능을 제공합니다.

---

## 🛠 기술 스택

| 항목 | 내용 |
|------|------|
| 프레임워크 | Vue 3 (Composition API) |
| 빌드 도구 | Vite 7 |
| 상태 관리 | Pinia |
| 라우터 | Vue Router 5 |
| HTTP 클라이언트 | Axios |
| 캘린더 컴포넌트 | Vue-Cal |
| 아이콘 | Lucide Vue Next |
| 날짜 처리 | date-fns |

---

## 📁 프로젝트 구조

```
frontend/
├── index.html                  # HTML 진입점
├── vite.config.js              # Vite 설정 (@/ 경로 별칭 포함)
├── package.json                # 의존성 및 스크립트
└── src/
    ├── main.js                 # 앱 마운트 (Vue + Pinia + Router)
    ├── App.vue                 # 최상위 레이아웃 (네비게이션 바, 사이드바)
    ├── assets/
    │   └── main.css            # 전역 스타일 (CSS 변수, 다크 모드 토큰)
    ├── router/
    │   └── index.js            # 라우트 정의 (/, /login)
    ├── api/
    │   ├── auth.js             # 로그인 / 회원가입 / 로그아웃 API
    │   ├── calendar.js         # 이벤트 CRUD API
    │   ├── friends.js          # 친구 요청 / 목록 API
    │   └── post.js             # 게시물 관련 API
    ├── stores/
    │   └── counter.js          # Pinia 스토어
    ├── components/
    │   ├── EventModal.vue      # 이벤트 생성/상세 모달
    │   ├── FriendManagerModal.vue  # 친구 관리 모달
    │   └── ProfileCard.vue     # 프로필 카드 컴포넌트
    └── views/
        ├── CalendarView.vue    # 메인 캘린더 화면 (월별/주별 뷰)
        └── LoginView.vue       # 로그인 / 회원가입 화면
```

---

## ⚙️ 시작하기

### 1. 사전 요구사항

- Node.js `^20.19.0` 또는 `>=22.12.0`
- npm

### 2. 의존성 설치

```bash
cd frontend
npm install
```

### 3. 개발 서버 실행

```bash
npm run dev
```

| 항목 | URL |
|------|-----|
| 프론트엔드 | http://localhost:5173 |
| 백엔드 API | http://localhost:8000 |

> 백엔드 서버가 먼저 실행 중이어야 정상적으로 동작합니다.

---

## 📜 스크립트

| 명령어 | 설명 |
|--------|------|
| `npm run dev` | 개발 서버 시작 (HMR 포함) |
| `npm run build` | 프로덕션 빌드 (`dist/` 생성) |
| `npm run preview` | 빌드 결과물 로컬 미리보기 |

---

## 📄 주요 화면

### `/` — 캘린더 뷰 (CalendarView.vue)
- Vue-Cal 컴포넌트를 이용한 **월별 / 주별 캘린더** 표시
- 로그인한 사용자의 이벤트 목록 렌더링
- 날짜 클릭 → **이벤트 생성 모달** (EventModal) 팝업
- 이벤트 클릭 → **이벤트 상세 / 삭제** 기능

### `/login` — 로그인 / 회원가입 (LoginView.vue)
- 탭 전환으로 **로그인 / 회원가입** 전환
- 성공 시 JWT를 `localStorage`에 저장하고 캘린더로 이동

---

## 🧩 주요 컴포넌트

### `App.vue` — 전역 레이아웃
- **상단 네비게이션 바**: 로고, 다크 모드 토글, 친구 관리, 로그인/로그아웃 버튼
- **사이드바**: 일정 필터 (내 일정 / 친구 일정)
- 라우트 변경 시 로그인 상태 자동 갱신

### `EventModal.vue` — 이벤트 모달
- 이벤트 제목, 설명, 장소, 시작/종료 시각, 공개 범위 입력
- 이벤트 생성 및 삭제 지원

### `FriendManagerModal.vue` — 친구 관리 모달
- 사용자명으로 친구 요청 전송
- 친구 목록 조회 및 상태(`대기 중` / `수락됨`) 표시

---

## 🔐 인증 흐름

```
사용자 로그인
    ↓
POST /login → JWT 토큰 수신
    ↓
localStorage에 토큰 저장
    ↓
axios 인터셉터가 모든 요청에 Authorization 헤더 자동 첨부
    ↓
로그아웃 시 localStorage에서 토큰 삭제
```

---

## 🎨 다크 모드

- `App.vue`의 토글 버튼으로 제어
- `document.documentElement`에 `data-theme="dark"` 속성을 설정/해제
- `main.css`의 CSS 변수(`--bg-primary`, `--text-primary` 등)로 테마 전환

---

## 🔧 API 연동 (`src/api/`)

| 파일 | 제공 함수 |
|------|-----------|
| `auth.js` | `login()`, `register()`, `logout()`, `isLoggedIn()`, `getToken()` |
| `calendar.js` | 이벤트 목록 조회, 이벤트 생성 |
| `friends.js` | 친구 요청 전송, 친구 목록 조회 |

모든 API 요청은 `axios` 인스턴스(`baseURL: http://localhost:8000`)를 공유하며,  
요청 인터셉터에서 JWT 토큰을 자동으로 헤더에 추가합니다.

---

## 📦 주요 의존성

| 패키지 | 버전 | 용도 |
|--------|------|------|
| vue | ^3.5.29 | 프론트엔드 프레임워크 |
| vue-router | ^5.0.3 | 클라이언트 라우팅 |
| pinia | ^3.0.4 | 상태 관리 |
| axios | ^1.14.0 | HTTP 클라이언트 |
| vue-cal | ^4.10.2 | 캘린더 UI 컴포넌트 |
| date-fns | ^4.1.0 | 날짜 변환 및 포맷 |
| lucide-vue-next | ^1.0.0 | 아이콘 |
| vite | ^7.3.1 | 빌드 도구 |
