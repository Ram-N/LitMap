<template>
  <div
    class="flex gap-3 overflow-x-auto px-6 pb-2 snap-x snap-mandatory scrollbar-hide"
  >
    <slot />
  </div>
</template>

<style scoped>
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
</style>
