<template>
  <div class="min-h-screen bg-parchment-50 pb-20">
    <BookDetails
      v-if="book"
      :book="book"
      @close="$router.back()"
    />

    <div v-else-if="booksStore.isLoading" class="flex items-center justify-center min-h-screen">
      <LoadingSpinner message="Loading book..." />
    </div>

    <EmptyState
      v-else
      title="Book not found"
      description="This book may have been removed"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import BookDetails from '@/components/search/BookDetails.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import EmptyState from '@/components/shared/EmptyState.vue'
import { useBooksStore } from '@/stores/books'

const route = useRoute()
const booksStore = useBooksStore()

const bookId = computed(() => route.params.id)
const book = computed(() => booksStore.allBooks.find(b => b.id === bookId.value))
</script>
