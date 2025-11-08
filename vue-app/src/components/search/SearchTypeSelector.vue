<template>
  <div class="mb-4">
    <p class="text-sm font-medium text-gray-700 mb-2">Search in:</p>
    <div class="flex flex-wrap gap-2">
      <label
        v-for="option in searchOptions"
        :key="option.value"
        class="flex items-center"
      >
        <input
          type="radio"
          :value="option.value"
          :checked="modelValue === option.value"
          @change="$emit('update:modelValue', option.value)"
          class="sr-only peer"
        />
        <span
          class="px-4 py-2 rounded-full text-sm font-medium border-2 cursor-pointer transition-all touch-target
                 peer-checked:bg-primary-600 peer-checked:text-white peer-checked:border-primary-600
                 border-gray-300 text-gray-700 hover:border-primary-400"
        >
          {{ option.label }}
        </span>
      </label>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: String,
    default: 'any'
  }
})

defineEmits(['update:modelValue'])

const searchOptions = [
  { value: 'any', label: 'Any' },
  { value: 'title', label: 'Title' },
  { value: 'author', label: 'Author' },
  { value: 'location', label: 'Location' },
  { value: 'keyword', label: 'Keyword' },
]
</script>
