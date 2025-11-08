<template>
  <div
    class="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
    @click="$emit('click')"
  >
    <div class="flex gap-3 p-3">
      <!-- Book Cover -->
      <div class="flex-shrink-0">
        <img
          v-if="book.isbn"
          :src="coverUrl"
          :alt="`Cover of ${book.title}`"
          class="w-16 h-24 object-cover rounded"
          @error="handleImageError"
        />
        <div
          v-else
          class="w-16 h-24 bg-gradient-to-br from-primary-400 to-primary-600 rounded flex items-center justify-center text-white font-bold text-xs"
        >
          {{ bookInitials }}
        </div>
      </div>

      <!-- Book Info -->
      <div class="flex-1 min-w-0">
        <h3 class="font-semibold text-gray-900 line-clamp-2 mb-1">
          {{ book.title }}
        </h3>
        <p class="text-sm text-gray-600 mb-2">{{ book.author }}</p>

        <div v-if="book.booktype" class="inline-block px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded mb-2">
          {{ book.booktype }}
        </div>

        <!-- Locations -->
        <div v-if="book.locations && book.locations.length > 0" class="text-xs text-gray-500">
          <span class="inline-flex items-center gap-1">
            <MapPin :size="12" />
            {{ locationText }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { MapPin } from 'lucide-vue-next'

const props = defineProps({
  book: {
    type: Object,
    required: true
  }
})

defineEmits(['click'])

const imageError = ref(false)

const coverUrl = computed(() => {
  return `https://covers.openlibrary.org/b/isbn/${props.book.isbn}-M.jpg`
})

const bookInitials = computed(() => {
  return props.book.title
    .split(' ')
    .slice(0, 2)
    .map(word => word[0])
    .join('')
    .toUpperCase()
})

const locationText = computed(() => {
  if (!props.book.locations || props.book.locations.length === 0) return ''

  const location = props.book.locations[0]
  const parts = [location.city, location.state, location.country].filter(Boolean)

  if (props.book.locations.length > 1) {
    return `${parts.join(', ')} +${props.book.locations.length - 1} more`
  }

  return parts.join(', ')
})

function handleImageError() {
  imageError.value = true
}
</script>
