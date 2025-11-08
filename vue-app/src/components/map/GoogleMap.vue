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
import { ref, computed, onMounted } from 'vue'
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
  console.log('Clicked book:', book.title)
  // TODO: Show book details in bottom sheet
}

onMounted(() => {
  console.log('GoogleMap component mounted with gmp-map web component')
  console.log(`Will render ${bookMarkers.value.length} markers`)
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
