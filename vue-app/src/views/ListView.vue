<template>
  <div class="h-screen flex flex-col bg-parchment-50">
    <!-- Header -->
    <header class="bg-white border-b border-parchment-200 px-4 py-4 flex items-center gap-4 flex-shrink-0">
      <button @click="$router.back()" class="p-2 hover:bg-parchment-100 rounded-full">
        <i class="fa-solid fa-arrow-left text-xl text-text-primary"></i>
      </button>
      <h1 class="font-serif text-xl font-semibold text-text-primary flex-1">
        {{ headerTitle }}
      </h1>
      <button class="p-2 hover:bg-parchment-100 rounded-full">
        <i class="fa-solid fa-filter text-xl text-text-secondary"></i>
      </button>
    </header>

    <!-- Results count -->
    <div class="px-6 py-3 text-sm text-text-secondary flex-shrink-0">
      {{ displayBooks.length }} books found
    </div>

    <!-- Scrollable book list -->
    <div class="flex-1 overflow-y-auto px-4 pb-24">
      <div class="space-y-4 pb-4">
        <BookCard
          v-for="book in displayBooks"
          :key="book.id"
          :book="book"
          @click="viewBook(book)"
        />
      </div>

      <!-- Empty state -->
      <EmptyState
        v-if="displayBooks.length === 0 && !booksStore.isLoading"
        title="No books in this area"
        description="Zoom out or pan the map to see more books"
      />

      <!-- Loading -->
      <div v-if="booksStore.isLoading" class="flex justify-center py-12">
        <LoadingSpinner message="Loading books..." />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import BookCard from '@/components/search/BookCard.vue'
import EmptyState from '@/components/shared/EmptyState.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import { useBooksStore } from '@/stores/books'
import { useUIStore } from '@/stores/ui'

const router = useRouter()
const booksStore = useBooksStore()
const uiStore = useUIStore()

const headerTitle = computed(() => {
  if (uiStore.mapBounds) {
    return 'Books in View'
  }
  return 'All Books'
})

const displayBooks = computed(() => {
  const bounds = uiStore.mapBounds
  if (!bounds) {
    return booksStore.allBooks
  }

  return booksStore.allBooks.filter(book => {
    if (!book.locations || book.locations.length === 0) return false
    return book.locations.some(loc => {
      const lat = loc.lat || loc.latitude
      const lng = loc.lng || loc.longitude
      if (lat == null || lng == null) return false
      return lat >= bounds.south && lat <= bounds.north &&
             lng >= bounds.west && lng <= bounds.east
    })
  })
})

function viewBook(book) {
  router.push({ name: 'book-detail', params: { id: book.id } })
}
</script>
