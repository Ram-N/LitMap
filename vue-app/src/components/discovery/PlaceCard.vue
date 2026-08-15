<template>
  <div
    class="w-40 flex-shrink-0 snap-start cursor-pointer group"
    @click="$emit('click')"
  >
    <!-- Cover image or fallback -->
    <div class="w-40 h-24 rounded-xl overflow-hidden mb-2 relative">
      <img
        v-if="place.coverBook?.hasCover"
        :src="`${baseUrl}covers/${place.coverBook.id}.jpg`"
        :alt="place.country"
        class="w-full h-full object-cover group-hover:scale-105 transition-transform"
        @error="coverFailed = true"
      />
      <div
        v-if="!place.coverBook?.hasCover || coverFailed"
        class="w-full h-full flex items-center justify-center"
        :style="{ backgroundColor: placeColor }"
      >
        <MapPin class="w-8 h-8 text-white opacity-30" :stroke-width="1.5" />
      </div>
    </div>
    <h3 class="font-serif text-sm font-semibold text-text-primary truncate">{{ place.country }}</h3>
    <p class="text-xs text-text-secondary">{{ place.bookCount }} {{ place.bookCount === 1 ? 'book' : 'books' }}</p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { MapPin } from 'lucide-vue-next'

const props = defineProps({
  place: {
    type: Object,
    required: true
  }
})

defineEmits(['click'])

const coverFailed = ref(false)
const baseUrl = import.meta.env.BASE_URL

const placeColor = computed(() => {
  let hash = 0
  for (let i = 0; i < props.place.country.length; i++) {
    hash = ((hash << 5) - hash) + props.place.country.charCodeAt(i)
    hash |= 0
  }
  const hue = Math.abs(hash) % 360
  return `hsl(${hue}, 35%, 55%)`
})
</script>
