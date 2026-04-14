<script setup>
import { ref, onMounted } from 'vue'
import { getMe, uploadProfileImage, updateUsername, updatePassword } from '../api/mypage'
import { useRouter } from 'vue-router'

const router = useRouter()
const user = ref(null)
const newUsername = ref('')
const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const profileFile = ref(null)
const profilePreview = ref('')
const message = ref({ text: '', type: '' }) // type: 'success' | 'error'

const showOldPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

const fetchUser = async () => {
  try {
    user.value = await getMe()
    newUsername.value = user.value.username
    if (user.value.profile_image) {
      profilePreview.value = 'http://localhost:8000' + user.value.profile_image
    }
  } catch (err) {
    console.error("Failed to fetch user info", err)
    if (err.response && err.response.status === 401) {
      router.push('/login')
    } else {
      showMessage('사용자 정보를 불러오는데 실패했습니다. 서버 상태를 확인해주세요.', 'error')
    }
  }
}

onMounted(fetchUser)

const onFileChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    profileFile.value = file
    profilePreview.value = URL.createObjectURL(file)
  }
}

const handleUploadImage = async () => {
  if (!profileFile.value) return
  try {
    const updatedUser = await uploadProfileImage(profileFile.value)
    user.value = updatedUser
    showMessage('프로필 이미지가 변경되었습니다!', 'success')
  } catch (err) {
    showMessage('이미지 업로드 실패', 'error')
  }
}

const handleUpdateUsername = async () => {
  if (newUsername.value === user.value.username) return
  try {
    const updatedUser = await updateUsername(newUsername.value)
    user.value = updatedUser
    showMessage('닉네임이 성공적으로 변경되었습니다!', 'success')
  } catch (err) {
    showMessage(err.response?.data?.detail || '닉네임 변경 실패 (이미 사용 중이거나 오류)', 'error')
  }
}

const handleUpdatePassword = async () => {
  if (!oldPassword.value || !newPassword.value) {
    return showMessage('비밀번호를 입력해주세요.', 'error')
  }
  if (newPassword.value !== confirmPassword.value) {
    return showMessage('새 비밀번호가 일치하지 않습니다.', 'error')
  }
  
  try {
    await updatePassword(oldPassword.value, newPassword.value)
    showMessage('비밀번호가 안전하게 변경되었습니다.', 'success')
    oldPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
  } catch (err) {
    showMessage(err.response?.data?.detail || '비밀번호 변경 실패', 'error')
  }
}

const showMessage = (text, type) => {
  message.value = { text, type }
  setTimeout(() => {
    message.value = { text: '', type: '' }
  }, 3000)
}
</script>

<template>
  <div class="mypage-container" v-if="user">
    <div class="mypage-header">
      <h2 class="title">내 정보 관리</h2>
      <p class="subtitle">개인 정보를 수정하고 프로필을 완성해보세요.</p>
    </div>

    <div class="mypage-grid">
      <!-- Profile Section -->
      <div class="card profile-card">
        <h3 class="section-title">프로필 사진</h3>
        <div class="profile-upload-area">
          <div class="avatar-preview">
            <img v-if="profilePreview" :src="profilePreview" alt="Profile" />
            <div v-else class="avatar-placeholder">{{ user.username.substring(0,1).toUpperCase() }}</div>
          </div>
          <div class="upload-controls">
            <input type="file" ref="fileInput" @change="onFileChange" accept="image/*" hidden />
            <button class="btn btn-outline" @click="$refs.fileInput.click()">사진 선택</button>
            <button class="btn btn-primary" @click="handleUploadImage" :disabled="!profileFile">업로드</button>
          </div>
        </div>
      </div>

      <!-- Info Edit Section -->
      <div class="card info-card">
        <h3 class="section-title">계정 정보</h3>
        
        <div class="form-group">
          <label>닉네임 (아이디)</label>
          <div class="input-row">
            <input type="text" v-model="newUsername" class="form-control" />
            <button class="btn btn-primary" @click="handleUpdateUsername">변경</button>
          </div>
          <small class="help-text">다른 사용자와 중복되지 않는 고유한 이름을 사용하세요.</small>
        </div>

        <div class="divider"></div>

        <h3 class="section-title">비밀번호 변경</h3>
        <div class="form-group">
          <label>현재 비밀번호</label>
          <div class="input-row">
            <input :type="showOldPassword ? 'text' : 'password'" v-model="oldPassword" class="form-control" placeholder="현재 비밀번호 입력" />
            <button class="btn btn-icon" @click="showOldPassword = !showOldPassword">{{ showOldPassword ? '🔓' : '🔒' }}</button>
          </div>
        </div>
        <div class="form-group">
          <label>새 비밀번호</label>
          <div class="input-row">
            <input :type="showNewPassword ? 'text' : 'password'" v-model="newPassword" class="form-control" placeholder="새 비밀번호 입력" />
            <button class="btn btn-icon" @click="showNewPassword = !showNewPassword">{{ showNewPassword ? '🔓' : '🔒' }}</button>
          </div>
        </div>
        <div class="form-group">
          <label>새 비밀번호 확인</label>
          <div class="input-row">
            <input :type="showConfirmPassword ? 'text' : 'password'" v-model="confirmPassword" class="form-control" placeholder="비밀번호 확인" />
            <button class="btn btn-icon" @click="showConfirmPassword = !showConfirmPassword">{{ showConfirmPassword ? '🔓' : '🔒' }}</button>
          </div>
        </div>
        <button class="btn btn-primary w-full" @click="handleUpdatePassword">비밀번호 업데이트</button>
      </div>
    </div>

    <!-- Alert Message -->
    <Transition name="fade">
      <div v-if="message.text" class="alert-msg" :class="message.type">
        {{ message.text }}
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.mypage-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.mypage-header .title {
  font-size: 1.75rem;
  font-weight: 800;
  margin-bottom: 0.25rem;
}

.mypage-header .subtitle {
  color: var(--text-secondary);
}

.mypage-grid {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 1.5rem;
}

@media (max-width: 768px) {
  .mypage-grid {
    grid-template-columns: 1fr;
  }
}

.section-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
}

.profile-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
}

.profile-upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  width: 100%;
}

.avatar-preview {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  overflow: hidden;
  background-color: var(--bg-color);
  border: 4px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  font-size: 3rem;
  font-weight: 700;
  color: var(--primary);
}

.upload-controls {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
}

.info-card {
  padding: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.input-row {
  display: flex;
  gap: 0.5rem;
}

.input-row .form-control {
  flex: 1;
}

.divider {
  height: 1px;
  background-color: var(--border-color);
  margin: 2rem 0;
}

.w-full {
  width: 100%;
  padding: 0.75rem;
}

.alert-msg {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  padding: 1rem 2rem;
  border-radius: var(--radius-md);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  font-weight: 600;
  z-index: 1000;
}

.alert-msg.success { background-color: #d1fae5; color: #065f46; border: 1px solid #6ee7b7; }
.alert-msg.error { background-color: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s, transform 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translate(-50%, 10px); }
</style>
