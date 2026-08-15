<template>
  <div class="pb-24 min-h-screen">
    <!-- Header -->
    <div class="px-6 pt-10 pb-6 text-center">
      <h1 class="font-serif text-4xl font-bold text-text-primary mb-2">LitMap</h1>
      <p class="text-text-secondary text-lg">Discover books through places, people and stories</p>
    </div>

    <!-- Three Entry Point Cards -->
    <div class="px-4 space-y-3 mb-8">
      <!-- Explore the World -->
      <button
        @click="$router.push('/map')"
        class="w-full bg-white rounded-2xl shadow-card hover:shadow-elevated transition-shadow p-5 border border-parchment-200 text-left flex items-center gap-4"
      >
        <div class="w-12 h-12 rounded-xl bg-teal-deep/10 flex items-center justify-center flex-shrink-0">
          <Globe class="w-6 h-6 text-teal-deep" :stroke-width="1.5" />
        </div>
        <div class="flex-1 min-w-0">
          <h2 class="font-serif text-lg font-semibold text-text-primary">Explore the World</h2>
          <p class="text-sm text-text-secondary">Browse books on an interactive map</p>
        </div>
        <ChevronRight class="w-5 h-5 text-text-tertiary flex-shrink-0" />
      </button>

      <!-- Find My Next Book -->
      <button
        @click="$router.push('/discover')"
        class="w-full bg-white rounded-2xl shadow-card hover:shadow-elevated transition-shadow p-5 border border-parchment-200 text-left flex items-center gap-4"
      >
        <div class="w-12 h-12 rounded-xl bg-copper-warm/10 flex items-center justify-center flex-shrink-0">
          <Compass class="w-6 h-6 text-copper-warm" :stroke-width="1.5" />
        </div>
        <div class="flex-1 min-w-0">
          <h2 class="font-serif text-lg font-semibold text-text-primary">Find My Next Book</h2>
          <p class="text-sm text-text-secondary">Filter by mood, genre and region</p>
        </div>
        <ChevronRight class="w-5 h-5 text-text-tertiary flex-shrink-0" />
      </button>

      <!-- Explore a Place -->
      <div class="w-full bg-white rounded-2xl shadow-card p-5 border border-parchment-200">
        <div class="flex items-center gap-4 mb-3">
          <div class="w-12 h-12 rounded-xl bg-genre-historical/10 flex items-center justify-center flex-shrink-0">
            <MapPin class="w-6 h-6 text-genre-historical" :stroke-width="1.5" />
          </div>
          <div class="flex-1 min-w-0">
            <h2 class="font-serif text-lg font-semibold text-text-primary">Explore a Place</h2>
            <p class="text-sm text-text-secondary">See all books set in a location</p>
          </div>
        </div>
        <form @submit.prevent="goToPlace" class="flex gap-2">
          <input
            v-model="placeQuery"
            type="text"
            placeholder="e.g. Kenya, Tokyo, Paris..."
            class="flex-1 px-4 py-2.5 rounded-xl border border-parchment-200 bg-parchment-50 text-text-primary placeholder-text-tertiary text-sm focus:outline-none focus:border-teal-deep focus:ring-1 focus:ring-teal-deep"
          />
          <button
            type="submit"
            :disabled="!placeQuery.trim()"
            class="px-4 py-2.5 rounded-xl bg-teal-deep text-white text-sm font-medium disabled:opacity-40 transition-opacity"
          >
            Go
          </button>
        </form>
      </div>
    </div>

    <!-- Stats Bar -->
    <div v-if="booksStore.booksCount > 0" class="px-6 mb-8">
      <div class="flex justify-center gap-6 text-sm text-text-secondary">
        <span class="font-medium">{{ booksStore.booksCount }} books</span>
        <span class="text-parchment-200">|</span>
        <span class="font-medium">{{ countryCount }} countries</span>
      </div>
    </div>

    <!-- Discovery Sections (Phase 2) -->
    <div v-if="booksStore.booksCount > 0">
      <!-- Places Worth Exploring -->
      <section class="mb-8">
        <h2 class="font-serif text-xl font-semibold text-text-primary px-6 mb-3">Places Worth Exploring</h2>
        <HorizontalScroller>
          <PlaceCard
            v-for="place in placesWorthExploring"
            :key="place.country"
            :place="place"
            @click="$router.push(`/place/${encodeURIComponent(place.country)}`)"
          />
        </HorizontalScroller>
      </section>

      <!-- Books You Might Like -->
      <section class="mb-8">
        <h2 class="font-serif text-xl font-semibold text-text-primary px-6 mb-3">Books You Might Like</h2>
        <HorizontalScroller>
          <div v-for="book in featuredBooks" :key="book.id" class="w-64 flex-shrink-0">
            <BookCard :book="book" @click="$router.push(`/book/${book.id}`)" />
          </div>
        </HorizontalScroller>
      </section>

      <!-- Author Trails -->
      <section class="mb-8">
        <h2 class="font-serif text-xl font-semibold text-text-primary px-6 mb-3">Author Trails</h2>
        <HorizontalScroller>
          <AuthorTrailCard
            v-for="trail in authorTrails"
            :key="trail.author"
            :trail="trail"
            @click="$router.push(`/author/${encodeURIComponent(trail.author)}`)"
          />
        </HorizontalScroller>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Globe, Compass, MapPin, ChevronRight } from 'lucide-vue-next'
import { useBooksStore } from '@/stores/books'
import { useDiscovery } from '@/composables/useDiscovery'
import HorizontalScroller from '@/components/discovery/HorizontalScroller.vue'
import PlaceCard from '@/components/discovery/PlaceCard.vue'
import AuthorTrailCard from '@/components/discovery/AuthorTrailCard.vue'
import BookCard from '@/components/search/BookCard.vue'

const router = useRouter()
const booksStore = useBooksStore()
const { placesWorthExploring, featuredBooks, authorTrails, countryCount } = useDiscovery()

const placeQuery = ref('')

function goToPlace() {
  const query = placeQuery.value.trim()
  if (query) {
    router.push(`/place/${encodeURIComponent(query)}`)
  }
}
</script>
