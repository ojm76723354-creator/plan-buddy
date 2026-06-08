<script setup>
import { ref, onMounted, defineEmits, defineProps, watch, nextTick } from 'vue'
import { Search, X, MapPin } from 'lucide-vue-next'

const props = defineProps({ lat: Number, lng: Number })
const emit = defineEmits(['update:location'])

const mapContainer = ref(null)
const searchQuery = ref('')
const searchResults = ref([])
const showResults = ref(false)
const isSearching = ref(false)
let map = null
let marker = null

const CATEGORY_MAP = {
  subway_entrance: '지하철역', station: '기차역', bus_stop: '버스정류장',
  tram_stop: '전차정류장', ferry_terminal: '선착장',
  restaurant: '음식점', cafe: '카페', fast_food: '패스트푸드', bar: '바',
  bakery: '베이커리', ice_cream: '아이스크림',
  hospital: '병원', pharmacy: '약국', clinic: '의원', dentist: '치과',
  school: '학교', university: '대학교', college: '전문대', kindergarten: '유치원',
  library: '도서관', museum: '박물관', gallery: '미술관',
  cinema: '영화관', theatre: '공연장', nightclub: '나이트클럽',
  park: '공원', playground: '놀이터', sports_centre: '스포츠센터',
  swimming_pool: '수영장', gym: '헬스장',
  bank: '은행', atm: 'ATM', post_office: '우체국',
  supermarket: '대형마트', convenience: '편의점', department_store: '백화점',
  mall: '쇼핑몰', marketplace: '시장',
  hotel: '호텔', motel: '모텔', hostel: '호스텔', guest_house: '게스트하우스',
  fuel: '주유소', car_wash: '세차장', parking: '주차장',
  place_of_worship: '종교시설', townhall: '관공서', police: '경찰서',
  fire_station: '소방서', courthouse: '법원',
}

// ── 지도 초기화 ──────────────────────────────────
const initMap = () => {
  if (!window.naver || !mapContainer.value) return

  const lat = props.lat || 37.5665
  const lng = props.lng || 126.9780

  map = new naver.maps.Map(mapContainer.value, {
    center: new naver.maps.LatLng(lat, lng),
    zoom: 15,
    mapTypeControl: true,
  })

  marker = new naver.maps.Marker({
    position: new naver.maps.LatLng(lat, lng),
    map,
  })

  naver.maps.Event.addListener(map, 'click', (e) => {
    showResults.value = false
    moveMarker(e.latlng)
  })

  setTimeout(() => { if (map) naver.maps.Event.trigger(map, 'resize') }, 300)
}

// ── 마커 이동 + 역지오코딩 ──────────────────────
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
    orders: [naver.maps.Service.OrderType.ROAD_ADDR, naver.maps.Service.OrderType.ADDR].join(','),
  }, (status, response) => {
    let addr = ''
    if (status === naver.maps.Service.Status.OK) {
      const v2 = response.v2
      addr = v2.address?.roadAddress || v2.address?.jibunAddress || ''
      if (!addr && v2.results?.length) {
        const r = v2.results[0]
        addr = [r.region.area1.name, r.region.area2.name, r.region.area3.name, r.land?.number1]
          .filter(Boolean).join(' ')
      }
    }
    emit('update:location', { lat: latlng.lat(), lng: latlng.lng(), address: addr })
  })
}

// ── Nominatim 검색 ───────────────────────────────
const searchWithNominatim = async (query) => {
  const params = new URLSearchParams({
    q: `${query} 한국`,
    format: 'json',
    countrycodes: 'kr',
    limit: '7',
    addressdetails: '1',
    'accept-language': 'ko',
  })

  const res = await fetch(`https://nominatim.openstreetmap.org/search?${params}`)
  if (!res.ok) throw new Error('nominatim_error')
  const data = await res.json()

  return data.map(item => {
    const parts = item.display_name.split(',').map(s => s.trim())
    const title = parts[0]
    const addrParts = parts.slice(1)
      .filter(p => p !== '대한민국' && !/^\d{5,}$/.test(p))
      .slice(0, 3)
    const category = CATEGORY_MAP[item.type] || CATEGORY_MAP[item.class] || ''
    return {
      title,
      address: addrParts.join(' '),
      category,
      lat: parseFloat(item.lat),
      lng: parseFloat(item.lon),
    }
  })
}

// ── 네이버 지오코더 폴백 ─────────────────────────
const searchWithNaverGeocode = (query) => {
  return new Promise((resolve) => {
    if (!window.naver?.maps?.Service) { resolve([]); return }
    naver.maps.Service.geocode({ query }, (status, response) => {
      if (status !== naver.maps.Service.Status.OK) { resolve([]); return }
      const addresses = response.v2?.addresses || []
      resolve(addresses.slice(0, 5).map(item => ({
        title: item.roadAddress || item.jibunAddress,
        address: item.jibunAddress || '',
        category: '주소',
        lat: parseFloat(item.y),
        lng: parseFloat(item.x),
      })))
    })
  })
}

// ── 검색 실행 ────────────────────────────────────
const searchPlaces = async () => {
  const query = searchQuery.value.trim()
  if (!query) return

  isSearching.value = true
  searchResults.value = []
  showResults.value = false

  try {
    let results = await searchWithNominatim(query)

    if (!results.length) {
      results = await searchWithNaverGeocode(query)
    }

    if (!results.length) {
      alert('검색 결과가 없습니다. 다른 검색어를 입력해 보세요.')
      return
    }

    searchResults.value = results
    showResults.value = true
  } catch {
    // Nominatim 실패 시 네이버 지오코더로 전환
    const results = await searchWithNaverGeocode(query)
    if (results.length) {
      searchResults.value = results
      showResults.value = true
    } else {
      alert('검색 중 오류가 발생했습니다.')
    }
  } finally {
    isSearching.value = false
  }
}

const selectPlace = (place) => {
  showResults.value = false
  searchQuery.value = place.title
  const latlng = new naver.maps.LatLng(place.lat, place.lng)
  moveMarker(latlng, place.address || place.title)
  map.setZoom(17)
}

const clearSearch = () => {
  searchQuery.value = ''
  searchResults.value = []
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
  <div class="map-selector" @keydown.escape="showResults = false">
    <!-- 검색바 -->
    <div class="search-row">
      <div class="input-wrap">
        <Search class="icon-search" :size="16" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="장소명, 주소 검색 (예: 대방역, 강남구 테헤란로)"
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
        :disabled="isSearching || !searchQuery.trim()"
        @click="searchPlaces"
        type="button"
      >
        <span v-if="isSearching" class="spinner" />
        <span v-else>검색</span>
      </button>
    </div>

    <!-- 검색 결과 드롭다운 -->
    <Transition name="dropdown">
      <div v-if="showResults && searchResults.length" class="results-panel">
        <ul>
          <li
            v-for="(place, i) in searchResults"
            :key="i"
            @click="selectPlace(place)"
          >
            <div class="place-icon">
              <MapPin :size="16" />
            </div>
            <div class="place-info">
              <div class="place-name">{{ place.title }}</div>
              <div class="place-meta">
                <span v-if="place.category" class="place-badge">{{ place.category }}</span>
                <span class="place-addr">{{ place.address }}</span>
              </div>
            </div>
          </li>
        </ul>
        <div class="panel-footer" @click="showResults = false">목록 닫기</div>
      </div>
    </Transition>

    <!-- 지도 -->
    <div ref="mapContainer" class="map-canvas" />
    <p class="map-hint">지도를 직접 클릭해도 장소를 지정할 수 있어요.</p>
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
}

.input-wrap input {
  width: 100%;
  padding: 10px 32px 10px 34px;
  border-radius: var(--radius-md);
  border: 1.5px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.875rem;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-wrap input:focus {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px rgba(var(--accent-primary-rgb), 0.12);
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
  padding: 3px;
  border-radius: 50%;
  transition: background 0.15s;
}

.btn-clear:hover {
  background: var(--border-color);
  color: var(--text-primary);
}

.btn-search {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 0 20px;
  height: 40px;
  background: var(--accent-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius-md);
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  white-space: nowrap;
  min-width: 68px;
  transition: background 0.2s, opacity 0.2s;
}

.btn-search:hover:not(:disabled) {
  background: var(--accent-dark);
}

.btn-search:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

/* 로딩 스피너 */
.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* ── 결과 패널 ── */
.results-panel {
  position: absolute;
  top: 48px;
  left: 0;
  right: 0;
  background: var(--bg-primary, #fff);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  box-shadow: 0 8px 24px rgba(0,0,0,0.14);
  z-index: 300;
  overflow: hidden;
}

.results-panel ul {
  list-style: none;
  margin: 0;
  padding: 6px 0;
}

.results-panel li {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 14px;
  cursor: pointer;
  transition: background 0.13s;
}

.results-panel li:hover {
  background: var(--bg-secondary);
}

.place-icon {
  flex-shrink: 0;
  margin-top: 2px;
  color: var(--accent-primary);
}

.place-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  overflow: hidden;
  min-width: 0;
}

.place-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.place-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.place-badge {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--accent-primary);
  background: rgba(var(--accent-primary-rgb), 0.1);
  border-radius: 4px;
  padding: 1px 6px;
  white-space: nowrap;
}

.place-addr {
  font-size: 0.75rem;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.panel-footer {
  text-align: center;
  padding: 7px;
  font-size: 0.75rem;
  color: var(--text-secondary);
  cursor: pointer;
  border-top: 1px solid var(--border-color);
  transition: background 0.13s;
}

.panel-footer:hover {
  background: var(--bg-secondary);
}

/* 드롭다운 애니메이션 */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s, transform 0.15s;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* ── 지도 ── */
.map-canvas {
  width: 100%;
  height: 300px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background: #eee;
  overflow: hidden;
}

.map-hint {
  font-size: 0.72rem;
  color: var(--text-secondary);
  text-align: center;
  margin: 0;
}

[data-theme="dark"] .map-canvas {
  filter: brightness(0.92) saturate(0.9);
}
</style>
