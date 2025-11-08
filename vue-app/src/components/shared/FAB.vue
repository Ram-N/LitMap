<template>
  <button
    class="w-14 h-14 bg-primary-600 text-white rounded-full shadow-lg hover:bg-primary-700 active:bg-primary-800 hover:shadow-xl transition-all duration-200 flex items-center justify-center touch-target"
    :aria-label="ariaLabel"
    @click="$emit('click')"
  >
    <component :is="iconComponent" :size="24" />
  </button>
</template>

<script setup>
import { computed } from 'vue'
import * as LucideIcons from 'lucide-vue-next'

const props = defineProps({
  icon: {
    type: String,
    required: true
  },
  ariaLabel: {
    type: String,
    default: 'Action button'
  }
})

defineEmits(['click'])

const iconComponent = computed(() => {
  return LucideIcons[props.icon] || LucideIcons.Circle
})
</script>
