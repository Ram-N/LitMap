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

    <!-- Router view for main content -->
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>

    <!-- Bottom Navigation (always visible) -->
    <BottomNavigation
      :active-tab="currentTab"
      @navigate="handleNavigate"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import ComponentShowcase from './components/ComponentShowcase.vue'
import BottomNavigation from './components/layout/BottomNavigation.vue'
import { useBooksStore } from './stores/books'
import { useFirebase } from './composables/useFirebase'
import { initFirebase } from './utils/firebase'

const router = useRouter()
const route = useRoute()
const showComponentShowcase = ref(false)
const booksStore = useBooksStore()
const { loadBooks } = useFirebase()

// Paper grain texture as data URL
const textureDataUrl = "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E\")"

// Compute current tab from route meta
const currentTab = computed(() => route.meta.tab || '')

onMounted(async () => {
  // Initialize Firebase and app
  console.log('LitMap Vue app mounted')

  try {
    // Initialize Firebase
    initFirebase()

    // Load initial book collection (default: 'books')
    await loadBooks()

    console.log(`Loaded ${booksStore.booksCount} books`)
  } catch (error) {
    console.error('Error initializing app:', error)
  }
})

function handleNavigate(tab) {
  router.push({ name: tab })
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
