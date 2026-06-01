<script setup>
import { ref, onMounted, defineEmits, defineProps } from 'vue'

const props = defineProps({
  lat: Number,
  lng: Number
})

const emit = defineEmits(['update:location'])
const mapContainer = ref(null)
let map = null
let marker = null

onMounted(() => {
  if (!window.naver) {
    console.error('Naver Maps API not loaded')
    return
  }

  const initialLat = props.lat || 37.5665
  const initialLng = props.lng || 126.9780

  const mapOptions = {
    center: new naver.maps.LatLng(initialLat, initialLng),
    zoom: 15
  }

  map = new naver.maps.Map(mapContainer.value, mapOptions)

  marker = new naver.maps.Marker({
    position: new naver.maps.LatLng(initialLat, initialLng),
    map: map
  })

  naver.maps.Event.addListener(map, 'click', (e) => {
    const latlng = e.latlng
    marker.setPosition(latlng)
    emit('update:location', { lat: latlng.lat(), lng: latlng.lng() })
  })
})
</script>

<template>
  <div class="map-selector">
    <div ref="mapContainer" class="map-canvas"></div>
    <p class="map-hint">지도를 클릭하여 약속 장소를 지정하세요.</p>
  </div>
</template>

<style scoped>
.map-selector {
  width: 100%;
}
.map-canvas {
  width: 100%;
  height: 250px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}
.map-hint {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
  text-align: center;
}
</style>
