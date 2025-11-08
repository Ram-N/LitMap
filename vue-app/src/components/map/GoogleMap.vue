<template>
  <div class="relative w-full h-full">
    <!-- Map Controls -->
    <MapControls class="absolute top-4 left-4 right-4 z-10" />

    <!-- Google Map -->
    <div ref="mapContainer" class="w-full h-full"></div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import MapControls from './MapControls.vue'
import { useBooksStore } from '@/stores/books'
import { useUIStore } from '@/stores/ui'
import { useMap } from '@/composables/useMap'
import { generateBookColor, getTitleInitials } from '@/utils/colors'

const booksStore = useBooksStore()
const uiStore = useUIStore()
const { googleMapRef } = useMap()

// Google Maps configuration
const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY
const mapId = import.meta.env.VITE_GOOGLE_MAPS_MAP_ID

// Map container reference
const mapContainer = ref(null)

// Store map instance and markers
const mapInstance = ref(null)
const advancedMarkers = ref([])
let currentlyHighlightedMarker = null

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

async function initializeMap() {
  if (!mapContainer.value) {
    console.error('Map container not found')
    return
  }

  try {
    // Wait for Google Maps to be available
    while (!window.google?.maps) {
      console.log('Waiting for Google Maps API...')
      await new Promise(resolve => setTimeout(resolve, 100))
    }

    console.log('Google Maps API loaded, initializing map...')
    console.log('Map ID being used:', mapId)
    console.log('Map container dimensions:', {
      width: mapContainer.value.offsetWidth,
      height: mapContainer.value.offsetHeight,
      visible: mapContainer.value.offsetParent !== null
    })

    // CRITICAL TEST: Try without mapTypeId to see if that's conflicting
    mapInstance.value = new google.maps.Map(mapContainer.value, {
      center: uiStore.mapCenter || { lat: 20.5937, lng: 78.9629 },
      zoom: uiStore.mapZoom,
      mapId: mapId,
      // mapTypeId: uiStore.mapType || 'terrain',  // REMOVED - may conflict with mapId
      disableDefaultUI: true,
      zoomControl: false,
      mapTypeControl: false,
      streetViewControl: false,
      fullscreenControl: false,
    })

    console.log('Map initialized successfully', mapInstance.value)
    console.log('Map div element:', mapInstance.value.getDiv())
    console.log('Map.mapId:', mapInstance.value.get('mapId'))

    // Watch for map state changes
    watch(() => uiStore.mapCenter, (newCenter) => {
      if (mapInstance.value && newCenter) {
        mapInstance.value.setCenter(newCenter)
      }
    })

    watch(() => uiStore.mapZoom, (newZoom) => {
      if (mapInstance.value && newZoom) {
        mapInstance.value.setZoom(newZoom)
      }
    })

    watch(() => uiStore.mapType, (newType) => {
      if (mapInstance.value && newType) {
        mapInstance.value.setMapTypeId(newType)
      }
    })

    // If books are already loaded, create markers now
    if (!booksStore.isLoading && bookMarkers.value.length > 0) {
      const { AdvancedMarkerElement } = await google.maps.importLibrary('marker')
      console.log('AdvancedMarkerElement loaded:', AdvancedMarkerElement)

      bookMarkers.value.forEach(({ book, location, position }) => {
        const marker = createAdvancedMarker(AdvancedMarkerElement, book, location, position)
        if (marker) {
          advancedMarkers.value.push(marker)
        }
      })
      console.log(`Created ${advancedMarkers.value.length} markers immediately`)
    }
  } catch (error) {
    console.error('Error initializing map:', error)
  }
}

function createAdvancedMarker(AdvancedMarkerElement, book, location, position) {
  // Create marker content
  const content = buildMarkerContent(book, location)

  try {
    // Create Advanced Marker
    const marker = new AdvancedMarkerElement({
      map: mapInstance.value,
      position: position,
      content: content,
      title: `${book.title} by ${book.author}`
    })

    // Debug: Log first few markers
    if (advancedMarkers.value.length < 3) {
      console.log('Created marker:', {
        title: book.title,
        position: position,
        hasMap: !!marker.map,
        hasContent: !!marker.content,
        element: marker.element,
        contentHTML: content.outerHTML.substring(0, 100)
      })
    }

    // Check if first marker rendered
    if (advancedMarkers.value.length === 0) {
      setTimeout(() => {
        console.log('First marker element in DOM:', document.querySelector('.book-marker'))
      }, 1000)
    }

    // Add click listener
    marker.content.addEventListener('click', () => {
      if (!marker.content.classList.contains('highlight')) {
        // Close any currently highlighted marker
        if (currentlyHighlightedMarker) {
          closeHighlight(currentlyHighlightedMarker)
        }
        // Highlight this marker
        openHighlight(marker, book)
        currentlyHighlightedMarker = marker
      }
    })

    // Add hover listeners for tooltip
    const infoWindow = new google.maps.InfoWindow({
      content: `<div class="p-2"><strong>${book.title}</strong><br/>${book.author}</div>`,
      disableAutoPan: true
    })

    marker.content.addEventListener('mouseenter', () => {
      if (!marker.content.classList.contains('highlight')) {
        infoWindow.open({ anchor: marker, map: mapInstance.value })
      }
    })

    marker.content.addEventListener('mouseleave', () => {
      infoWindow.close()
    })

    return marker
  } catch (error) {
    console.error('Error creating marker:', error, { book: book.title, position })
    return null
  }
}

function buildMarkerContent(book, location) {
  const content = document.createElement('div')
  content.classList.add('book-marker')

  const bookColor = generateBookColor(book)
  const initials = getTitleInitials(book.title)

  // Set inline styles to ensure visibility
  content.style.backgroundColor = bookColor
  content.style.display = 'block'
  content.style.position = 'relative'

  const coverUrl = book.isbn ? `https://covers.openlibrary.org/b/isbn/${book.isbn}-M.jpg` : ''
  const description = location.description || book.description || ''

  content.innerHTML = `
    <div class="marker-initials" style="display: block;">${initials}</div>
    <div class="marker-expanded" style="display: none;">
      <button class="close-button">×</button>
      <div class="marker-content">
        <div class="marker-cover">
          ${coverUrl ? `<img src="${coverUrl}" alt="${book.title}" class="cover-image" />` : '<div class="no-cover">No Cover</div>'}
          <div class="location-label">${location.city || ''}</div>
        </div>
        <div class="marker-info">
          <div class="marker-title">${book.title}</div>
          <div class="marker-author">${book.author}</div>
          <div class="marker-description">${description.substring(0, 150)}...</div>
          <div class="marker-type">${book.booktype || ''}</div>
        </div>
      </div>
    </div>
  `

  return content
}

function openHighlight(marker, book) {
  const content = marker.content
  const initials = content.querySelector('.marker-initials')
  const expanded = content.querySelector('.marker-expanded')
  const closeBtn = content.querySelector('.close-button')
  const coverImg = content.querySelector('.cover-image')

  // Show expanded, hide initials
  initials.style.display = 'none'
  expanded.style.display = 'block'
  content.classList.add('highlight')

  // Close button handler
  closeBtn.addEventListener('click', (e) => {
    e.stopPropagation()
    closeHighlight(marker)
  })

  // Cover click to open Goodreads
  if (coverImg && book.isbn) {
    coverImg.style.cursor = 'pointer'
    coverImg.addEventListener('click', (e) => {
      e.stopPropagation()
      window.open(`https://www.goodreads.com/book/isbn/${book.isbn}`, '_blank')
    })
  }
}

function closeHighlight(marker) {
  const content = marker.content
  const initials = content.querySelector('.marker-initials')
  const expanded = content.querySelector('.marker-expanded')

  // Show initials, hide expanded
  initials.style.display = 'block'
  expanded.style.display = 'none'
  content.classList.remove('highlight')

  if (currentlyHighlightedMarker === marker) {
    currentlyHighlightedMarker = null
  }
}

function clearMarkers() {
  advancedMarkers.value.forEach(marker => {
    marker.map = null
  })
  advancedMarkers.value = []
}

function handleMapClick() {
  // Clear highlighted marker when clicking on map
  if (currentlyHighlightedMarker) {
    closeHighlight(currentlyHighlightedMarker)
  }
  uiStore.clearHighlightedMarker()
}

// Watch for book changes and re-render markers
watch(() => booksStore.allBooks, async () => {
  if (mapInstance.value && window.google) {
    const { AdvancedMarkerElement } = await google.maps.importLibrary('marker')
    clearMarkers()

    bookMarkers.value.forEach(({ book, location, position }) => {
      const marker = createAdvancedMarker(AdvancedMarkerElement, book, location, position)
      advancedMarkers.value.push(marker)
    })
  }
})

onMounted(() => {
  console.log('GoogleMap component mounted')
  console.log('mapContainer.value:', mapContainer.value)

  // Initialize map immediately (even if books are still loading)
  if (mapContainer.value) {
    initializeMap()
  } else {
    console.error('Map container element not found!')
  }
})

// Watch for books to be loaded and create markers
watch(() => booksStore.isLoading, (loading) => {
  if (!loading && mapInstance.value && bookMarkers.value.length > 0) {
    console.log('Books loaded, creating markers...')
    console.log(`Found ${bookMarkers.value.length} book markers to create`)

    // Use legacy markers with custom SVG icons (works with JavaScript API)
    clearMarkers()

    bookMarkers.value.forEach(({ book, location, position }) => {
      const bookColor = generateBookColor(book)
      const initials = getTitleInitials(book.title)

      // Create SVG icon as data URI
      const svgIcon = `
        <svg width="40" height="40" xmlns="http://www.w3.org/2000/svg">
          <circle cx="20" cy="20" r="18" fill="${bookColor}" stroke="white" stroke-width="2"/>
          <text x="20" y="26" font-size="14" font-weight="bold" fill="white" text-anchor="middle">${initials}</text>
        </svg>
      `
      const iconUrl = 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(svgIcon)

      const marker = new google.maps.Marker({
        map: mapInstance.value,
        position: position,
        title: `${book.title} by ${book.author}`,
        icon: {
          url: iconUrl,
          scaledSize: new google.maps.Size(40, 40),
          anchor: new google.maps.Point(20, 20)
        }
      })

      // Add click listener
      marker.addListener('click', () => {
        // TODO: Open book details in bottom sheet
        console.log('Clicked book:', book.title)
      })

      advancedMarkers.value.push(marker)
    })

    console.log(`✓ Created ${advancedMarkers.value.length} legacy markers with custom SVG icons!`)
  }
})

onBeforeUnmount(() => {
  clearMarkers()
  mapInstance.value = null
})
</script>

<style>
/* Force Advanced Markers to be visible and interactive */
gmp-advanced-marker {
  pointer-events: auto !important;
  opacity: 1 !important;
  visibility: visible !important;
}

/* Custom marker styles - NOT scoped so they apply to dynamically created markers */
.book-marker {
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  position: relative;
  z-index: 1;
  pointer-events: auto !important;
}

.marker-initials {
  padding: 8px 12px;
  font-weight: bold;
  font-size: 14px;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  white-space: nowrap;
}

.book-marker.highlight {
  z-index: 1000 !important;
}

.marker-expanded {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
  min-width: 320px;
  max-width: 380px;
  padding: 0;
}

.close-button {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  border: none;
  font-size: 20px;
  line-height: 1;
  cursor: pointer;
  z-index: 10;
  transition: background 0.2s;
}

.close-button:hover {
  background: rgba(0, 0, 0, 0.8);
}

.marker-content {
  display: flex;
  gap: 12px;
  padding: 16px;
}

.marker-cover {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cover-image {
  width: 80px;
  height: 120px;
  object-fit: cover;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.no-cover {
  width: 80px;
  height: 120px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 11px;
  text-align: center;
  padding: 8px;
}

.location-label {
  font-size: 11px;
  color: #666;
  text-align: center;
}

.marker-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.marker-title {
  font-weight: bold;
  font-size: 15px;
  color: #1a1a1a;
  line-height: 1.3;
}

.marker-author {
  font-size: 13px;
  color: #666;
}

.marker-description {
  font-size: 12px;
  color: #444;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
}

.marker-type {
  font-size: 11px;
  color: #888;
  text-transform: capitalize;
}
</style>
