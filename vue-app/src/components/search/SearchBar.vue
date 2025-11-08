<template>
  <div class="relative">
    <!-- Search Button (collapsed state) -->
    <button
      v-if="!isExpanded"
      @click="expand"
      class="touch-target p-2 rounded-lg hover:bg-gray-100 active:bg-gray-200 transition-colors"
      aria-label="Search books"
    >
      <Search :size="24" class="text-gray-700" />
    </button>

    <!-- Expanded Search Form -->
    <div
      v-else
      class="fixed inset-x-0 top-0 safe-top bg-white shadow-lg z-50 p-4 transition-all duration-300"
    >
      <div class="max-w-2xl mx-auto">
        <!-- Header with close button -->
        <div class="flex items-center mb-4">
          <h2 class="text-lg font-semibold flex-1">Search Books</h2>
          <button
            @click="collapse"
            class="touch-target p-2 -mr-2 rounded-lg hover:bg-gray-100"
            aria-label="Close search"
          >
            <X :size="24" class="text-gray-700" />
          </button>
        </div>

        <!-- Search Input -->
        <div class="relative mb-4">
          <input
            ref="searchInput"
            v-model="searchQuery"
            type="text"
            placeholder="Search by title, author, location..."
            class="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            @keyup.enter="handleSearch"
          />
          <button
            v-if="searchQuery"
            @click="clearSearch"
            class="absolute right-2 top-1/2 -translate-y-1/2 p-2 hover:bg-gray-100 rounded-lg"
            aria-label="Clear search"
          >
            <X :size="20" class="text-gray-400" />
          </button>
        </div>

        <!-- Search Type Selector -->
        <SearchTypeSelector v-model="searchField" />

        <!-- Search Button -->
        <button
          @click="handleSearch"
          :disabled="!searchQuery.trim()"
          class="w-full touch-target bg-primary-600 text-white py-3 rounded-lg font-medium hover:bg-primary-700 active:bg-primary-800 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          Search
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { Search, X } from 'lucide-vue-next'
import SearchTypeSelector from './SearchTypeSelector.vue'
import { useUIStore } from '@/stores/ui'
import { useSearch } from '@/composables/useSearch'

const uiStore = useUIStore()
const { performSearch } = useSearch()

const isExpanded = ref(false)
const searchQuery = ref('')
const searchField = ref('any')
const searchInput = ref(null)

async function expand() {
  isExpanded.value = true
  await nextTick()
  searchInput.value?.focus()
}

function collapse() {
  isExpanded.value = false
  if (!searchQuery.value) {
    searchField.value = 'any'
  }
}

function clearSearch() {
  searchQuery.value = ''
  uiStore.clearSearch()
}

function handleSearch() {
  if (!searchQuery.value.trim()) return

  performSearch(searchQuery.value, searchField.value)
  collapse()
}
</script>
