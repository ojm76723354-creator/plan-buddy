<script setup>
import { ref, onMounted, defineEmits, defineProps, watch, nextTick } from 'vue'
import { Search } from 'lucide-vue-next'

const props = defineProps({
  lat: Number,
  lng: Number
})

const emit = defineEmits(['update:location'])
const mapContainer = ref(null)
const searchQuery = ref('')
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
    const latlng = e.latlng
    moveMarker(latlng)
  })

  // Ensure map occupies full container if it was hidden initially
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
    // Reverse geocode to get address if not provided
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
          addr = result.results[0].region.area1.name + ' ' + 
                 result.results[0].region.area2.name + ' ' + 
                 result.results[0].region.area3.name + ' ' + 
                 result.results[0].land.number1
        }
      }
      emit('update:location', { lat: latlng.lat(), lng: latlng.lng(), address: addr })
    })
  }
}

const searchAddress = () => {
  if (!searchQuery.value.trim()) return

  if (!window.naver || !window.naver.maps.Service) {
    alert('지도 서비스가 준비되지 않았습니다.')
    return
  }

  naver.maps.Service.geocode({
    query: searchQuery.value
  }, (status, response) => {
    if (status !== naver.maps.Service.Status.OK) {
      alert('검색 중 오류가 발생했습니다.')
      return
    }

    const result = response.v2
    const items = result.addresses

    if (items.length === 0) {
      alert('검색 결과가 없습니다. 정식 주소를 입력해 주세요.')
      return
    }

    const item = items[0]
    const latlng = new naver.maps.LatLng(item.y, item.x)
    
    // Use the road address or jibun address from the result
    const address = item.roadAddress || item.jibunAddress
    moveMarker(latlng, address)
  })
}

onMounted(async () => {
  await nextTick()
  // Small delay to allow modal animations to settle
  setTimeout(initMap, 100)
})

// Update map if props change (e.g. when editing an existing event)
watch(() => [props.lat, props.lng], ([newLat, newLng]) => {
  if (map && marker && newLat && newLng) {
    const pos = new naver.maps.LatLng(newLat, newLng)
    map.setCenter(pos)
    marker.setPosition(pos)
  }
})
</script>

<template>
  <div class="map-selector">
    <div class="search-bar">
      <div class="input-wrapper">
        <Search class="search-icon" :size="18" />
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="장소나 주소를 검색하세요" 
          @keyup.enter="searchAddress"
        />
      </div>
      <button class="search-btn" @click="searchAddress">검색</button>
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

.search-btn:hover {
  background-color: var(--accent-dark);
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

/* Dark mode adjustments if needed */
[data-theme="dark"] .map-canvas {
  filter: grayscale(1) invert(0.9) hue-rotate(180deg);
}
</style>
