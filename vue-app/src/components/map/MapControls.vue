<template>
  <div class="flex flex-col md:flex-row gap-2">
    <!-- Location Selector Dropdown -->
    <select
      v-model="selectedLocation"
      @change="handleLocationChange"
      class="px-3 py-2 bg-white rounded-lg shadow-md border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 touch-target"
    >
      <option
        v-for="option in locationOptions"
        :key="option.value"
        :value="option.value"
      >
        {{ option.label }}
      </option>
    </select>

    <!-- Manual Location Input -->
    <div class="relative flex-1 md:max-w-xs">
      <input
        v-model="manualLocation"
        type="text"
        placeholder="Enter location..."
        class="w-full px-3 py-2 pr-10 bg-white rounded-lg shadow-md border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
        @keyup.enter="handleManualLocation"
      />
      <button
        v-if="manualLocation"
        @click="clearManualLocation"
        class="absolute right-2 top-1/2 -translate-y-1/2 p-1 hover:bg-gray-100 rounded"
      >
        <X :size="16" class="text-gray-400" />
      </button>
    </div>

    <!-- Zoom Controls -->
    <div class="flex items-center gap-1 bg-white rounded-lg shadow-md px-2 py-1">
      <button
        @click="zoomOut"
        class="touch-target p-1.5 hover:bg-gray-100 rounded transition-colors"
        aria-label="Zoom out"
      >
        <Minus :size="20" class="text-gray-700" />
      </button>

      <span class="min-w-[2rem] text-center text-sm font-medium text-gray-700">
        {{ currentZoom }}
      </span>

      <button
        @click="zoomIn"
        class="touch-target p-1.5 hover:bg-gray-100 rounded transition-colors"
        aria-label="Zoom in"
      >
        <Plus :size="20" class="text-gray-700" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { X, Plus, Minus } from 'lucide-vue-next'
import { useUIStore } from '@/stores/ui'
import { useMap } from '@/composables/useMap'
import { locationOptions } from '@/utils/mapLocations'

const uiStore = useUIStore()
const { goToLocation, geocodeAddress } = useMap()

const selectedLocation = ref('')
const manualLocation = ref('')

const currentZoom = computed(() => uiStore.mapZoom)

const minZoom = 2
const maxZoom = 17

function handleLocationChange() {
  if (selectedLocation.value) {
    goToLocation(selectedLocation.value)
  }
}

async function handleManualLocation() {
  if (!manualLocation.value.trim()) return

  try {
    await geocodeAddress(manualLocation.value)
    // Clear input after successful geocoding
    // manualLocation.value = ''
  } catch (error) {
    alert(`Could not find location: ${manualLocation.value}`)
  }
}

function clearManualLocation() {
  manualLocation.value = ''
  selectedLocation.value = ''
}

function zoomIn() {
  const newZoom = Math.min(currentZoom.value + 1, maxZoom)
  uiStore.setMapZoom(newZoom)
}

function zoomOut() {
  const newZoom = Math.max(currentZoom.value - 1, minZoom)
  uiStore.setMapZoom(newZoom)
}
</script>
