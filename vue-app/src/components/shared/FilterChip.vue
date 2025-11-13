<template>
  <button
    :class="chipClasses"
    @click="handleClick"
    class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all border-2 min-h-touch"
  >
    <span>{{ label }}</span>
    <X
      v-if="removable && selected"
      class="w-4 h-4"
      :stroke-width="2"
    />
  </button>
</template>

<script setup>
import { computed } from 'vue';
import { X } from 'lucide-vue-next';

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  selected: {
    type: Boolean,
    default: false
  },
  removable: {
    type: Boolean,
    default: false
  },
  color: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'memoir', 'adventure', 'historical', 'travel'].includes(value)
  }
});

const emit = defineEmits(['click']);

const chipClasses = computed(() => {
  const baseClasses = 'cursor-pointer';

  if (props.selected) {
    // Selected state colors based on color prop
    const colorMap = {
      default: 'bg-teal-deep border-teal-deep text-white',
      memoir: 'bg-genre-memoir border-genre-memoir text-white',
      adventure: 'bg-genre-adventure border-genre-adventure text-white',
      historical: 'bg-genre-historical border-genre-historical text-white',
      travel: 'bg-genre-travel border-genre-travel text-white'
    };
    return `${baseClasses} ${colorMap[props.color]}`;
  } else {
    // Unselected state - neutral
    return `${baseClasses} bg-parchment-50 border-parchment-200 text-text-secondary hover:border-teal-deep hover:text-teal-deep`;
  }
});

function handleClick() {
  emit('click');
}
</script>
