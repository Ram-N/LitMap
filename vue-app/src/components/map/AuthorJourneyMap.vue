<template>
  <div class="relative w-full h-64 bg-parchment-100 rounded-lg overflow-hidden">
    <div ref="mapContainer" class="w-full h-full"></div>

    <!-- Info overlay -->
    <div class="absolute bottom-3 left-3 right-3 bg-white/90 backdrop-blur-sm px-3 py-2 rounded-lg text-xs text-text-secondary">
      {{ locations.length }} locations across {{ uniqueCountries }} countries
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
  locations: {
    type: Array,
    required: true
  }
})

const mapContainer = ref(null)
let map = null
let markers = []

const uniqueCountries = computed(() => {
  const countries = new Set(props.locations.map(loc => loc.country))
  return countries.size
})

function initMap() {
  if (!mapContainer.value) return

  if (map) {
    map.remove()
    map = null
  }

  const center = props.locations[0]
    ? [props.locations[0].lat || props.locations[0].latitude, props.locations[0].lng || props.locations[0].longitude]
    : [40, -3]

  map = L.map(mapContainer.value, {
    zoom: 4,
    center,
    zoomControl: false,
    attributionControl: false,
  })

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
  }).addTo(map)

  // Add markers
  markers = props.locations.map(loc => {
    const lat = loc.lat || loc.latitude
    const lng = loc.lng || loc.longitude
    return L.circleMarker([lat, lng], {
      radius: 6,
      fillColor: '#3D6960',
      color: '#fff',
      weight: 2,
      fillOpacity: 0.8,
    }).addTo(map).bindTooltip(loc.city || loc.country || '')
  })

  // Fit bounds
  if (props.locations.length > 0) {
    const points = props.locations.map(loc => [
      loc.lat || loc.latitude,
      loc.lng || loc.longitude
    ])
    map.fitBounds(L.latLngBounds(points), { padding: [20, 20] })
  }
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
