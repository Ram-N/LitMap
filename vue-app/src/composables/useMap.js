import { ref } from 'vue'
import { useUIStore } from '@/stores/ui'
import { presetLocations, getRandomLocation } from '@/utils/mapLocations'

export function useMap() {
  const uiStore = useUIStore()

  /**
   * Navigate to a preset location
   */
  function goToLocation(locationKey) {
    if (!locationKey || !presetLocations[locationKey]) return

    const location = presetLocations[locationKey]
    uiStore.setMapCenter({ lat: location.lat, lng: location.lng })
    uiStore.setMapZoom(location.zoom)
  }

  /**
   * Navigate to a random location
   */
  function goToRandomLocation() {
    const location = getRandomLocation()

    uiStore.setMapCenter({ lat: location.lat, lng: location.lng })
    uiStore.setMapZoom(11)

    return location
  }

  /**
   * Geocode an address using OpenStreetMap Nominatim (free, no API key)
   */
  async function geocodeAddress(address) {
    if (!address || !address.trim()) return

    try {
      const encoded = encodeURIComponent(address.trim())
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encoded}&limit=1`,
        { headers: { 'Accept-Language': 'en' } }
      )

      if (!response.ok) {
        throw new Error(`Geocoding failed: ${response.status}`)
      }

      const results = await response.json()

      if (results.length === 0) {
        throw new Error('No results found')
      }

      const result = results[0]
      const lat = parseFloat(result.lat)
      const lng = parseFloat(result.lon)
      const zoom = getZoomForNominatimType(result.type, result.class)

      uiStore.setMapCenter({ lat, lng })
      uiStore.setMapZoom(zoom)

      return { lat, lng, zoom }
    } catch (error) {
      console.error('Error geocoding address:', error)
      throw error
    }
  }

  /**
   * Get appropriate zoom level for Nominatim result type
   */
  function getZoomForNominatimType(type, cls) {
    if (type === 'continent') return 3
    if (type === 'country' || cls === 'boundary') return 5
    if (type === 'state' || type === 'administrative') return 7
    if (type === 'county') return 9
    if (type === 'city' || type === 'town' || type === 'village') return 11
    if (type === 'suburb' || type === 'neighbourhood') return 13
    if (type === 'road' || type === 'street') return 15
    return 10
  }

  return {
    goToLocation,
    goToRandomLocation,
    geocodeAddress,
  }
}
