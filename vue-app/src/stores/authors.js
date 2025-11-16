import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useBooksStore } from './books'

export const useAuthorsStore = defineStore('authors', () => {
  // State
  const authorsCache = ref(new Map())
  const isLoading = ref(false)
  const error = ref(null)

  // Getters
  const getAuthorByName = computed(() => (authorName) => {
    return authorsCache.value.get(authorName)
  })

  const allAuthors = computed(() => {
    return Array.from(authorsCache.value.values())
  })

  // Actions
  function computeAuthorProfile(authorName) {
    const booksStore = useBooksStore()

    // Find all books by this author
    const authorBooks = booksStore.allBooks.filter(
      book => book.author === authorName
    )

    if (authorBooks.length === 0) {
      return null
    }

    // Aggregate data
    const profile = {
      name: authorName,
      books: authorBooks,
      bookCount: authorBooks.length,

      // Aggregate locations (countries visited)
      countries: getUniqueCountries(authorBooks),
      countryCount: 0,

      // Aggregate genres
      genres: getUniqueGenres(authorBooks),

      // Generate avatar (initials + color)
      avatar: generateAvatar(authorName),

      // Bio (placeholder - can be added manually later)
      bio: null,

      // Journey map data (all locations)
      journeyLocations: aggregateLocations(authorBooks)
    }

    profile.countryCount = profile.countries.length

    // Cache it
    authorsCache.value.set(authorName, profile)

    return profile
  }

  function getUniqueCountries(books) {
    const countries = new Set()
    books.forEach(book => {
      book.locations?.forEach(loc => {
        if (loc.country) countries.add(loc.country)
      })
    })
    return Array.from(countries)
  }

  function getUniqueGenres(books) {
    const genres = new Set()
    books.forEach(book => {
      if (book.genre) genres.add(book.genre)
      if (book.booktype) genres.add(book.booktype)
      book.tags?.forEach(tag => genres.add(tag))
    })
    return Array.from(genres).slice(0, 5) // Limit to 5 genres
  }

  function aggregateLocations(books) {
    const locationsMap = new Map()

    books.forEach(book => {
      book.locations?.forEach(loc => {
        const key = `${loc.latitude},${loc.longitude}`
        if (!locationsMap.has(key)) {
          locationsMap.set(key, {
            ...loc,
            lat: loc.latitude,
            lng: loc.longitude,
            books: []
          })
        }
        locationsMap.get(key).books.push({
          id: book.id,
          title: book.title
        })
      })
    })

    return Array.from(locationsMap.values())
  }

  function generateAvatar(name) {
    // Get initials
    const initials = name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)

    // Generate color based on name hash
    const hash = name.split('').reduce((acc, char) => {
      return char.charCodeAt(0) + ((acc << 5) - acc)
    }, 0)
    const hue = Math.abs(hash) % 360
    const color = `hsl(${hue}, 50%, 55%)`

    return { initials, color }
  }

  async function fetchAuthorProfile(authorName) {
    isLoading.value = true
    error.value = null

    try {
      // Check cache first
      let profile = authorsCache.value.get(authorName)

      if (!profile) {
        // Compute from books
        profile = computeAuthorProfile(authorName)
      }

      return profile
    } catch (err) {
      error.value = err.message
      return null
    } finally {
      isLoading.value = false
    }
  }

  function precomputeAllAuthors() {
    const booksStore = useBooksStore()
    const authorNames = new Set(
      booksStore.allBooks.map(book => book.author).filter(Boolean)
    )

    authorNames.forEach(name => {
      computeAuthorProfile(name)
    })
  }

  return {
    // State
    authorsCache,
    isLoading,
    error,
    // Getters
    getAuthorByName,
    allAuthors,
    // Actions
    computeAuthorProfile,
    fetchAuthorProfile,
    precomputeAllAuthors,
  }
})
