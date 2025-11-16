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
import { ref, computed, onMounted, watch } from 'vue'

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

async function initMap() {
  if (!mapContainer.value || !window.google) return

  // Create map
  const { Map } = await google.maps.importLibrary("maps")
  const { AdvancedMarkerElement } = await google.maps.importLibrary("marker")

  // Get center from first location or default
  const center = props.locations[0]
    ? { lat: props.locations[0].lat, lng: props.locations[0].lng }
    : { lat: 40, lng: -3 }

  map = new Map(mapContainer.value, {
    zoom: 4,
    center: center,
    mapId: 'author-journey-map',
    disableDefaultUI: true,
    gestureHandling: 'greedy',
    styles: [
      {
        featureType: 'all',
        elementType: 'geometry',
        stylers: [{ saturation: -20 }]
      }
    ]
  })

  // Add markers for all locations
  markers = props.locations.map(location => {
    const marker = new AdvancedMarkerElement({
      map,
      position: { lat: location.lat, lng: location.lng },
      title: location.city || location.country
    })

    return marker
  })

  // Fit bounds to show all markers
  if (props.locations.length > 0) {
    const bounds = new google.maps.LatLngBounds()
    props.locations.forEach(loc => {
      bounds.extend({ lat: loc.lat, lng: loc.lng })
    })
    map.fitBounds(bounds)
  }
}

onMounted(() => {
  initMap()
})

watch(() => props.locations, () => {
  if (map) {
    // Clear old markers
    markers.forEach(marker => marker.map = null)
    // Re-init map
    initMap()
  }
})
</script>
