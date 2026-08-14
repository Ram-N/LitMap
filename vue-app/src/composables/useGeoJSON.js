import { useBooksStore } from '@/stores/books'

const GEOJSON_URL = import.meta.env.BASE_URL + 'litmap-data.geojson'

export function useGeoJSON() {
  const booksStore = useBooksStore()

  /**
   * Load books from static GeoJSON file and update the store.
   *
   * GeoJSON has one Feature per book-location. We group features by bookId
   * to reconstruct the book-with-locations structure the rest of the app expects.
   */
  async function loadBooks() {
    booksStore.setLoading(true)
    booksStore.setError(null)

    try {
      console.log(`[GeoJSON] Fetching from: ${GEOJSON_URL}`)
      console.time('[GeoJSON] fetch + parse')
      const response = await fetch(GEOJSON_URL)
      if (!response.ok) {
        throw new Error(`Failed to fetch GeoJSON: ${response.status}`)
      }

      const geojson = await response.json()
      console.timeEnd('[GeoJSON] fetch + parse')
      console.time('[GeoJSON] geojsonToBooks')
      const books = geojsonToBooks(geojson)
      console.timeEnd('[GeoJSON] geojsonToBooks')

      booksStore.setBooks(books)
      console.log(`Loaded ${books.length} books from GeoJSON (${geojson.features.length} location features)`)

      return books
    } catch (error) {
      console.error('Error loading books:', error)
      booksStore.setError(error.message)
      throw error
    } finally {
      booksStore.setLoading(false)
    }
  }

  /**
   * Convert GeoJSON FeatureCollection into the book array format
   * that the rest of the app (stores, search, views) expects.
   */
  function geojsonToBooks(geojson) {
    const bookMap = new Map()

    for (const feature of geojson.features) {
      const props = feature.properties
      const bookId = props.bookId || `${props.title}-${props.author}`

      if (!bookMap.has(bookId)) {
        bookMap.set(bookId, {
          id: bookId,
          title: props.title || '',
          author: props.author || '',
          description: props.description || '',
          booktype: props.booktype || '',
          genre: props.genre || '',
          rating: props.rating,
          pageCount: props.pageCount,
          isbn: props.isbn || '',
          language: props.language || '',
          publisher: props.publisher || '',
          publicationDate: props.publicationDate || '',
          coverImageUrl: props.coverImageUrl || '',
          hasCover: props.hasCover || false,
          tags: props.tags || [],
          locations: [],
        })
      }

      // Add location from this feature's geometry
      const [lng, lat] = feature.geometry.coordinates
      bookMap.get(bookId).locations.push({
        latitude: lat,
        longitude: lng,
        lat,
        lng,
        city: props.locationCity || '',
        country: props.locationCountry || '',
        description: props.locationDescription || '',
      })
    }

    return Array.from(bookMap.values())
  }

  /**
   * Refresh (just re-fetch; there's no cache to bust with static files)
   */
  async function refreshBookCache() {
    booksStore.clearBooks()
    return await loadBooks()
  }

  return {
    loadBooks,
    refreshBookCache,
  }
}
