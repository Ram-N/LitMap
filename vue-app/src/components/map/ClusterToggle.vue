<template>
  <button
    class="absolute top-20 right-4 z-10 bg-white rounded-full p-3 shadow-card hover:shadow-elevated transition-shadow touch-target"
    @click="toggleClustering"
    :title="clusteringEnabled ? 'Show individual markers' : 'Show clustered markers'"
  >
    <!-- Show layer-group icon when clustering is OFF (click to enable clustering) -->
    <!-- Show location-dot icon when clustering is ON (click to show individual markers) -->
    <i
      :class="clusteringEnabled ? 'fa-solid fa-location-dot' : 'fa-solid fa-layer-group'"
      class="text-lg text-teal-deep"
    ></i>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useUIStore } from '@/stores/ui'

const uiStore = useUIStore()
const clusteringEnabled = computed(() => uiStore.isClusteringEnabled)

function toggleClustering() {
  uiStore.toggleClustering()
}
</script>
