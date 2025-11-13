<template>
  <button
    class="absolute top-20 right-4 z-10 bg-white rounded-full p-3 shadow-card hover:shadow-elevated transition-shadow touch-target"
    @click="toggleClustering"
    :title="clusteringEnabled ? 'Disable clustering' : 'Enable clustering'"
  >
    <component
      :is="clusteringEnabled ? Grid3x3 : MapIcon"
      class="w-5 h-5 text-teal-deep"
      :stroke-width="2"
    />
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { Grid3x3, Map as MapIcon } from 'lucide-vue-next'
import { useUIStore } from '@/stores/ui'

const uiStore = useUIStore()
const clusteringEnabled = computed(() => uiStore.clusteringEnabled)

function toggleClustering() {
  uiStore.toggleClustering()
}
</script>
