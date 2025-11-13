<template>
  <!-- Toggle between showcase and main app -->
  <div v-if="showShowcase">
    <ComponentShowcase />
    <button
      @click="showShowcase = false"
      class="fixed top-4 right-4 z-50 bg-teal-deep text-white px-4 py-2 rounded-lg shadow-elevated"
    >
      Back to App
    </button>
  </div>
  <div v-else>
    <MainApp />
    <button
      @click="showShowcase = true"
      class="fixed top-20 right-4 z-50 bg-copper-warm text-white px-4 py-2 rounded-lg shadow-elevated"
    >
      View Components
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import ComponentShowcase from './components/ComponentShowcase.vue';
import MainApp from './AppOriginal.vue';

const showShowcase = ref(true); // Start with showcase visible
</script>
