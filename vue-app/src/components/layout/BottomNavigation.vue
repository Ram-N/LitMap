<template>
  <nav class="fixed bottom-0 left-0 right-0 bg-white border-t border-parchment-200 z-30 pb-safe">
    <div class="flex justify-around items-center h-20">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="tabClasses(tab)"
        @click="handleNavigate(tab.id)"
        class="flex flex-col items-center justify-center gap-1 px-4 py-2 transition-colors min-h-touch"
      >
        <component :is="tab.icon" :class="iconClasses(tab)" :stroke-width="2" />
        <span :class="labelClasses(tab)">{{ tab.label }}</span>
      </button>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue';
import { Map, List, BookmarkCheck, Plus } from 'lucide-vue-next';

const props = defineProps({
  activeTab: {
    type: String,
    default: 'map'
  }
});

const emit = defineEmits(['navigate']);

const tabs = [
  { id: 'map', label: 'Map', icon: Map },
  { id: 'list', label: 'List', icon: List },
  { id: 'library', label: 'Library', icon: BookmarkCheck },
  { id: 'contribute', label: 'Contribute', icon: Plus }
];

function handleNavigate(tabId) {
  emit('navigate', tabId);
}

function tabClasses(tab) {
  return {
    'text-teal-deep': props.activeTab === tab.id,
    'text-text-tertiary hover:text-text-secondary': props.activeTab !== tab.id
  };
}

function iconClasses(tab) {
  return props.activeTab === tab.id ? 'w-6 h-6' : 'w-6 h-6';
}

function labelClasses(tab) {
  return {
    'text-xs font-medium': props.activeTab === tab.id,
    'text-xs': props.activeTab !== tab.id
  };
}
</script>

<style scoped>
/* Safe area support for iOS notch/home indicator */
@supports (padding-bottom: env(safe-area-inset-bottom)) {
  .pb-safe {
    padding-bottom: env(safe-area-inset-bottom);
  }
}
</style>
