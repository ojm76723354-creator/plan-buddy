# 🌐 Plan Buddy 실전 클라우드 배포 가이드

이 가이드는 로컬 개발 환경에서 만든 프로젝트를 인터넷 세상에 공개하는 단계별 매뉴얼입니다.

---

## 🏗️ 0단계: GitHub에 코드 올리기
클라우드 서비스(Render, Vercel)는 내 컴퓨터의 파일이 아닌, GitHub 저장소의 코드를 읽어서 배포합니다.

1.  GitHub에 접속하여 새 저장소(New Repository)를 만듭니다. (이름 예시: `plan-buddy`)
2.  프로젝트 루트 폴더(`fastapi-vue-board`)에서 코드를 업로드합니다.
    - 터미널이나 GitHub Desktop을 사용하여 Push 합니다.
    - **주의**: `.env` 파일은 보안상 올리지 않도록 주의하세요 (이미 `.gitignore`에 설정되어 있을 것입니다).

---

## 🐍 1단계: Backend 배포 (Render.com)
FastAPI 서버를 배포하는 단계입니다.

1.  [Render.com](https://render.com)에 로그인하고 **[New]** -> **[Web Service]**를 클릭합니다.
2.  사용자님의 GitHub 저장소를 연결합니다.
3.  **Build Command**: `uv pip install -r requirements.txt` (또는 `pip install -r requirements.txt`)
4.  **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5.  **Environment Variables (가장 중요!)**: [Environment] 탭에서 아래 내용을 추가합니다.
    - `SECRET_KEY`: 아주 복잡한 아무 문자열 (예: `your-super-secret-1234`)
    - `DATABASE_URL`: `sqlite:///./sql_app.db` (초기 단계용) 또는 Render의 정식 PostgreSQL 주소
    - `FRONTEND_URL`: (Vercel 배포 후 나오는 주소를 나중에 입력)
6.  **배포 완료**: 잠시 기다리면 `https://...onrender.com` 형태의 주소가 발급됩니다.

---

## ⚡ 2단계: Frontend 배포 (Vercel.com)
Vue.js 화면을 배포하는 단계입니다.

1.  [Vercel.com](https://vercel.com)에 로그인하고 **[Add New]** -> **[Project]**를 클릭합니다.
2.  GitHub 저장소를 선택하여 불러옵니다.
3.  **Framework Preset**: Vite가 자동으로 감지될 것입니다.
4.  **Root Directory**: `frontend` 폴더를 선택해야 합니다. (중요!)
5.  **Environment Variables**:
    - `VITE_API_BASE_URL`: **1단계에서 발급받은 Render 주소**를 입력합니다. (예: `https://my-api.onrender.com`)
6.  **Deploy**: 버튼을 누르고 1~2분 기다리면 사용자만의 웹 주소가 발급됩니다!

---

## ✅ 3단계: 마무리 (주소 연결)
이제 프론트엔드 주소가 생겼으니, 백엔드에게 "이 주소에서 오는 요청은 믿어도 돼"라고 알려줘야 합니다.

1.  Render 대시보드로 다시 가서 `FRONTEND_URL` 환경 변수에 **Vercel 주소**를 입력하고 다시 저장(Save Changes)합니다.

---

### 🚨 문제가 생겼나요?
- **화면이 안 떠요**: 브라우저 개발자 도구(F12)의 'Network' 탭을 확인해 보세요. `VITE_API_BASE_URL`이 잘 설정되었는지 확인이 필요합니다.
- **이미지가 안 보여요**: 무료 티어에서는 서버가 재시작되면 저장된 이미지가 사라집니다. (이는 나중에 클라우드 전용 저장소를 써서 해결할 수 있습니다.)

언제든 에러 메시지를 복사해서 저에게 알려주세요! 끝까지 도와드리겠습니다. 😊
