<script setup>
import { ref, watchEffect, onMounted, watch } from 'vue'
import { RouterView, useRouter, useRoute } from 'vue-router'
import { isLoggedIn as checkLogin, logout } from './api/auth'
import FriendManagerModal from './components/FriendManagerModal.vue'

const router = useRouter()
const route = useRoute()
const isDarkMode = ref(false)
const isLoggedIn = ref(false)
const isFriendModalOpen = ref(false)

onMounted(() => {
  isLoggedIn.value = checkLogin()
})

// Re-check login whenever route changes (e.g. after redirect from login page)
watch(() => route.path, () => {
  isLoggedIn.value = checkLogin()
})

const handleLogout = () => {
  logout()
  isLoggedIn.value = false
  router.push('/login')
}

const goToLogin = () => {
  router.push('/login')
}

const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value
}

const openFriendModal = () => {
  if (!isLoggedIn.value) {
    alert('로그인이 필요한 기능입니다.')
    router.push('/login')
    return
  }
  isFriendModalOpen.value = true
}

// 다크모드 적용
watchEffect(() => {
  if (isDarkMode.value) {
    document.documentElement.setAttribute('data-theme', 'dark')
  } else {
    document.documentElement.removeAttribute('data-theme')
  }
})
</script>

<template>
  <div class="app-layout">
    <header class="top-nav card">
      <div class="nav-brand" style="cursor: pointer;" @click="router.push('/')">
        <img src="@/assets/logo_buddy.png" alt="Plan Buddy" class="logo-image" />
      </div>
      <div class="nav-actions">
        <button class="btn btn-icon" @click="toggleTheme" title="테마 전환">
          {{ isDarkMode ? '☀️' : '🌙' }}
        </button>
        <button class="btn btn-outline" @click="openFriendModal">
          👥 친구 관리
        </button>
        <button v-if="isLoggedIn" class="btn btn-outline" @click="router.push('/mypage')">
          👤 내 정보
        </button>
        <button v-if="!isLoggedIn" class="btn btn-primary" @click="goToLogin">
          로그인
        </button>
        <button v-else class="btn btn-outline" title="로그아웃" @click="handleLogout">
          로그아웃
        </button>
      </div>
    </header>

    <main class="main-content">
      
      <div class="content">
        <RouterView />
      </div>
    </main>

    <FriendManagerModal :isOpen="isFriendModalOpen" @close="isFriendModalOpen = false" />
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 2rem;
  border-radius: 0;
  border-left: none;
  border-right: none;
  border-top: none;
  z-index: 10;
  position: relative;
}

.nav-brand .logo-image {
  height: 100px;
  width: auto;
  object-fit: contain;
  transition: transform 0.2s;
}

.nav-brand .logo-image:hover {
  transform: scale(1.05);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-outline {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}

.main-content {
  display: flex;
  flex: 1;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  padding: 1.5rem 2rem;
  gap: 2rem;
}

.content {
  flex: 1;
  min-width: 0;
}

@media (max-width: 768px) {
  .main-content {
    padding: 1rem;
  }
}
</style>