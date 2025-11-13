<template>
  <header class="h-16 bg-parchment-50 px-6 flex items-center border-b border-parchment-200 relative z-10">
    <!-- Logo/Title with Georgia serif -->
    <h1 class="font-serif text-2xl font-semibold text-text-primary tracking-tight">
      LitMap
    </h1>

    <!-- Search Button -->
    <button
      @click="openSearch"
      class="ml-auto p-2 hover:bg-parchment-200/50 rounded-full transition-colors touch-target"
      aria-label="Open search"
    >
      <Search class="w-6 h-6 text-teal-deep" :stroke-width="2" />
    </button>

    <!-- Search Bar (Floating overlay - kept for now) -->
    <SearchBar v-if="showSearch" @close="showSearch = false" />
  </header>
</template>

<script setup>
import { ref } from 'vue'
import { Search } from 'lucide-vue-next'
import SearchBar from '../search/SearchBar.vue'

const showSearch = ref(false)

function openSearch() {
  showSearch.value = true
}
</script>
