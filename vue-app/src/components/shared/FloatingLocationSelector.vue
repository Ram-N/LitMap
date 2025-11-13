<template>
  <div class="fixed top-20 left-4 z-20">
    <!-- Compact Location Selector -->
    <select
      v-model="selectedLocation"
      @change="handleLocationChange"
      class="px-3 py-2 bg-white rounded-lg shadow-elevated text-sm font-medium text-text-primary focus:outline-none focus:ring-2 focus:ring-teal-deep border-0 touch-target cursor-pointer transition-shadow hover:shadow-fab"
    >
      <option value="">Jump to...</option>
      <optgroup label="Cities">
        <option value="new_york">New York</option>
        <option value="london">London</option>
        <option value="tokyo">Tokyo</option>
        <option value="sydney">Sydney</option>
        <option value="paris">Paris</option>
        <option value="dubai">Dubai</option>
        <option value="toronto">Toronto</option>
        <option value="mexico_city">Mexico City</option>
        <option value="beijing">Beijing</option>
        <option value="mumbai">Mumbai</option>
      </optgroup>
      <optgroup label="Countries">
        <option value="india">India</option>
        <option value="uk">United Kingdom</option>
        <option value="usa">United States</option>
      </optgroup>
      <optgroup label="Regions">
        <option value="africa">Africa</option>
        <option value="south_america">South America</option>
        <option value="sub_saharan_africa">Sub-Saharan Africa</option>
        <option value="middle_east">Middle East</option>
        <option value="eastern_europe">Eastern Europe</option>
      </optgroup>
    </select>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useMap } from '@/composables/useMap'

const { goToLocation } = useMap()

const selectedLocation = ref('')

function handleLocationChange() {
  if (selectedLocation.value) {
    goToLocation(selectedLocation.value)
    // Reset after selection so user can select the same location again
    setTimeout(() => {
      selectedLocation.value = ''
    }, 300)
  }
}
</script>
