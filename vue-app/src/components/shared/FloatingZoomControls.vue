<template>
  <div class="fixed left-6 bottom-28 flex flex-col gap-2 z-20">
    <!-- Zoom In -->
    <button
      @click="zoomIn"
      class="w-10 h-10 rounded-full bg-white shadow-elevated hover:shadow-fab transition-all flex items-center justify-center touch-target"
      aria-label="Zoom in"
      title="Zoom in"
    >
      <Plus :size="20" class="text-text-primary" :stroke-width="2.5" />
    </button>

    <!-- Zoom Level Display -->
    <div class="w-10 h-8 rounded-full bg-white shadow-card flex items-center justify-center">
      <span class="text-xs font-medium text-text-secondary">{{ currentZoom }}</span>
    </div>

    <!-- Zoom Out -->
    <button
      @click="zoomOut"
      class="w-10 h-10 rounded-full bg-white shadow-elevated hover:shadow-fab transition-all flex items-center justify-center touch-target"
      aria-label="Zoom out"
      title="Zoom out"
    >
      <Minus :size="20" class="text-text-primary" :stroke-width="2.5" />
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Plus, Minus } from 'lucide-vue-next'
import { useUIStore } from '@/stores/ui'

const uiStore = useUIStore()

const currentZoom = computed(() => uiStore.mapZoom)

const minZoom = 2
const maxZoom = 17

function zoomIn() {
  const newZoom = Math.min(currentZoom.value + 1, maxZoom)
  uiStore.setMapZoom(newZoom)
}

function zoomOut() {
  const newZoom = Math.max(currentZoom.value - 1, minZoom)
  uiStore.setMapZoom(newZoom)
}
</script>
