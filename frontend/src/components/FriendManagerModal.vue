<script setup>
import { ref, defineProps, defineEmits, watch } from 'vue'
import { getFriends, requestFriend, acceptFriend } from '../api/friends'

const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close'])

const friendList = ref([])
const friendSearchName = ref('')
const message = ref('')

const fetchFriends = async () => {
  try {
    friendList.value = await getFriends()
  } catch (err) {
    console.error('Failed to fetch friends')
  }
}

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    fetchFriends()
    message.value = ''
    friendSearchName.value = ''
  }
})

const handleRequestFriend = async () => {
  if (!friendSearchName.value.trim()) return
  message.value = ''
  try {
    await requestFriend(friendSearchName.value.trim())
    message.value = '친구 요청을 보냈습니다!'
    friendSearchName.value = ''
    await fetchFriends()
  } catch (err) {
    message.value = err.response?.data?.detail || '친구 요청 실패 (아이디 확인)'
  }
}

const handleAcceptFriend = async (friendshipId) => {
  try {
    await acceptFriend(friendshipId)
    message.value = '친구 요청을 수락했습니다!'
    await fetchFriends()
  } catch (err) {
    message.value = '친구 수락 실패'
  }
}

const closeModal = () => {
  emit('close')
}
</script>

<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content card">
      <div class="modal-header">
        <h3 class="modal-title">친구 관리</h3>
        <button class="btn btn-icon close-btn" @click="closeModal">✕</button>
      </div>

      <div class="modal-body">
        <div class="form-group friend-search">
          <label>친구 추가 (아이디 검색)</label>
          <div class="search-row">
            <input type="text" v-model="friendSearchName" class="form-control" placeholder="아이디를 입력하세요" @keyup.enter="handleRequestFriend" />
            <button class="btn btn-primary" @click="handleRequestFriend">요청</button>
          </div>
          <small class="msg" v-if="message">{{ message }}</small>
        </div>

        <div class="friend-list-area">
          <h4>내 친구 목록</h4>
          <ul class="friend-list" v-if="friendList.length > 0">
            <li v-for="friend in friendList" :key="friend.id" class="friend-item">
              <span class="f-name">{{ friend.friend_username }}</span>
              <div class="f-actions">
                <span class="f-status" :class="friend.status.toLowerCase()">
                  {{ friend.status === 'PENDING' ? (friend.is_sender ? '요청중' : '수락 대기') : '친구' }}
                </span>
                <button 
                  v-if="friend.status === 'PENDING' && !friend.is_sender" 
                  class="btn btn-sm btn-outline-primary accept-btn"
                  @click="handleAcceptFriend(friend.id)"
                >
                  수락
                </button>
              </div>
            </li>
          </ul>
          <p v-else class="empty-text">아직 친구가 없습니다. 친구를 찾아보세요!</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  width: 90%;
  max-width: 450px;
  background-color: var(--surface-color);
  display: flex;
  flex-direction: column;
  animation: slide-up 0.3s ease-out forwards;
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.modal-header {
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-color);
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
}

.modal-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.form-group label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.search-row {
  display: flex;
  gap: 0.5rem;
}

.search-row .form-control {
  flex: 1;
}

.search-row .btn {
  white-space: nowrap;
}

.msg {
  color: var(--primary);
  font-size: 0.8rem;
  margin-top: 0.25rem;
}

.friend-list-area h4 {
  font-size: 1rem;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.friend-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.friend-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background-color: var(--bg-color);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.f-name {
  font-weight: 600;
}

.f-status {
  font-size: 0.8rem;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  background-color: #e2e8f0;
  color: #475569;
}

.f-status.pending { background-color: #fef3c7; color: #d97706; }
.f-status.accepted { background-color: #d1fae5; color: #059669; }

.f-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

.btn-outline-primary {
  background-color: transparent;
  border: 1px solid var(--primary);
  color: var(--primary);
}

.btn-outline-primary:hover {
  background-color: var(--primary);
  color: white;
}

.empty-text {
  color: var(--text-secondary);
  font-size: 0.9rem;
  text-align: center;
  padding: 2rem 0;
}
</style>
