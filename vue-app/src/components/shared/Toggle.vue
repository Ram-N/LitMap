<template>
  <label class="flex items-start cursor-pointer group">
    <div class="relative flex-shrink-0">
      <input
        type="checkbox"
        :checked="modelValue"
        @change="$emit('update:modelValue', $event.target.checked)"
        class="sr-only peer"
      />
      <div
        class="w-11 h-6 bg-gray-300 rounded-full peer-checked:bg-primary-600 transition-colors duration-200 ease-in-out"
      />
      <div
        class="absolute left-0.5 top-0.5 w-5 h-5 bg-white rounded-full shadow-md transition-transform duration-200 ease-in-out peer-checked:translate-x-5"
      />
    </div>
    <div v-if="label" class="ml-3 flex-1">
      <p class="font-medium text-gray-700">{{ label }}</p>
      <p v-if="description" class="text-sm text-gray-500 mt-0.5">{{ description }}</p>
    </div>
  </label>
</template>

<script setup>
defineProps({
  modelValue: {
    type: Boolean,
    required: true
  },
  label: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  }
})

defineEmits(['update:modelValue'])
</script>
