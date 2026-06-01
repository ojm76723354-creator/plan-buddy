<script setup>
import { ref, defineProps, defineEmits, watch, onMounted } from 'vue'
import axios from 'axios'
import NaverMapSelector from './NaverMapSelector.vue'

const props = defineProps({
  isOpen: Boolean,
  eventData: Object
})

const emit = defineEmits(['close', 'save'])

const title = ref('')
const content = ref('')
const location = ref('')
const latitude = ref(null)
const longitude = ref(null)
const radius = ref(50)
const visibility = ref('PUBLIC')
const startTime = ref('')
const endTime = ref('')

const friends = ref([])
const invitees = ref([])

onMounted(async () => {
  try {
    const res = await axios.get('http://localhost:8000/api/friend/list', { withCredentials: true })
    friends.value = res.data.filter(f => f.status === 'ACCEPTED')
  } catch (err) {
    console.error("Failed to load friends", err)
  }
})

// Convert a JS Date or ISO string to "YYYY-MM-DDTHH:mm" for datetime-local input
const toLocalDatetimeString = (val) => {
  if (!val) return ''
  const d = val instanceof Date ? val : new Date(val)
  if (isNaN(d.getTime())) return ''
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

watch(() => props.eventData, (newVal) => {
  if (newVal) {
    title.value = newVal.title || ''
    content.value = newVal.content || ''
    location.value = newVal.location || ''
    latitude.value = newVal.latitude || null
    longitude.value = newVal.longitude || null
    radius.value = newVal.radius || 50
    visibility.value = newVal.visibility || 'PUBLIC'
    startTime.value = toLocalDatetimeString(newVal.start)
    endTime.value = toLocalDatetimeString(newVal.end)
    invitees.value = newVal.invitees || []
  } else {
    title.value = ''
    content.value = ''
    location.value = ''
    latitude.value = null
    longitude.value = null
    radius.value = 50
    visibility.value = 'PUBLIC'
    startTime.value = ''
    endTime.value = ''
    invitees.value = []
  }
}, { immediate: true })

const closeModal = () => {
  emit('close')
}

const updateLocation = (loc) => {
  latitude.value = loc.lat
  longitude.value = loc.lng
}

const toggleInvitee = (username) => {
  const idx = invitees.value.indexOf(username)
  if (idx > -1) {
    invitees.value.splice(idx, 1)
  } else {
    invitees.value.push(username)
  }
}

const startLiveTracking = () => {
  if (props.eventData?.id) {
    window.location.href = `/live/${props.eventData.id}`
  }
}

const saveEvent = () => {
  if (!title.value.trim()) { alert('제목을 입력해주세요.'); return }
  if (!startTime.value || !endTime.value) { alert('시작/종료 시간을 입력해주세요.'); return }
  emit('save', {
    ...props.eventData,
    title: title.value,
    content: content.value,
    location: location.value,
    latitude: latitude.value,
    longitude: longitude.value,
    radius: radius.value,
    visibility: visibility.value,
    start: new Date(startTime.value),
    end: new Date(endTime.value),
    invitees: invitees.value
  })
}
</script>

<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content card">
      <div class="modal-header">
        <h3 class="modal-title">{{ eventData?.id ? '일정 수정' : '새 일정 추가' }}</h3>
        <button class="btn btn-icon close-btn" @click="closeModal">✕</button>
      </div>

      <div class="modal-body scrollable">
        <div class="form-group">
          <label>일정 제목 *</label>
          <input type="text" v-model="title" class="form-control" placeholder="일정 제목을 입력하세요" />
        </div>

        <div class="form-group">
          <label>상세 내용</label>
          <textarea v-model="content" class="form-control" rows="2" placeholder="자세한 일정을 입력하세요"></textarea>
        </div>

        <div class="time-row">
          <div class="form-group">
            <label>시작 시간 *</label>
            <input type="datetime-local" v-model="startTime" class="form-control" />
          </div>
          <div class="form-group">
            <label>종료 시간 *</label>
            <input type="datetime-local" v-model="endTime" class="form-control" />
          </div>
        </div>

        <!-- Location Selection -->
        <div class="form-group">
          <label>약속 장소 (네이버 지도)</label>
          <input type="text" v-model="location" class="form-control" placeholder="장소 이름을 입력하세요 (예: 강남역 카페)" />
          <div class="map-wrapper">
            <NaverMapSelector :lat="latitude" :lng="longitude" @update:location="updateLocation" />
          </div>
          <div class="radius-control" v-if="latitude">
            <label>도착 판정 반경: {{ radius }}m</label>
            <input type="range" v-model.number="radius" min="10" max="200" step="10" />
          </div>
        </div>

        <!-- Invite Friends -->
        <div class="form-group">
          <label>함께할 친구 초대</label>
          <div class="friend-selector-grid" v-if="friends.length > 0">
            <div 
              v-for="friend in friends" 
              :key="friend.friend_username" 
              class="friend-select-item"
              :class="{ selected: invitees.includes(friend.friend_username) }"
              @click="toggleInvitee(friend.friend_username)"
            >
              <div v-if="friend.profile_image" class="avatar-small">
                <img :src="'http://localhost:8000' + friend.profile_image" />
              </div>
              <span v-else class="avatar-placeholder">{{ friend.friend_username[0].toUpperCase() }}</span>
              <span class="friend-name">{{ friend.friend_username }}</span>
            </div>
          </div>
          <p v-else class="empty-text">초대 가능한 수락된 친구가 없습니다.</p>
        </div>

        <div class="form-group">
          <label>공개 범위</label>
          <div class="radio-group">
            <label class="radio-label">
              <input type="radio" v-model="visibility" value="PUBLIC" />
              <span>전체 공개 (자세히)</span>
            </label>
            <label class="radio-label">
              <input type="radio" v-model="visibility" value="FRIENDS_ONLY" />
              <span>친구에게만 보임</span>
            </label>
            <label class="radio-label">
              <input type="radio" v-model="visibility" value="PRIVATE" />
              <span>나만 보기 (친구에겐 '바쁨' 표시)</span>
            </label>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button v-if="eventData?.id" class="btn btn-success" @click="startLiveTracking">📍 실시간 추적 시작</button>
        <button class="btn btn-outline" @click="closeModal">취소</button>
        <button class="btn btn-primary" @click="saveEvent">저장 및 초대</button>
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
  max-width: 500px;
  background-color: var(--surface-color);
  display: flex;
  flex-direction: column;
  animation: slide-up 0.3s ease-out forwards;
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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
  gap: 1.25rem;
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

.form-control {
  padding: 0.75rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background-color: var(--bg-color);
  color: var(--text-primary);
  font-family: inherit;
  font-size: 0.875rem;
  transition: border-color 0.2s;
}

.form-control:focus {
  outline: none;
  border-color: var(--primary);
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background-color: var(--bg-color);
  padding: 1rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  cursor: pointer;
  color: var(--text-primary);
}

.modal-footer {
  padding: 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  border-top: 1px solid var(--border-color);
}

.time-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.scrollable {
  max-height: 60vh;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.map-wrapper {
  margin-top: 0.5rem;
}

.radius-control {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-top: 0.75rem;
  font-size: 0.75rem;
  color: var(--primary);
}

.friend-selector-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 0.5rem;
  background-color: var(--bg-color);
  padding: 1rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.friend-select-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.friend-select-item:hover {
  background-color: var(--surface-color);
}

.friend-select-item.selected {
  background-color: var(--primary-light);
  border-color: var(--primary);
}

.avatar-small {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
}

.avatar-small img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.75rem;
}

.friend-name {
  font-size: 0.75rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100%;
  text-align: center;
}

.empty-text {
  font-size: 0.75rem;
  color: var(--text-secondary);
  text-align: center;
  padding: 1rem;
}
</style>
