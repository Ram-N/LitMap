<template>
  <div class="pb-24 min-h-screen">
    <!-- Header -->
    <div class="px-6 pt-8 pb-4">
      <button
        @click="$router.back()"
        class="inline-flex items-center gap-1 text-sm text-text-secondary mb-4 hover:text-text-primary transition-colors"
      >
        <ArrowLeft class="w-4 h-4" />
        Back
      </button>
      <h1 class="font-serif text-3xl font-bold text-text-primary mb-1">{{ displayName }}</h1>
      <p class="text-text-secondary">
        {{ books.length }} {{ books.length === 1 ? 'book' : 'books' }}
      </p>
    </div>

    <!-- View on Map button -->
    <div v-if="placeCoordinates" class="px-6 mb-6">
      <button
        @click="viewOnMap"
        class="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl border-2 border-teal-deep text-teal-deep text-sm font-medium hover:bg-teal-deep hover:text-white transition-colors"
      >
        <MapIcon class="w-4 h-4" />
        View on Map
      </button>
    </div>

    <!-- No books found -->
    <div v-if="books.length === 0 && !booksStore.isLoading" class="px-6 py-12 text-center">
      <MapPin class="w-12 h-12 text-text-tertiary mx-auto mb-3" :stroke-width="1.5" />
      <p class="text-text-secondary mb-1">No books found for "{{ displayName }}"</p>
      <p class="text-sm text-text-tertiary">Try a different spelling or search for a country name</p>
    </div>

    <!-- Books by type -->
    <div v-for="group in booksByType" :key="group.type" class="mb-6">
      <h2 class="font-serif text-lg font-semibold text-text-primary px-6 mb-3">
        {{ group.type }}
        <span class="text-text-tertiary font-normal text-base ml-1">{{ group.books.length }}</span>
      </h2>
      <div class="px-4 space-y-3">
        <BookCard
          v-for="book in group.books"
          :key="book.id"
          :book="book"
          @click="$router.push(`/book/${book.id}`)"
        />
      </div>
    </div>

    <!-- Related Places -->
    <div v-if="relatedPlaces.length > 0" class="px-6 mt-8 mb-6">
      <h2 class="font-serif text-lg font-semibold text-text-primary mb-3">Related Places</h2>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="place in relatedPlaces"
          :key="place.name"
          @click="$router.push(`/place/${encodeURIComponent(place.name)}`)"
          class="px-3 py-1.5 rounded-full bg-parchment-100 border border-parchment-200 text-sm text-text-secondary hover:border-teal-deep hover:text-teal-deep transition-colors"
        >
          {{ place.name }} ({{ place.bookCount }})
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Map as MapIcon, MapPin } from 'lucide-vue-next'
import { useBooksStore } from '@/stores/books'
import { usePlace } from '@/composables/usePlace'
import BookCard from '@/components/search/BookCard.vue'

const route = useRoute()
const router = useRouter()
const booksStore = useBooksStore()

const placeName = computed(() => decodeURIComponent(route.params.placeName || ''))

const { books, booksByType, placeCoordinates, relatedPlaces } = usePlace(placeName)

const displayName = computed(() => placeName.value || '')

function viewOnMap() {
  if (placeCoordinates.value) {
    router.push({
      path: '/map',
      query: {
        lat: placeCoordinates.value.lat.toFixed(4),
        lng: placeCoordinates.value.lng.toFixed(4),
        zoom: 6,
      }
    })
  }
}
</script>
