import { collection, getDocs } from 'firebase/firestore'
import { getDb } from '@/utils/firebase'
import { useBooksStore } from '@/stores/books'

export function useFirebase() {
  const booksStore = useBooksStore()

  /**
   * Get all books from Firestore 'books' collection
   */
  async function getAllBooks() {
    const db = getDb()

    try {
      const booksRef = collection(db, 'books')
      const querySnapshot = await getDocs(booksRef)
      const books = []

      querySnapshot.forEach((doc) => {
        books.push({
          id: doc.id,
          ...doc.data()
        })
      })

      return books
    } catch (error) {
      console.error('Error fetching books:', error)
      throw error
    }
  }

  /**
   * Load books from Firestore and update the store
   */
  async function loadBooks() {
    booksStore.setLoading(true)
    booksStore.setError(null)

    try {
      // Fetch books from Firestore
      const books = await getAllBooks()

      // Update store
      booksStore.setBooks(books)

      console.log(`Loaded ${books.length} books from 'books' collection`)

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
   * Refresh the book cache (clear and reload)
   */
  async function refreshBookCache() {
    booksStore.clearBooks()
    return await loadBooks()
  }

  return {
    getAllBooks,
    loadBooks,
    refreshBookCache,
  }
}
