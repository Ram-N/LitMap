<template>
  <div class="pb-24 min-h-screen">
    <!-- Header -->
    <div class="px-6 pt-8 pb-2">
      <h1 class="font-serif text-3xl font-bold text-text-primary mb-1">Find Your Next Book</h1>
      <p class="text-text-secondary text-sm">Filter by type, region and genre</p>
    </div>

    <!-- Type filter -->
    <section class="px-6 pt-3 pb-1">
      <h2 class="text-xs font-medium text-text-tertiary uppercase tracking-wide mb-2">Type</h2>
      <div class="flex flex-wrap gap-2">
        <FilterChip
          v-for="type in availableTypes"
          :key="type.label"
          :label="`${type.label} (${type.count})`"
          :selected="selectedTypes.includes(type.label)"
          @click="toggleType(type.label)"
        />
      </div>
    </section>

    <!-- Region filter -->
    <section class="px-6 pt-3 pb-1">
      <h2 class="text-xs font-medium text-text-tertiary uppercase tracking-wide mb-2">Region</h2>
      <div class="flex flex-wrap gap-2">
        <FilterChip
          v-for="region in availableRegions"
          :key="region"
          :label="region"
          :selected="selectedRegion === region"
          @click="setRegion(region)"
        />
      </div>
    </section>

    <!-- Genre filter -->
    <section class="px-6 pt-3 pb-1">
      <h2 class="text-xs font-medium text-text-tertiary uppercase tracking-wide mb-2">Genre</h2>
      <div class="flex flex-wrap gap-2">
        <FilterChip
          v-for="genre in availableGenres"
          :key="genre.label"
          :label="genre.label"
          :selected="selectedGenres.includes(genre.label)"
          @click="toggleGenre(genre.label)"
        />
      </div>
    </section>

    <!-- Results header -->
    <div class="px-6 pt-4 pb-2 flex items-center justify-between border-b-2 border-parchment-300">
      <p class="text-sm font-medium text-text-primary">
        {{ filteredBooks.length }} {{ filteredBooks.length === 1 ? 'book' : 'books' }}
      </p>
      <button
        v-if="hasActiveFilters"
        @click="clearAll"
        class="text-sm text-teal-deep font-medium"
      >
        Clear filters
      </button>
    </div>

    <!-- Results -->
    <div class="px-4 py-3 space-y-3">
      <BookCard
        v-for="book in displayedBooks"
        :key="book.id"
        :book="book"
        @click="$router.push(`/book/${book.id}`)"
      />
    </div>

    <!-- Show more -->
    <div v-if="filteredBooks.length > displayLimit" class="px-6 pb-4 text-center">
      <button
        @click="displayLimit += 20"
        class="px-6 py-2.5 rounded-xl border-2 border-parchment-200 text-sm text-text-secondary font-medium hover:border-teal-deep hover:text-teal-deep transition-colors"
      >
        Show more ({{ filteredBooks.length - displayLimit }} remaining)
      </button>
    </div>

    <!-- Empty state -->
    <div v-if="hasActiveFilters && filteredBooks.length === 0" class="px-6 py-8 text-center">
      <Search class="w-10 h-10 text-text-tertiary mx-auto mb-2" :stroke-width="1.5" />
      <p class="text-text-secondary">No books match these filters</p>
      <button
        @click="clearAll"
        class="mt-2 text-sm text-teal-deep font-medium"
      >
        Clear all filters
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search } from 'lucide-vue-next'
import { useFilters } from '@/composables/useFilters'
import FilterChip from '@/components/shared/FilterChip.vue'
import BookCard from '@/components/search/BookCard.vue'

const {
  selectedTypes,
  selectedRegion,
  selectedGenres,
  availableTypes,
  availableRegions,
  availableGenres,
  filteredBooks,
  hasActiveFilters,
  toggleType,
  setRegion,
  toggleGenre,
  clearAll,
} = useFilters()

const displayLimit = ref(20)

const displayedBooks = computed(() => filteredBooks.value.slice(0, displayLimit.value))
</script>
