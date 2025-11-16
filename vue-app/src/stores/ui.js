import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUIStore = defineStore('ui', () => {
  // State
  const isMenuOpen = ref(false)
  const isSearchModalOpen = ref(false)
  const bottomSheetState = ref('hidden') // 'hidden', 'half', 'full'
  const bottomSheetContent = ref(null) // 'search-results', 'book-details'
  const selectedBook = ref(null)
  const highlightedMarkerId = ref(null)
  const isClusteringEnabled = ref(true)
  const searchQuery = ref('')
  const searchField = ref('any') // 'title', 'author', 'location', 'keyword', 'any'
  const searchResults = ref([])

  // Map state
  const mapCenter = ref(null)
  const mapZoom = ref(3)
  const shouldFitBounds = ref(0) // Counter to trigger fitBounds (increment to trigger)

  // Getters
  const hasSearchResults = computed(() => searchResults.value.length > 0)
  const isBottomSheetVisible = computed(() => bottomSheetState.value !== 'hidden')
  const searchResultsCount = computed(() => searchResults.value.length)

  // Actions
  function toggleMenu() {
    isMenuOpen.value = !isMenuOpen.value
  }

  function openMenu() {
    isMenuOpen.value = true
  }

  function closeMenu() {
    isMenuOpen.value = false
  }

  function openSearchModal() {
    isSearchModalOpen.value = true
  }

  function closeSearchModal() {
    isSearchModalOpen.value = false
  }

  function setBottomSheet(state, content = null) {
    bottomSheetState.value = state
    if (content) {
      bottomSheetContent.value = content
    }
  }

  function showSearchResults(results) {
    searchResults.value = results
    bottomSheetContent.value = 'search-results'
    bottomSheetState.value = results.length > 0 ? 'half' : 'hidden'
  }

  function showBookDetails(book) {
    console.log('showBookDetails called for:', book.title, 'Current state:', bottomSheetState.value)
    selectedBook.value = book
    bottomSheetContent.value = 'book-details'
    bottomSheetState.value = 'half'
  }

  function hideBottomSheet() {
    console.log('hideBottomSheet called - current state:', bottomSheetState.value)
    bottomSheetState.value = 'hidden'
    // Clear highlighted marker immediately
    clearHighlightedMarker()
    // Clear content after animation
    const wasBookDetails = bottomSheetContent.value === 'book-details'
    setTimeout(() => {
      console.log('Clearing bottom sheet content after animation')
      bottomSheetContent.value = null
      if (wasBookDetails) {
        selectedBook.value = null
      }
    }, 300)
  }

  function setHighlightedMarker(markerId) {
    highlightedMarkerId.value = markerId
  }

  function clearHighlightedMarker() {
    highlightedMarkerId.value = null
  }

  function toggleClustering() {
    isClusteringEnabled.value = !isClusteringEnabled.value
  }

  function setSearchQuery(query) {
    searchQuery.value = query
  }

  function setSearchField(field) {
    searchField.value = field
  }

  function clearSearch() {
    searchQuery.value = ''
    searchResults.value = []
    hideBottomSheet()
  }

  function setMapCenter(center) {
    mapCenter.value = center
  }

  function setMapZoom(zoom) {
    mapZoom.value = zoom
  }

  function triggerFitBounds() {
    shouldFitBounds.value++
  }

  return {
    // State
    isMenuOpen,
    isSearchModalOpen,
    bottomSheetState,
    bottomSheetContent,
    selectedBook,
    highlightedMarkerId,
    isClusteringEnabled,
    searchQuery,
    searchField,
    searchResults,
    mapCenter,
    mapZoom,
    shouldFitBounds,
    // Getters
    hasSearchResults,
    isBottomSheetVisible,
    searchResultsCount,
    // Actions
    toggleMenu,
    openMenu,
    closeMenu,
    openSearchModal,
    closeSearchModal,
    setBottomSheet,
    showSearchResults,
    showBookDetails,
    hideBottomSheet,
    setHighlightedMarker,
    clearHighlightedMarker,
    toggleClustering,
    setSearchQuery,
    setSearchField,
    clearSearch,
    setMapCenter,
    setMapZoom,
    triggerFitBounds,
  }
})
