<template>
  <div class="flex items-center justify-center" :class="containerClass">
    <div class="loading-spinner" :style="{ width: size, height: size }">
      <div class="spinner-ring" :style="spinnerStyle"></div>
    </div>
    <p v-if="message" class="mt-4 text-gray-600 text-sm">{{ message }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  size: {
    type: String,
    default: '40px'
  },
  color: {
    type: String,
    default: '#0ea5e9' // primary-600
  },
  message: {
    type: String,
    default: ''
  },
  containerClass: {
    type: String,
    default: 'p-8'
  }
})

const spinnerStyle = computed(() => ({
  borderColor: `${props.color}33`, // 20% opacity
  borderTopColor: props.color,
  width: props.size,
  height: props.size,
}))
</script>

<style scoped>
.spinner-ring {
  border: 3px solid;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
