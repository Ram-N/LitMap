<template>
  <div
    class="w-48 flex-shrink-0 snap-start cursor-pointer bg-white rounded-xl shadow-card hover:shadow-elevated transition-shadow p-4 border border-parchment-200"
    @click="$emit('click')"
  >
    <h3 class="font-serif text-sm font-semibold text-text-primary truncate mb-1">{{ trail.author }}</h3>
    <p class="text-xs text-text-secondary mb-2">
      {{ trail.bookCount }} {{ trail.bookCount === 1 ? 'book' : 'books' }}
    </p>
    <div class="flex flex-wrap gap-1">
      <span
        v-for="country in displayCountries"
        :key="country"
        class="text-xs px-2 py-0.5 rounded-full bg-parchment-100 text-text-secondary"
      >
        {{ country }}
      </span>
      <span
        v-if="trail.countries.length > 3"
        class="text-xs px-2 py-0.5 rounded-full bg-parchment-100 text-text-tertiary"
      >
        +{{ trail.countries.length - 3 }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  trail: {
    type: Object,
    required: true
  }
})

defineEmits(['click'])

const displayCountries = computed(() => props.trail.countries.slice(0, 3))
</script>
