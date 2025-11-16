<template>
  <div class="min-h-screen pb-20 bg-parchment-50">
    <header class="bg-white border-b border-parchment-200 px-4 py-4 flex items-center gap-4">
      <button @click="$router.back()" class="p-2 hover:bg-parchment-100 rounded-full">
        <i class="fa-solid fa-arrow-left text-xl text-text-primary"></i>
      </button>
      <h1 class="font-serif text-xl font-semibold text-text-primary">
        Author Profile
      </h1>
    </header>

    <EmptyState
      title="Author Profiles Coming Soon"
      description="Author profile pages will be implemented in Phase 4"
    />
  </div>
</template>

<script setup>
import EmptyState from '@/components/shared/EmptyState.vue'
</script>
