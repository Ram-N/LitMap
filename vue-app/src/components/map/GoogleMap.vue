<template>
  <div class="relative w-full h-full">
    <!-- Google Map using Web Component -->
    <gmp-map
      ref="mapElement"
      :center="uiStore.mapCenter || { lat: 20.5937, lng: 78.9629 }"
      :zoom="uiStore.mapZoom"
      :map-id="mapId"
      class="w-full h-full"
    >
      <!-- Markers are created programmatically in JavaScript for clustering support -->
    </gmp-map>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onBeforeUnmount } from 'vue'
import { MarkerClusterer } from '@googlemaps/markerclusterer'
import { useBooksStore } from '@/stores/books'
import { useUIStore } from '@/stores/ui'
import { generateBookColor, getTitleInitials } from '@/utils/colors'

const booksStore = useBooksStore()
const uiStore = useUIStore()

// Google Maps configuration
const mapId = import.meta.env.VITE_GOOGLE_MAPS_MAP_ID

// Map element reference
const mapElement = ref(null)
const mapInstance = ref(null)
const markerInstances = ref([])
const markerClusterer = ref(null)

// Create marker data from books with locations
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

// Create custom marker content
function createMarkerContent(book) {
  const div = document.createElement('div')
  div.className = 'book-marker'
  div.style.cssText = `
    background-color: ${generateBookColor(book)};
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: bold;
    font-size: 14px;
    border: 2px solid white;
    cursor: pointer;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    transition: transform 0.2s ease;
  `
  div.textContent = getTitleInitials(book.title)

  // Add hover effect
  div.addEventListener('mouseenter', () => {
    div.style.transform = 'scale(1.2)'
    div.style.zIndex = '1000'
  })
  div.addEventListener('mouseleave', () => {
    div.style.transform = 'scale(1)'
    div.style.zIndex = 'auto'
  })

  return div
}

// Initialize map and markers
async function initializeMap() {
  console.log('Initializing map...')

  // Check if Google Maps is loaded
  if (typeof google === 'undefined' || !google.maps) {
    console.warn('Google Maps not loaded yet, retrying...')
    setTimeout(initializeMap, 200)
    return
  }

  if (!mapElement.value) {
    console.warn('Map element not ready, retrying...')
    setTimeout(initializeMap, 100)
    return
  }

  // Get the map instance from gmp-map element
  // Try different properties to access the internal Google Map
  let map = mapElement.value.innerMap ||
            mapElement.value.map ||
            mapElement.value._map ||
            mapElement.value.$map

  // If still not found, try getting it from the element's properties
  if (!map && mapElement.value) {
    console.log('Checking all properties of gmp-map element:', Object.keys(mapElement.value))
    // Access the private property that holds the map
    const keys = Object.keys(mapElement.value)
    const mapKey = keys.find(key => key.includes('map') || key.includes('Map'))
    if (mapKey) {
      map = mapElement.value[mapKey]
      console.log(`Found map via property: ${mapKey}`)
    }
  }

  if (!map) {
    console.warn('Map instance not ready, retrying...')
    setTimeout(initializeMap, 100)
    return
  }

  mapInstance.value = map
  console.log('Map instance obtained:', map)

  try {
    // Load the marker library
    const { AdvancedMarkerElement } = await google.maps.importLibrary('marker')
    console.log('AdvancedMarkerElement loaded:', AdvancedMarkerElement)

    // Clear existing markers
    clearMarkers()

    // Create marker instances
    console.log('Creating', bookMarkers.value.length, 'markers...')

    markerInstances.value = bookMarkers.value.map(markerData => {
      const marker = new AdvancedMarkerElement({
        map: map,
        position: markerData.position,
        content: createMarkerContent(markerData.book),
        title: `${markerData.book.title} by ${markerData.book.author}`
      })

      // Add click listener
      marker.addListener('click', () => {
        handleMarkerClick(markerData.book)
      })

      return marker
    })

    console.log('Created', markerInstances.value.length, 'marker instances')

    // Add zoom change listener to sync zoom level with store
    map.addListener('zoom_changed', () => {
      const currentZoom = map.getZoom()
      if (currentZoom !== undefined && currentZoom !== uiStore.mapZoom) {
        uiStore.setMapZoom(currentZoom)
      }
    })

    // Initialize clustering if enabled
    updateClustering()
  } catch (error) {
    console.error('Error initializing map markers:', error)
    // Retry after a delay
    setTimeout(initializeMap, 500)
  }
}

// Fit map to show markers from specific books (or all markers if no books specified)
function fitMapToMarkers(books = null) {
  if (!mapInstance.value) {
    return
  }

  const bounds = new google.maps.LatLngBounds()
  let hasLocations = false

  // If books are specified, fit to those books' locations
  if (books && books.length > 0) {
    books.forEach(book => {
      if (book.locations && Array.isArray(book.locations)) {
        book.locations.forEach(location => {
          const lat = location.lat || location.latitude
          const lng = location.lng || location.longitude
          if (lat && lng) {
            bounds.extend({ lat, lng })
            hasLocations = true
          }
        })
      }
    })
  } else {
    // Fit to all markers
    if (markerInstances.value.length === 0) {
      return
    }
    markerInstances.value.forEach(marker => {
      bounds.extend(marker.position)
      hasLocations = true
    })
  }

  if (!hasLocations) {
    console.warn('No locations found to fit bounds')
    return
  }

  mapInstance.value.fitBounds(bounds)

  // Update the store's zoom level after fitBounds completes
  google.maps.event.addListenerOnce(mapInstance.value, 'bounds_changed', () => {
    const zoom = mapInstance.value.getZoom()
    if (zoom > 15) {
      mapInstance.value.setZoom(15)
      uiStore.setMapZoom(15)
    } else {
      uiStore.setMapZoom(zoom)
    }
  })

  console.log('Fitted map to show markers')
}

// Handle marker click
function handleMarkerClick(book) {
  uiStore.showBookDetails(book)
}

// Clear all markers
function clearMarkers() {
  console.log('Clearing markers...')

  // Clear clusterer
  if (markerClusterer.value) {
    markerClusterer.value.clearMarkers()
    markerClusterer.value = null
  }

  // Remove all marker instances
  markerInstances.value.forEach(marker => {
    marker.map = null
  })
  markerInstances.value = []
}

// Update clustering based on toggle state
function updateClustering() {
  console.log('updateClustering called, enabled:', uiStore.isClusteringEnabled)
  console.log('Marker instances:', markerInstances.value.length)
  console.log('Map instance:', mapInstance.value)

  if (!mapInstance.value || markerInstances.value.length === 0) {
    console.warn('Cannot update clustering - map or markers not ready, will retry')
    // Retry after a short delay if map is still initializing
    setTimeout(() => {
      if (mapInstance.value && markerInstances.value.length > 0) {
        updateClustering()
      }
    }, 200)
    return
  }

  // Clear existing clusterer
  if (markerClusterer.value) {
    console.log('Clearing existing clusterer')
    markerClusterer.value.clearMarkers()
    markerClusterer.value = null
  }

  if (uiStore.isClusteringEnabled) {
    console.log('Enabling clustering...')
    // Create new clusterer
    markerClusterer.value = new MarkerClusterer({
      map: mapInstance.value,
      markers: markerInstances.value,
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

    console.log('Clustering enabled with', markerClusterer.value.clusters.length, 'clusters')
  } else {
    console.log('Clustering disabled, showing individual markers')
    // Re-add all markers to map individually
    markerInstances.value.forEach(marker => {
      marker.map = mapInstance.value
    })
  }
}

// Watch for clustering toggle changes
watch(() => uiStore.isClusteringEnabled, () => {
  console.log('Clustering toggle changed to:', uiStore.isClusteringEnabled)
  updateClustering()
})

// Watch for book changes and recreate markers
watch(() => bookMarkers.value.length, () => {
  console.log('Book markers changed, reinitializing...')
  if (mapInstance.value) {
    initializeMap()
  }
})

// Watch for fitBounds trigger (from author/location searches)
watch(() => uiStore.shouldFitBounds, () => {
  if (uiStore.shouldFitBounds > 0 && uiStore.searchResults.length > 0) {
    console.log('Fitting bounds to search results')
    fitMapToMarkers(uiStore.searchResults)
  }
})

onMounted(() => {
  console.log('GoogleMap component mounted')
  console.log('Total book markers:', bookMarkers.value.length)

  // Wait for map element to be ready
  setTimeout(() => {
    initializeMap()
  }, 500)
})

onBeforeUnmount(() => {
  clearMarkers()
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
