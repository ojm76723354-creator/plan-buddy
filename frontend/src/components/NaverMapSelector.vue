<script setup>
import { ref, onMounted, defineEmits, defineProps, watch, nextTick } from 'vue'
import { Search } from 'lucide-vue-next'
import { api } from '../api/auth.js'

const props = defineProps({
  lat: Number,
  lng: Number
})

const emit = defineEmits(['update:location'])
const mapContainer = ref(null)
const searchQuery = ref('')
const searchResults = ref([])
const showResults = ref(false)
const isSearching = ref(false)
let map = null
let marker = null

const initMap = () => {
  if (!window.naver) {
    console.error('Naver Maps API not loaded. Check index.html and your Client ID.')
    return
  }

  if (!mapContainer.value) return

  const initialLat = props.lat || 37.5665
  const initialLng = props.lng || 126.9780

  const mapOptions = {
    center: new naver.maps.LatLng(initialLat, initialLng),
    zoom: 15,
    mapTypeControl: true
  }

  map = new naver.maps.Map(mapContainer.value, mapOptions)

  marker = new naver.maps.Marker({
    position: new naver.maps.LatLng(initialLat, initialLng),
    map: map
  })

  naver.maps.Event.addListener(map, 'click', (e) => {
    moveMarker(e.latlng)
  })

  setTimeout(() => {
    if (map) naver.maps.Event.trigger(map, 'resize')
  }, 300)
}

const moveMarker = (latlng, address = null) => {
  if (!marker) return
  marker.setPosition(latlng)
  map.panTo(latlng)

  if (address) {
    emit('update:location', { lat: latlng.lat(), lng: latlng.lng(), address })
  } else {
    naver.maps.Service.reverseGeocode({
      coords: latlng,
      orders: [
        naver.maps.Service.OrderType.ADDR,
        naver.maps.Service.OrderType.ROAD_ADDR
      ].join(',')
    }, (status, response) => {
      let addr = ''
      if (status === naver.maps.Service.Status.OK) {
        const result = response.v2
        if (result.address && result.address.jibunAddress) {
          addr = result.address.jibunAddress
        } else if (result.results && result.results.length > 0) {
          const r = result.results[0]
          addr = `${r.region.area1.name} ${r.region.area2.name} ${r.region.area3.name} ${r.land.number1}`
        }
      }
      emit('update:location', { lat: latlng.lat(), lng: latlng.lng(), address: addr })
    })
  }
}

const searchPlaces = async () => {
  const query = searchQuery.value.trim()
  if (!query) return

  isSearching.value = true
  searchResults.value = []

  try {
    const { data } = await api.get('/places/search', { params: { q: query } })
    searchResults.value = data.items || []
    showResults.value = searchResults.value.length > 0
    if (searchResults.value.length === 0) {
      alert('검색 결과가 없습니다. 다른 검색어를 입력해 주세요.')
    }
  } catch (err) {
    const msg = err.response?.data?.detail || '검색 중 오류가 발생했습니다.'
    alert(msg)
  } finally {
    isSearching.value = false
  }
}

const selectPlace = (place) => {
  showResults.value = false
  searchQuery.value = place.title
  const latlng = new naver.maps.LatLng(place.lat, place.lng)
  const address = place.roadAddress || place.address || place.title
  moveMarker(latlng, address)
  map.setZoom(17)
}

const closeResults = () => {
  showResults.value = false
}

onMounted(async () => {
  await nextTick()
  setTimeout(initMap, 100)
})

watch(() => [props.lat, props.lng], ([newLat, newLng]) => {
  if (map && marker && newLat && newLng) {
    const pos = new naver.maps.LatLng(newLat, newLng)
    map.setCenter(pos)
    marker.setPosition(pos)
  }
})
</script>

<template>
  <div class="map-selector" @click.self="closeResults">
    <div class="search-bar">
      <div class="input-wrapper">
        <Search class="search-icon" :size="18" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="장소나 주소를 검색하세요"
          @keyup.enter="searchPlaces"
          @focus="showResults = searchResults.length > 0"
        />
      </div>
      <button class="search-btn" :disabled="isSearching" @click="searchPlaces">
        {{ isSearching ? '검색 중...' : '검색' }}
      </button>
    </div>

    <div v-if="showResults" class="search-results">
      <ul>
        <li
          v-for="(place, idx) in searchResults"
          :key="idx"
          @click="selectPlace(place)"
        >
          <div class="place-title">{{ place.title }}</div>
          <div class="place-meta">
            <span v-if="place.category" class="place-category">{{ place.category }}</span>
            <span class="place-address">{{ place.roadAddress || place.address }}</span>
          </div>
        </li>
      </ul>
    </div>

    <div ref="mapContainer" class="map-canvas"></div>
    <p class="map-hint">검색하거나 지도를 클릭하여 장소를 지정하세요.</p>
  </div>
</template>

<style scoped>
.map-selector {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: relative;
}

.search-bar {
  display: flex;
  gap: 10px;
  width: 100%;
}

.input-wrapper {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 12px;
  color: var(--text-secondary);
  pointer-events: none;
}

.input-wrapper input {
  width: 100%;
  padding: 10px 12px 10px 40px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.9rem;
  transition: all 0.2s ease;
  outline: none;
}

.input-wrapper input:focus {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 2px rgba(var(--accent-primary-rgb), 0.1);
}

.search-btn {
  padding: 0 20px;
  background-color: var(--accent-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
  white-space: nowrap;
}

.search-btn:hover:not(:disabled) {
  background-color: var(--accent-dark);
}

.search-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.search-results {
  position: absolute;
  top: 50px;
  left: 0;
  right: 0;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  z-index: 100;
  max-height: 240px;
  overflow-y: auto;
}

.search-results ul {
  list-style: none;
  margin: 0;
  padding: 4px 0;
}

.search-results li {
  padding: 10px 14px;
  cursor: pointer;
  transition: background-color 0.15s;
}

.search-results li:hover {
  background-color: var(--bg-secondary);
}

.place-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.place-meta {
  display: flex;
  gap: 8px;
  font-size: 0.75rem;
  color: var(--text-secondary);
  flex-wrap: wrap;
}

.place-category {
  color: var(--accent-primary);
}

.map-canvas {
  width: 100%;
  height: 300px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background-color: #eee;
  overflow: hidden;
}

.map-hint {
  font-size: 0.75rem;
  color: var(--text-secondary);
  text-align: center;
  margin: 0;
}

[data-theme="dark"] .map-canvas {
  filter: grayscale(1) invert(0.9) hue-rotate(180deg);
}
</style>
