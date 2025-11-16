import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useBooksStore = defineStore('books', () => {
  // State
  const allBooks = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  const lastFetchTime = ref(null)

  // Getters
  const booksCount = computed(() => allBooks.value.length)

  const booksWithLocations = computed(() =>
    allBooks.value.filter(book =>
      book.locations && book.locations.length > 0
    )
  )

  // Actions
  function setBooks(books) {
    allBooks.value = books
    lastFetchTime.value = Date.now()
  }

  function setLoading(loading) {
    isLoading.value = loading
  }

  function setError(err) {
    error.value = err
  }

  function clearBooks() {
    allBooks.value = []
    lastFetchTime.value = null
  }

  return {
    // State
    allBooks,
    isLoading,
    error,
    lastFetchTime,
    // Getters
    booksCount,
    booksWithLocations,
    // Actions
    setBooks,
    setLoading,
    setError,
    clearBooks,
  }
})
