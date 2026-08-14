<template>
  <div class="h-screen flex flex-col bg-parchment-50">
    <!-- Header -->
    <div class="flex items-center gap-3 px-4 py-3 bg-white border-b border-parchment-200">
      <button
        @click="$router.back()"
        class="p-2 -ml-2 rounded-lg hover:bg-parchment-100 transition-colors"
      >
        <ArrowLeft class="w-5 h-5 text-text-secondary" />
      </button>
      <div class="min-w-0">
        <h1 class="font-serif text-lg font-semibold text-text-primary truncate">
          {{ book?.title }}
        </h1>
        <p v-if="book" class="text-xs text-text-secondary">
          {{ book.locations.length }} stops &middot; Journey Map
        </p>
      </div>
    </div>

    <!-- Map -->
    <div class="flex-1 min-h-0">
      <BookJourneyMap
        v-if="book && book.locations.length > 0"
        :locations="book.locations"
        :book-title="book.title"
      />

      <div v-else-if="booksStore.isLoading" class="flex items-center justify-center h-full">
        <LoadingSpinner message="Loading book..." />
      </div>

      <EmptyState
        v-else
        title="Book not found"
        description="This book may have been removed"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft } from 'lucide-vue-next'
import BookJourneyMap from '@/components/map/BookJourneyMap.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import EmptyState from '@/components/shared/EmptyState.vue'
import { useBooksStore } from '@/stores/books'

const route = useRoute()
const booksStore = useBooksStore()

const bookId = computed(() => route.params.id)
const book = computed(() => booksStore.allBooks.find(b => b.id === bookId.value))
</script>
