<template>
  <div class="p-4">
    <!-- Header -->
    <div class="mb-4">
      <h2 class="font-serif text-xl font-semibold text-text-primary">
        {{ place.name }}
      </h2>
      <p class="text-sm text-text-secondary mt-1">
        {{ place.books.length }} {{ place.books.length === 1 ? 'book' : 'books' }} connected to this place
      </p>
    </div>

    <!-- Action Buttons -->
    <div class="flex gap-3 mb-5">
      <button
        @click="handleZoomIn"
        class="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 bg-parchment-50 border border-parchment-200 rounded-xl text-sm font-medium text-text-primary hover:bg-parchment-100 transition-colors"
      >
        <ZoomIn class="w-4 h-4" />
        Zoom In
      </button>
      <router-link
        :to="{ name: 'place', params: { placeName: place.name } }"
        class="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 bg-teal-deep text-white rounded-xl text-sm font-medium hover:bg-teal-deep/90 transition-colors"
        @click="uiStore.hideBottomSheet()"
      >
        <MapPin class="w-4 h-4" />
        Explore This Place
      </router-link>
    </div>

    <!-- Book Cards -->
    <div class="space-y-3">
      <BookCard
        v-for="book in place.books"
        :key="book.id"
        :book="book"
        @click="uiStore.showBookDetails(book)"
      />
    </div>
  </div>
</template>

<script setup>
import { ZoomIn, MapPin } from 'lucide-vue-next'
import BookCard from '@/components/search/BookCard.vue'
import { useUIStore } from '@/stores/ui'

const props = defineProps({
  place: {
    type: Object,
    required: true
  }
})

const uiStore = useUIStore()

function handleZoomIn() {
  // Compute center of the place's books and zoom in
  const points = []
  props.place.books.forEach(book => {
    if (book.locations && Array.isArray(book.locations)) {
      book.locations.forEach(loc => {
        const lat = loc.lat || loc.latitude
        const lng = loc.lng || loc.longitude
        if (lat && lng) points.push({ lat, lng })
      })
    }
  })

  if (points.length > 0) {
    const avgLat = points.reduce((sum, p) => sum + p.lat, 0) / points.length
    const avgLng = points.reduce((sum, p) => sum + p.lng, 0) / points.length
    uiStore.setMapCenter({ lat: avgLat, lng: avgLng })
    uiStore.setMapZoom(Math.min((uiStore.mapZoom || 3) + 3, 15))
  }

  uiStore.hideBottomSheet()
}
</script>
