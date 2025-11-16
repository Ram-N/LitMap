<template>
  <div class="min-h-screen pb-20 bg-parchment-50">
    <header class="bg-white border-b border-parchment-200 px-6 py-4">
      <h1 class="font-serif text-2xl font-semibold text-text-primary">
        My Library
      </h1>
      <p class="text-text-secondary text-sm mt-1">Coming in Phase 5</p>
    </header>

    <EmptyState
      title="Library Coming Soon"
      description="Personal library feature will be implemented in Phase 5"
    />
  </div>
</template>

<script setup>
import EmptyState from '@/components/shared/EmptyState.vue'
</script>
