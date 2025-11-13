<template>
  <div class="pb-6">
    <!-- Book Cover -->
    <div class="px-6 py-6">
      <div
        class="w-48 h-64 mx-auto rounded-lg shadow-elevated"
        :style="{ backgroundColor: coverColor }"
      >
        <!-- Mock cover design -->
        <div class="w-full h-full flex items-center justify-center opacity-20">
          <BookOpen class="w-16 h-16 text-white" :stroke-width="1.5" />
        </div>
      </div>
    </div>

    <!-- Title & Author -->
    <div class="px-6 mb-6">
      <h1 class="font-serif text-2xl font-semibold text-text-primary mb-2 leading-tight">
        {{ book.title }}
      </h1>
      <p class="text-lg text-text-secondary">
        {{ book.author }}
      </p>
    </div>

    <!-- Genre Badges -->
    <div v-if="displayGenres.length > 0" class="px-6 mb-6 flex gap-2 flex-wrap">
      <GenreBadge v-for="genre in displayGenres" :key="genre" :genre="genre" />
    </div>

    <!-- Metadata -->
    <div class="px-6 mb-6 flex gap-6">
      <div v-if="book.publication_year" class="flex items-center gap-2 text-text-secondary">
        <Calendar class="w-4 h-4" />
        <span class="text-sm">{{ book.publication_year }}</span>
      </div>
      <div v-if="book.page_count" class="flex items-center gap-2 text-text-secondary">
        <BookOpenIcon class="w-4 h-4" />
        <span class="text-sm">{{ book.page_count }} pages</span>
      </div>
    </div>

    <!-- Journey Location Section -->
    <section v-if="book.locations && book.locations.length > 0" class="px-6 mb-6">
      <h2 class="font-serif text-xl font-semibold text-text-primary mb-3">
        Journey Locations
      </h2>
      <div class="bg-parchment-50 rounded-xl p-4 border border-parchment-200">
        <div class="space-y-2">
          <div
            v-for="(location, index) in book.locations"
            :key="index"
            class="flex items-center gap-2 text-sm text-text-secondary"
          >
            <MapPin class="w-4 h-4 text-teal-deep" />
            <span>{{ formatLocation(location) }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Synopsis Section -->
    <section v-if="book.description" class="px-6 mb-6">
      <h2 class="font-serif text-xl font-semibold text-text-primary mb-3">
        Synopsis
      </h2>
      <div class="bg-white rounded-xl shadow-card p-5">
        <p class="text-text-secondary leading-relaxed">
          {{ book.description }}
        </p>
      </div>
    </section>

    <!-- Goodreads Link -->
    <div v-if="book.isbn" class="px-6">
      <a
        :href="goodreadsUrl"
        target="_blank"
        rel="noopener noreferrer"
        class="block w-full bg-copper-warm text-white text-center py-4 rounded-xl font-medium hover:shadow-elevated transition-shadow"
      >
        View on Goodreads
      </a>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { MapPin, Calendar, BookOpen as BookOpenIcon } from 'lucide-vue-next'
import { BookOpen } from 'lucide-vue-next'
import GenreBadge from '../shared/GenreBadge.vue'

const props = defineProps({
  book: {
    type: Object,
    required: true
  }
})

// Generate color based on book title hash
const coverColor = computed(() => {
  const hash = hashString(props.book.title)
  const hue = hash % 360
  return `hsl(${hue}, 40%, 60%)`
})

// Simple string hash function
function hashString(str) {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash // Convert to 32bit integer
  }
  return Math.abs(hash)
}

const goodreadsUrl = computed(() => {
  return `https://www.goodreads.com/book/isbn/${props.book.isbn}`
})

// Display genres
const displayGenres = computed(() => {
  const genres = []

  if (props.book.genre) {
    genres.push(props.book.genre)
  }

  if (props.book.tags && Array.isArray(props.book.tags)) {
    genres.push(...props.book.tags.slice(0, 3 - genres.length))
  }

  return genres.slice(0, 3)
})

function formatLocation(location) {
  const parts = []

  if (location.place) parts.push(location.place)
  if (location.city) parts.push(location.city)
  if (location.state) parts.push(location.state)
  if (location.country) parts.push(location.country)

  return parts.join(', ') || 'Unknown location'
}
</script>
