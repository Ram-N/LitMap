<template>
  <div class="min-h-screen pb-20 bg-parchment-50">
    <header class="bg-white border-b border-parchment-200 px-6 py-4">
      <h1 class="font-serif text-2xl font-semibold text-text-primary">
        Contribute
      </h1>
      <p class="text-text-secondary text-sm mt-1">Submit a book location</p>
    </header>

    <EmptyState
      title="Contributions Coming Soon"
      description="Book submission feature will be implemented later"
    />
  </div>
</template>

<script setup>
import EmptyState from '@/components/shared/EmptyState.vue'
</script>
