<template>
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

      <!-- Floating Controls (hidden when loading, search modal, or bottom sheet is open) -->
      <FloatingLocationSelector
        v-if="!booksStore.isLoading && !uiStore.isSearchModalOpen && !uiStore.isBottomSheetVisible"
      />
      <FloatingZoomControls
        v-if="!booksStore.isLoading && !uiStore.isSearchModalOpen && !uiStore.isBottomSheetVisible"
      />
      <ClusterToggle
        v-if="!booksStore.isLoading && !uiStore.isSearchModalOpen && !uiStore.isBottomSheetVisible"
      />

      <!-- FAB Buttons -->
      <FAB
        v-if="!booksStore.isLoading"
        @random-location="handleRandomLocation"
      />
    </main>

    <!-- Bottom Sheet -->
    <BottomSheet />
  </div>
</template>

<script setup>
import TopBar from '@/components/layout/TopBar.vue'
import BottomSheet from '@/components/layout/BottomSheet.vue'
import GoogleMapComponent from '@/components/map/GoogleMap.vue'
import ClusterToggle from '@/components/map/ClusterToggle.vue'
import FAB from '@/components/shared/FAB.vue'
import FloatingLocationSelector from '@/components/shared/FloatingLocationSelector.vue'
import FloatingZoomControls from '@/components/shared/FloatingZoomControls.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import { useBooksStore } from '@/stores/books'
import { useUIStore } from '@/stores/ui'
import { useMap } from '@/composables/useMap'

const booksStore = useBooksStore()
const uiStore = useUIStore()
const { goToRandomLocation } = useMap()

function handleRandomLocation() {
  const location = goToRandomLocation()
  console.log('Random location:', location.name)
}
</script>
