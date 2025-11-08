<template>
  <!-- Overlay -->
  <Transition name="fade">
    <div
      v-if="uiStore.isMenuOpen"
      class="fixed inset-0 bg-black bg-opacity-50 z-40"
      @click="uiStore.closeMenu"
    />
  </Transition>

  <!-- Sidebar -->
  <Transition name="slide">
    <aside
      v-if="uiStore.isMenuOpen"
      class="fixed top-0 left-0 h-full w-80 max-w-[85vw] bg-white shadow-2xl z-50 safe-top safe-bottom overflow-y-auto"
    >
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b">
        <h2 class="text-xl font-bold text-gray-800">Settings</h2>
        <button
          @click="uiStore.closeMenu"
          class="touch-target p-2 -mr-2 rounded-lg hover:bg-gray-100"
          aria-label="Close menu"
        >
          <X :size="24" class="text-gray-700" />
        </button>
      </div>

      <!-- Menu Content -->
      <div class="p-4 space-y-6">
        <!-- Collection Selector -->
        <div>
          <h3 class="text-sm font-semibold text-gray-700 mb-2">Book Collection</h3>
          <div class="space-y-2">
            <label
              v-for="collection in collections"
              :key="collection.value"
              class="flex items-center p-3 rounded-lg border-2 cursor-pointer transition-all
                     hover:bg-gray-50"
              :class="booksStore.currentCollection === collection.value
                ? 'border-primary-600 bg-primary-50'
                : 'border-gray-200'"
            >
              <input
                type="radio"
                :value="collection.value"
                :checked="booksStore.currentCollection === collection.value"
                @change="handleCollectionChange(collection.value)"
                class="sr-only"
              />
              <span class="flex-1 font-medium" :class="booksStore.currentCollection === collection.value ? 'text-primary-700' : 'text-gray-700'">
                {{ collection.label }}
              </span>
              <span class="text-sm text-gray-500">{{ collection.count }}</span>
            </label>
          </div>
        </div>

        <!-- Clustering Toggle -->
        <div>
          <h3 class="text-sm font-semibold text-gray-700 mb-2">Map Settings</h3>
          <Toggle
            v-model="uiStore.isClusteringEnabled"
            label="Cluster Markers"
            description="Group nearby markers together"
          />
        </div>

        <!-- Map Type Selector -->
        <div>
          <h3 class="text-sm font-semibold text-gray-700 mb-2">Map Type</h3>
          <div class="grid grid-cols-2 gap-2">
            <button
              v-for="type in mapTypes"
              :key="type.value"
              @click="uiStore.setMapType(type.value)"
              class="p-3 rounded-lg border-2 font-medium text-sm transition-all touch-target"
              :class="uiStore.mapType === type.value
                ? 'border-primary-600 bg-primary-50 text-primary-700'
                : 'border-gray-200 text-gray-700 hover:bg-gray-50'"
            >
              {{ type.label }}
            </button>
          </div>
        </div>

        <!-- About Section -->
        <div class="pt-4 border-t">
          <p class="text-sm text-gray-600">
            Discover books through the places they're set
          </p>
          <p class="text-xs text-gray-500 mt-2">
            Version 2.0 (Vue 3)
          </p>
        </div>
      </div>
    </aside>
  </Transition>
</template>

<script setup>
import { X } from 'lucide-vue-next'
import Toggle from '../shared/Toggle.vue'
import { useUIStore } from '@/stores/ui'
import { useBooksStore } from '@/stores/books'
import { useFirebase } from '@/composables/useFirebase'

const uiStore = useUIStore()
const booksStore = useBooksStore()
const { switchCollection } = useFirebase()

const collections = [
  { value: 'newbooks', label: 'New Books', count: '~50' },
  { value: 'books', label: 'Mid Collection', count: '~200' },
  { value: 'small_books', label: 'All Books', count: '~500' },
]

const mapTypes = [
  { value: 'roadmap', label: 'Roadmap' },
  { value: 'satellite', label: 'Satellite' },
  { value: 'hybrid', label: 'Hybrid' },
  { value: 'terrain', label: 'Terrain' },
]

async function handleCollectionChange(collection) {
  console.log('Collection changed to:', collection)

  try {
    await switchCollection(collection)
    console.log(`Switched to ${collection}: ${booksStore.booksCount} books`)

    // Close search results if open
    uiStore.clearSearch()
  } catch (error) {
    console.error('Error switching collection:', error)
  }
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.slide-enter-active, .slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from, .slide-leave-to {
  transform: translateX(-100%);
}
</style>
