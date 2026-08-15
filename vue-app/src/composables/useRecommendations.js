import { computed } from 'vue'
import { useBooksStore } from '@/stores/books'

export function useRecommendations(bookRef) {
  const booksStore = useBooksStore()

  const relatedBooks = computed(() => {
    const book = bookRef.value
    if (!book) return []

    const scored = new Map() // bookId -> { book, score, reasons }

    booksStore.allBooks.forEach(candidate => {
      if (candidate.id === book.id) return

      const reasons = []
      let score = 0

      // Same author
      if (candidate.author && book.author && candidate.author === book.author) {
        score += 10
        reasons.push('By the same author')
      }

      // Shared locations (city or country)
      if (book.locations && candidate.locations) {
        const bookCountries = new Set(book.locations.map(l => l.country).filter(Boolean))
        const bookCities = new Set(book.locations.map(l => l.city).filter(Boolean))

        for (const loc of candidate.locations) {
          if (loc.city && bookCities.has(loc.city)) {
            score += 8
            reasons.push(`Also set in ${loc.city}`)
            break
          }
          if (loc.country && bookCountries.has(loc.country)) {
            score += 5
            reasons.push(`Also set in ${loc.country}`)
            break
          }
        }
      }

      // Shared genre
      const bookGenres = normalizeArray(book.genre)
      const candidateGenres = normalizeArray(candidate.genre)
      const sharedGenres = bookGenres.filter(g => candidateGenres.includes(g))
      if (sharedGenres.length > 0) {
        score += 3
        reasons.push(`Also ${sharedGenres[0]}`)
      }

      // Shared tags
      const bookTags = normalizeArray(book.tags)
      const candidateTags = normalizeArray(candidate.tags)
      const sharedTags = bookTags.filter(t => candidateTags.includes(t))
      if (sharedTags.length > 0) {
        score += 2 * Math.min(sharedTags.length, 2)
      }

      // Same booktype
      if (candidate.booktype && book.booktype && candidate.booktype === book.booktype) {
        score += 1
      }

      if (score > 0 && reasons.length > 0) {
        scored.set(candidate.id, {
          book: candidate,
          score,
          reason: reasons[0] // Use the strongest reason
        })
      }
    })

    // Sort by score descending and return top 6
    return Array.from(scored.values())
      .sort((a, b) => b.score - a.score)
      .slice(0, 6)
  })

  return { relatedBooks }
}

function normalizeArray(value) {
  if (!value) return []
  if (Array.isArray(value)) return value
  return [value]
}
