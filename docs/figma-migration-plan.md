# LitMap Figma Design Migration Plan

**Version**: 1.0
**Date**: November 2025
**Estimated Timeline**: 8-10 weeks
**Complexity**: Medium-High

---

## Executive Summary

This document outlines the comprehensive migration of the LitMap Vue.js application to match the Figma-generated design system and components found in `/design/mockups/`. The migration includes a complete visual redesign with a vintage literary aesthetic and two major new features: Author Profile pages and Personal Library functionality.

### Scope Decisions

**Migration Approach**: Full feature implementation (8-10 weeks)

**Key Decisions**:
- ✅ **Settings**: Remove collection switcher and map type selector; keep only essential clustering toggle
- ✅ **Authentication**: Skip for initial release (implement later)
- ✅ **Library Storage**: Use localStorage (device-specific, no sync)
- ✅ **Author Data**: Compute dynamically from existing books in Firestore
- ✅ **Must-Have Features**: Personal Library + Author Profile pages
- ⏸️ **Deferred Features**: User contributions, advanced filtering with timeline slider

### Current State

**Vue App**: Mobile-first Google Maps application with:
- Fullscreen map with marker clustering
- Search with expandable overlay
- Bottom sheet for book details
- Hamburger menu for settings
- Blue/cyan color scheme
- System sans-serif typography

**Figma Mockups**: Complete redesign with:
- 7 high-fidelity mobile screens
- Vintage literary aesthetic (parchment colors, Georgia serif)
- Material You design principles
- Bottom navigation (4 tabs)
- Enhanced book cards and details
- Author profiles and personal library

---

## Phase Overview

| Phase | Duration | Focus Area | Deliverable |
|-------|----------|------------|-------------|
| 1 | Week 1 | Design System Foundation | Tailwind config, color tokens, base components |
| 2 | Weeks 2-3 | Core UI Migration | Restyled existing components, bottom nav |
| 3 | Week 4 | New Views | ListView, enhanced BookDetails, SearchDrawer |
| 4 | Weeks 5-6 | Author Profiles | Author aggregation, profile view, journey maps |
| 5 | Weeks 7-8 | Personal Library | Library store, save/unsave, tabs, localStorage |
| 6 | Weeks 9-10 | Polish & Testing | Cross-browser testing, performance, accessibility |

---

## Phase 1: Design System Foundation (Week 1)

### Objectives
- Establish new color palette and typography
- Create design tokens
- Build foundational shared components
- Update Tailwind configuration

### 1.1 Tailwind Config Update

**File**: `tailwind.config.js`

```javascript
// Add to theme.extend
colors: {
  // Primary Colors
  'teal': {
    deep: '#3D6960',  // Primary action color
  },
  'copper': {
    warm: '#C17A3A',  // Accent color
  },
  'parchment': {
    50: '#F5F1E8',   // Light background
    100: '#E8E3D8',  // Medium background
    200: '#E0D9C8',  // Border color
    300: '#D5CFC0',  // Darker background
  },
  // Text Colors
  'text': {
    primary: '#2D3E3C',
    secondary: '#6B7C7A',
    tertiary: '#9CA5A3',
  },
  // Genre Colors
  'genre': {
    memoir: '#8B5A8E',
    adventure: '#C17A3A',
    historical: '#A67C52',
    travel: '#3D6960',
  }
},
fontFamily: {
  'serif': ['Georgia', 'serif'],
  'sans': ['system-ui', '-apple-system', 'sans-serif'],
},
borderRadius: {
  'xl': '16px',
  '2xl': '24px',
},
```

### 1.2 Design Tokens File

**File**: `src/styles/design-tokens.css` (new)

```css
:root {
  /* Colors */
  --color-primary: #3D6960;
  --color-accent: #C17A3A;
  --color-bg-light: #F5F1E8;
  --color-bg-medium: #E8E3D8;
  --color-border: #E0D9C8;
  --color-text-primary: #2D3E3C;
  --color-text-secondary: #6B7C7A;
  --color-text-tertiary: #9CA5A3;

  /* Typography */
  --font-serif: Georgia, serif;
  --font-sans: system-ui, -apple-system, sans-serif;

  /* Spacing */
  --space-card: 1rem;
  --space-section: 1.5rem;

  /* Shadows */
  --shadow-card: 0 2px 8px rgba(45, 62, 60, 0.1);
  --shadow-elevated: 0 4px 16px rgba(45, 62, 60, 0.15);
  --shadow-fab: 0 6px 20px rgba(45, 62, 60, 0.2);

  /* Border Radius */
  --radius-card: 16px;
  --radius-drawer: 24px;
  --radius-button: 12px;
  --radius-fab: 50%;
}
```

### 1.3 Base Components to Create

#### BottomNavigation.vue (new)

**File**: `src/components/BottomNavigation.vue`

**Features**:
- 4 tabs: Map, List, Library, Contribute
- Active state with color change
- Icons from lucide-vue-next
- Fixed position at bottom
- Safe area support (iOS notch)

**Props**:
- `activeTab: string` - Currently active tab

**Structure**:
```vue
<template>
  <nav class="fixed bottom-0 left-0 right-0 bg-white border-t border-parchment-200 pb-safe">
    <div class="flex justify-around items-center h-20">
      <button v-for="tab in tabs" :key="tab.id"
              :class="tabClasses(tab)"
              @click="$emit('navigate', tab.id)">
        <component :is="tab.icon" class="w-6 h-6" />
        <span class="text-xs mt-1">{{ tab.label }}</span>
      </button>
    </div>
  </nav>
</template>
```

#### FilterChip.vue (new)

**File**: `src/components/FilterChip.vue`

**Features**:
- Pill-shaped button
- Selected/unselected states
- Removable option (x icon)
- Color variants (primary, genre-specific)

**Props**:
- `label: string`
- `selected: boolean`
- `removable: boolean`
- `color: string` (default, memoir, historical, etc.)

#### GenreBadge.vue (new)

**File**: `src/components/GenreBadge.vue`

**Features**:
- Small pill with genre-specific color
- Used in BookCard and BookDetails

**Props**:
- `genre: string`

### 1.4 Font Setup

**File**: `index.html`

Add Georgia serif font (already available in most systems, but add web font fallback):

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<!-- Backup: Use Libre Baskerville as Georgia alternative -->
<link href="https://fonts.googleapis.com/fonts/css2?family=Libre+Baskerville:wght@400;700&display=swap" rel="stylesheet">
```

Update CSS:
```css
font-family: {
  'serif': ['Georgia', 'Libre Baskerville', 'serif'],
}
```

### 1.5 Tasks Checklist

- [ ] Update `tailwind.config.js` with new color palette
- [ ] Create `src/styles/design-tokens.css`
- [ ] Import design tokens in `main.js`
- [ ] Install lucide-vue-next: `npm install lucide-vue-next`
- [ ] Create `BottomNavigation.vue`
- [ ] Create `FilterChip.vue`
- [ ] Create `GenreBadge.vue`
- [ ] Add Georgia/Libre Baskerville font
- [ ] Test components in isolation (Storybook-style page)

**Deliverable**: Design system ready, 3 new shared components built

---

## Phase 2: Core UI Migration (Weeks 2-3)

### Objectives
- Restyle all existing components with new design system
- Implement bottom navigation structure
- Update layout and spacing
- Remove/simplify settings

### 2.1 App.vue Restructure

**File**: `src/App.vue`

**Changes**:
- Add bottom navigation (always visible)
- Adjust main content area to account for bottom nav (padding-bottom: 80px)
- Add paper grain texture overlay
- Change background to parchment gradient

```vue
<template>
  <div class="min-h-screen bg-gradient-to-br from-parchment-100 via-parchment-50 to-parchment-200 relative">
    <!-- Paper grain texture overlay -->
    <div
      class="fixed inset-0 opacity-[0.03] pointer-events-none mix-blend-multiply"
      style="background-image: url('data:image/svg+xml,...')"
    ></div>

    <!-- Main content -->
    <div class="pb-20">
      <component :is="currentView" />
    </div>

    <!-- Bottom Navigation -->
    <BottomNavigation
      :active-tab="currentTab"
      @navigate="handleNavigate"
    />
  </div>
</template>
```

### 2.2 TopBar.vue Redesign

**File**: `src/components/TopBar.vue`

**Changes**:
- Change logo to Georgia serif, larger (24px)
- Remove hamburger menu button
- Keep only search button
- Update colors to teal/parchment
- Simplify layout

```vue
<template>
  <header class="h-16 bg-parchment-50 px-6 flex items-center border-b border-parchment-200">
    <h1 class="font-serif text-2xl font-semibold text-text-primary tracking-tight">
      LitMap
    </h1>
    <button
      class="ml-auto p-2 hover:bg-parchment-200/50 rounded-full transition-colors"
      @click="$emit('open-search')"
    >
      <Search class="w-6 h-6 text-teal-deep" :stroke-width="2" />
    </button>
  </header>
</template>
```

**Remove**: Hamburger menu button (no longer needed)

### 2.3 GoogleMapComponent.vue Enhancements

**File**: `src/components/GoogleMapComponent.vue`

**Changes**:
- Add info overlay at bottom of map
- Update map styling (vintage map aesthetic if possible)
- Genre-specific marker colors
- Labeled pins for individual markers

**New Feature**: Info Overlay

```vue
<template>
  <!-- Existing map -->
  <div ref="mapContainer" class="w-full h-full">
    <!-- Map renders here -->
  </div>

  <!-- NEW: Info overlay -->
  <div class="absolute bottom-6 left-6 right-6 bg-white/90 backdrop-blur-sm px-4 py-3 rounded-xl shadow-card">
    <p class="text-text-primary text-sm">
      {{ infoText }}
    </p>
  </div>
</template>

<script setup>
const infoText = computed(() => {
  const count = booksStore.filteredBooks.length;
  const region = currentRegion.value || 'this area';
  return `Showing ${count} books in ${region}`;
});
</script>
```

**Marker Colors**: Map genres to colors

```javascript
const genreColors = {
  'Memoir': '#8B5A8E',
  'Adventure': '#C17A3A',
  'Historical': '#A67C52',
  'Travel': '#3D6960',
  'Fiction': '#5A7B8E',
  // Default fallback
  'default': '#3D6960'
};

function getMarkerColor(book) {
  const primaryGenre = book.genre || book.tags?.[0] || 'default';
  return genreColors[primaryGenre] || genreColors.default;
}
```

### 2.4 BookCard.vue Redesign

**File**: `src/components/BookCard.vue`

**Changes**:
- Add mock book cover (colored rectangle with design)
- Use Georgia serif for title
- Add genre badges
- Enhanced shadow on hover
- Better spacing and layout

```vue
<template>
  <div class="bg-white rounded-xl shadow-card hover:shadow-elevated transition-shadow p-4 cursor-pointer border border-transparent hover:border-copper-warm">
    <div class="flex gap-4">
      <!-- Mock book cover -->
      <div
        class="w-20 h-28 rounded-lg flex-shrink-0"
        :style="{ backgroundColor: coverColor }"
      >
        <div class="w-full h-full flex items-center justify-center opacity-20">
          <BookOpen class="w-8 h-8 text-white" />
        </div>
      </div>

      <!-- Book info -->
      <div class="flex-1 min-w-0">
        <h3 class="font-serif text-lg font-semibold text-text-primary mb-1 line-clamp-2">
          {{ book.title }}
        </h3>
        <p class="text-sm text-text-secondary mb-2">
          {{ book.author }}
        </p>

        <!-- Genre badges -->
        <div class="flex gap-2 flex-wrap mb-2">
          <GenreBadge
            v-for="genre in displayGenres"
            :key="genre"
            :genre="genre"
          />
        </div>

        <!-- Metadata -->
        <div class="flex items-center gap-4 text-xs text-text-tertiary">
          <span v-if="book.publication_year">{{ book.publication_year }}</span>
          <span v-if="primaryLocation">{{ primaryLocation }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const coverColor = computed(() => {
  // Generate color based on book title hash
  const hash = hashString(props.book.title);
  const hue = hash % 360;
  return `hsl(${hue}, 40%, 60%)`;
});
</script>
```

### 2.5 BookDetails.vue Enhancement

**File**: `src/components/BookDetails.vue`

**Changes**:
- Restructure layout with sections
- Add genre badges at top
- Add metadata icons (Calendar, BookOpen)
- Mini map for journey location
- "Add to Library" button (placeholder for Phase 5)
- Share button (stub)

```vue
<template>
  <div class="bg-parchment-50 min-h-full pb-20">
    <!-- Header -->
    <header class="flex items-center justify-between px-6 py-4 border-b border-parchment-200">
      <button @click="$emit('close')" class="p-2 hover:bg-parchment-200 rounded-full">
        <ArrowLeft class="w-6 h-6 text-text-primary" />
      </button>
      <div class="flex gap-2">
        <button class="p-2 hover:bg-parchment-200 rounded-full">
          <Share2 class="w-5 h-5 text-text-secondary" />
        </button>
        <button
          class="p-2 hover:bg-parchment-200 rounded-full"
          @click="toggleLibrary"
        >
          <Bookmark
            class="w-5 h-5"
            :class="isInLibrary ? 'fill-copper-warm text-copper-warm' : 'text-text-secondary'"
          />
        </button>
      </div>
    </header>

    <!-- Book Cover -->
    <div class="px-6 py-8">
      <div
        class="w-48 h-64 mx-auto rounded-lg shadow-elevated"
        :style="{ backgroundColor: coverColor }"
      >
        <!-- Mock cover design -->
      </div>
    </div>

    <!-- Title & Author -->
    <div class="px-6 mb-6">
      <h1 class="font-serif text-2xl font-semibold text-text-primary mb-2 leading-tight">
        {{ book.title }}
      </h1>
      <button
        class="text-lg text-text-secondary hover:text-teal-deep transition-colors"
        @click="viewAuthor"
      >
        {{ book.author }}
      </button>
    </div>

    <!-- Genre Badges -->
    <div class="px-6 mb-6 flex gap-2 flex-wrap">
      <GenreBadge v-for="genre in genres" :key="genre" :genre="genre" />
    </div>

    <!-- Metadata -->
    <div class="px-6 mb-6 flex gap-6">
      <div v-if="book.publication_year" class="flex items-center gap-2 text-text-secondary">
        <Calendar class="w-4 h-4" />
        <span class="text-sm">{{ book.publication_year }}</span>
      </div>
      <div v-if="book.page_count" class="flex items-center gap-2 text-text-secondary">
        <BookOpen class="w-4 h-4" />
        <span class="text-sm">{{ book.page_count }} pages</span>
      </div>
    </div>

    <!-- Journey Location Section -->
    <section class="px-6 mb-6">
      <h2 class="font-serif text-xl font-semibold text-text-primary mb-3">
        Journey Location
      </h2>
      <div class="bg-white rounded-xl shadow-card p-4">
        <!-- Mini map (placeholder) -->
        <div class="w-full h-40 bg-parchment-100 rounded-lg mb-3">
          <!-- Google Maps mini view -->
        </div>
        <div class="flex flex-wrap gap-2">
          <div
            v-for="location in book.locations"
            :key="location.city"
            class="flex items-center gap-2 text-sm text-text-secondary"
          >
            <MapPin class="w-4 h-4" />
            <span>{{ location.city }}, {{ location.country }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Synopsis Section -->
    <section class="px-6 mb-6">
      <h2 class="font-serif text-xl font-semibold text-text-primary mb-3">
        Synopsis
      </h2>
      <div class="bg-white rounded-xl shadow-card p-5">
        <p class="text-text-secondary leading-relaxed">
          {{ book.description }}
        </p>
      </div>
    </section>

    <!-- Add to Library Button -->
    <div class="px-6 mb-8">
      <button
        class="w-full bg-teal-deep text-white py-4 rounded-xl shadow-elevated hover:shadow-fab transition-shadow flex items-center justify-center gap-2 font-medium"
        @click="addToLibrary"
      >
        <Heart class="w-5 h-5" />
        <span>Add to My Library</span>
      </button>
    </div>
  </div>
</template>
```

### 2.6 FAB.vue Update

**File**: `src/components/FAB.vue`

**Changes**:
- Add second FAB (target icon for center location)
- Update styling to match Material You
- Stack vertically

```vue
<template>
  <div class="fixed right-6 bottom-28 flex flex-col gap-3 z-20">
    <!-- Random location FAB -->
    <button
      class="w-12 h-12 rounded-full bg-teal-deep shadow-fab hover:shadow-xl transition-shadow flex items-center justify-center"
      @click="$emit('random-location')"
      title="Random location"
    >
      <Dices class="w-5 h-5 text-white" :stroke-width="2" />
    </button>

    <!-- Center location FAB -->
    <button
      class="w-14 h-14 rounded-full bg-teal-deep shadow-fab hover:shadow-xl transition-shadow flex items-center justify-center"
      @click="$emit('center-location')"
      title="Center on your location"
    >
      <Target class="w-6 h-6 text-white" :stroke-width="2" />
    </button>
  </div>
</template>
```

### 2.7 Settings Simplification

**Remove**:
- `HamburgerMenu.vue` component (delete file)
- Collection switcher functionality
- Map type selector functionality

**Keep**:
- Clustering toggle - Move to a small icon button on the map (top-right corner)

**New**: Clustering toggle button

**File**: `src/components/ClusterToggle.vue` (new)

```vue
<template>
  <button
    class="absolute top-20 right-4 z-10 bg-white rounded-full p-3 shadow-card hover:shadow-elevated transition-shadow"
    @click="toggleClustering"
    :title="clusteringEnabled ? 'Disable clustering' : 'Enable clustering'"
  >
    <component
      :is="clusteringEnabled ? Grid3x3 : Map"
      class="w-5 h-5 text-teal-deep"
    />
  </button>
</template>

<script setup>
import { Grid3x3, Map } from 'lucide-vue-next';
import { useUIStore } from '@/stores/ui';

const uiStore = useUIStore();
const clusteringEnabled = computed(() => uiStore.clusteringEnabled);

function toggleClustering() {
  uiStore.toggleClustering();
}
</script>
```

### 2.8 BottomSheet.vue Styling Update

**File**: `src/components/BottomSheet.vue`

**Changes**:
- Update background to white/parchment
- Add drag handle (visual indicator)
- Update border radius to 24px (top only)
- Adjust shadow

```vue
<template>
  <div
    class="fixed left-0 right-0 bg-white rounded-t-3xl shadow-elevated transition-transform z-30"
    :style="{ bottom: 0, transform: `translateY(${translateY}px)` }"
  >
    <!-- Drag handle -->
    <div class="flex justify-center pt-3 pb-2">
      <div class="w-12 h-1 bg-parchment-200 rounded-full"></div>
    </div>

    <!-- Content -->
    <div class="overflow-y-auto" :style="{ height: contentHeight }">
      <slot></slot>
    </div>
  </div>
</template>
```

### 2.9 Tasks Checklist

- [ ] Update `App.vue` with new layout and bottom nav
- [ ] Add paper grain texture overlay
- [ ] Redesign `TopBar.vue` (remove hamburger)
- [ ] Enhance `GoogleMapComponent.vue` (info overlay, genre colors)
- [ ] Redesign `BookCard.vue` with new style
- [ ] Enhance `BookDetails.vue` with sections
- [ ] Update `FAB.vue` (add second FAB)
- [ ] Create `ClusterToggle.vue`
- [ ] Update `BottomSheet.vue` styling
- [ ] Remove `HamburgerMenu.vue`
- [ ] Remove collection switcher from stores
- [ ] Remove map type selector from stores
- [ ] Test responsive layout on mobile devices

**Deliverable**: All existing components restyled, simplified settings, new navigation

---

## Phase 3: New Views - List & Enhanced Search (Week 4)

### Objectives
- Implement dedicated ListView
- Create SearchDrawer (bottom sheet style)
- Add Vue Router for multi-page navigation
- Enhanced book detail integration

### 3.1 Vue Router Setup

**File**: `src/router/index.js` (new or update)

```javascript
import { createRouter, createWebHistory } from 'vue-router';
import MapView from '@/views/MapView.vue';
import ListView from '@/views/ListView.vue';
import LibraryView from '@/views/LibraryView.vue';
import ContributeView from '@/views/ContributeView.vue';
import BookDetailView from '@/views/BookDetailView.vue';
import AuthorProfileView from '@/views/AuthorProfileView.vue';

const routes = [
  {
    path: '/',
    name: 'map',
    component: MapView,
    meta: { tab: 'map' }
  },
  {
    path: '/list',
    name: 'list',
    component: ListView,
    meta: { tab: 'list' }
  },
  {
    path: '/library',
    name: 'library',
    component: LibraryView,
    meta: { tab: 'library' }
  },
  {
    path: '/contribute',
    name: 'contribute',
    component: ContributeView,
    meta: { tab: 'contribute' }
  },
  {
    path: '/book/:id',
    name: 'book-detail',
    component: BookDetailView,
  },
  {
    path: '/author/:name',
    name: 'author-profile',
    component: AuthorProfileView,
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router;
```

**Update**: `src/main.js`

```javascript
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import './styles/design-tokens.css';
import './index.css';

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.mount('#app');
```

### 3.2 Restructure App.vue

**File**: `src/App.vue`

```vue
<template>
  <div class="min-h-screen bg-gradient-to-br from-parchment-100 via-parchment-50 to-parchment-200 relative">
    <!-- Paper grain texture -->
    <div class="fixed inset-0 opacity-[0.03] pointer-events-none mix-blend-multiply texture-overlay"></div>

    <!-- Router view for main content -->
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>

    <!-- Bottom Navigation (always visible) -->
    <BottomNavigation
      :active-tab="currentTab"
      @navigate="handleNavigate"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import BottomNavigation from '@/components/BottomNavigation.vue';

const router = useRouter();
const route = useRoute();

const currentTab = computed(() => route.meta.tab || '');

function handleNavigate(tab) {
  router.push({ name: tab });
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.texture-overlay {
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
}
</style>
```

### 3.3 MapView Component

**File**: `src/views/MapView.vue` (new)

Move existing map functionality from App.vue:

```vue
<template>
  <div class="h-screen flex flex-col">
    <!-- Top Bar -->
    <TopBar @open-search="openSearch" />

    <!-- Map -->
    <div class="flex-1 relative">
      <GoogleMapComponent />

      <!-- Cluster Toggle -->
      <ClusterToggle />

      <!-- FABs -->
      <FAB
        @random-location="handleRandomLocation"
        @center-location="handleCenterLocation"
      />
    </div>

    <!-- Search Drawer -->
    <SearchDrawer
      v-model:open="searchOpen"
      @search="handleSearch"
    />

    <!-- Bottom Sheet (Book Details) -->
    <BottomSheet
      v-if="selectedBook"
      v-model:state="sheetState"
    >
      <BookDetails :book="selectedBook" @close="closeDetails" />
    </BottomSheet>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import TopBar from '@/components/TopBar.vue';
import GoogleMapComponent from '@/components/GoogleMapComponent.vue';
import ClusterToggle from '@/components/ClusterToggle.vue';
import FAB from '@/components/FAB.vue';
import SearchDrawer from '@/components/SearchDrawer.vue';
import BottomSheet from '@/components/BottomSheet.vue';
import BookDetails from '@/components/BookDetails.vue';
import { useBooksStore } from '@/stores/books';
import { useUIStore } from '@/stores/ui';

const booksStore = useBooksStore();
const uiStore = useUIStore();

const searchOpen = ref(false);
const selectedBook = computed(() => uiStore.selectedBook);
const sheetState = computed({
  get: () => uiStore.sheetState,
  set: (val) => uiStore.setSheetState(val)
});

function openSearch() {
  searchOpen.value = true;
}

function handleSearch(query) {
  booksStore.searchBooks(query);
  searchOpen.value = false;
}

function handleRandomLocation() {
  booksStore.selectRandomBook();
}

function handleCenterLocation() {
  // Center map on user location (geolocation API)
}

function closeDetails() {
  uiStore.clearSelectedBook();
}
</script>
```

### 3.4 ListView Component

**File**: `src/views/ListView.vue` (new)

```vue
<template>
  <div class="min-h-screen pb-20">
    <!-- Header -->
    <header class="bg-white border-b border-parchment-200 px-4 py-4 flex items-center gap-4">
      <button @click="$router.back()" class="p-2 hover:bg-parchment-100 rounded-full">
        <ArrowLeft class="w-6 h-6 text-text-primary" />
      </button>
      <h1 class="font-serif text-xl font-semibold text-text-primary flex-1">
        {{ pageTitle }}
      </h1>
      <button @click="openFilters" class="p-2 hover:bg-parchment-100 rounded-full">
        <Filter class="w-6 h-6 text-text-secondary" />
      </button>
    </header>

    <!-- Results count -->
    <div class="px-6 py-4 text-sm text-text-secondary">
      {{ resultsCount }} books found
    </div>

    <!-- Book list -->
    <div class="px-4 space-y-4 pb-8">
      <BookCard
        v-for="book in displayBooks"
        :key="book.id"
        :book="book"
        @click="viewBook(book)"
      />
    </div>

    <!-- Empty state -->
    <EmptyState
      v-if="displayBooks.length === 0"
      title="No books found"
      description="Try adjusting your search or filters"
    />

    <!-- Loading -->
    <LoadingSpinner v-if="loading" />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ArrowLeft, Filter } from 'lucide-vue-next';
import BookCard from '@/components/BookCard.vue';
import EmptyState from '@/components/EmptyState.vue';
import LoadingSpinner from '@/components/LoadingSpinner.vue';
import { useBooksStore } from '@/stores/books';
import { useUIStore } from '@/stores/ui';

const router = useRouter();
const booksStore = useBooksStore();
const uiStore = useUIStore();

const displayBooks = computed(() => booksStore.filteredBooks || booksStore.allBooks);
const loading = computed(() => booksStore.isLoading);
const resultsCount = computed(() => displayBooks.value.length);

const pageTitle = computed(() => {
  const query = uiStore.searchQuery;
  if (query) return `Results for "${query}"`;
  const filter = uiStore.activeFilter;
  if (filter) return `Books in ${filter}`;
  return 'All Books';
});

function viewBook(book) {
  router.push({ name: 'book-detail', params: { id: book.id } });
}

function openFilters() {
  uiStore.setSearchDrawerOpen(true);
}

onMounted(() => {
  if (!booksStore.allBooks.length) {
    booksStore.fetchBooks();
  }
});
</script>
```

### 3.5 SearchDrawer Component

**File**: `src/components/SearchDrawer.vue` (new)

Replace the existing `SearchBar.vue` approach:

```vue
<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-40"
        @click.self="close"
      >
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/30 backdrop-blur-sm"></div>

        <!-- Drawer -->
        <div class="absolute bottom-0 left-0 right-0 bg-white rounded-t-3xl shadow-elevated max-h-[70vh] flex flex-col">
          <!-- Drag handle -->
          <div class="flex justify-center pt-3 pb-2">
            <div class="w-12 h-1 bg-parchment-200 rounded-full"></div>
          </div>

          <!-- Content -->
          <div class="flex-1 overflow-y-auto px-6 pb-6">
            <!-- Title -->
            <h2 class="font-serif text-3xl font-semibold text-text-primary mb-6">
              Discover Journeys
            </h2>

            <!-- Search input -->
            <div class="relative mb-6">
              <Search class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-text-tertiary" />
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search titles, authors, places..."
                class="w-full pl-12 pr-4 py-3 bg-parchment-50 border border-parchment-200 rounded-xl text-text-primary placeholder-text-tertiary focus:outline-none focus:border-teal-deep"
                @keyup.enter="performSearch"
              />
            </div>

            <!-- Quick Filters -->
            <div class="mb-6">
              <h3 class="text-sm font-medium text-text-secondary mb-3">Quick Filters</h3>
              <div class="flex flex-wrap gap-2">
                <FilterChip
                  v-for="filter in quickFilters"
                  :key="filter.id"
                  :label="filter.label"
                  :selected="activeQuickFilter === filter.id"
                  @click="selectQuickFilter(filter.id)"
                />
              </div>
            </div>

            <!-- Advanced Filters (collapsible) -->
            <div class="mb-6">
              <button
                class="flex items-center justify-between w-full py-2"
                @click="advancedExpanded = !advancedExpanded"
              >
                <h3 class="text-sm font-medium text-text-secondary">Advanced Filters</h3>
                <ChevronDown
                  class="w-5 h-5 text-text-tertiary transition-transform"
                  :class="{ 'rotate-180': advancedExpanded }"
                />
              </button>

              <Transition name="expand">
                <div v-if="advancedExpanded" class="mt-4 space-y-4">
                  <!-- Genre checkboxes -->
                  <div>
                    <h4 class="text-sm font-medium text-text-primary mb-2">Genre</h4>
                    <div class="space-y-2">
                      <label
                        v-for="genre in genres"
                        :key="genre"
                        class="flex items-center gap-2 cursor-pointer"
                      >
                        <input
                          type="checkbox"
                          :value="genre"
                          v-model="selectedGenres"
                          class="w-4 h-4 rounded border-parchment-300 text-teal-deep focus:ring-teal-deep"
                        />
                        <span class="text-sm text-text-secondary">{{ genre }}</span>
                      </label>
                    </div>
                  </div>

                  <!-- Future: Timeline slider would go here -->
                  <!-- Deferred for initial release -->
                </div>
              </Transition>
            </div>

            <!-- Apply button -->
            <button
              class="w-full bg-copper-warm text-white py-4 rounded-xl font-medium hover:shadow-elevated transition-shadow"
              @click="applyFilters"
            >
              Apply Filters
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed } from 'vue';
import { Search, ChevronDown } from 'lucide-vue-next';
import FilterChip from './FilterChip.vue';

const props = defineProps({
  modelValue: Boolean
});

const emit = defineEmits(['update:modelValue', 'search']);

const searchQuery = ref('');
const activeQuickFilter = ref('all');
const advancedExpanded = ref(false);
const selectedGenres = ref([]);

const quickFilters = [
  { id: 'all', label: 'All' },
  { id: 'author', label: 'Author' },
  { id: 'location', label: 'Location' },
  { id: 'theme', label: 'Theme' }
];

const genres = [
  'Adventure',
  'Memoir',
  'Historical',
  'Travel',
  'Fiction',
  'Photography'
];

function close() {
  emit('update:modelValue', false);
}

function selectQuickFilter(filterId) {
  activeQuickFilter.value = filterId;
}

function performSearch() {
  applyFilters();
}

function applyFilters() {
  emit('search', {
    query: searchQuery.value,
    quickFilter: activeQuickFilter.value,
    genres: selectedGenres.value
  });
  close();
}
</script>

<style scoped>
.drawer-enter-active, .drawer-leave-active {
  transition: opacity 0.3s ease;
}
.drawer-enter-from, .drawer-leave-to {
  opacity: 0;
}
.drawer-enter-active .absolute:last-child,
.drawer-leave-active .absolute:last-child {
  transition: transform 0.3s ease;
}
.drawer-enter-from .absolute:last-child,
.drawer-leave-to .absolute:last-child {
  transform: translateY(100%);
}

.expand-enter-active, .expand-leave-active {
  transition: all 0.3s ease;
}
.expand-enter-from, .expand-leave-to {
  opacity: 0;
  max-height: 0;
}
.expand-enter-to, .expand-leave-from {
  opacity: 1;
  max-height: 500px;
}
</style>
```

### 3.6 BookDetailView (Full Page)

**File**: `src/views/BookDetailView.vue` (new)

Convert `BookDetails.vue` component to a full-page view:

```vue
<template>
  <div class="min-h-screen bg-parchment-50 pb-20">
    <!-- Use the enhanced BookDetails component from Phase 2 -->
    <BookDetails
      v-if="book"
      :book="book"
      @close="$router.back()"
      @view-author="viewAuthor"
    />

    <LoadingSpinner v-else-if="loading" />

    <EmptyState
      v-else
      title="Book not found"
      description="This book may have been removed"
    />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import BookDetails from '@/components/BookDetails.vue';
import LoadingSpinner from '@/components/LoadingSpinner.vue';
import EmptyState from '@/components/EmptyState.vue';
import { useBooksStore } from '@/stores/books';

const route = useRoute();
const router = useRouter();
const booksStore = useBooksStore();

const bookId = computed(() => route.params.id);
const book = computed(() => booksStore.getBookById(bookId.value));
const loading = computed(() => booksStore.isLoading);

function viewAuthor() {
  if (book.value?.author) {
    router.push({
      name: 'author-profile',
      params: { name: book.value.author }
    });
  }
}

onMounted(() => {
  if (!book.value && !loading.value) {
    booksStore.fetchBookById(bookId.value);
  }
});
</script>
```

### 3.7 EmptyState Component

**File**: `src/components/EmptyState.vue`

```vue
<template>
  <div class="flex flex-col items-center justify-center py-16 px-6 text-center">
    <div class="w-24 h-24 bg-parchment-100 rounded-full flex items-center justify-center mb-6">
      <BookOpen class="w-12 h-12 text-text-tertiary" />
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
import { BookOpen } from 'lucide-vue-next';

defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  }
});
</script>
```

### 3.8 Update Books Store

**File**: `src/stores/books.js`

Add methods for new features:

```javascript
export const useBooksStore = defineStore('books', {
  state: () => ({
    allBooks: [],
    filteredBooks: null,
    currentBook: null,
    isLoading: false,
    error: null,
    searchQuery: '',
    activeFilters: {
      genres: [],
      quickFilter: 'all'
    }
  }),

  getters: {
    getBookById: (state) => (id) => {
      return state.allBooks.find(book => book.id === id);
    },

    displayBooks(state) {
      return state.filteredBooks || state.allBooks;
    }
  },

  actions: {
    async searchBooks(searchParams) {
      this.searchQuery = searchParams.query || '';
      this.activeFilters = {
        genres: searchParams.genres || [],
        quickFilter: searchParams.quickFilter || 'all'
      };

      // Apply filters
      this.filteredBooks = this.allBooks.filter(book => {
        // Text search
        if (this.searchQuery) {
          const query = this.searchQuery.toLowerCase();
          const matchesTitle = book.title?.toLowerCase().includes(query);
          const matchesAuthor = book.author?.toLowerCase().includes(query);
          const matchesLocation = book.locations?.some(loc =>
            loc.city?.toLowerCase().includes(query) ||
            loc.country?.toLowerCase().includes(query)
          );

          if (!matchesTitle && !matchesAuthor && !matchesLocation) {
            return false;
          }
        }

        // Genre filter
        if (this.activeFilters.genres.length > 0) {
          const bookGenres = book.genre ? [book.genre] : book.tags || [];
          const hasMatchingGenre = this.activeFilters.genres.some(genre =>
            bookGenres.includes(genre)
          );
          if (!hasMatchingGenre) return false;
        }

        return true;
      });
    },

    clearFilters() {
      this.filteredBooks = null;
      this.searchQuery = '';
      this.activeFilters = { genres: [], quickFilter: 'all' };
    }
  }
});
```

### 3.9 Tasks Checklist

- [ ] Install Vue Router: `npm install vue-router`
- [ ] Create `src/router/index.js` with routes
- [ ] Update `src/main.js` to use router
- [ ] Restructure `App.vue` with router-view
- [ ] Create `src/views/MapView.vue` (move map logic)
- [ ] Create `src/views/ListView.vue`
- [ ] Create `src/views/BookDetailView.vue`
- [ ] Create `src/components/SearchDrawer.vue`
- [ ] Create `src/components/EmptyState.vue`
- [ ] Update `src/stores/books.js` with search methods
- [ ] Test navigation between views
- [ ] Test search and filtering
- [ ] Test browser back button

**Deliverable**: Multi-page navigation, ListView, SearchDrawer, enhanced search

---

## Phase 4: Author Profile System (Weeks 5-6)

### Objectives
- Aggregate author data from existing books
- Create author profile pages
- Show author journey maps
- Link from book details to author profiles

### 4.1 Author Store

**File**: `src/stores/authors.js` (new)

```javascript
import { defineStore } from 'pinia';
import { useBooksStore } from './books';

export const useAuthorsStore = defineStore('authors', {
  state: () => ({
    authorsCache: new Map(),
    isLoading: false,
    error: null
  }),

  getters: {
    getAuthorByName: (state) => (authorName) => {
      return state.authorsCache.get(authorName);
    },

    allAuthors(state) {
      return Array.from(state.authorsCache.values());
    }
  },

  actions: {
    /**
     * Compute author profile from book data
     */
    computeAuthorProfile(authorName) {
      const booksStore = useBooksStore();

      // Find all books by this author
      const authorBooks = booksStore.allBooks.filter(
        book => book.author === authorName
      );

      if (authorBooks.length === 0) {
        return null;
      }

      // Aggregate data
      const profile = {
        name: authorName,
        books: authorBooks,
        bookCount: authorBooks.length,

        // Aggregate locations (countries visited)
        countries: this.getUniqueCountries(authorBooks),
        countryCount: 0,

        // Aggregate genres
        genres: this.getUniqueGenres(authorBooks),

        // Generate avatar (initials + color)
        avatar: this.generateAvatar(authorName),

        // Bio (placeholder - can be added manually later)
        bio: null,

        // Journey map data (all locations)
        journeyLocations: this.aggregateLocations(authorBooks)
      };

      profile.countryCount = profile.countries.length;

      // Cache it
      this.authorsCache.set(authorName, profile);

      return profile;
    },

    getUniqueCountries(books) {
      const countries = new Set();
      books.forEach(book => {
        book.locations?.forEach(loc => {
          if (loc.country) countries.add(loc.country);
        });
      });
      return Array.from(countries);
    },

    getUniqueGenres(books) {
      const genres = new Set();
      books.forEach(book => {
        if (book.genre) genres.add(book.genre);
        book.tags?.forEach(tag => genres.add(tag));
      });
      return Array.from(genres);
    },

    aggregateLocations(books) {
      const locationsMap = new Map();

      books.forEach(book => {
        book.locations?.forEach(loc => {
          const key = `${loc.lat},${loc.lng}`;
          if (!locationsMap.has(key)) {
            locationsMap.set(key, {
              ...loc,
              books: []
            });
          }
          locationsMap.get(key).books.push({
            id: book.id,
            title: book.title
          });
        });
      });

      return Array.from(locationsMap.values());
    },

    generateAvatar(name) {
      // Get initials
      const initials = name
        .split(' ')
        .map(word => word[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);

      // Generate color based on name hash
      const hash = name.split('').reduce((acc, char) => {
        return char.charCodeAt(0) + ((acc << 5) - acc);
      }, 0);
      const hue = Math.abs(hash) % 360;
      const color = `hsl(${hue}, 50%, 55%)`;

      return { initials, color };
    },

    /**
     * Fetch or compute author profile
     */
    async fetchAuthorProfile(authorName) {
      this.isLoading = true;
      this.error = null;

      try {
        // Check cache first
        let profile = this.getAuthorByName(authorName);

        if (!profile) {
          // Compute from books
          profile = this.computeAuthorProfile(authorName);
        }

        return profile;
      } catch (err) {
        this.error = err.message;
        return null;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Precompute all author profiles
     */
    precomputeAllAuthors() {
      const booksStore = useBooksStore();
      const authorNames = new Set(
        booksStore.allBooks.map(book => book.author).filter(Boolean)
      );

      authorNames.forEach(name => {
        this.computeAuthorProfile(name);
      });
    }
  }
});
```

### 4.2 AuthorProfileView

**File**: `src/views/AuthorProfileView.vue` (new)

```vue
<template>
  <div class="min-h-screen bg-parchment-50 pb-20">
    <!-- Header -->
    <header class="bg-white border-b border-parchment-200 px-4 py-4 flex items-center gap-4">
      <button @click="$router.back()" class="p-2 hover:bg-parchment-100 rounded-full">
        <ArrowLeft class="w-6 h-6 text-text-primary" />
      </button>
      <h1 class="font-serif text-xl font-semibold text-text-primary">
        Author Profile
      </h1>
    </header>

    <div v-if="author" class="px-6 py-8">
      <!-- Author Card -->
      <div class="bg-white rounded-2xl shadow-card p-6 mb-8">
        <!-- Avatar -->
        <div
          class="w-24 h-24 rounded-full mx-auto mb-4 flex items-center justify-center text-white text-2xl font-semibold"
          :style="{ backgroundColor: author.avatar.color }"
        >
          {{ author.avatar.initials }}
        </div>

        <!-- Name -->
        <h2 class="font-serif text-2xl font-semibold text-text-primary text-center mb-2">
          {{ author.name }}
        </h2>

        <!-- Bio (if exists) -->
        <p v-if="author.bio" class="text-text-secondary text-center mb-4 leading-relaxed">
          {{ author.bio }}
        </p>

        <!-- Stats -->
        <div class="flex justify-center gap-8 mt-6">
          <div class="text-center">
            <div class="text-2xl font-semibold text-teal-deep">{{ author.bookCount }}</div>
            <div class="text-sm text-text-tertiary">books</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-semibold text-teal-deep">{{ author.countryCount }}</div>
            <div class="text-sm text-text-tertiary">countries</div>
          </div>
        </div>

        <!-- Genres -->
        <div v-if="author.genres.length > 0" class="mt-6 flex justify-center gap-2 flex-wrap">
          <GenreBadge
            v-for="genre in author.genres"
            :key="genre"
            :genre="genre"
          />
        </div>
      </div>

      <!-- Journey Map Section -->
      <section class="mb-8">
        <h3 class="font-serif text-xl font-semibold text-text-primary mb-4">
          Journey Map
        </h3>
        <div class="bg-white rounded-2xl shadow-card p-4">
          <AuthorJourneyMap :locations="author.journeyLocations" />
        </div>
      </section>

      <!-- Books by this Author -->
      <section>
        <h3 class="font-serif text-xl font-semibold text-text-primary mb-4">
          Books by {{ author.name }}
        </h3>
        <div class="space-y-4">
          <BookCard
            v-for="book in author.books"
            :key="book.id"
            :book="book"
            @click="viewBook(book)"
          />
        </div>
      </section>
    </div>

    <LoadingSpinner v-else-if="loading" />

    <EmptyState
      v-else
      title="Author not found"
      description="This author may not have any books in our collection"
    />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ArrowLeft } from 'lucide-vue-next';
import BookCard from '@/components/BookCard.vue';
import GenreBadge from '@/components/GenreBadge.vue';
import AuthorJourneyMap from '@/components/AuthorJourneyMap.vue';
import LoadingSpinner from '@/components/LoadingSpinner.vue';
import EmptyState from '@/components/EmptyState.vue';
import { useAuthorsStore } from '@/stores/authors';

const route = useRoute();
const router = useRouter();
const authorsStore = useAuthorsStore();

const authorName = computed(() => decodeURIComponent(route.params.name));
const author = computed(() => authorsStore.getAuthorByName(authorName.value));
const loading = computed(() => authorsStore.isLoading);

function viewBook(book) {
  router.push({ name: 'book-detail', params: { id: book.id } });
}

onMounted(async () => {
  if (!author.value) {
    await authorsStore.fetchAuthorProfile(authorName.value);
  }
});
</script>
```

### 4.3 AuthorJourneyMap Component

**File**: `src/components/AuthorJourneyMap.vue` (new)

```vue
<template>
  <div class="relative w-full h-64 bg-parchment-100 rounded-lg overflow-hidden">
    <div ref="mapContainer" class="w-full h-full"></div>

    <!-- Info overlay -->
    <div class="absolute bottom-3 left-3 right-3 bg-white/90 backdrop-blur-sm px-3 py-2 rounded-lg text-xs text-text-secondary">
      {{ locations.length }} locations across {{ uniqueCountries }} countries
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';

const props = defineProps({
  locations: {
    type: Array,
    required: true
  }
});

const mapContainer = ref(null);
let map = null;
let markers = [];

const uniqueCountries = computed(() => {
  const countries = new Set(props.locations.map(loc => loc.country));
  return countries.size;
});

async function initMap() {
  if (!mapContainer.value || !window.google) return;

  // Create map
  const { Map } = await google.maps.importLibrary("maps");
  const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

  map = new Map(mapContainer.value, {
    zoom: 4,
    center: props.locations[0] || { lat: 40, lng: -3 },
    mapId: 'author-journey-map',
    disableDefaultUI: true,
    gestureHandling: 'greedy'
  });

  // Add markers for all locations
  markers = props.locations.map(location => {
    const marker = new AdvancedMarkerElement({
      map,
      position: { lat: location.lat, lng: location.lng },
      title: location.city || location.country
    });

    return marker;
  });

  // Fit bounds to show all markers
  if (props.locations.length > 0) {
    const bounds = new google.maps.LatLngBounds();
    props.locations.forEach(loc => {
      bounds.extend({ lat: loc.lat, lng: loc.lng });
    });
    map.fitBounds(bounds);
  }
}

onMounted(() => {
  initMap();
});

watch(() => props.locations, () => {
  if (map) {
    // Clear old markers
    markers.forEach(marker => marker.map = null);
    // Re-init map
    initMap();
  }
});
</script>
```

### 4.4 Update BookDetails Component

**File**: `src/components/BookDetails.vue`

Add click handler for author name:

```vue
<button
  class="text-lg text-text-secondary hover:text-teal-deep transition-colors underline"
  @click="$emit('view-author')"
>
  {{ book.author }}
</button>
```

Add emit:
```javascript
defineEmits(['close', 'view-author']);
```

### 4.5 Tasks Checklist

- [ ] Create `src/stores/authors.js`
- [ ] Create `src/views/AuthorProfileView.vue`
- [ ] Create `src/components/AuthorJourneyMap.vue`
- [ ] Update `BookDetails.vue` with author click handler
- [ ] Add author route to `router/index.js`
- [ ] Test author profile generation from books
- [ ] Test navigation from book → author → book
- [ ] Test journey map with multiple locations
- [ ] Verify stats calculation (book count, country count)

**Deliverable**: Author profile system with computed data and journey maps

---

## Phase 5: Personal Library (localStorage) (Weeks 7-8)

### Objectives
- Create library store with localStorage persistence
- Build LibraryView with tabs (Saved, Reading List)
- Add save/unsave functionality to BookDetails
- Sync library state across app

### 5.1 Library Store

**File**: `src/stores/library.js` (new)

```javascript
import { defineStore } from 'pinia';

export const useLibraryStore = defineStore('library', {
  state: () => ({
    savedBooks: [],
    readingList: [],
    isInitialized: false
  }),

  getters: {
    isBookSaved: (state) => (bookId) => {
      return state.savedBooks.some(book => book.id === bookId);
    },

    isBookInReadingList: (state) => (bookId) => {
      return state.readingList.some(book => book.id === bookId);
    },

    savedBooksCount(state) {
      return state.savedBooks.length;
    },

    readingListCount(state) {
      return state.readingList.length;
    },

    allLibraryBooks(state) {
      // Combine both lists, removing duplicates
      const allBooks = [...state.savedBooks, ...state.readingList];
      const uniqueBooks = allBooks.filter((book, index, self) =>
        index === self.findIndex(b => b.id === book.id)
      );
      return uniqueBooks;
    }
  },

  actions: {
    /**
     * Initialize from localStorage
     */
    init() {
      if (this.isInitialized) return;

      try {
        const savedData = localStorage.getItem('litmap-library');
        if (savedData) {
          const data = JSON.parse(savedData);
          this.savedBooks = data.savedBooks || [];
          this.readingList = data.readingList || [];
        }
      } catch (err) {
        console.error('Failed to load library from localStorage:', err);
      }

      this.isInitialized = true;
    },

    /**
     * Persist to localStorage
     */
    persist() {
      try {
        const data = {
          savedBooks: this.savedBooks,
          readingList: this.readingList,
          lastUpdated: new Date().toISOString()
        };
        localStorage.setItem('litmap-library', JSON.stringify(data));
      } catch (err) {
        console.error('Failed to save library to localStorage:', err);
      }
    },

    /**
     * Add book to Saved
     */
    addToSaved(book) {
      if (!this.isBookSaved(book.id)) {
        this.savedBooks.push({
          ...book,
          savedAt: new Date().toISOString()
        });
        this.persist();
      }
    },

    /**
     * Remove book from Saved
     */
    removeFromSaved(bookId) {
      this.savedBooks = this.savedBooks.filter(book => book.id !== bookId);
      this.persist();
    },

    /**
     * Toggle saved status
     */
    toggleSaved(book) {
      if (this.isBookSaved(book.id)) {
        this.removeFromSaved(book.id);
      } else {
        this.addToSaved(book);
      }
    },

    /**
     * Add book to Reading List
     */
    addToReadingList(book) {
      if (!this.isBookInReadingList(book.id)) {
        this.readingList.push({
          ...book,
          addedAt: new Date().toISOString()
        });
        this.persist();
      }
    },

    /**
     * Remove book from Reading List
     */
    removeFromReadingList(bookId) {
      this.readingList = this.readingList.filter(book => book.id !== bookId);
      this.persist();
    },

    /**
     * Toggle reading list status
     */
    toggleReadingList(book) {
      if (this.isBookInReadingList(book.id)) {
        this.removeFromReadingList(book.id);
      } else {
        this.addToReadingList(book);
      }
    },

    /**
     * Clear all library data
     */
    clearLibrary() {
      this.savedBooks = [];
      this.readingList = [];
      this.persist();
    },

    /**
     * Export library data (for future sync)
     */
    exportData() {
      return {
        savedBooks: this.savedBooks,
        readingList: this.readingList,
        exportedAt: new Date().toISOString()
      };
    },

    /**
     * Import library data (for future sync)
     */
    importData(data) {
      if (data.savedBooks) this.savedBooks = data.savedBooks;
      if (data.readingList) this.readingList = data.readingList;
      this.persist();
    }
  }
});
```

### 5.2 Initialize Library in App

**File**: `src/main.js`

```javascript
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import { useLibraryStore } from './stores/library';
import './styles/design-tokens.css';
import './index.css';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);

// Initialize library from localStorage
const libraryStore = useLibraryStore();
libraryStore.init();

app.mount('#app');
```

### 5.3 LibraryView Component

**File**: `src/views/LibraryView.vue` (new)

```vue
<template>
  <div class="min-h-screen bg-parchment-50 pb-20">
    <!-- Header -->
    <header class="bg-white border-b border-parchment-200 px-6 py-4">
      <div class="flex items-center justify-between mb-4">
        <h1 class="font-serif text-2xl font-semibold text-text-primary">
          My Library
        </h1>
        <div class="flex gap-2">
          <button class="p-2 hover:bg-parchment-100 rounded-full">
            <Search class="w-5 h-5 text-text-secondary" />
          </button>
          <button class="p-2 hover:bg-parchment-100 rounded-full">
            <Filter class="w-5 h-5 text-text-secondary" />
          </button>
        </div>
      </div>

      <!-- Tabs -->
      <div class="flex gap-1 bg-parchment-50 rounded-xl p-1">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2"
          :class="activeTab === tab.id
            ? 'bg-white text-text-primary shadow-sm'
            : 'text-text-secondary hover:text-text-primary'"
          @click="activeTab = tab.id"
        >
          <component :is="tab.icon" class="w-4 h-4" />
          <span>{{ tab.label }}</span>
        </button>
      </div>
    </header>

    <!-- Content -->
    <div class="px-4 py-6">
      <!-- Saved Tab -->
      <div v-if="activeTab === 'saved'">
        <div class="mb-4 text-sm text-text-secondary">
          {{ savedCount }} book{{ savedCount !== 1 ? 's' : '' }} saved
        </div>

        <div v-if="savedBooks.length > 0" class="space-y-4">
          <BookCard
            v-for="book in savedBooks"
            :key="book.id"
            :book="book"
            @click="viewBook(book)"
          />
        </div>

        <EmptyState
          v-else
          title="No saved books yet"
          description="Books you bookmark will appear here"
        />
      </div>

      <!-- Reading List Tab -->
      <div v-if="activeTab === 'reading-list'">
        <div class="mb-4 text-sm text-text-secondary">
          {{ readingListCount }} book{{ readingListCount !== 1 ? 's' : '' }} in reading list
        </div>

        <div v-if="readingListBooks.length > 0" class="space-y-4">
          <BookCard
            v-for="book in readingListBooks"
            :key="book.id"
            :book="book"
            @click="viewBook(book)"
          />
        </div>

        <EmptyState
          v-else
          title="Reading list is empty"
          description="Add books you want to read to your reading list"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { Search, Filter, BookmarkCheck, Heart } from 'lucide-vue-next';
import BookCard from '@/components/BookCard.vue';
import EmptyState from '@/components/EmptyState.vue';
import { useLibraryStore } from '@/stores/library';

const router = useRouter();
const libraryStore = useLibraryStore();

const activeTab = ref('saved');

const tabs = [
  { id: 'saved', label: 'Saved', icon: BookmarkCheck },
  { id: 'reading-list', label: 'Reading List', icon: Heart }
];

const savedBooks = computed(() => libraryStore.savedBooks);
const readingListBooks = computed(() => libraryStore.readingList);
const savedCount = computed(() => libraryStore.savedBooksCount);
const readingListCount = computed(() => libraryStore.readingListCount);

function viewBook(book) {
  router.push({ name: 'book-detail', params: { id: book.id } });
}
</script>
```

### 5.4 Update BookDetails Component

**File**: `src/components/BookDetails.vue`

Add library integration:

```vue
<script setup>
import { computed } from 'vue';
import { useLibraryStore } from '@/stores/library';

const libraryStore = useLibraryStore();

const props = defineProps({
  book: {
    type: Object,
    required: true
  }
});

const isInLibrary = computed(() => libraryStore.isBookSaved(props.book.id));
const isInReadingList = computed(() => libraryStore.isBookInReadingList(props.book.id));

function toggleLibrary() {
  libraryStore.toggleSaved(props.book);
}

function addToLibrary() {
  if (!isInLibrary.value) {
    libraryStore.addToSaved(props.book);
  }
}
</script>

<template>
  <!-- ... existing template ... -->

  <!-- Update Bookmark button in header -->
  <button
    class="p-2 hover:bg-parchment-200 rounded-full"
    @click="toggleLibrary"
  >
    <Bookmark
      class="w-5 h-5"
      :class="isInLibrary ? 'fill-copper-warm text-copper-warm' : 'text-text-secondary'"
    />
  </button>

  <!-- ... rest of template ... -->
</template>
```

### 5.5 Library Action Menu

**File**: `src/components/LibraryActionMenu.vue` (new)

Optional: Add long-press menu for more library options:

```vue
<template>
  <div class="flex gap-2">
    <button
      class="flex-1 py-3 px-4 rounded-xl border-2 transition-all"
      :class="isInSaved
        ? 'border-teal-deep bg-teal-deep/10 text-teal-deep'
        : 'border-parchment-200 text-text-secondary hover:border-teal-deep'"
      @click="toggleSaved"
    >
      <BookmarkCheck class="w-5 h-5 mx-auto mb-1" />
      <span class="text-xs">{{ isInSaved ? 'Saved' : 'Save' }}</span>
    </button>

    <button
      class="flex-1 py-3 px-4 rounded-xl border-2 transition-all"
      :class="isInReadingList
        ? 'border-copper-warm bg-copper-warm/10 text-copper-warm'
        : 'border-parchment-200 text-text-secondary hover:border-copper-warm'"
      @click="toggleReadingList"
    >
      <Heart class="w-5 h-5 mx-auto mb-1" />
      <span class="text-xs">{{ isInReadingList ? 'In List' : 'Add to List' }}</span>
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { BookmarkCheck, Heart } from 'lucide-vue-next';
import { useLibraryStore } from '@/stores/library';

const props = defineProps({
  book: {
    type: Object,
    required: true
  }
});

const libraryStore = useLibraryStore();

const isInSaved = computed(() => libraryStore.isBookSaved(props.book.id));
const isInReadingList = computed(() => libraryStore.isBookInReadingList(props.book.id));

function toggleSaved() {
  libraryStore.toggleSaved(props.book);
}

function toggleReadingList() {
  libraryStore.toggleReadingList(props.book);
}
</script>
```

Use in BookDetails:

```vue
<!-- Replace single "Add to Library" button with -->
<div class="px-6 mb-8">
  <LibraryActionMenu :book="book" />
</div>
```

### 5.6 Tasks Checklist

- [ ] Create `src/stores/library.js`
- [ ] Update `main.js` to initialize library
- [ ] Create `src/views/LibraryView.vue`
- [ ] Create `src/components/LibraryActionMenu.vue`
- [ ] Update `BookDetails.vue` with library integration
- [ ] Add library route to router
- [ ] Test save/unsave functionality
- [ ] Test localStorage persistence (refresh page)
- [ ] Test both tabs (Saved, Reading List)
- [ ] Test empty states
- [ ] Test navigation to book details from library

**Deliverable**: Fully functional personal library with localStorage persistence

---

## Phase 6: Polish & Testing (Weeks 9-10)

### Objectives
- Cross-browser testing
- Mobile device testing
- Performance optimization
- Accessibility improvements
- Bug fixes and refinements

### 6.1 Performance Optimization

#### Image Loading
- Add lazy loading for book covers
- Implement loading placeholders
- Optimize image sizes

#### Code Splitting
```javascript
// router/index.js
const routes = [
  {
    path: '/',
    name: 'map',
    component: () => import('@/views/MapView.vue')
  },
  {
    path: '/list',
    name: 'list',
    component: () => import('@/views/ListView.vue')
  },
  // ... etc
];
```

#### Firestore Optimization
- Add pagination for book list (50 per page)
- Implement incremental loading
- Cache frequently accessed data

### 6.2 Accessibility

**ARIA Labels**:
- Add proper labels to all buttons
- Add role attributes to interactive elements
- Add alt text to images

**Keyboard Navigation**:
- Ensure tab order is logical
- Add keyboard shortcuts (optional)
- Test all interactions with keyboard only

**Color Contrast**:
- Verify all text meets WCAG AA standards
- Test in high contrast mode
- Ensure color is not the only indicator

**Screen Reader Testing**:
- Test with VoiceOver (iOS)
- Test with TalkBack (Android)
- Add skip navigation links

### 6.3 Mobile Testing Checklist

**Devices to Test**:
- [ ] iPhone SE (small screen)
- [ ] iPhone 14 Pro (notch)
- [ ] iPhone 14 Pro Max (large screen)
- [ ] Samsung Galaxy S22 (Android)
- [ ] iPad (tablet view)

**Features to Test**:
- [ ] Touch interactions (tap, swipe, pinch)
- [ ] Safe areas (notches, home indicators)
- [ ] Bottom sheet swipe gestures
- [ ] Map interactions (pan, zoom, marker tap)
- [ ] Navigation between views
- [ ] Search drawer open/close
- [ ] Library save/unsave
- [ ] Author profile navigation
- [ ] Back button behavior
- [ ] Landscape orientation

### 6.4 Browser Testing Checklist

**Browsers**:
- [ ] Chrome (latest)
- [ ] Safari (iOS 15+)
- [ ] Firefox (latest)
- [ ] Edge (latest)
- [ ] Samsung Internet

**Features to Test**:
- [ ] localStorage (private mode)
- [ ] Google Maps loading
- [ ] CSS Grid/Flexbox layouts
- [ ] Backdrop blur effects
- [ ] Custom fonts loading
- [ ] Touch events

### 6.5 Bug Fixes & Refinements

**Common Issues**:
1. **Bottom sheet overlapping bottom nav**: Adjust z-index
2. **Map markers not updating**: Force re-render on data change
3. **localStorage quota exceeded**: Add error handling
4. **Search not filtering correctly**: Debug filter logic
5. **Author profile showing duplicate books**: Fix aggregation logic
6. **iOS safe area issues**: Add proper padding classes

### 6.6 Documentation Updates

Update files:
- [ ] `README.md` - New features and architecture
- [ ] `CLAUDE.md` - Updated project structure
- [ ] Add inline code comments for complex logic
- [ ] Document localStorage schema
- [ ] Document Pinia store structure

### 6.7 Deployment Checklist

**GitHub Pages**:
- [ ] Update `vite.config.js` base path
- [ ] Build production version: `npm run build`
- [ ] Test production build locally: `npm run preview`
- [ ] Deploy to GitHub Pages
- [ ] Verify all routes work with SPA fallback
- [ ] Check Google Maps API key permissions
- [ ] Verify Firebase config in production

**Environment Variables**:
```javascript
// .env.production
VITE_GOOGLE_MAPS_API_KEY=your_key_here
VITE_FIREBASE_API_KEY=your_key_here
VITE_FIREBASE_PROJECT_ID=litmap-88358
```

### 6.8 Final Tasks Checklist

- [ ] Run full test suite on all target devices
- [ ] Fix all critical bugs
- [ ] Verify accessibility with automated tools
- [ ] Optimize bundle size (check with `vite build --report`)
- [ ] Update documentation
- [ ] Create deployment build
- [ ] Deploy to production
- [ ] Monitor for errors (console logs)
- [ ] Gather user feedback

**Deliverable**: Production-ready application deployed to GitHub Pages

---

## Component Migration Matrix

### Existing Components (Restyle)

| Component | File | Changes Required | Priority | Complexity |
|-----------|------|-----------------|----------|------------|
| App.vue | `src/App.vue` | Add router-view, bottom nav, paper texture | High | Medium |
| TopBar.vue | `src/components/TopBar.vue` | Serif logo, remove hamburger, update colors | High | Low |
| GoogleMapComponent.vue | `src/components/GoogleMapComponent.vue` | Info overlay, genre colors, labeled pins | High | Medium |
| BookCard.vue | `src/components/BookCard.vue` | New card style, genre badges, hover effects | High | Low |
| BookDetails.vue | `src/components/BookDetails.vue` | Sections, mini map, library buttons | High | Medium |
| BottomSheet.vue | `src/components/BottomSheet.vue` | Update styling, drag handle | Medium | Low |
| FAB.vue | `src/components/FAB.vue` | Add second FAB, update styling | Medium | Low |
| LoadingSpinner.vue | `src/components/LoadingSpinner.vue` | Update colors to match theme | Low | Low |

### New Shared Components

| Component | File | Purpose | Priority | Complexity |
|-----------|------|---------|----------|------------|
| BottomNavigation | `src/components/BottomNavigation.vue` | 4-tab navigation | High | Low |
| FilterChip | `src/components/FilterChip.vue` | Filter buttons | High | Low |
| GenreBadge | `src/components/GenreBadge.vue` | Genre pills | High | Low |
| EmptyState | `src/components/EmptyState.vue` | Empty view placeholder | Medium | Low |
| SearchDrawer | `src/components/SearchDrawer.vue` | Bottom sheet search | High | Medium |
| ClusterToggle | `src/components/ClusterToggle.vue` | Map clustering toggle | Medium | Low |
| AuthorJourneyMap | `src/components/AuthorJourneyMap.vue` | Mini map for author | Medium | Medium |
| LibraryActionMenu | `src/components/LibraryActionMenu.vue` | Save/reading list buttons | Medium | Low |

### New View Components

| Component | File | Purpose | Priority | Complexity |
|-----------|------|---------|----------|------------|
| MapView | `src/views/MapView.vue` | Main map page | High | Low |
| ListView | `src/views/ListView.vue` | Book list page | High | Low |
| BookDetailView | `src/views/BookDetailView.vue` | Full-page book details | High | Low |
| AuthorProfileView | `src/views/AuthorProfileView.vue` | Author profile page | High | Medium |
| LibraryView | `src/views/LibraryView.vue` | Personal library page | High | Medium |
| ContributeView | `src/views/ContributeView.vue` | Submission form (stub) | Low | Low |

### Components to Remove

| Component | File | Reason |
|-----------|------|--------|
| HamburgerMenu.vue | `src/components/HamburgerMenu.vue` | Settings simplified |
| SearchTypeSelector.vue | `src/components/SearchTypeSelector.vue` | Replaced by SearchDrawer |
| MapControls.vue | `src/components/MapControls.vue` | Not in Figma design |

---

## Design System Specifications

### Color Palette

```css
/* Primary Colors */
--teal-deep: #3D6960;        /* Primary actions, buttons, active states */
--copper-warm: #C17A3A;      /* Accent color, secondary actions */

/* Backgrounds */
--parchment-50: #F5F1E8;     /* Light background */
--parchment-100: #E8E3D8;    /* Medium background */
--parchment-200: #E0D9C8;    /* Borders */
--parchment-300: #D5CFC0;    /* Darker background */

/* Text Colors */
--text-primary: #2D3E3C;     /* Headings, primary text */
--text-secondary: #6B7C7A;   /* Body text, metadata */
--text-tertiary: #9CA5A3;    /* Placeholders, disabled */

/* Genre Colors */
--genre-memoir: #8B5A8E;     /* Purple */
--genre-adventure: #C17A3A;  /* Orange/Copper */
--genre-historical: #A67C52; /* Brown */
--genre-travel: #3D6960;     /* Teal */
```

### Typography Scale

```css
/* Font Families */
--font-serif: Georgia, 'Libre Baskerville', serif;
--font-sans: system-ui, -apple-system, sans-serif;

/* Sizes */
--text-xs: 0.75rem;      /* 12px - Metadata, labels */
--text-sm: 0.875rem;     /* 14px - Body text, descriptions */
--text-base: 1rem;       /* 16px - Default body */
--text-lg: 1.125rem;     /* 18px - Author names */
--text-xl: 1.25rem;      /* 20px - Section headings */
--text-2xl: 1.5rem;      /* 24px - Page titles */
--text-3xl: 1.875rem;    /* 30px - Hero text */

/* Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;

/* Line Heights */
--leading-tight: 1.25;   /* Headings */
--leading-normal: 1.5;   /* Body text */
--leading-relaxed: 1.625; /* Descriptions */
```

### Spacing System

```css
/* Spacing Scale (Tailwind-based) */
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px - Bottom nav height */
```

### Border Radius

```css
--radius-sm: 8px;     /* Small elements */
--radius-md: 12px;    /* Buttons, chips */
--radius-lg: 16px;    /* Cards */
--radius-xl: 20px;    /* Large cards */
--radius-2xl: 24px;   /* Drawers, modals */
--radius-full: 9999px; /* FABs, avatars */
```

### Shadows

```css
/* Elevation Levels */
--shadow-card: 0 2px 8px rgba(45, 62, 60, 0.1);
--shadow-elevated: 0 4px 16px rgba(45, 62, 60, 0.15);
--shadow-fab: 0 6px 20px rgba(45, 62, 60, 0.2);
--shadow-modal: 0 8px 32px rgba(45, 62, 60, 0.25);
```

### Transitions

```css
/* Duration */
--duration-fast: 150ms;
--duration-normal: 250ms;
--duration-slow: 350ms;

/* Easing */
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in: cubic-bezier(0.4, 0, 1, 1);
```

---

## Technical Debt & Future Enhancements

### Deferred Features

1. **User Authentication**
   - Firebase Auth integration
   - Google Sign-In
   - Email/password auth
   - Profile management
   - **Timing**: Post-launch, Phase 7

2. **Cloud Library Sync**
   - Migrate from localStorage to Firestore
   - Cross-device sync
   - Conflict resolution
   - **Timing**: After authentication

3. **User Contributions**
   - Book submission form (exists as stub)
   - Image upload to Cloud Storage
   - Moderation dashboard
   - Admin approval workflow
   - **Timing**: Phase 8 (2-3 weeks)

4. **Advanced Filtering**
   - Timeline slider for publication year
   - Multi-dimensional filters
   - Filter combinations
   - Save filter presets
   - **Timing**: Phase 9 (1-2 weeks)

5. **Social Features**
   - Share book links
   - Share reading lists
   - User profiles (public)
   - Follow other users
   - **Timing**: Future (3-4 weeks)

6. **Analytics**
   - Track popular books
   - Track search queries
   - User engagement metrics
   - Firebase Analytics integration
   - **Timing**: Post-launch

### Known Limitations

1. **Author Data**: Computed from books only, no external bio source
2. **Library Storage**: Device-local only (localStorage)
3. **Search**: Basic text matching, no fuzzy search or typo tolerance
4. **Map Pins**: Color-coded by genre but limited customization
5. **Offline Support**: No PWA or service worker implementation
6. **Performance**: No pagination on book list (all books loaded)

### Potential Improvements

1. **PWA Support**: Add service worker for offline access
2. **Enhanced Search**: Implement Algolia or Meilisearch
3. **Book Recommendations**: ML-based suggestions
4. **Reading Progress**: Track pages read, reading speed
5. **Notes & Highlights**: Add annotation features
6. **Reading Challenges**: Gamification (e.g., "Read 12 countries in 2025")
7. **Export Options**: Export library as CSV/JSON
8. **Dark Mode**: Toggle between light/dark themes
9. **Multi-language**: i18n support
10. **Accessibility**: Enhanced screen reader support

---

## Risk Assessment

### High Risk

**Risk**: Google Maps API quota exceeded
**Impact**: Map doesn't load, core functionality broken
**Mitigation**:
- Monitor API usage in Google Cloud Console
- Set up billing alerts
- Implement map caching
- Consider alternative map providers as fallback

**Risk**: localStorage quota exceeded (typically 5-10MB)
**Impact**: Library saves fail silently
**Mitigation**:
- Implement quota checking before save
- Show user warning when approaching limit
- Provide export/clear library options
- Plan migration to cloud storage

**Risk**: Firestore read quotas exceeded
**Impact**: Books fail to load
**Mitigation**:
- Implement aggressive caching
- Reduce unnecessary queries
- Add pagination
- Monitor Firestore usage

### Medium Risk

**Risk**: Browser compatibility issues (especially Safari)
**Impact**: Visual glitches, broken features
**Mitigation**:
- Test on Safari early and often
- Use Autoprefixer for CSS
- Avoid bleeding-edge CSS features
- Provide fallbacks

**Risk**: Performance issues on older devices
**Impact**: Slow loading, janky animations
**Mitigation**:
- Code splitting and lazy loading
- Optimize images and assets
- Test on low-end devices
- Consider reduced motion mode

**Risk**: Author name inconsistencies
**Impact**: Duplicate author profiles
**Mitigation**:
- Normalize author names (trim, lowercase)
- Handle "Last, First" vs "First Last" formats
- Consider fuzzy matching
- Manual deduplication if needed

### Low Risk

**Risk**: Design not matching Figma exactly
**Impact**: Visual inconsistencies
**Mitigation**:
- Regular design reviews
- Reference Figma during development
- Get user feedback early

**Risk**: Missing book cover images
**Impact**: Ugly placeholder colors
**Mitigation**:
- Design attractive mock covers
- Add texture/patterns to placeholders
- Consider fetching covers from OpenLibrary API

---

## Success Metrics

### User Experience

- [ ] All pages load in < 2 seconds on 4G
- [ ] Touch targets minimum 44x44px
- [ ] No console errors in production
- [ ] Lighthouse score > 90 (Performance, Accessibility)
- [ ] Works on iOS Safari, Chrome, Firefox
- [ ] No layout shift (CLS < 0.1)

### Feature Completeness

- [ ] All 7 Figma screens implemented
- [ ] Bottom navigation functional
- [ ] Search with filters working
- [ ] Author profiles generating correctly
- [ ] Library save/unsave functional
- [ ] localStorage persistence working
- [ ] Map markers color-coded by genre

### Code Quality

- [ ] No linting errors
- [ ] All components have proper props validation
- [ ] Stores follow consistent patterns
- [ ] Router setup clean and logical
- [ ] CSS follows design system
- [ ] No duplicate code

---

## Rollback Plan

If critical issues arise post-deployment:

1. **Keep old version**: Tag current production as `v1-stable`
2. **Feature flags**: Use environment variables to toggle new features
3. **Gradual rollout**: Deploy to subset of users first (if possible)
4. **Quick revert**: `git revert` or restore old GitHub Pages build
5. **Communication**: Notify users of known issues

**Critical Issues** (require immediate rollback):
- Map not loading
- All books fail to load
- Library data loss
- App completely broken on iOS

**Non-Critical Issues** (can be fixed in place):
- Visual glitches
- Author profile errors
- Search not finding all results
- Minor layout issues

---

## Timeline Summary

| Week | Phase | Focus | Deliverable |
|------|-------|-------|-------------|
| 1 | Phase 1 | Design System | Tailwind config, design tokens, 3 base components |
| 2 | Phase 2a | Core UI (Part 1) | App structure, TopBar, Map, BookCard restyled |
| 3 | Phase 2b | Core UI (Part 2) | BookDetails, FAB, Settings removal, BottomSheet |
| 4 | Phase 3 | New Views | Router, ListView, SearchDrawer, BookDetailView |
| 5 | Phase 4a | Author System (Part 1) | Author store, profile computation |
| 6 | Phase 4b | Author System (Part 2) | AuthorProfileView, journey maps |
| 7 | Phase 5a | Library (Part 1) | Library store, localStorage persistence |
| 8 | Phase 5b | Library (Part 2) | LibraryView, save/unsave integration |
| 9 | Phase 6a | Polish (Part 1) | Testing, bug fixes, accessibility |
| 10 | Phase 6b | Polish (Part 2) | Performance, deployment, documentation |

**Total**: 10 weeks (can be compressed to 8 weeks if resources allow)

---

## Getting Help

### Resources

- **Vue 3 Docs**: https://vuejs.org/guide/
- **Pinia Docs**: https://pinia.vuejs.org/
- **Tailwind CSS**: https://tailwindcss.com/docs
- **Google Maps JS API**: https://developers.google.com/maps/documentation/javascript
- **Material Design**: https://m3.material.io/

### Common Issues

**Q: Map not loading?**
A: Check Google Maps API key, check console for errors, verify API is enabled in Google Cloud Console

**Q: localStorage not persisting?**
A: Check browser private mode, check quota, verify library.init() is called

**Q: Author profile empty?**
A: Verify author name matches exactly in books, check aggregation logic, verify books store has data

**Q: Bottom nav overlapping content?**
A: Add `pb-20` class to main content wrapper

**Q: Figma colors don't match?**
A: Double-check Tailwind config colors, verify hex codes, check for opacity/alpha values

---

## Conclusion

This migration plan transforms LitMap from a functional map-based book discovery app into a polished, literary-themed platform with author profiles and personal library features. The phased approach allows for incremental delivery and testing while maintaining a working application throughout the process.

**Key Success Factors**:
1. Strict adherence to the design system
2. Thorough testing on mobile devices
3. Careful attention to performance
4. Clear component boundaries and reusability
5. Consistent state management patterns

**Next Steps**:
1. Review and approve this plan
2. Set up project milestones in GitHub
3. Begin Phase 1 (Design System Foundation)
4. Schedule weekly progress reviews
5. Gather user feedback at Phase 2 and Phase 5 completions

Good luck with the migration! 🎉📚🗺️
