<template>
  <div class="relative w-full h-full">
    <div ref="mapContainer" class="w-full h-full"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onBeforeUnmount } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'
import { useBooksStore } from '@/stores/books'
import { useUIStore } from '@/stores/ui'
import { generateBookColor, getTitleInitials } from '@/utils/colors'

const booksStore = useBooksStore()
const uiStore = useUIStore()

const mapContainer = ref(null)
const mapInstance = ref(null)
const markerClusterGroup = ref(null)
const markerLayer = ref(null) // plain layer group for unclustered mode
const markers = ref([]) // all individual markers
let updatingFromMap = false // guard to prevent moveend → watcher → setView loop

// Stadia Maps — Stamen Watercolor tiles for vintage aesthetic
const STADIA_KEY = import.meta.env.VITE_STADIA_API_KEY || ''
const WATERCOLOR_URL = `https://tiles.stadiamaps.com/tiles/stamen_watercolor/{z}/{x}/{y}.jpg${STADIA_KEY ? '?api_key=' + STADIA_KEY : ''}`
const LABELS_URL = `https://tiles.stadiamaps.com/tiles/stamen_terrain_labels/{z}/{x}/{y}{r}.png${STADIA_KEY ? '?api_key=' + STADIA_KEY : ''}`
const STADIA_ATTRIBUTION = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> &copy; <a href="https://stamen.com/">Stamen Design</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'

// Fallback OSM tiles if no Stadia key
const OSM_URL = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
const OSM_ATTRIBUTION = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'

// Create marker data from books with locations
const bookMarkers = computed(() => {
  const items = []
  booksStore.booksWithLocations.forEach(book => {
    if (book.locations && Array.isArray(book.locations)) {
      book.locations.forEach(location => {
        const lat = location.lat || location.latitude
        const lng = location.lng || location.longitude
        if (lat && lng) {
          items.push({ book, location, lat, lng })
        }
      })
    }
  })
  return items
})

// Create a Leaflet DivIcon for a book marker
function createBookIcon(book) {
  const color = generateBookColor(book)
  const initials = getTitleInitials(book.title)
  return L.divIcon({
    className: 'book-marker-icon',
    html: `<div class="book-marker" style="
      background-color: ${color};
      width: 36px;
      height: 36px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-weight: bold;
      font-size: 12px;
      border: 2px solid white;
      cursor: pointer;
      box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    ">${initials}</div>`,
    iconSize: [36, 36],
    iconAnchor: [18, 18],
  })
}

function initializeMap() {
  console.log('[LeafletMap] initializeMap called')
  if (!mapContainer.value) return

  const center = uiStore.mapCenter || { lat: 20, lng: 30 }
  const zoom = uiStore.mapZoom || 3

  const map = L.map(mapContainer.value, {
    center: [center.lat, center.lng],
    zoom,
    zoomControl: false, // we have custom zoom controls
    attributionControl: true,
  })

  if (STADIA_KEY) {
    // Watercolor base + terrain labels overlay
    L.tileLayer(WATERCOLOR_URL, {
      attribution: STADIA_ATTRIBUTION,
      maxZoom: 18,
    }).addTo(map)
    L.tileLayer(LABELS_URL, {
      attribution: '',
      maxZoom: 18,
    }).addTo(map)
  } else {
    L.tileLayer(OSM_URL, {
      attribution: OSM_ATTRIBUTION,
      maxZoom: 18,
    }).addTo(map)
  }

  // Sync map state back to store (guarded to prevent feedback loop)
  map.on('zoomend', () => {
    updatingFromMap = true
    uiStore.setMapZoom(map.getZoom())
    updatingFromMap = false
  })
  map.on('moveend', () => {
    updatingFromMap = true
    const c = map.getCenter()
    uiStore.setMapCenter({ lat: c.lat, lng: c.lng })
    const b = map.getBounds()
    uiStore.setMapBounds({
      north: b.getNorth(),
      south: b.getSouth(),
      east: b.getEast(),
      west: b.getWest(),
    })
    updatingFromMap = false
  })

  mapInstance.value = map
  console.log('[LeafletMap] Map initialized, creating markers')
  createMarkers()
}

function createMarkers() {
  if (!mapInstance.value) return
  console.log(`[LeafletMap] createMarkers: ${bookMarkers.value.length} markers to create`)

  clearMarkers()

  // Create marker cluster group
  markerClusterGroup.value = L.markerClusterGroup({
    maxClusterRadius: 50,
    disableClusteringAtZoom: 16,
    spiderfyOnMaxZoom: true,
    showCoverageOnHover: false,
    chunkedLoading: true,
    iconCreateFunction: (cluster) => {
      const count = cluster.getChildCount()
      let size = 'small'
      if (count >= 100) size = 'large'
      else if (count >= 10) size = 'medium'
      return L.divIcon({
        html: `<div class="cluster-icon cluster-${size}">${count}</div>`,
        className: 'book-cluster-icon',
        iconSize: L.point(40, 40),
      })
    },
  })

  // Plain layer group for unclustered mode
  markerLayer.value = L.layerGroup()

  // Create all markers
  markers.value = bookMarkers.value.map(({ book, location, lat, lng }) => {
    const marker = L.marker([lat, lng], {
      icon: createBookIcon(book),
      title: `${book.title} by ${book.author}`,
    })

    // Popup with book info
    marker.bindPopup(`
      <div style="min-width: 160px; font-family: 'Libre Baskerville', Georgia, serif;">
        <strong style="font-size: 13px;">${book.title}</strong><br>
        <em style="font-size: 12px; color: #6B7C7A;">${book.author}</em><br>
        <span style="font-size: 11px; color: #999;">${location.city || location.place || ''}, ${location.country || ''}</span>
      </div>
    `, { closeButton: true, maxWidth: 250 })

    marker.on('click', () => {
      uiStore.showBookDetails(book)
    })

    return marker
  })

  updateClustering()
}

function clearMarkers() {
  if (markerClusterGroup.value) {
    markerClusterGroup.value.clearLayers()
    if (mapInstance.value && mapInstance.value.hasLayer(markerClusterGroup.value)) {
      mapInstance.value.removeLayer(markerClusterGroup.value)
    }
  }
  if (markerLayer.value) {
    markerLayer.value.clearLayers()
    if (mapInstance.value && mapInstance.value.hasLayer(markerLayer.value)) {
      mapInstance.value.removeLayer(markerLayer.value)
    }
  }
  markers.value = []
}

function updateClustering() {
  if (!mapInstance.value) return

  // Remove both layers first
  if (markerClusterGroup.value && mapInstance.value.hasLayer(markerClusterGroup.value)) {
    mapInstance.value.removeLayer(markerClusterGroup.value)
  }
  if (markerLayer.value && mapInstance.value.hasLayer(markerLayer.value)) {
    mapInstance.value.removeLayer(markerLayer.value)
  }

  if (uiStore.isClusteringEnabled) {
    markerClusterGroup.value.clearLayers()
    markers.value.forEach(m => markerClusterGroup.value.addLayer(m))
    mapInstance.value.addLayer(markerClusterGroup.value)
  } else {
    markerLayer.value.clearLayers()
    markers.value.forEach(m => markerLayer.value.addLayer(m))
    mapInstance.value.addLayer(markerLayer.value)
  }
}

// Fit map to show markers from specific books (or all markers)
function fitMapToMarkers(books = null) {
  if (!mapInstance.value) return

  const points = []

  if (books && books.length > 0) {
    books.forEach(book => {
      if (book.locations && Array.isArray(book.locations)) {
        book.locations.forEach(loc => {
          const lat = loc.lat || loc.latitude
          const lng = loc.lng || loc.longitude
          if (lat && lng) points.push([lat, lng])
        })
      }
    })
  } else {
    markers.value.forEach(m => {
      const ll = m.getLatLng()
      points.push([ll.lat, ll.lng])
    })
  }

  if (points.length === 0) return

  const bounds = L.latLngBounds(points)
  mapInstance.value.fitBounds(bounds, { padding: [40, 40], maxZoom: 15 })
}

// Watch clustering toggle
watch(() => uiStore.isClusteringEnabled, () => {
  updateClustering()
})

// Watch book data changes
watch(() => bookMarkers.value.length, () => {
  if (mapInstance.value) {
    createMarkers()
  }
})

// Watch map center/zoom from store (for preset locations, geocoding, etc.)
// Skip when the change originated from map events (prevents infinite loop)
watch(() => uiStore.mapCenter, (newCenter) => {
  if (updatingFromMap) return
  if (newCenter && mapInstance.value) {
    console.log('[LeafletMap] Store mapCenter changed externally, calling setView')
    mapInstance.value.setView([newCenter.lat, newCenter.lng], uiStore.mapZoom, { animate: true })
  }
}, { deep: true })

watch(() => uiStore.mapZoom, (newZoom) => {
  if (updatingFromMap) return
  if (newZoom && mapInstance.value && mapInstance.value.getZoom() !== newZoom) {
    console.log('[LeafletMap] Store mapZoom changed externally, calling setZoom')
    mapInstance.value.setZoom(newZoom)
  }
})

// Watch for fitBounds trigger
watch(() => uiStore.shouldFitBounds, () => {
  if (uiStore.shouldFitBounds > 0 && uiStore.searchResults.length > 0) {
    fitMapToMarkers(uiStore.searchResults)
  }
})

onMounted(() => {
  // Small delay to ensure DOM is ready
  setTimeout(() => {
    initializeMap()
  }, 100)
})

onBeforeUnmount(() => {
  if (mapInstance.value) {
    mapInstance.value.remove()
    mapInstance.value = null
  }
})
</script>

<style>
/* Book marker icon - remove default leaflet icon styling */
.book-marker-icon {
  background: none !important;
  border: none !important;
}

.book-marker {
  transition: transform 0.2s ease;
}

.book-marker:hover {
  transform: scale(1.2);
  z-index: 1000 !important;
}

/* Cluster icon styling - parchment/vintage theme */
.book-cluster-icon {
  background: none !important;
  border: none !important;
}

.cluster-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  color: white;
  font-weight: bold;
  font-family: 'Libre Baskerville', Georgia, serif;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

.cluster-small {
  background-color: #3D6960;
  width: 36px;
  height: 36px;
  font-size: 13px;
}

.cluster-medium {
  background-color: #C17A3A;
  width: 44px;
  height: 44px;
  font-size: 14px;
}

.cluster-large {
  background-color: #8B4513;
  width: 52px;
  height: 52px;
  font-size: 15px;
}

/* Override default Leaflet popup styling for vintage feel */
.leaflet-popup-content-wrapper {
  border-radius: 8px;
  box-shadow: 0 3px 12px rgba(0,0,0,0.2);
}

.leaflet-popup-content {
  margin: 10px 14px;
}
</style>
