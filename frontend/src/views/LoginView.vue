<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login, register as registerApi } from '../api/auth'

const router = useRouter()

const isLoginMode = ref(true)
const username = ref('')
const email = ref('')
const password = ref('')
const errorMsg = ref('')

const toggleMode = () => {
  isLoginMode.value = !isLoginMode.value
  errorMsg.value = ''
  username.value = ''
  email.value = ''
  password.value = ''
}

const handleSubmit = async () => {
  errorMsg.value = ''
  try {
    if (isLoginMode.value) {
      await login(username.value, password.value)
      // Navigate normally - App.vue will pick up the token from localStorage
      router.push('/')
    } else {
      await registerApi(username.value, email.value, password.value)
      isLoginMode.value = true
      errorMsg.value = ''
      username.value = ''
      email.value = ''
      password.value = ''
      alert('회원가입이 완료되었습니다. 로그인해주세요!')
    }
  } catch (err) {
    if (err.response?.data?.detail) {
      errorMsg.value = err.response.data.detail
    } else {
      errorMsg.value = '오류가 발생했습니다. 다시 시도해주세요.'
    }
  }
}
</script>

<template>
  <div class="login-wrapper">
    <div class="login-card card">
      <div class="logo-area">
        <h1>{{ isLoginMode ? '환영합니다! 👋' : '새로운 시작! 🚀' }}</h1>
        <p class="subtitle">{{ isLoginMode ? 'Campus Calendar에 로그인하세요' : '친구들과 일정을 공유해보세요' }}</p>
      </div>

      <form @submit.prevent="handleSubmit" class="login-form">
        <div class="form-group">
          <label>사용자 이름 (아이디)</label>
          <input type="text" v-model="username" class="form-control" required placeholder="아이디를 입력하세요"/>
        </div>

        <div class="form-group" v-if="!isLoginMode">
          <label>이메일</label>
          <input type="email" v-model="email" class="form-control" placeholder="example@univ.edu" required/>
        </div>

        <div class="form-group">
          <label>비밀번호</label>
          <input type="password" v-model="password" class="form-control" required placeholder="비밀번호를 입력하세요"/>
        </div>

        <div v-if="errorMsg" class="error-message">
          {{ errorMsg }}
        </div>

        <button type="submit" class="btn btn-primary submit-btn">
          {{ isLoginMode ? '로그인' : '회원가입' }}
        </button>
      </form>

      <div class="toggle-mode">
        <p>
          {{ isLoginMode ? '계정이 없으신가요?' : '이미 계정이 있으신가요?' }}
          <a href="#" @click.prevent="toggleMode" class="toggle-link">
            {{ isLoginMode ? '회원가입' : '로그인' }}
          </a>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 120px);
  width: 100%;
}

.login-card {
  width: 100%;
  max-width: 420px;
  padding: 2.5rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  animation: fade-in 0.4s ease-out;
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.logo-area h1 {
  font-size: 1.75rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.form-control {
  padding: 0.85rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background-color: var(--bg-color);
  color: var(--text-primary);
  font-family: inherit;
  font-size: 0.95rem;
  transition: all 0.2s;
}

.form-control:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-light);
}

.submit-btn {
  margin-top: 1rem;
  font-size: 1rem;
  padding: 0.85rem;
  font-weight: 700;
}

.error-message {
  color: var(--danger);
  font-size: 0.85rem;
  text-align: center;
  padding: 0.5rem;
  background-color: rgba(239, 68, 68, 0.1);
  border-radius: var(--radius-sm);
}

.toggle-mode {
  text-align: center;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.toggle-link {
  color: var(--primary);
  font-weight: 600;
  text-decoration: none;
  margin-left: 0.25rem;
}

.toggle-link:hover {
  text-decoration: underline;
}
</style>
