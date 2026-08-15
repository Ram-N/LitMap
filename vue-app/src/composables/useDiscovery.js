import { computed } from 'vue'
import { useBooksStore } from '@/stores/books'

export function useDiscovery() {
  const booksStore = useBooksStore()

  /**
   * Count of unique countries across all books.
   */
  const countryCount = computed(() => {
    const countries = new Set()
    for (const book of booksStore.allBooks) {
      for (const loc of book.locations || []) {
        if (loc.country) countries.add(loc.country)
      }
    }
    return countries.size
  })

  /**
   * Top 8 countries by book count, with a representative cover.
   */
  const placesWorthExploring = computed(() => {
    const countryMap = new Map()

    for (const book of booksStore.allBooks) {
      for (const loc of book.locations || []) {
        if (!loc.country) continue
        if (!countryMap.has(loc.country)) {
          countryMap.set(loc.country, { books: new Set(), coverBook: null })
        }
        const entry = countryMap.get(loc.country)
        entry.books.add(book.id)
        if (!entry.coverBook && book.hasCover) {
          entry.coverBook = book
        }
      }
    }

    return Array.from(countryMap.entries())
      .map(([country, data]) => ({
        country,
        bookCount: data.books.size,
        coverBook: data.coverBook,
      }))
      .sort((a, b) => b.bookCount - a.bookCount)
      .slice(0, 8)
  })

  /**
   * Random 6 books that have covers.
   */
  const featuredBooks = computed(() => {
    const withCovers = booksStore.allBooks.filter(b => b.hasCover)
    return shuffleDeterministic(withCovers).slice(0, 6)
  })

  /**
   * Authors with 3+ books, showing book count and countries spanned.
   */
  const authorTrails = computed(() => {
    const authorMap = new Map()

    for (const book of booksStore.allBooks) {
      if (!book.author) continue
      if (!authorMap.has(book.author)) {
        authorMap.set(book.author, { books: [], countries: new Set() })
      }
      const entry = authorMap.get(book.author)
      entry.books.push(book)
      for (const loc of book.locations || []) {
        if (loc.country) entry.countries.add(loc.country)
      }
    }

    return Array.from(authorMap.entries())
      .filter(([, data]) => data.books.length >= 3)
      .map(([author, data]) => ({
        author,
        bookCount: data.books.length,
        countries: Array.from(data.countries),
        coverBook: data.books.find(b => b.hasCover) || data.books[0],
      }))
      .sort((a, b) => b.bookCount - a.bookCount)
      .slice(0, 10)
  })

  return {
    countryCount,
    placesWorthExploring,
    featuredBooks,
    authorTrails,
  }
}

/**
 * Deterministic shuffle based on current date (changes daily).
 */
function shuffleDeterministic(arr) {
  const copy = [...arr]
  const seed = new Date().toDateString()
  let hash = 0
  for (let i = 0; i < seed.length; i++) {
    hash = ((hash << 5) - hash) + seed.charCodeAt(i)
    hash |= 0
  }

  for (let i = copy.length - 1; i > 0; i--) {
    hash = ((hash << 5) - hash + i) | 0
    const j = Math.abs(hash) % (i + 1)
    ;[copy[i], copy[j]] = [copy[j], copy[i]]
  }
  return copy
}
