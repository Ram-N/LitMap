import { collection, getDocs } from 'firebase/firestore'
import { getDb } from '@/utils/firebase'
import { useBooksStore } from '@/stores/books'

export function useFirebase() {
  const booksStore = useBooksStore()

  /**
   * Get all books from a specific Firestore collection
   */
  async function getAllBooks(collectionName = null) {
    const db = getDb()
    const targetCollection = collectionName || booksStore.currentCollection

    try {
      const booksRef = collection(db, targetCollection)
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
  async function loadBooks(collectionName = null) {
    booksStore.setLoading(true)
    booksStore.setError(null)

    try {
      const targetCollection = collectionName || booksStore.currentCollection

      // Update collection in store if different
      if (collectionName && collectionName !== booksStore.currentCollection) {
        booksStore.setCollection(collectionName)
      }

      // Fetch books from Firestore
      const books = await getAllBooks(targetCollection)

      // Update store
      booksStore.setBooks(books)

      console.log(`Loaded ${books.length} books from ${targetCollection}`)

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

  /**
   * Switch to a different collection and load books
   */
  async function switchCollection(collectionName) {
    if (collectionName === booksStore.currentCollection) {
      console.log('Already on collection:', collectionName)
      return booksStore.allBooks
    }

    console.log('Switching to collection:', collectionName)
    return await loadBooks(collectionName)
  }

  return {
    getAllBooks,
    loadBooks,
    refreshBookCache,
    switchCollection,
  }
}
