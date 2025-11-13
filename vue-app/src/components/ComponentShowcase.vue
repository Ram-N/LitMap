<template>
  <div class="min-h-screen bg-gradient-to-br from-parchment-100 via-parchment-50 to-parchment-200 p-8">
    <!-- Paper grain texture overlay -->
    <div
      class="fixed inset-0 opacity-[0.03] pointer-events-none mix-blend-multiply"
      style="background-image: url(&quot;data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E&quot;)"
    ></div>

    <div class="max-w-4xl mx-auto relative z-10">
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="font-serif text-4xl font-semibold text-text-primary mb-3 tracking-tight">
          LitMap Design System
        </h1>
        <p class="text-text-secondary text-lg">
          Phase 1: Component Showcase
        </p>
      </div>

      <!-- Color Palette Section -->
      <section class="bg-white rounded-2xl shadow-card p-6 mb-8">
        <h2 class="font-serif text-2xl font-semibold text-text-primary mb-4">Color Palette</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div class="w-full h-20 rounded-xl bg-teal-deep mb-2"></div>
            <p class="text-sm text-text-secondary">Teal Deep</p>
            <p class="text-xs text-text-tertiary">#3D6960</p>
          </div>
          <div>
            <div class="w-full h-20 rounded-xl bg-copper-warm mb-2"></div>
            <p class="text-sm text-text-secondary">Copper Warm</p>
            <p class="text-xs text-text-tertiary">#C17A3A</p>
          </div>
          <div>
            <div class="w-full h-20 rounded-xl bg-parchment-50 border-2 border-parchment-200 mb-2"></div>
            <p class="text-sm text-text-secondary">Parchment 50</p>
            <p class="text-xs text-text-tertiary">#F5F1E8</p>
          </div>
          <div>
            <div class="w-full h-20 rounded-xl bg-parchment-200 mb-2"></div>
            <p class="text-sm text-text-secondary">Parchment 200</p>
            <p class="text-xs text-text-tertiary">#E0D9C8</p>
          </div>
        </div>

        <h3 class="font-serif text-xl font-semibold text-text-primary mt-6 mb-4">Genre Colors</h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div class="w-full h-20 rounded-xl bg-genre-memoir mb-2"></div>
            <p class="text-sm text-text-secondary">Memoir</p>
          </div>
          <div>
            <div class="w-full h-20 rounded-xl bg-genre-adventure mb-2"></div>
            <p class="text-sm text-text-secondary">Adventure</p>
          </div>
          <div>
            <div class="w-full h-20 rounded-xl bg-genre-historical mb-2"></div>
            <p class="text-sm text-text-secondary">Historical</p>
          </div>
          <div>
            <div class="w-full h-20 rounded-xl bg-genre-travel mb-2"></div>
            <p class="text-sm text-text-secondary">Travel</p>
          </div>
        </div>
      </section>

      <!-- Typography Section -->
      <section class="bg-white rounded-2xl shadow-card p-6 mb-8">
        <h2 class="font-serif text-2xl font-semibold text-text-primary mb-4">Typography</h2>
        <div class="space-y-4">
          <div>
            <p class="font-serif text-4xl font-semibold text-text-primary">Georgia Serif</p>
            <p class="text-sm text-text-tertiary mt-1">Used for headings and book titles</p>
          </div>
          <div>
            <p class="font-sans text-2xl text-text-secondary">System Sans-Serif</p>
            <p class="text-sm text-text-tertiary mt-1">Used for body text and UI elements</p>
          </div>
        </div>
      </section>

      <!-- GenreBadge Component -->
      <section class="bg-white rounded-2xl shadow-card p-6 mb-8">
        <h2 class="font-serif text-2xl font-semibold text-text-primary mb-4">Genre Badges</h2>
        <div class="flex flex-wrap gap-3">
          <GenreBadge genre="Memoir" />
          <GenreBadge genre="Adventure" />
          <GenreBadge genre="Historical" />
          <GenreBadge genre="Travel" />
          <GenreBadge genre="Fiction" />
          <GenreBadge genre="Poetry" />
          <GenreBadge genre="Photography" />
          <GenreBadge genre="Biography" />
        </div>
      </section>

      <!-- FilterChip Component -->
      <section class="bg-white rounded-2xl shadow-card p-6 mb-8">
        <h2 class="font-serif text-2xl font-semibold text-text-primary mb-4">Filter Chips</h2>

        <h3 class="text-lg font-medium text-text-secondary mb-3">Default Style</h3>
        <div class="flex flex-wrap gap-3 mb-6">
          <FilterChip label="All" :selected="selectedFilter === 'all'" @click="selectedFilter = 'all'" />
          <FilterChip label="Author" :selected="selectedFilter === 'author'" @click="selectedFilter = 'author'" />
          <FilterChip label="Location" :selected="selectedFilter === 'location'" @click="selectedFilter = 'location'" />
          <FilterChip label="Theme" :selected="selectedFilter === 'theme'" @click="selectedFilter = 'theme'" />
        </div>

        <h3 class="text-lg font-medium text-text-secondary mb-3">Genre Colors</h3>
        <div class="flex flex-wrap gap-3">
          <FilterChip
            label="Memoir"
            color="memoir"
            :selected="selectedGenres.includes('memoir')"
            @click="toggleGenre('memoir')"
          />
          <FilterChip
            label="Adventure"
            color="adventure"
            :selected="selectedGenres.includes('adventure')"
            @click="toggleGenre('adventure')"
          />
          <FilterChip
            label="Historical"
            color="historical"
            :selected="selectedGenres.includes('historical')"
            @click="toggleGenre('historical')"
          />
          <FilterChip
            label="Travel"
            color="travel"
            :selected="selectedGenres.includes('travel')"
            @click="toggleGenre('travel')"
          />
        </div>
      </section>

      <!-- Bottom Navigation Component -->
      <section class="bg-white rounded-2xl shadow-card p-6 mb-24">
        <h2 class="font-serif text-2xl font-semibold text-text-primary mb-4">Bottom Navigation</h2>
        <p class="text-text-secondary mb-4">Click the tabs below to see the active state:</p>
        <div class="relative border-2 border-parchment-200 rounded-xl overflow-hidden" style="height: 100px;">
          <BottomNavigation :active-tab="activeTab" @navigate="handleNavigate" />
        </div>
        <p class="text-sm text-text-tertiary mt-3">
          Active tab: <span class="font-medium text-teal-deep">{{ activeTab }}</span>
        </p>
      </section>
    </div>

    <!-- Actual Bottom Navigation (sticky) -->
    <BottomNavigation :active-tab="activeTab" @navigate="handleNavigate" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import GenreBadge from './shared/GenreBadge.vue';
import FilterChip from './shared/FilterChip.vue';
import BottomNavigation from './layout/BottomNavigation.vue';

const selectedFilter = ref('all');
const selectedGenres = ref([]);
const activeTab = ref('map');

function toggleGenre(genre) {
  const index = selectedGenres.value.indexOf(genre);
  if (index > -1) {
    selectedGenres.value.splice(index, 1);
  } else {
    selectedGenres.value.push(genre);
  }
}

function handleNavigate(tab) {
  activeTab.value = tab;
  console.log('Navigated to:', tab);
}
</script>
