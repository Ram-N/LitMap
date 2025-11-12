<template>
  <div class="relative w-full h-full">
    <!-- Map Controls -->
    <MapControls class="absolute top-4 left-4 right-4 z-10" />

    <!-- Google Map using Web Component -->
    <gmp-map
      ref="mapElement"
      :center="uiStore.mapCenter || { lat: 20.5937, lng: 78.9629 }"
      :zoom="uiStore.mapZoom"
      :map-id="mapId"
      class="w-full h-full"
    >
      <!-- Advanced Markers for each book location -->
      <gmp-advanced-marker
        v-for="(marker, index) in bookMarkers"
        :key="`${marker.book.id}-${index}`"
        :ref="el => setMarkerRef(el, index)"
        :position="marker.position"
        :title="`${marker.book.title} by ${marker.book.author}`"
        gmp-clickable
        @gmp-click="handleMarkerClick(marker.book)"
      >
        <!-- Custom marker content -->
        <div
          class="book-marker"
          :style="{
            backgroundColor: generateBookColor(marker.book),
            width: '40px',
            height: '40px',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontWeight: 'bold',
            fontSize: '14px',
            border: '2px solid white',
            cursor: 'pointer',
            boxShadow: '0 2px 6px rgba(0,0,0,0.3)'
          }"
        >
          {{ getTitleInitials(marker.book.title) }}
        </div>
      </gmp-advanced-marker>
    </gmp-map>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onBeforeUnmount } from 'vue'
import { MarkerClusterer } from '@googlemaps/markerclusterer'
import MapControls from './MapControls.vue'
import { useBooksStore } from '@/stores/books'
import { useUIStore } from '@/stores/ui'
import { generateBookColor, getTitleInitials } from '@/utils/colors'

const booksStore = useBooksStore()
const uiStore = useUIStore()

// Google Maps configuration
const mapId = import.meta.env.VITE_GOOGLE_MAPS_MAP_ID

// Map element reference
const mapElement = ref(null)
const markerClusterer = ref(null)
const markerElements = ref([])
const mapInstance = ref(null)

// Create markers from books with locations
const bookMarkers = computed(() => {
  const markers = []

  booksStore.booksWithLocations.forEach(book => {
    if (book.locations && Array.isArray(book.locations)) {
      book.locations.forEach(location => {
        const lat = location.lat || location.latitude
        const lng = location.lng || location.longitude

        if (lat && lng) {
          markers.push({
            book,
            location,
            position: { lat, lng }
          })
        }
      })
    }
  })

  return markers
})

// Handle marker click
function handleMarkerClick(book) {
  uiStore.showBookDetails(book)
}

// Store marker references
function setMarkerRef(el, index) {
  if (el) {
    markerElements.value[index] = el
  }
}

// Initialize clustering
function initializeClustering() {
  // Get the map instance from the gmp-map element
  if (!mapElement.value) {
    return
  }

  // Access the internal map - might be 'innerMap' or just the element itself exposes the map
  const map = mapElement.value.innerMap || mapElement.value.map

  if (!map) {
    // Try again after a delay if map isn't ready
    setTimeout(initializeClustering, 500)
    return
  }

  mapInstance.value = map

  // Clear existing clusterer
  if (markerClusterer.value) {
    markerClusterer.value.clearMarkers()
    markerClusterer.value = null
  }

  // Only create clusterer if clustering is enabled
  if (!uiStore.isClusteringEnabled) {
    return
  }

  // Get actual marker instances from the gmp-advanced-marker elements
  const markers = markerElements.value
    .filter(Boolean)
    .map(el => el.marker || el.$el?.marker || el)
    .filter(Boolean)

  if (markers.length === 0) {
    console.warn('No markers available for clustering')
    return
  }

  // Create new clusterer
  markerClusterer.value = new MarkerClusterer({
    map: mapInstance.value,
    markers: markers,
    zoomOnClick: false,
    gridSize: 50,
    maxZoom: 15,
  })

  // Add cluster click handler
  markerClusterer.value.addListener('clusterclick', (cluster) => {
    const bounds = cluster.getBounds()
    mapInstance.value.fitBounds(bounds)

    // Limit zoom level
    google.maps.event.addListenerOnce(mapInstance.value, 'zoom_changed', () => {
      if (mapInstance.value.getZoom() > 10) {
        mapInstance.value.setZoom(10)
      }
    })
  })
}

// Watch for clustering toggle
watch(() => uiStore.isClusteringEnabled, (enabled) => {
  if (enabled) {
    initializeClustering()
  } else if (markerClusterer.value) {
    markerClusterer.value.clearMarkers()
    markerClusterer.value = null
  }
})

// Watch for marker changes
watch(() => bookMarkers.value, () => {
  // Re-initialize clustering when markers change
  setTimeout(() => {
    initializeClustering()
  }, 500)
}, { deep: true })

onMounted(() => {
  // Wait for map to be ready, then initialize clustering
  setTimeout(() => {
    initializeClustering()
  }, 1000)
})

onBeforeUnmount(() => {
  if (markerClusterer.value) {
    markerClusterer.value.clearMarkers()
    markerClusterer.value = null
  }
})
</script>

<style>
/* Force Advanced Markers to be visible and interactive */
gmp-advanced-marker {
  pointer-events: auto !important;
  opacity: 1 !important;
  visibility: visible !important;
}

/* Custom marker styles */
.book-marker {
  transition: transform 0.2s ease;
}

.book-marker:hover {
  transform: scale(1.2);
  z-index: 1000;
}
</style>
