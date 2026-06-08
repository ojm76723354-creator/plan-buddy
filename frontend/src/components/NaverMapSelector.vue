<script setup>
import { ref, onMounted, defineEmits, defineProps, watch, nextTick } from 'vue'
import { Search, X } from 'lucide-vue-next'

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
    console.error('Naver Maps API not loaded.')
    return
  }
  if (!mapContainer.value) return

  const lat = props.lat || 37.5665
  const lng = props.lng || 126.9780

  map = new naver.maps.Map(mapContainer.value, {
    center: new naver.maps.LatLng(lat, lng),
    zoom: 15,
    mapTypeControl: true
  })

  marker = new naver.maps.Marker({
    position: new naver.maps.LatLng(lat, lng),
    map: map
  })

  naver.maps.Event.addListener(map, 'click', (e) => {
    showResults.value = false
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
    return
  }

  naver.maps.Service.reverseGeocode({
    coords: latlng,
    orders: [naver.maps.Service.OrderType.ROAD_ADDR, naver.maps.Service.OrderType.ADDR].join(',')
  }, (status, response) => {
    let addr = ''
    if (status === naver.maps.Service.Status.OK) {
      const v2 = response.v2
      addr = v2.address?.roadAddress || v2.address?.jibunAddress || ''
      if (!addr && v2.results?.length > 0) {
        const r = v2.results[0]
        addr = [r.region.area1.name, r.region.area2.name, r.region.area3.name, r.land?.number1]
          .filter(Boolean).join(' ')
      }
    }
    emit('update:location', { lat: latlng.lat(), lng: latlng.lng(), address: addr })
  })
}

const searchPlaces = () => {
  const query = searchQuery.value.trim()
  if (!query) return

  if (!window.naver?.maps?.Service) {
    alert('지도 서비스를 불러오는 중입니다. 잠시 후 다시 시도해 주세요.')
    return
  }

  isSearching.value = true
  searchResults.value = []
  showResults.value = false

  naver.maps.Service.geocode({ query }, (status, response) => {
    isSearching.value = false

    if (status !== naver.maps.Service.Status.OK) {
      alert('검색 중 오류가 발생했습니다.')
      return
    }

    const addresses = response.v2?.addresses || []
    if (addresses.length === 0) {
      alert('검색 결과가 없습니다.\n지하철역·주소 형식으로 입력해 보세요.\n예) 강남역, 서울역, 서울 강남구 테헤란로 123')
      return
    }

    searchResults.value = addresses.slice(0, 5).map(item => ({
      title: item.roadAddress || item.jibunAddress,
      sub: item.roadAddress ? item.jibunAddress : '',
      lat: parseFloat(item.y),
      lng: parseFloat(item.x)
    }))
    showResults.value = true
  })
}

const selectPlace = (place) => {
  showResults.value = false
  searchQuery.value = place.title
  const latlng = new naver.maps.LatLng(place.lat, place.lng)
  moveMarker(latlng, place.title)
  map.setZoom(17)
}

const clearSearch = () => {
  searchQuery.value = ''
  searchResults.value = []
  showResults.value = false
}

const handleKeydown = (e) => {
  if (e.key === 'Escape') showResults.value = false
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
  <div class="map-selector" @keydown="handleKeydown">
    <!-- 검색바 -->
    <div class="search-row">
      <div class="input-wrap">
        <Search class="icon-search" :size="16" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="주소 또는 장소명 (예: 강남역, 서울역)"
          @keyup.enter="searchPlaces"
          @focus="showResults = searchResults.length > 0"
          autocomplete="off"
        />
        <button v-if="searchQuery" class="btn-clear" @click="clearSearch" type="button">
          <X :size="14" />
        </button>
      </div>
      <button
        class="btn-search"
        :class="{ loading: isSearching }"
        :disabled="isSearching || !searchQuery.trim()"
        @click="searchPlaces"
        type="button"
      >
        {{ isSearching ? '검색 중…' : '검색' }}
      </button>
    </div>

    <!-- 검색 결과 드롭다운 -->
    <div v-if="showResults && searchResults.length" class="results-dropdown">
      <ul>
        <li
          v-for="(place, i) in searchResults"
          :key="i"
          @click="selectPlace(place)"
        >
          <span class="result-dot" />
          <div class="result-text">
            <span class="result-title">{{ place.title }}</span>
            <span v-if="place.sub" class="result-sub">{{ place.sub }}</span>
          </div>
        </li>
      </ul>
      <div class="results-footer" @click="showResults = false">닫기</div>
    </div>

    <!-- 지도 캔버스 -->
    <div ref="mapContainer" class="map-canvas" />
    <p class="map-hint">지도를 클릭해도 위치를 지정할 수 있습니다.</p>
  </div>
</template>

<style scoped>
.map-selector {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
  position: relative;
}

/* ── 검색바 ── */
.search-row {
  display: flex;
  gap: 8px;
}

.input-wrap {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
}

.icon-search {
  position: absolute;
  left: 10px;
  color: var(--text-secondary);
  pointer-events: none;
  flex-shrink: 0;
}

.input-wrap input {
  width: 100%;
  padding: 9px 34px 9px 34px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.875rem;
  outline: none;
  transition: border-color 0.2s;
}

.input-wrap input:focus {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 2px rgba(var(--accent-primary-rgb), 0.1);
}

.btn-clear {
  position: absolute;
  right: 8px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  padding: 2px;
}

.btn-clear:hover {
  color: var(--text-primary);
}

.btn-search {
  padding: 0 18px;
  background-color: var(--accent-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius-md);
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  white-space: nowrap;
  transition: background-color 0.2s, opacity 0.2s;
  min-width: 64px;
}

.btn-search:hover:not(:disabled) {
  background-color: var(--accent-dark);
}

.btn-search:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-search.loading {
  opacity: 0.7;
}

/* ── 드롭다운 ── */
.results-dropdown {
  position: absolute;
  top: 46px;
  left: 0;
  right: 0;
  background-color: var(--bg-primary, #fff);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
  z-index: 200;
  overflow: hidden;
}

.results-dropdown ul {
  list-style: none;
  margin: 0;
  padding: 4px 0;
}

.results-dropdown li {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 14px;
  cursor: pointer;
  transition: background-color 0.15s;
}

.results-dropdown li:hover {
  background-color: var(--bg-secondary);
}

.result-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--accent-primary);
  margin-top: 5px;
  flex-shrink: 0;
}

.result-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow: hidden;
}

.result-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.result-sub {
  font-size: 0.75rem;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.results-footer {
  text-align: center;
  padding: 6px;
  font-size: 0.75rem;
  color: var(--text-secondary);
  cursor: pointer;
  border-top: 1px solid var(--border-color);
}

.results-footer:hover {
  background-color: var(--bg-secondary);
}

/* ── 지도 ── */
.map-canvas {
  width: 100%;
  height: 300px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background-color: #eee;
  overflow: hidden;
}

.map-hint {
  font-size: 0.72rem;
  color: var(--text-secondary);
  text-align: center;
  margin: 0;
}

[data-theme="dark"] .map-canvas {
  filter: grayscale(1) invert(0.9) hue-rotate(180deg);
}

[data-theme="dark"] .results-dropdown {
  background-color: var(--bg-primary);
}
</style>
