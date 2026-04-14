<script setup>
import { ref, defineProps, defineEmits, watch } from 'vue'

const props = defineProps({
  isOpen: Boolean,
  eventData: Object
})

const emit = defineEmits(['close', 'save'])

const title = ref('')
const content = ref('')
const visibility = ref('PUBLIC')
const startTime = ref('')
const endTime = ref('')

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
    visibility.value = newVal.visibility || 'PUBLIC'
    startTime.value = toLocalDatetimeString(newVal.start)
    endTime.value = toLocalDatetimeString(newVal.end)
  } else {
    title.value = ''
    content.value = ''
    visibility.value = 'PUBLIC'
    startTime.value = ''
    endTime.value = ''
  }
}, { immediate: true })

const closeModal = () => {
  emit('close')
}

const saveEvent = () => {
  if (!title.value.trim()) { alert('제목을 입력해주세요.'); return }
  if (!startTime.value || !endTime.value) { alert('시작/종료 시간을 입력해주세요.'); return }
  emit('save', {
    ...props.eventData,
    title: title.value,
    content: content.value,
    visibility: visibility.value,
    start: new Date(startTime.value),
    end: new Date(endTime.value),
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

      <div class="modal-body">
        <div class="form-group">
          <label>일정 제목 *</label>
          <input type="text" v-model="title" class="form-control" placeholder="일정 제목을 입력하세요" />
        </div>

        <div class="form-group">
          <label>상세 내용</label>
          <textarea v-model="content" class="form-control" rows="3" placeholder="자세한 일정을 입력하세요"></textarea>
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
        <button class="btn btn-outline" @click="closeModal">취소</button>
        <button class="btn btn-primary" @click="saveEvent">저장</button>
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
</style>
