<script setup>
import { ref, computed, onMounted } from 'vue'
import VueCal from 'vue-cal'
import 'vue-cal/dist/vuecal.css'
import EventModal from '../components/EventModal.vue'
import { getEvents, createEvent, getFriendEvents } from '../api/calendar'
import { getFriends } from '../api/friends'
import { getMe } from '../api/mypage'

const selectedDate = ref(new Date())
const activeView = ref('week') // 'month', 'week', 'day'
const isModalOpen = ref(false)
const selectedEvent = ref(null)

const events = ref([])
const friendList = ref([])
const currentUser = ref(null)
const selectedUser = ref({ id: 'me', username: '내 일정' })

const fetchUserEvents = async () => {
  try {
    let data
    if (selectedUser.value.id === 'me') {
      data = await getEvents()
    } else {
      data = await getFriendEvents(selectedUser.value.username)
    }
    
    events.value = data.map(ev => ({
      ...ev,
      start: new Date(ev.start_time),
      end: new Date(ev.end_time),
      content: ev.description
    }))
  } catch (error) {
    console.error("Failed to fetch events", error)
  }
}

const fetchFriendList = async () => {
  try {
    const list = await getFriends()
    // 필터링: 수락된 친구만 표시 (상태가 ACCEPTED인 것만)
    friendList.value = list.filter(f => f.status === 'ACCEPTED')
  } catch (err) {
    console.error("Failed to fetch friend list")
  }
}

const fetchCurrentUser = async () => {
  try {
    currentUser.value = await getMe()
  } catch (err) {
    console.error("Failed to fetch current user profile")
  }
}

onMounted(async () => {
  await fetchCurrentUser()
  await fetchFriendList()
  await fetchUserEvents()
})

const selectUser = async (user) => {
  selectedUser.value = user
  await fetchUserEvents()
}

// 일정 클릭 시 동작 (이후 모달과 연동)
const onEventClick = (event, e) => {
  selectedEvent.value = { ...event }
  isModalOpen.value = true
  e.stopPropagation()
}

const onEventCreate = (event, deleteEventFunction) => {
  selectedEvent.value = { ...event }
  isModalOpen.value = true
  return event
}

const openNewEventModal = () => {
  const now = new Date()
  const later = new Date(now.getTime() + 60 * 60 * 1000) // +1 hour
  selectedEvent.value = {
    title: '',
    content: '',
    visibility: 'PUBLIC',
    start: now,
    end: later
  }
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
  selectedEvent.value = null
}

const handleSaveEvent = async (savedEvent) => {
  try {
    const payload = {
      title: savedEvent.title || '새 일정',
      description: savedEvent.content || '',
      start_time: savedEvent.start instanceof Date ? savedEvent.start.toISOString() : new Date(savedEvent.start).toISOString(),
      end_time: savedEvent.end instanceof Date ? savedEvent.end.toISOString() : new Date(savedEvent.end).toISOString(),
      visibility: savedEvent.visibility || 'PRIVATE'
    }
    const newEv = await createEvent(payload)
    events.value.push({
      ...newEv,
      start: new Date(newEv.start_time),
      end: new Date(newEv.end_time),
      content: newEv.description
    })
    closeModal()
  } catch (error) {
    console.error("Failed to save event", error)
    alert('일정 저장에 실패했습니다. 로그인이 되어있는지 확인해주세요!')
  }
}
</script>

<template>
  <div class="page-layout">
    <!-- Sidebar for Friends -->
    <aside class="sidebar card">
      <div class="sidebar-header">
        <h3 class="sidebar-title">일정 목록</h3>
      </div>
      <nav class="friend-nav">
        <div 
          class="nav-item" 
          :class="{ active: selectedUser.id === 'me' }"
          @click="selectUser({ id: 'me', username: '내 일정' })"
        >
          <div v-if="currentUser?.profile_image" class="friend-avatar profile-small">
            <img :src="'http://localhost:8000' + currentUser.profile_image" alt="Me" />
          </div>
          <span v-else class="nav-icon">👤</span>
          <span class="nav-text">내 일정</span>
        </div>
        
        <div class="sidebar-divider">친구</div>
        
        <div v-if="friendList.length > 0">
          <div 
            v-for="friend in friendList" 
            :key="friend.id" 
            class="nav-item" 
            :class="{ active: selectedUser.id === friend.id }"
            @click="selectUser({ id: friend.id, username: friend.friend_username })"
          >
            <div v-if="friend.profile_image" class="friend-avatar profile-small">
              <img :src="'http://localhost:8000' + friend.profile_image" alt="Friend" />
            </div>
            <div v-else class="friend-avatar">{{ friend.friend_username.substring(0, 1).toUpperCase() }}</div>
            <span class="nav-text">{{ friend.friend_username }}</span>
          </div>
        </div>
        <p v-else class="empty-sidebar">추가된 친구가 없습니다.</p>
      </nav>
    </aside>

    <div class="calendar-container">
      <div class="calendar-header card">
        <div class="header-content">
          <div>
            <h2 class="title">{{ selectedUser.id === 'me' ? (activeView === 'month' ? '월간 일정' : '주간 일정') : `${selectedUser.username}님의 일정` }}</h2>
            <p class="subtitle">{{ selectedUser.id === 'me' ? '나의 캠퍼스 라이프를 스케줄해보세요.' : '친구의 스케줄을 확인하고 함께해보세요.' }}</p>
          </div>
          <div class="view-toggles">
            <button 
              class="btn" 
              :class="activeView === 'month' ? 'btn-primary' : 'btn-outline'" 
              @click="activeView = 'month'"
            >월간</button>
            <button 
              class="btn" 
              :class="activeView === 'week' ? 'btn-primary' : 'btn-outline'" 
              @click="activeView = 'week'"
            >주간</button>
            <button v-if="selectedUser.id === 'me'" class="btn btn-primary add-btn" @click="openNewEventModal">
              ＋ 일정 추가
            </button>
          </div>
        </div>
      </div>

      <!-- Calendar Area -->
      <div class="calendar-card card">
        <vue-cal
          class="vuecal--blue-theme campus-cal"
          :selected-date="selectedDate"
          :active-view="activeView"
          :events="events"
          :disable-views="['years', 'year']"
          events-on-month-view="short"
          :editable-events="selectedUser.id === 'me'"
          @view-change="activeView = $event.view"
          @event-click="onEventClick"
          @event-create="onEventCreate"
          locale="ko"
          :time-from="8 * 60"
          :time-to="23 * 60"
          :time-step="30"
        >
          <template #event="{ event, view }">
            <div class="custom-event">
              <div class="event-title">{{ event.title }}</div>
              <div class="event-content" v-if="view === 'week' || view === 'day'">
                {{ event.content }}
              </div>
            </div>
          </template>
        </vue-cal>
      </div>
      
      <EventModal 
        v-if="selectedUser.id === 'me'"
        :isOpen="isModalOpen" 
        :eventData="selectedEvent" 
        @close="closeModal" 
        @save="handleSaveEvent" 
      ></EventModal>
    </div>
  </div>
</template>

<style scoped>
.page-layout {
  display: flex;
  gap: 1.5rem;
  height: calc(100vh - 120px);
}

.sidebar {
  width: 260px;
  display: flex;
  flex-direction: column;
  padding: 1rem;
}

.sidebar-header {
  padding: 0.5rem 0.5rem 1rem;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 1rem;
}

.sidebar-title {
  font-size: 1rem;
  font-weight: 700;
}

.friend-nav {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-secondary);
}

.nav-item:hover {
  background-color: var(--bg-color);
  color: var(--text-primary);
}

.nav-item.active {
  background-color: var(--primary-light);
  color: var(--primary);
  font-weight: 600;
}

.nav-icon {
  font-size: 1.25rem;
}

.sidebar-divider {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 1.5rem 0.5rem 0.5rem;
}

.friend-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: var(--primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  overflow: hidden;
}

.friend-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.empty-sidebar {
  padding: 1rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
  text-align: center;
}

.calendar-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  min-width: 0; /* overflow 방지 */
}

.calendar-header {
  padding: 1.5rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.view-toggles {
  display: flex;
  gap: 0.5rem;
}

.btn-outline {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}

.btn-outline:hover {
  background: var(--surface-color);
  border-color: var(--primary);
  color: var(--primary);
}

.calendar-card {
  flex: 1;
  padding: 1rem;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Customizing vue-cal to fit dark mode & premium design */
:deep(.campus-cal) {
  border-radius: var(--radius-md);
  flex: 1;
}

:deep(.vuecal__menu) {
  background-color: var(--surface-color) !important;
  border-bottom: 1px solid var(--border-color);
}

:deep(.vuecal__cell) {
  background-color: var(--surface-color);
}

[data-theme='dark'] :deep(.vuecal__cell) {
  border-color: var(--border-color);
}

[data-theme='dark'] :deep(.vuecal__time-column) {
  border-color: var(--border-color);
}

[data-theme='dark'] :deep(.vuecal__bg) {
  background-color: var(--bg-color);
}

.custom-event {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 4px;
  font-size: 0.8rem;
  text-align: left;
}

.event-title {
  font-weight: 600;
  margin-bottom: 2px;
}

:deep(.vuecal__event) {
  background-color: var(--primary-light);
  color: var(--primary);
  border-left: 3px solid var(--primary);
  border-radius: 4px;
}

:deep(.vuecal__event:hover) {
  opacity: 0.9;
}
</style>
