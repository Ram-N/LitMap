<template>
  <div class="pb-24 min-h-screen">
    <div class="px-6 pt-8 pb-4">
      <h1 class="font-serif text-3xl font-bold text-text-primary mb-2">Find Your Next Book</h1>
      <p class="text-text-secondary">Filter by type, region and genre</p>
    </div>

    <div class="px-6 py-12 text-center">
      <Compass class="w-12 h-12 text-text-tertiary mx-auto mb-3" :stroke-width="1.5" />
      <p class="text-text-secondary">Coming soon</p>
      <p class="text-sm text-text-tertiary mt-1">Guided book discovery is being built</p>
    </div>
  </div>
</template>

<script setup>
import { Compass } from 'lucide-vue-next'
</script>
