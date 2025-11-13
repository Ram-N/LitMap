<template>
  <!-- Component Showcase Mode (temporary for testing) -->
  <ComponentShowcase v-if="showComponentShowcase" />

  <!-- Main App -->
  <div v-else class="min-h-screen bg-gradient-to-br from-parchment-100 via-parchment-50 to-parchment-200 relative">
    <!-- Paper grain texture overlay -->
    <div
      class="fixed inset-0 opacity-[0.03] pointer-events-none mix-blend-multiply z-0"
      :style="{ backgroundImage: textureDataUrl }"
    ></div>

    <!-- Toggle Button for Showcase (temporary) -->
    <button
      @click="showComponentShowcase = true"
      class="fixed top-20 right-4 z-50 bg-copper-warm text-white px-3 py-2 rounded-lg shadow-elevated text-sm"
      title="View new design system components"
    >
      🎨 Design System
    </button>

    <!-- Main content wrapper with padding for bottom nav -->
    <div class="min-h-screen pb-20">
      <!-- Top Bar -->
      <TopBar />

      <!-- Main Content: Map View -->
      <main class="relative h-[calc(100vh-4rem-5rem)]">
        <!-- Google Map (always rendered) -->
        <GoogleMapComponent />

        <!-- Loading State Overlay -->
        <div v-if="booksStore.isLoading" class="absolute inset-0 z-50 bg-white/95 flex items-center justify-center pointer-events-none">
          <LoadingSpinner message="Loading books..." />
        </div>

        <!-- Error State Overlay -->
        <div v-else-if="booksStore.error" class="absolute inset-0 z-50 bg-white/95 flex items-center justify-center">
          <div class="text-center p-8">
            <p class="text-red-600 mb-4 font-medium">Error loading books</p>
            <p class="text-text-secondary text-sm">{{ booksStore.error }}</p>
          </div>
        </div>

        <!-- FAB Buttons -->
        <FAB
          v-if="!booksStore.isLoading"
          @random-location="handleRandomLocation"
        />
      </main>

      <!-- Bottom Sheet -->
      <BottomSheet />
    </div>

    <!-- Bottom Navigation (always visible) -->
    <BottomNavigation
      :active-tab="currentTab"
      @navigate="handleNavigate"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ComponentShowcase from './components/ComponentShowcase.vue'
import TopBar from './components/layout/TopBar.vue'
import BottomSheet from './components/layout/BottomSheet.vue'
import BottomNavigation from './components/layout/BottomNavigation.vue'
import GoogleMapComponent from './components/map/GoogleMap.vue'
import FAB from './components/shared/FAB.vue'
import LoadingSpinner from './components/shared/LoadingSpinner.vue'
import { useBooksStore } from './stores/books'
import { useUIStore } from './stores/ui'
import { useFirebase } from './composables/useFirebase'
import { useMap } from './composables/useMap'
import { initFirebase } from './utils/firebase'

const showComponentShowcase = ref(false)
const currentTab = ref('map')
const booksStore = useBooksStore()
const uiStore = useUIStore()
const { loadBooks } = useFirebase()
const { goToRandomLocation } = useMap()

// Paper grain texture as data URL
const textureDataUrl = "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E\")"

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

function handleNavigate(tab) {
  currentTab.value = tab
  console.log('Navigate to:', tab)
  // TODO: Implement navigation in Phase 3
}
</script>

<style scoped>
/* Component-specific styles if needed */
</style>
