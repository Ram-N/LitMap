<template>
  <div
    class="bg-white rounded-xl shadow-card hover:shadow-elevated transition-shadow p-4 cursor-pointer border border-transparent hover:border-copper-warm"
    @click="$emit('click')"
  >
    <div class="flex gap-4">
      <!-- Mock book cover with generated color -->
      <div
        class="w-20 h-28 rounded-lg flex-shrink-0 relative overflow-hidden"
        :style="{ backgroundColor: coverColor }"
      >
        <!-- Pattern overlay -->
        <div class="absolute inset-0 flex items-center justify-center opacity-20">
          <BookOpen class="w-8 h-8 text-white" :stroke-width="1.5" />
        </div>
      </div>

      <!-- Book Info -->
      <div class="flex-1 min-w-0">
        <!-- Title with Georgia serif -->
        <h3 class="font-serif text-lg font-semibold text-text-primary mb-1 line-clamp-2 leading-tight">
          {{ book.title }}
        </h3>

        <!-- Author -->
        <p class="text-sm text-text-secondary mb-2">
          {{ book.author }}
        </p>

        <!-- Genre badges -->
        <div v-if="displayGenres.length > 0" class="flex gap-2 flex-wrap mb-2">
          <GenreBadge
            v-for="genre in displayGenres"
            :key="genre"
            :genre="genre"
          />
        </div>

        <!-- Metadata -->
        <div class="flex items-center gap-4 text-xs text-text-tertiary">
          <span v-if="book.publication_year">{{ book.publication_year }}</span>
          <span v-if="primaryLocation" class="inline-flex items-center gap-1">
            <MapPin :size="12" />
            {{ primaryLocation }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { MapPin, BookOpen } from 'lucide-vue-next'
import GenreBadge from '../shared/GenreBadge.vue'

const props = defineProps({
  book: {
    type: Object,
    required: true
  }
})

defineEmits(['click'])

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

// Display up to 2 genres
const displayGenres = computed(() => {
  const genres = []

  // Handle genre - it can be a string or an array
  if (props.book.genre) {
    if (Array.isArray(props.book.genre)) {
      genres.push(...props.book.genre)
    } else {
      genres.push(props.book.genre)
    }
  }

  // Add tags if we don't have enough genres yet
  if (props.book.tags && Array.isArray(props.book.tags) && genres.length < 2) {
    genres.push(...props.book.tags.slice(0, 2 - genres.length))
  }

  // Remove duplicates using Set and return up to 2 unique genres
  return [...new Set(genres)].slice(0, 2)
})

// Primary location for display
const primaryLocation = computed(() => {
  if (!props.book.locations || props.book.locations.length === 0) return ''

  const location = props.book.locations[0]
  const parts = [location.city, location.country].filter(Boolean)

  if (props.book.locations.length > 1) {
    return `${parts.join(', ')} +${props.book.locations.length - 1}`
  }

  return parts.join(', ')
})
</script>
