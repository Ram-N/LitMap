import { useUIStore } from '@/stores/ui'
import { useBooksStore } from '@/stores/books'

export function useSearch() {
  const uiStore = useUIStore()
  const booksStore = useBooksStore()

  /**
   * Perform fuzzy search on books
   * Matches the original firebase.js logic
   */
  function performSearch(query, field) {
    if (!query || !query.trim()) {
      uiStore.clearSearch()
      return
    }

    const searchTerm = query.toLowerCase().trim()
    const results = []

    // Perform fuzzy search on all books
    for (const book of booksStore.allBooks) {
      if (matchesSearch(book, searchTerm, field)) {
        results.push(book)
      }
    }

    // Build search query description (like original)
    let searchQuery
    switch (field) {
      case 'title':
      case 'author':
        searchQuery = `${field} contains "${searchTerm}"`
        break
      case 'location':
        searchQuery = `location contains "${searchTerm}"`
        break
      case 'keyword':
        searchQuery = `"${searchTerm}" in tags, genre`
        break
      case 'any':
      default:
        searchQuery = `"${searchTerm}" in any field`
    }

    console.log('Search Results:', results)
    console.log('Search Query:', searchQuery)

    uiStore.setSearchQuery(query)
    uiStore.setSearchField(field)
    uiStore.showSearchResults(results)

    // Fit map bounds for author or location searches
    if ((field === 'author' || field === 'location') && results.length > 0) {
      console.log(`Fitting map bounds for ${field} search results`)
      uiStore.triggerFitBounds()
    }

    return { results, searchQuery }
  }

  function matchesSearch(book, searchTerm, field) {
    // Handle location search (special case with nested array)
    if (field === 'location') {
      return matchesLocation(book, searchTerm)
    }

    // Single field search
    if (field === 'title' || field === 'author') {
      return book[field] && book[field].toLowerCase().includes(searchTerm)
    }

    // Keyword field search (tags + genre)
    if (field === 'keyword') {
      return matchesKeyword(book, searchTerm)
    }

    // 'any' field search (default)
    // Search in title, author, and description
    const title = book.title ? book.title.toLowerCase() : ''
    const author = book.author ? book.author.toLowerCase() : ''
    const description = book.description ? book.description.toLowerCase() : ''

    return (
      title.includes(searchTerm) ||
      author.includes(searchTerm) ||
      description.includes(searchTerm)
    )
  }

  function matchesLocation(book, searchTerm) {
    if (!book.locations || !Array.isArray(book.locations)) {
      return false
    }

    return book.locations.some(location => {
      const city = location.city ? location.city.toLowerCase() : ''
      const state = location.state ? location.state.toLowerCase() : ''
      const country = location.country ? location.country.toLowerCase() : ''

      return (
        city.includes(searchTerm) ||
        state.includes(searchTerm) ||
        country.includes(searchTerm)
      )
    })
  }

  function matchesKeyword(book, searchTerm) {
    // Search in tags and genre fields
    const searchFields = []

    if (book.tags) {
      if (Array.isArray(book.tags)) {
        searchFields.push(...book.tags)
      } else if (typeof book.tags === 'string') {
        searchFields.push(book.tags)
      }
    }

    if (book.genre) {
      searchFields.push(book.genre)
    }

    return searchFields.some(field =>
      field && field.toLowerCase().includes(searchTerm)
    )
  }

  return {
    performSearch
  }
}
