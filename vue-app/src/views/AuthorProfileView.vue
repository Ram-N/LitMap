<template>
  <div class="min-h-screen bg-parchment-50 pb-20">
    <!-- Header -->
    <header class="bg-white border-b border-parchment-200 px-4 py-4 flex items-center gap-4">
      <button @click="$router.back()" class="p-2 hover:bg-parchment-100 rounded-full">
        <i class="fa-solid fa-arrow-left text-xl text-text-primary"></i>
      </button>
      <h1 class="font-serif text-xl font-semibold text-text-primary">
        Author Profile
      </h1>
    </header>

    <div v-if="author" class="px-6 py-8">
      <!-- Author Card -->
      <div class="bg-white rounded-2xl shadow-card p-6 mb-8">
        <!-- Avatar -->
        <div
          class="w-24 h-24 rounded-full mx-auto mb-4 flex items-center justify-center text-white text-2xl font-semibold"
          :style="{ backgroundColor: author.avatar.color }"
        >
          {{ author.avatar.initials }}
        </div>

        <!-- Name -->
        <h2 class="font-serif text-2xl font-semibold text-text-primary text-center mb-2">
          {{ author.name }}
        </h2>

        <!-- Bio (if exists) -->
        <p v-if="author.bio" class="text-text-secondary text-center mb-4 leading-relaxed">
          {{ author.bio }}
        </p>

        <!-- Stats -->
        <div class="flex justify-center gap-8 mt-6">
          <div class="text-center">
            <div class="text-2xl font-semibold text-teal-deep">{{ author.bookCount }}</div>
            <div class="text-sm text-text-tertiary">books</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-semibold text-teal-deep">{{ author.countryCount }}</div>
            <div class="text-sm text-text-tertiary">countries</div>
          </div>
        </div>

        <!-- Genres -->
        <div v-if="author.genres.length > 0" class="mt-6 flex justify-center gap-2 flex-wrap">
          <GenreBadge
            v-for="genre in author.genres"
            :key="genre"
            :genre="genre"
          />
        </div>
      </div>

      <!-- Journey Map Section -->
      <section class="mb-8">
        <h3 class="font-serif text-xl font-semibold text-text-primary mb-4">
          Journey Map
        </h3>
        <div class="bg-white rounded-2xl shadow-card p-4">
          <AuthorJourneyMap :locations="author.journeyLocations" />
        </div>
      </section>

      <!-- Books by this Author -->
      <section>
        <h3 class="font-serif text-xl font-semibold text-text-primary mb-4">
          Books by {{ author.name }}
        </h3>
        <div class="space-y-4">
          <BookCard
            v-for="book in author.books"
            :key="book.id"
            :book="book"
            @click="viewBook(book)"
          />
        </div>
      </section>
    </div>

    <div v-else-if="authorsStore.isLoading" class="flex items-center justify-center min-h-screen">
      <LoadingSpinner message="Loading author profile..." />
    </div>

    <EmptyState
      v-else
      title="Author not found"
      description="This author may not have any books in our collection"
    />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BookCard from '@/components/search/BookCard.vue'
import GenreBadge from '@/components/shared/GenreBadge.vue'
import AuthorJourneyMap from '@/components/map/AuthorJourneyMap.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import EmptyState from '@/components/shared/EmptyState.vue'
import { useAuthorsStore } from '@/stores/authors'

const route = useRoute()
const router = useRouter()
const authorsStore = useAuthorsStore()

const authorName = computed(() => decodeURIComponent(route.params.name))
const author = computed(() => authorsStore.getAuthorByName.value(authorName.value))

function viewBook(book) {
  router.push({ name: 'book-detail', params: { id: book.id } })
}

onMounted(async () => {
  if (!author.value) {
    await authorsStore.fetchAuthorProfile(authorName.value)
  }
})
</script>
