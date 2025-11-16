<template>
  <div class="flex flex-col items-center justify-center py-16 px-6 text-center">
    <div class="w-24 h-24 bg-parchment-100 rounded-full flex items-center justify-center mb-6">
      <i class="fa-solid fa-book-open text-4xl text-text-tertiary"></i>
    </div>
    <h3 class="font-serif text-xl font-semibold text-text-primary mb-2">
      {{ title }}
    </h3>
    <p class="text-text-secondary max-w-sm">
      {{ description }}
    </p>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  }
})
</script>
