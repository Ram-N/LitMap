<template>
  <div class="relative w-full h-full">
    <div ref="mapContainer" class="w-full h-full"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
  locations: {
    type: Array,
    required: true
  },
  bookTitle: {
    type: String,
    default: ''
  }
})

const mapContainer = ref(null)
let map = null
let layerGroup = null

function getLatLng(loc) {
  return [loc.lat || loc.latitude, loc.lng || loc.longitude]
}

function formatLabel(loc) {
  if (loc.city && loc.country) return `${loc.city}, ${loc.country}`
  return loc.city || loc.place || loc.country || ''
}

function initMap() {
  if (!mapContainer.value || props.locations.length === 0) return

  if (map) {
    map.remove()
    map = null
  }

  const points = props.locations.map(getLatLng)

  map = L.map(mapContainer.value, {
    zoomControl: true,
    attributionControl: false,
  })

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
  }).addTo(map)

  layerGroup = L.layerGroup().addTo(map)

  // River-like polyline — bottom layer: thick semi-transparent teal
  L.polyline(points, {
    weight: 6,
    color: '#3D6960',
    opacity: 0.55,
    lineCap: 'round',
    lineJoin: 'round',
  }).addTo(layerGroup)

  // River-like polyline — top layer: thin dashed white overlay
  L.polyline(points, {
    weight: 2,
    color: '#fff',
    opacity: 0.8,
    dashArray: '6, 10',
    lineCap: 'round',
    lineJoin: 'round',
  }).addTo(layerGroup)

  // Numbered stop markers
  props.locations.forEach((loc, index) => {
    const latlng = getLatLng(loc)
    const isEndpoint = index === 0 || index === props.locations.length - 1
    const bgColor = isEndpoint ? '#C17A3A' : '#3D6960'

    const icon = L.divIcon({
      className: 'journey-stop-icon',
      html: `<div style="
        width: 28px; height: 28px;
        border-radius: 50%;
        background: ${bgColor};
        color: #fff;
        border: 3px solid #fff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: 600;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
      ">${index + 1}</div>`,
      iconSize: [28, 28],
      iconAnchor: [14, 14],
    })

    const marker = L.marker(latlng, { icon }).addTo(layerGroup)

    const label = formatLabel(loc)
    if (label) {
      marker.bindTooltip(label, {
        permanent: true,
        direction: 'top',
        offset: [0, -18],
        className: 'journey-label',
      })
    }
  })

  // Fit bounds
  map.fitBounds(L.latLngBounds(points), { padding: [50, 50] })
}

onMounted(() => {
  initMap()
})

onBeforeUnmount(() => {
  if (map) {
    map.remove()
    map = null
  }
})

watch(() => props.locations, () => {
  initMap()
})
</script>

<style>
.journey-stop-icon {
  background: transparent !important;
  border: none !important;
}

.journey-label {
  background: #fff;
  border: 1px solid #d4c5a9;
  border-radius: 4px;
  padding: 2px 8px;
  font-family: 'Georgia', serif;
  font-size: 12px;
  color: #3d3d3d;
  box-shadow: 0 1px 4px rgba(0,0,0,0.15);
}

.journey-label::before {
  display: none !important;
}
</style>
