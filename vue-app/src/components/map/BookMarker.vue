<template>
  <Marker
    :options="markerOptions"
    @click="handleClick"
    @mouseover="showInfoWindow"
    @mouseout="hideInfoWindow"
  >
    <!-- Custom Marker Content -->
    <template #default>
      <div
        :class="[
          'book-marker',
          { 'highlighted': isHighlighted }
        ]"
        :style="{ backgroundColor: bookColor }"
      >
        <!-- Unhighlighted state: Just initials -->
        <div v-if="!isHighlighted" class="marker-initials">
          {{ bookInitials }}
        </div>

        <!-- Highlighted state: Full book card -->
        <div v-else class="marker-expanded">
          <!-- Close button -->
          <button
            @click.stop="handleClose"
            class="close-button"
          >
            <X :size="16" />
          </button>

          <!-- Book content -->
          <div class="flex gap-3">
            <!-- Book cover -->
            <div class="flex-shrink-0">
              <img
                v-if="book.isbn"
                :src="coverUrl"
                :alt="`Cover of ${book.title}`"
                class="w-16 h-24 object-cover rounded cursor-pointer"
                @click.stop="openGoodreads"
                @error="handleImageError"
              />
              <div
                v-else
                class="w-16 h-24 bg-gray-200 rounded flex items-center justify-center text-xs text-gray-500"
              >
                No Cover
              </div>
              <div class="text-xs text-center mt-1 text-gray-600">
                {{ location.city }}
              </div>
            </div>

            <!-- Book info -->
            <div class="flex-1 min-w-0">
              <h3 class="font-bold text-sm line-clamp-2 mb-1">
                {{ book.title }}
              </h3>
              <p class="text-xs text-gray-600 mb-2">
                {{ book.author }}
              </p>
              <div class="text-xs text-gray-700 line-clamp-3 mb-2">
                {{ description }}
              </div>
              <div class="text-xs text-gray-500">
                {{ book.booktype }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </Marker>

  <!-- Info Window (hover tooltip) -->
  <InfoWindow
    v-if="showTooltip && !isHighlighted"
    :options="infoWindowOptions"
  >
    <div class="p-2 max-w-[200px]">
      <h3 class="font-bold text-sm mb-1">{{ book.title }}</h3>
      <p class="text-xs text-gray-600">{{ book.author }}</p>
      <p class="text-xs text-gray-500 mt-1">{{ book.booktype }}</p>
    </div>
  </InfoWindow>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Marker, InfoWindow } from 'vue3-google-map'
import { X } from 'lucide-vue-next'
import { useUIStore } from '@/stores/ui'
import { generateBookColor, getTitleInitials } from '@/utils/colors'

const props = defineProps({
  book: {
    type: Object,
    required: true
  },
  location: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['click'])

const uiStore = useUIStore()

const showTooltip = ref(false)
const imageError = ref(false)

// Marker configuration
const markerOptions = computed(() => ({
  position: {
    lat: props.location.lat || props.location.latitude,
    lng: props.location.lng || props.location.longitude
  },
  title: `${props.book.title} by ${props.book.author}`
}))

const infoWindowOptions = computed(() => ({
  position: markerOptions.value.position,
  disableAutoPan: true
}))

// Marker appearance
const bookColor = computed(() => generateBookColor(props.book))
const bookInitials = computed(() => getTitleInitials(props.book.title))

const isHighlighted = computed(() => {
  return uiStore.highlightedMarkerId === `${props.book.id}-${props.location.lat}-${props.location.lng}`
})

const coverUrl = computed(() => {
  return `https://covers.openlibrary.org/b/isbn/${props.book.isbn}-M.jpg`
})

const description = computed(() => {
  return props.location.description || props.book.description || ''
})

function handleClick() {
  const markerId = `${props.book.id}-${props.location.lat}-${props.location.lng}`

  if (isHighlighted.value) {
    // Already highlighted, do nothing (close button handles closing)
    return
  }

  // Highlight this marker
  uiStore.setHighlightedMarker(markerId)

  // Also emit click for parent handling
  emit('click')
}

function handleClose() {
  uiStore.clearHighlightedMarker()
}

function showInfoWindow() {
  showTooltip.value = true
}

function hideInfoWindow() {
  showTooltip.value = false
}

function openGoodreads() {
  if (props.book.isbn) {
    const url = `https://www.goodreads.com/book/isbn/${props.book.isbn}`
    window.open(url, '_blank')
  }
}

function handleImageError() {
  imageError.value = true
}
</script>

<style scoped>
.book-marker {
  position: relative;
  border-radius: 8px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.marker-initials {
  padding: 8px 12px;
  font-weight: bold;
  font-size: 14px;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  white-space: nowrap;
}

.marker-expanded {
  background: white;
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 280px;
  max-width: 320px;
}

.book-marker.highlighted {
  z-index: 1000 !important;
}

.close-button {
  position: absolute;
  top: 4px;
  right: 4px;
  padding: 4px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  transition: background 0.2s;
}

.close-button:hover {
  background: rgba(0, 0, 0, 0.2);
}
</style>
