<template>
  <div class="min-h-screen pb-20 bg-parchment-50">
    <!-- Header -->
    <header class="bg-white border-b border-parchment-200 px-4 py-4 flex items-center gap-4">
      <button @click="$router.back()" class="p-2 hover:bg-parchment-100 rounded-full">
        <i class="fa-solid fa-arrow-left text-xl text-text-primary"></i>
      </button>
      <h1 class="font-serif text-xl font-semibold text-text-primary flex-1">
        All Books
      </h1>
      <button class="p-2 hover:bg-parchment-100 rounded-full">
        <i class="fa-solid fa-filter text-xl text-text-secondary"></i>
      </button>
    </header>

    <!-- Results count -->
    <div class="px-6 py-4 text-sm text-text-secondary">
      {{ displayBooks.length }} books found
    </div>

    <!-- Book list -->
    <div class="px-4 space-y-4 pb-8">
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
      title="No books found"
      description="Try adjusting your search or filters"
    />

    <!-- Loading -->
    <div v-if="booksStore.isLoading" class="flex justify-center py-12">
      <LoadingSpinner message="Loading books..." />
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

const router = useRouter()
const booksStore = useBooksStore()

const displayBooks = computed(() => booksStore.allBooks)

function viewBook(book) {
  router.push({ name: 'book-detail', params: { id: book.id } })
}
</script>
