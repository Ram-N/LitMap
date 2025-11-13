<template>
  <!-- Component Showcase Mode (temporary for testing) -->
  <ComponentShowcase v-if="showComponentShowcase" />

  <!-- Main App -->
  <div v-else class="flex flex-col h-screen w-screen overflow-hidden bg-gray-50">
    <!-- Top Bar -->
    <TopBar />

    <!-- Toggle Button for Showcase (temporary) -->
    <button
      @click="showComponentShowcase = true"
      class="fixed top-20 right-4 z-50 bg-copper-warm text-white px-3 py-2 rounded-lg shadow-elevated text-sm"
      title="View new design system components"
    >
      🎨 Design System
    </button>

    <!-- Main Content: Map View -->
    <main class="flex-1 relative overflow-hidden">
      <!-- Google Map (always rendered) -->
      <GoogleMapComponent />

      <!-- Loading State Overlay -->
      <div v-if="booksStore.isLoading" class="absolute inset-0 z-50 bg-white flex items-center justify-center pointer-events-none">
        <LoadingSpinner message="Loading books..." />
      </div>

      <!-- Error State Overlay -->
      <div v-else-if="booksStore.error" class="absolute inset-0 z-50 bg-white flex items-center justify-center">
        <div class="text-center p-8">
          <p class="text-red-600 mb-4">Error loading books</p>
          <p class="text-gray-600 text-sm">{{ booksStore.error }}</p>
        </div>
      </div>

      <!-- FAB Button -->
      <FAB
        v-if="!booksStore.isLoading"
        icon="Shuffle"
        @click="handleRandomLocation"
        class="absolute bottom-20 right-4 z-10"
      />
    </main>

    <!-- Bottom Sheet -->
    <BottomSheet />

    <!-- Hamburger Menu -->
    <HamburgerMenu />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ComponentShowcase from './components/ComponentShowcase.vue'
import TopBar from './components/layout/TopBar.vue'
import BottomSheet from './components/layout/BottomSheet.vue'
import HamburgerMenu from './components/layout/HamburgerMenu.vue'
import GoogleMapComponent from './components/map/GoogleMap.vue'
import FAB from './components/shared/FAB.vue'
import LoadingSpinner from './components/shared/LoadingSpinner.vue'
import { useBooksStore } from './stores/books'
import { useUIStore } from './stores/ui'
import { useFirebase } from './composables/useFirebase'
import { useMap } from './composables/useMap'
import { initFirebase } from './utils/firebase'

const showComponentShowcase = ref(false)
const booksStore = useBooksStore()
const uiStore = useUIStore()
const { loadBooks } = useFirebase()
const { goToRandomLocation } = useMap()

onMounted(async () => {
  // Initialize Firebase and app
  console.log('LitMap Vue app mounted')

  try {
    // Initialize Firebase
    initFirebase()

    // Load initial book collection (default: 'books')
    await loadBooks('books')

    console.log(`Loaded ${booksStore.booksCount} books`)
  } catch (error) {
    console.error('Error initializing app:', error)
  }
})

function handleRandomLocation() {
  const location = goToRandomLocation()
  console.log('Random location:', location.name)
}
</script>

<style scoped>
/* Component-specific styles if needed */
</style>
