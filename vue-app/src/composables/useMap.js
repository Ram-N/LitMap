import { ref } from 'vue'
import { useUIStore } from '@/stores/ui'
import { presetLocations, getRandomLocation } from '@/utils/mapLocations'

export function useMap() {
  const uiStore = useUIStore()
  const mapRef = ref(null)
  const googleMapRef = ref(null)

  /**
   * Navigate to a preset location
   */
  function goToLocation(locationKey) {
    if (!locationKey || !presetLocations[locationKey]) return

    const location = presetLocations[locationKey]
    uiStore.setMapCenter({ lat: location.lat, lng: location.lng })
    uiStore.setMapZoom(location.zoom)

    console.log(`Navigating to ${locationKey}:`, location)
  }

  /**
   * Navigate to a random location
   */
  function goToRandomLocation() {
    const location = getRandomLocation()

    uiStore.setMapCenter({ lat: location.lat, lng: location.lng })
    uiStore.setMapZoom(11) // City-level zoom

    console.log(`Random location: ${location.name}`, location)

    return location
  }

  /**
   * Geocode an address and navigate to it
   */
  async function geocodeAddress(address) {
    if (!address || !address.trim()) return

    try {
      // Using Google Maps Geocoding API
      const geocoder = new google.maps.Geocoder()

      return new Promise((resolve, reject) => {
        geocoder.geocode({ address }, (results, status) => {
          if (status === 'OK' && results[0]) {
            const result = results[0]
            const location = result.geometry.location

            // Determine zoom based on location type
            const zoom = getZoomLevelForLocationType(result.types)

            uiStore.setMapCenter({
              lat: location.lat(),
              lng: location.lng()
            })
            uiStore.setMapZoom(zoom)

            console.log(`Geocoded "${address}":`, {
              lat: location.lat(),
              lng: location.lng(),
              zoom
            })

            resolve({
              lat: location.lat(),
              lng: location.lng(),
              zoom,
              types: result.types
            })
          } else {
            console.error('Geocode failed:', status)
            reject(new Error(`Geocoding failed: ${status}`))
          }
        })
      })
    } catch (error) {
      console.error('Error geocoding address:', error)
      throw error
    }
  }

  /**
   * Get zoom level based on location type
   */
  function getZoomLevelForLocationType(types) {
    if (types.includes('continent')) return 3
    if (types.includes('country')) return 5
    if (types.includes('administrative_area_level_1')) return 7
    if (types.includes('administrative_area_level_2')) return 9
    if (types.includes('locality') || types.includes('postal_town')) return 11
    if (types.includes('neighborhood') || types.includes('sublocality')) return 13
    if (types.includes('route')) return 15
    return 10 // default zoom level
  }

  /**
   * Fit map bounds to show all markers
   */
  function fitBoundsToMarkers(books) {
    if (!books || books.length === 0) return

    const bounds = new google.maps.LatLngBounds()

    books.forEach(book => {
      if (book.locations && Array.isArray(book.locations)) {
        book.locations.forEach(location => {
          const lat = location.lat || location.latitude
          const lng = location.lng || location.longitude

          if (lat && lng) {
            bounds.extend({ lat, lng })
          }
        })
      }
    })

    // Update map to fit bounds
    if (googleMapRef.value && googleMapRef.value.$map) {
      googleMapRef.value.$map.fitBounds(bounds)
    }
  }

  return {
    mapRef,
    googleMapRef,
    goToLocation,
    goToRandomLocation,
    geocodeAddress,
    fitBoundsToMarkers,
  }
}
