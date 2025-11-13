<template>
  <div class="fixed right-6 bottom-28 flex flex-col gap-3 z-20">
    <!-- Random location FAB -->
    <button
      class="w-12 h-12 rounded-full bg-teal-deep shadow-fab hover:shadow-xl transition-shadow flex items-center justify-center touch-target"
      @click="$emit('random-location')"
      title="Random location"
      aria-label="Go to random location"
    >
      <Dices class="w-5 h-5 text-white" :stroke-width="2" />
    </button>

    <!-- Center location FAB -->
    <button
      class="w-14 h-14 rounded-full bg-teal-deep shadow-fab hover:shadow-xl transition-shadow flex items-center justify-center touch-target"
      @click="$emit('center-location')"
      title="Center on your location"
      aria-label="Center map on your location"
    >
      <Target class="w-6 h-6 text-white" :stroke-width="2" />
    </button>
  </div>
</template>

<script setup>
import { Dices, Target } from 'lucide-vue-next'

defineEmits(['random-location', 'center-location'])
</script>
