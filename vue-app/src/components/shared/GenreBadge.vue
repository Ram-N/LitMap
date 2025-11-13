<template>
  <span
    :class="badgeClasses"
    class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium"
  >
    {{ displayGenre }}
  </span>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  genre: {
    type: String,
    required: true
  }
});

const displayGenre = computed(() => {
  // Capitalize first letter and format
  return props.genre.charAt(0).toUpperCase() + props.genre.slice(1).toLowerCase();
});

const badgeClasses = computed(() => {
  // Normalize genre name for matching
  const normalizedGenre = props.genre.toLowerCase().trim();

  // Map genres to colors
  const genreColorMap = {
    'memoir': 'bg-genre-memoir/20 text-genre-memoir border border-genre-memoir/30',
    'adventure': 'bg-genre-adventure/20 text-genre-adventure border border-genre-adventure/30',
    'historical': 'bg-genre-historical/20 text-genre-historical border border-genre-historical/30',
    'travel': 'bg-genre-travel/20 text-genre-travel border border-genre-travel/30',
    'fiction': 'bg-teal-deep/20 text-teal-deep border border-teal-deep/30',
    'non-fiction': 'bg-copper-warm/20 text-copper-warm border border-copper-warm/30',
    'nonfiction': 'bg-copper-warm/20 text-copper-warm border border-copper-warm/30',
    'poetry': 'bg-purple-600/20 text-purple-600 border border-purple-600/30',
    'photography': 'bg-blue-600/20 text-blue-600 border border-blue-600/30',
    'biography': 'bg-amber-600/20 text-amber-600 border border-amber-600/30',
    'default': 'bg-parchment-200 text-text-secondary border border-parchment-300'
  };

  // Check for partial matches (e.g., "historical fiction" contains "historical")
  for (const [key, value] of Object.entries(genreColorMap)) {
    if (normalizedGenre.includes(key)) {
      return value;
    }
  }

  return genreColorMap.default;
});
</script>
