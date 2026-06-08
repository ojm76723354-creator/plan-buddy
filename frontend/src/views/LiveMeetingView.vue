<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { API_BASE_URL, api } from '../api/auth'

const route = useRoute()
const router = useRouter()
const eventId = route.params.id

const event = ref(null)
const participants = ref([])
const messages = ref([])
const newMessage = ref('')
const myStatus = ref('PENDING')
const mapContainer = ref(null)
const myUsername = localStorage.getItem('username') || ''
let map = null
let markers = {} // user_id -> marker

const API_BASE = API_BASE_URL + '/api'

// 1. 데이터 로드
const fetchEventData = async () => {
  try {
    const res = await api.get(`/calendar/${eventId}`, { withCredentials: true })
    event.value = res.data
    participants.value = res.data.participants
    const me = res.data.participants.find(p => p.username === localStorage.getItem('username'))
    if (me) myStatus.value = me.status
  } catch (err) {
    console.error("Failed to fetch event details", err)
  }
}

const fetchParticipants = async () => {
  try {
    const res = await api.get(`/location/${eventId}/participants`, { withCredentials: true })
    participants.value = res.data
    updateMarkers()
  } catch (err) {
    console.error("Failed to fetch locations", err)
  }
}

const fetchChat = async () => {
  try {
    const res = await api.get(`/location/${eventId}/chat`, { withCredentials: true })
    messages.value = res.data
  } catch (err) {
    console.error("Failed to fetch chat", err)
  }
}

// 2. 지도 초기화 및 업데이트
const initMap = async () => {
  if (!window.naver) {
    console.error('Naver Maps API not loaded')
    return
  }

  if (!event.value || !event.value.latitude) {
    console.warn('Event data not ready for map initialization')
    return
  }

  const mapOptions = {
    center: new naver.maps.LatLng(event.value.latitude, event.value.longitude),
    zoom: 14,
    mapTypeControl: true
  }
  
  if (mapContainer.value) {
    map = new naver.maps.Map(mapContainer.value, mapOptions)

    // 약속 장소 마커 (빨간색 등 강조)
    new naver.maps.Marker({
      position: new naver.maps.LatLng(event.value.latitude, event.value.longitude),
      map: map,
      title: event.value.location,
      icon: {
        content: '<div style="background: #ef4444; color: white; padding: 5px 10px; border-radius: 20px; font-weight: bold; border: 2px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.2)">🚩 약속 장소</div>',
        anchor: new naver.maps.Point(15, 15)
      }
    })

    // 레이아웃이 잡힌 후 크기 재조정
    setTimeout(() => {
      if (map) naver.maps.Event.trigger(map, 'resize')
    }, 500)
  }
}

const updateMarkers = () => {
  if (!map) return

  participants.value.forEach(p => {
    if (p.is_sharing_location && p.last_latitude) {
      const pos = new naver.maps.LatLng(p.last_latitude, p.last_longitude)
      if (markers[p.user_id]) {
        markers[p.user_id].setPosition(pos)
      } else {
        markers[p.user_id] = new naver.maps.Marker({
          position: pos,
          map: map,
          title: p.username,
          icon: {
            content: `<div class="user-marker">${p.username[0]}</div>`,
            anchor: new naver.maps.Point(15, 15)
          }
        })
      }
    } else {
        // 위치 공유 중지된 경우 마커 제거
        if (markers[p.user_id]) {
            markers[p.user_id].setMap(null)
            delete markers[p.user_id]
        }
    }
  })
}

// 3. 실시간 위치 추적 및 업데이트
let watchId = null
const startTracking = () => {
  if (!navigator.geolocation) return

  watchId = navigator.geolocation.watchPosition(
    async (pos) => {
      const { latitude, longitude } = pos.coords
      try {
        const res = await api.post(`/location/${eventId}/location`, {
          latitude,
          longitude
        }, { withCredentials: true })
        
        if (res.data.status === 'ARRIVED' && myStatus.value !== 'ARRIVED') {
          myStatus.value = 'ARRIVED'
          alert('장소에 도착하였습니다! 자동 체크인 되었습니다.')
        }
      } catch (err) {
        console.error("Location update failed", err)
      }
    },
    (err) => console.error("Geolocation error", err),
    { enableHighAccuracy: true }
  )
}

// 4. 채팅 전송
const sendChat = async () => {
  if (!newMessage.value.trim()) return
  try {
    await api.post(`/location/${eventId}/chat`, {
      message: newMessage.value
    }, { withCredentials: true })
    newMessage.value = ''
    fetchChat()
  } catch (err) {
    console.error("Chat failed", err)
  }
}

// 🧘 라이프사이클
onMounted(async () => {
  await fetchEventData()
  initMap()
  fetchParticipants()
  fetchChat()
  startTracking()

  // 주기적 업데이트 (폴링)
  const pollInterval = setInterval(() => {
    fetchParticipants()
    fetchChat()
  }, 5000)

  onUnmounted(() => {
    if (watchId) navigator.geolocation.clearWatch(watchId)
    clearInterval(pollInterval)
  })
})
</script>

<template>
  <div class="live-dashboard" v-if="event">
    <div class="header card">
      <div class="header-left">
        <button class="btn btn-icon" @click="router.back()">⬅</button>
        <div>
          <h2 class="title">{{ event.title }}</h2>
          <p class="subtitle">{{ event.location }} · {{ new Date(event.start_time).toLocaleString() }}</p>
        </div>
      </div>
      <div class="status-badge" :class="myStatus.toLowerCase()">
        {{ myStatus === 'ARRIVED' ? '도착 완료 ✨' : '이동 중...' }}
      </div>
    </div>

    <div class="main-content">
      <div class="map-section card">
        <div ref="mapContainer" class="live-map"></div>
      </div>

      <div class="side-section">
        <!-- Participants List -->
        <div class="participants-card card">
          <h3 class="section-title">참여자 상태</h3>
          <div class="participant-list">
            <div v-for="p in participants" :key="p.user_id" class="participant-item">
              <div class="avatar-placeholder">{{ p.username[0] }}</div>
              <div class="p-info">
                <span class="p-name">{{ p.username }}</span>
                <span class="p-status" :class="p.status.toLowerCase()">{{ p.status }}</span>
              </div>
              <div v-if="p.arrival_time" class="arrival-time">
                {{ new Date(p.arrival_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }} 도착
              </div>
            </div>
          </div>
        </div>

        <!-- Chat Section -->
        <div class="chat-card card">
          <h3 class="section-title">임시 채팅</h3>
          <div class="chat-messages" ref="chatBox">
            <div v-for="m in messages" :key="m.id" class="message" :class="{ mine: m.username === myUsername }">
              <div class="msg-meta" v-if="m.username !== myUsername">{{ m.username }}</div>
              <div class="msg-bubble">{{ m.message }}</div>
            </div>
          </div>
          <div class="chat-input-row">
            <input type="text" v-model="newMessage" @keyup.enter="sendChat" placeholder="메시지를 입력하세요" />
            <button class="btn btn-primary" @click="sendChat">전송</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.live-dashboard {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  height: calc(100vh - 100px);
}

.header {
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.title { margin: 0; font-size: 1.25rem; }
.subtitle { margin: 0; font-size: 0.875rem; color: var(--text-secondary); }

.status-badge {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 700;
  font-size: 0.875rem;
}
.status-badge.arrived { background: var(--primary-light); color: var(--primary); }
.status-badge.pending { background: #fef3c7; color: #d97706; }

.main-content {
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 1.5rem;
  flex: 1;
  min-height: 0;
}

.live-map {
  width: 100%;
  height: 100%;
  border-radius: var(--radius-md);
}

.side-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  min-height: 0;
}

.participants-card, .chat-card {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.section-title {
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.participant-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  overflow-y: auto;
}

.participant-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.p-info { display: flex; flex-direction: column; flex: 1; }
.p-name { font-weight: 600; font-size: 0.9rem; }
.p-status { font-size: 0.75rem; text-transform: uppercase; }
.p-status.arrived { color: var(--primary); font-weight: 700; }

.chat-messages {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.message {
  display: flex;
  flex-direction: column;
  max-width: 80%;
}
.message.mine { align-self: flex-end; align-items: flex-end; }

.msg-meta { font-size: 0.7rem; color: var(--text-secondary); margin-bottom: 2px; }
.msg-bubble {
  padding: 0.5rem 0.75rem;
  border-radius: 12px;
  background-color: var(--bg-color);
  font-size: 0.875rem;
}
.mine .msg-bubble { background-color: var(--primary); color: white; }

.chat-input-row {
  display: flex;
  gap: 0.5rem;
}
.chat-input-row input {
  flex: 1;
  padding: 0.5rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: 20px;
  background: var(--bg-color);
}

:deep(.user-marker) {
  background: var(--primary);
  color: white;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  border: 2px solid white;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
</style>
