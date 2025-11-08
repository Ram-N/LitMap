<template>
  <div class="space-y-4">
    <!-- Book Header -->
    <div class="flex gap-4">
      <img
        v-if="book.isbn"
        :src="coverUrl"
        :alt="`Cover of ${book.title}`"
        class="w-24 h-36 object-cover rounded-lg shadow-md"
      />
      <div class="flex-1">
        <h2 class="text-xl font-bold text-gray-900 mb-2">{{ book.title }}</h2>
        <p class="text-gray-700 mb-1">{{ book.author }}</p>
        <div v-if="book.booktype" class="inline-block px-3 py-1 bg-primary-100 text-primary-700 text-sm rounded-full">
          {{ book.booktype }}
        </div>
      </div>
    </div>

    <!-- Description -->
    <div v-if="book.description">
      <h3 class="font-semibold text-gray-900 mb-2">Description</h3>
      <p class="text-gray-700 text-sm leading-relaxed">{{ book.description }}</p>
    </div>

    <!-- Locations -->
    <div v-if="book.locations && book.locations.length > 0">
      <h3 class="font-semibold text-gray-900 mb-2">Locations</h3>
      <div class="space-y-2">
        <div
          v-for="(location, index) in book.locations"
          :key="index"
          class="flex items-start gap-2 text-sm"
        >
          <MapPin :size="16" class="text-primary-600 flex-shrink-0 mt-0.5" />
          <span class="text-gray-700">
            {{ formatLocation(location) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Genre/Tags -->
    <div v-if="book.genre || book.tags">
      <h3 class="font-semibold text-gray-900 mb-2">Tags</h3>
      <div class="flex flex-wrap gap-2">
        <span v-if="book.genre" class="px-3 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
          {{ book.genre }}
        </span>
        <span
          v-for="tag in parsedTags"
          :key="tag"
          class="px-3 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
        >
          {{ tag }}
        </span>
      </div>
    </div>

    <!-- Goodreads Link -->
    <a
      v-if="book.isbn"
      :href="goodreadsUrl"
      target="_blank"
      rel="noopener noreferrer"
      class="block w-full touch-target bg-primary-600 text-white text-center py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors"
    >
      View on Goodreads
    </a>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { MapPin } from 'lucide-vue-next'

const props = defineProps({
  book: {
    type: Object,
    required: true
  }
})

const coverUrl = computed(() => {
  return `https://covers.openlibrary.org/b/isbn/${props.book.isbn}-L.jpg`
})

const goodreadsUrl = computed(() => {
  return `https://www.goodreads.com/book/isbn/${props.book.isbn}`
})

const parsedTags = computed(() => {
  if (!props.book.tags) return []
  if (Array.isArray(props.book.tags)) return props.book.tags
  if (typeof props.book.tags === 'string') {
    return props.book.tags.split(',').map(tag => tag.trim()).filter(Boolean)
  }
  return []
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
