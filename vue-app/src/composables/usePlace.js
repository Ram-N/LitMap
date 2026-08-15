import { computed } from 'vue'
import { useBooksStore } from '@/stores/books'

export function usePlace(placeName) {
  const booksStore = useBooksStore()

  /**
   * All books where any location matches the given city or country (case-insensitive).
   */
  const books = computed(() => {
    const name = placeName.value?.toLowerCase()
    if (!name) return []

    return booksStore.allBooks.filter(book =>
      (book.locations || []).some(loc =>
        loc.city?.toLowerCase() === name ||
        loc.country?.toLowerCase() === name
      )
    )
  })

  /**
   * Books grouped by booktype (Fiction, Nonfiction, Travel, Poetry).
   */
  const booksByType = computed(() => {
    const groups = {}
    for (const book of books.value) {
      const type = book.booktype || 'Other'
      if (!groups[type]) groups[type] = []
      groups[type].push(book)
    }
    // Sort groups by count descending
    return Object.entries(groups)
      .sort(([, a], [, b]) => b.length - a.length)
      .map(([type, typeBooks]) => ({ type, books: typeBooks }))
  })

  /**
   * Average lat/lng of all matching locations for this place.
   */
  const placeCoordinates = computed(() => {
    const name = placeName.value?.toLowerCase()
    if (!name) return null

    const coords = []
    for (const book of booksStore.allBooks) {
      for (const loc of book.locations || []) {
        if (loc.city?.toLowerCase() === name || loc.country?.toLowerCase() === name) {
          if (loc.lat != null && loc.lng != null) {
            coords.push({ lat: loc.lat, lng: loc.lng })
          }
        }
      }
    }

    if (coords.length === 0) return null

    const avgLat = coords.reduce((s, c) => s + c.lat, 0) / coords.length
    const avgLng = coords.reduce((s, c) => s + c.lng, 0) / coords.length
    return { lat: avgLat, lng: avgLng }
  })

  /**
   * Other places that share books with this place.
   */
  const relatedPlaces = computed(() => {
    const name = placeName.value?.toLowerCase()
    if (!name) return []

    const placeSet = new Map()
    for (const book of books.value) {
      for (const loc of book.locations || []) {
        const locName = loc.country || loc.city
        if (!locName || locName.toLowerCase() === name) continue
        if (!placeSet.has(locName)) {
          placeSet.set(locName, { name: locName, bookCount: 0 })
        }
        placeSet.get(locName).bookCount++
      }
    }

    return Array.from(placeSet.values())
      .sort((a, b) => b.bookCount - a.bookCount)
      .slice(0, 6)
  })

  return {
    books,
    booksByType,
    placeCoordinates,
    relatedPlaces,
  }
}
