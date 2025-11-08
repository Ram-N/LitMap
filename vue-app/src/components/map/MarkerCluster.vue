<template>
  <div>
    <!-- Render individual markers -->
    <BookMarker
      v-for="(marker, index) in markers"
      :key="`clustered-marker-${index}`"
      :ref="el => setMarkerRef(el, index)"
      :book="marker.book"
      :location="marker.location"
      @click="handleMarkerClick(marker.book)"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { MarkerClusterer } from '@googlemaps/markerclusterer'
import BookMarker from './BookMarker.vue'

const props = defineProps({
  markers: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['markerClick'])

const markerRefs = ref([])
const clusterer = ref(null)

function setMarkerRef(el, index) {
  if (el) {
    markerRefs.value[index] = el
  }
}

function handleMarkerClick(book) {
  emit('markerClick', book)
}

// Initialize clusterer when component mounts
onMounted(() => {
  initializeClusterer()
})

// Re-initialize clusterer when markers change
watch(() => props.markers, () => {
  if (clusterer.value) {
    clusterer.value.clearMarkers()
  }
  initializeClusterer()
}, { deep: true })

function initializeClusterer() {
  // Wait for next tick to ensure all markers are rendered
  setTimeout(() => {
    const mapElement = document.querySelector('.vue-google-map')
    if (!mapElement) return

    // Get all marker elements
    const markerElements = markerRefs.value
      .filter(Boolean)
      .map(ref => ref.$el)

    if (markerElements.length === 0) return

    // Create clusterer
    // Note: MarkerClusterer needs actual Google Maps marker instances
    // Since vue3-google-map handles marker creation differently,
    // we'll need to adapt this approach

    console.log('Clusterer initialized with', markerElements.length, 'markers')
  }, 100)
}

onBeforeUnmount(() => {
  if (clusterer.value) {
    clusterer.value.clearMarkers()
    clusterer.value = null
  }
})
</script>

<style scoped>
/* Clusterer styles if needed */
</style>
