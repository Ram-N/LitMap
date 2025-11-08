<template>
  <!-- Overlay for full state -->
  <Transition name="fade">
    <div
      v-if="uiStore.bottomSheetState === 'full'"
      class="fixed inset-0 bg-black bg-opacity-30 z-30"
      @click="handleCollapse"
    />
  </Transition>

  <!-- Bottom Sheet -->
  <Transition name="sheet">
    <div
      v-if="uiStore.isBottomSheetVisible"
      ref="sheetRef"
      class="fixed bottom-0 left-0 right-0 bg-white rounded-t-3xl shadow-2xl z-40 safe-bottom"
      :class="sheetClasses"
      @touchstart="handleTouchStart"
      @touchmove="handleTouchMove"
      @touchend="handleTouchEnd"
    >
      <!-- Drag Handle -->
      <div class="flex justify-center pt-3 pb-2">
        <div class="w-12 h-1.5 bg-gray-300 rounded-full" />
      </div>

      <!-- Content -->
      <div class="overflow-y-auto" :style="{ maxHeight: contentMaxHeight }">
        <!-- Search Results -->
        <div v-if="uiStore.bottomSheetContent === 'search-results'" class="p-4">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold">
              {{ uiStore.searchResultsCount }} {{ uiStore.searchResultsCount === 1 ? 'book' : 'books' }} found
            </h2>
            <button
              @click="uiStore.clearSearch"
              class="text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              Clear
            </button>
          </div>

          <!-- Book Cards -->
          <div class="space-y-3">
            <BookCard
              v-for="book in uiStore.searchResults"
              :key="book.id"
              :book="book"
              @click="handleBookClick(book)"
            />
          </div>
        </div>

        <!-- Book Details -->
        <div v-else-if="uiStore.bottomSheetContent === 'book-details' && uiStore.selectedBook" class="p-4">
          <BookDetails :book="uiStore.selectedBook" />
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUIStore } from '@/stores/ui'
import BookCard from '../search/BookCard.vue'
import BookDetails from '../search/BookDetails.vue'

const uiStore = useUIStore()

const sheetRef = ref(null)
const touchStartY = ref(0)
const touchCurrentY = ref(0)
const isDragging = ref(false)

const sheetClasses = computed(() => {
  switch (uiStore.bottomSheetState) {
    case 'half':
      return 'h-[50vh]'
    case 'full':
      return 'h-[85vh]'
    default:
      return 'h-0'
  }
})

const contentMaxHeight = computed(() => {
  switch (uiStore.bottomSheetState) {
    case 'half':
      return 'calc(50vh - 60px)'
    case 'full':
      return 'calc(85vh - 60px)'
    default:
      return '0'
  }
})

function handleTouchStart(e) {
  touchStartY.value = e.touches[0].clientY
  isDragging.value = true
}

function handleTouchMove(e) {
  if (!isDragging.value) return
  touchCurrentY.value = e.touches[0].clientY
}

function handleTouchEnd() {
  if (!isDragging.value) return

  const deltaY = touchCurrentY.value - touchStartY.value

  // Swipe down threshold: 50px
  if (deltaY > 50) {
    if (uiStore.bottomSheetState === 'full') {
      uiStore.setBottomSheet('half')
    } else if (uiStore.bottomSheetState === 'half') {
      handleCollapse()
    }
  }
  // Swipe up threshold: -50px
  else if (deltaY < -50 && uiStore.bottomSheetState === 'half') {
    uiStore.setBottomSheet('full')
  }

  isDragging.value = false
  touchStartY.value = 0
  touchCurrentY.value = 0
}

function handleCollapse() {
  uiStore.hideBottomSheet()
}

function handleBookClick(book) {
  uiStore.showBookDetails(book)
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.sheet-enter-active, .sheet-leave-active {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.sheet-enter-from, .sheet-leave-to {
  transform: translateY(100%);
}
</style>
