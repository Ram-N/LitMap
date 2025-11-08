<template>
  <nav class="safe-top bg-white shadow-md z-50 flex items-center px-4 py-3">
    <!-- Hamburger Menu Button -->
    <button
      @click="uiStore.toggleMenu"
      class="touch-target p-2 -ml-2 mr-2 rounded-lg hover:bg-gray-100 active:bg-gray-200 transition-colors"
      aria-label="Open menu"
    >
      <Menu :size="24" class="text-gray-700" />
    </button>

    <!-- Logo/Title -->
    <div class="flex-1 flex items-center">
      <h1 class="text-xl md:text-2xl font-bold text-primary-600">LitMap</h1>
    </div>

    <!-- Search Bar (Floating) -->
    <SearchBar />
  </nav>
</template>

<script setup>
import { Menu } from 'lucide-vue-next'
import SearchBar from '../search/SearchBar.vue'
import { useUIStore } from '@/stores/ui'

const uiStore = useUIStore()
</script>
