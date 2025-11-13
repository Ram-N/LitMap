# Migrating LitMap to Mobile-First Vue 3

This document tracks the migration of LitMap from vanilla JavaScript to a modern, mobile-first Vue 3 application.

## Overview

**Migration Goal**: Transform LitMap into a mobile-first, Progressive Web App using Vue 3, maintaining all existing features while optimizing for touch interactions and small screens.

**Tech Stack**:
- Vue 3 (Composition API)
- Vite (build tool)
- Tailwind CSS (utility-first styling)
- Pinia (state management)
- vue3-google-map (Google Maps integration)
- Firebase/Firestore (existing database)

## Migration Strategy

The migration is being done in phases, with the new Vue app living in `/vue-app` directory alongside the existing vanilla JS app. Once complete and tested, the Vue build will replace the root files.

---

## Phase 1: Foundation Setup ✅ COMPLETE

### Project Structure Created

```
vue-app/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── TopBar.vue          # Nav with logo, menu, search
│   │   │   ├── HamburgerMenu.vue   # Slide-out sidebar
│   │   │   └── BottomSheet.vue     # Swipeable drawer
│   │   ├── search/
│   │   │   ├── SearchBar.vue       # Expandable search
│   │   │   ├── SearchTypeSelector.vue
│   │   │   ├── BookCard.vue        # Search result card
│   │   │   └── BookDetails.vue     # Full book details
│   │   └── shared/
│   │       ├── FAB.vue             # Floating action button
│   │       └── Toggle.vue          # Reusable toggle switch
│   ├── composables/
│   │   └── useSearch.js            # Search logic composable
│   ├── stores/
│   │   ├── books.js                # Book data state (Pinia)
│   │   └── ui.js                   # UI state (Pinia)
│   ├── App.vue                     # Root component
│   ├── main.js                     # Entry point
│   └── style.css                   # Tailwind imports
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── .env.example
```

### Configuration Files

**package.json**: Dependencies installed
- Vue 3.4.21
- Pinia 2.1.7
- Firebase 10.13.1
- vue3-google-map 0.20.0
- Tailwind CSS 3.4.1
- lucide-vue-next (icons)
- @vueuse/core (utilities)

**tailwind.config.js**: Custom configuration
- Mobile-first breakpoints
- Primary color palette (blues)
- Custom heights (90vh, 95vh for fullscreen map)
- Touch-target minimum sizes (44px)

**vite.config.js**: Build configuration
- Vue plugin enabled
- Path aliases (@/ → src/)
- Dev server on port 5173

### State Management

**Pinia Stores Created**:

1. **books.js** (Book Data Store)
   - `allBooks`: Array of all books from Firestore
   - `currentCollection`: Selected collection ('books', 'small_books', 'newbooks')
   - `isLoading`: Loading state
   - `booksWithLocations`: Computed getter for mappable books

2. **ui.js** (UI State Store)
   - `isMenuOpen`: Hamburger menu state
   - `bottomSheetState`: 'hidden' | 'half' | 'full'
   - `bottomSheetContent`: 'search-results' | 'book-details'
   - `selectedBook`: Currently viewed book
   - `highlightedMarkerId`: Active map marker
   - `isClusteringEnabled`: Marker clustering toggle
   - `searchQuery`, `searchField`, `searchResults`: Search state
   - `mapCenter`, `mapZoom`, `mapType`: Map state

### Components Built

**Layout Components**:

1. **TopBar.vue**: Fixed top navigation
   - Hamburger menu button (left)
   - LitMap logo/title (center)
   - Search button (right)
   - Safe area insets for notched devices

2. **HamburgerMenu.vue**: Slide-out sidebar
   - Collection selector (3 radio options)
   - Clustering toggle
   - Map type selector (roadmap/satellite/hybrid/terrain)
   - About section
   - Slide animation from left
   - Overlay backdrop

3. **BottomSheet.vue**: Swipeable drawer
   - Three states: hidden, half (50vh), full (85vh)
   - Swipe gestures: down to collapse, up to expand
   - Drag handle at top
   - Content: search results or book details
   - Smooth transitions

**Search Components**:

1. **SearchBar.vue**: Expandable search interface
   - Collapsed: Search icon button
   - Expanded: Full-screen search form
   - Search type selector (Title/Author/Location/Keyword/Any)
   - Enter key support

2. **SearchTypeSelector.vue**: Radio button group
   - 5 options styled as pill buttons
   - Active state highlighting
   - Touch-friendly sizing

3. **BookCard.vue**: Compact book display
   - Book cover from OpenLibrary API
   - Fallback: colored square with initials
   - Title, author, book type
   - Location preview (first + count)
   - Click to view details

4. **BookDetails.vue**: Full book information
   - Large cover image
   - Complete description
   - All locations listed
   - Tags/genre chips
   - "View on Goodreads" button

**Shared Components**:

1. **FAB.vue**: Floating Action Button
   - Circular button (56px)
   - Dynamic Lucide icon
   - Shadow and hover effects
   - Used for "Random Location" feature

2. **Toggle.vue**: Reusable toggle switch
   - iOS-style switch animation
   - Optional label and description
   - Used for clustering toggle

### Composables

**useSearch.js**: Search functionality
- `performSearch(query, field)`: Main search function
- Fuzzy matching across multiple fields
- Field-specific search logic:
  - Title/Author: Direct text matching
  - Location: Searches city, state, country, place
  - Keyword: Searches genre and tags
  - Any: Searches all fields
- Updates UI store with results
- Triggers bottom sheet display

### Mobile-First Design Decisions

1. **Touch Targets**: Minimum 44px for all interactive elements
2. **Safe Areas**: CSS env() variables for notched devices
3. **Viewport**: Fixed height (100vh) to prevent scroll
4. **Gestures**: Swipe support on bottom sheet
5. **Transitions**: Smooth animations (300ms cubic-bezier)
6. **Typography**: Responsive font sizes (text-xl on mobile, text-2xl on desktop)

### Custom Tailwind Utilities

```css
.touch-target: min-h-touch min-w-[44px]
.safe-top: padding-top: env(safe-area-inset-top)
.safe-bottom: padding-bottom: env(safe-area-inset-bottom)
```

---

## Phase 2: Firebase Integration ✅ COMPLETE

### Completed Tasks

- [x] Create Firebase configuration utility (utils/firebase.js)
- [x] Create useFirebase composable
- [x] Implement getAllBooks() from Firestore
- [x] Implement collection switching
- [x] Set up caching strategy
- [x] Handle loading and error states
- [x] Port fuzzy search logic from original firebase.js

### Files Created
- `utils/firebase.js` - Firebase initialization
- `composables/useFirebase.js` - Data fetching operations
- `composables/useSearch.js` - Search with fuzzy matching
- `.env` - Environment variables for API keys

---

## Phase 3: Google Maps Core ✅ COMPLETE

### Completed Tasks

- [x] Install and configure vue3-google-map
- [x] Create GoogleMap.vue component
- [x] Initialize map with terrain view
- [x] Create MapControls.vue component
- [x] Add preset locations (30+ cities/regions)
- [x] Implement geocoding for manual search
- [x] Port map initialization from map.js
- [x] Add random location feature

### Files Created
- `components/map/GoogleMap.vue` - Main map component
- `components/map/MapControls.vue` - Location/zoom controls
- `composables/useMap.js` - Map operations
- `utils/mapLocations.js` - Preset locations data
- `utils/colors.js` - Color generation utilities

---

## Phase 4: Marker System ✅ COMPLETE

### Completed Tasks

- [x] Create BookMarker.vue component
- [x] Implement title initials generation
- [x] Add color hashing for books
- [x] Build marker content (two states: pin/expanded)
- [x] Add click/hover interactions
- [x] Implement InfoWindow tooltips
- [x] Create MarkerCluster component
- [x] Connect clustering toggle to UI
- [x] Add loading spinner component
- [x] Implement error states

### Files Created
- `components/map/BookMarker.vue` - Individual marker with two states
- `components/map/MarkerCluster.vue` - Clustering wrapper
- `components/shared/LoadingSpinner.vue` - Loading indicator

---

## Phase 5: Search Integration (Pending)

### Tasks

- [ ] Connect search composable to Firebase data
- [ ] Test fuzzy matching with real data
- [ ] Implement search results display in BottomSheet
- [ ] Add "Clear" functionality
- [ ] Test all search fields (title, author, location, keyword, any)

---

## Phase 6: Mobile UX Polish (Pending)

### Tasks

- [ ] Test swipe gestures on iOS and Android
- [ ] Verify touch target sizes
- [ ] Test on various screen sizes
- [ ] Add loading skeletons
- [ ] Implement error states
- [ ] Add empty states

---

## Phase 7: Advanced Features (Pending)

### Tasks

- [ ] Random Location FAB functionality
- [ ] Collection switching with data reload
- [ ] Map type switching
- [ ] Goodreads link integration
- [ ] OpenLibrary cover fallbacks
- [ ] Auto-zoom to fit search results

---

## Phase 8: Optimization & Testing (Pending)

### Tasks

- [ ] Add lazy loading for book cards
- [ ] Implement virtual scrolling if needed
- [ ] Debounce search input
- [ ] Optimize marker rendering
- [ ] Test cross-browser compatibility
- [ ] Add meta tags for SEO
- [ ] Test on physical devices

---

## Phase 9: Deployment (Pending)

### Tasks

- [ ] Create .env file with API keys
- [ ] Test production build
- [ ] Configure Vercel deployment
- [ ] Set up environment variables on Vercel
- [ ] Deploy and test live
- [ ] Update documentation

---

## Key Differences from Original App

### Architecture Changes

| Original (Vanilla JS) | New (Vue 3) |
|----------------------|-------------|
| Module-based (3 files) | Component-based (20+ components) |
| Global state (window.books) | Pinia stores (centralized) |
| CustomEvents | Props/Emit + Pinia |
| Manual DOM manipulation | Vue reactivity |
| No build system | Vite build |

### UX Improvements

| Original | New (Mobile-First) |
|----------|-------------------|
| Desktop sidebar (15% width) | Hamburger slide-out menu |
| Split view (cards + map) | Bottom sheet over map |
| Button navigation | Touch gestures |
| Fixed layout | Responsive with safe areas |
| Desktop-first | Mobile-first |

### State Management

**Before**: Global variables + event system
```js
window.books = []
document.dispatchEvent(new CustomEvent('booksReady'))
```

**After**: Reactive Pinia stores
```js
const booksStore = useBooksStore()
booksStore.setBooks(books)
// Components automatically react
```

---

## Running the Project

### Development

```bash
cd vue-app
npm install
npm run dev
# Open http://localhost:5173
```

### Environment Setup

1. Copy `.env.example` to `.env`
2. Add Firebase config from existing app
3. Add Google Maps API key

### Building for Production

```bash
npm run build
npm run preview  # Test production build locally
```

---

## Testing Checklist

### Mobile Devices
- [ ] iPhone 12+ (Safari)
- [ ] iPhone SE (small screen)
- [ ] Android (Chrome)
- [ ] iPad (tablet size)

### Features to Test
- [ ] Search (all field types)
- [ ] Map markers (click, hover)
- [ ] Clustering toggle
- [ ] Bottom sheet (swipe gestures)
- [ ] Hamburger menu
- [ ] Collection switching
- [ ] Random location
- [ ] Goodreads links
- [ ] Image loading/fallbacks

### Browser Compatibility
- [ ] Chrome (desktop & mobile)
- [ ] Safari (desktop & mobile)
- [ ] Firefox
- [ ] Edge

---

## Migration Progress

**Phase 1**: ✅ Complete (Foundation)
**Phase 2**: ✅ Complete (Firebase)
**Phase 3**: ✅ Complete (Google Maps)
**Phase 4**: ✅ Complete (Markers & Clustering)
**Phase 5**: 🔄 In Progress (Testing & Refinement)
**Phases 6-9**: ⏳ Pending

**Overall**: ~44% complete (4 of 9 phases)

---

## Notes

- Original app remains functional in root directory
- Both apps can coexist during development
- Database/Streamlit admin untouched (still Python)
- Vue app will replace root files when complete
- Mobile-first approach may require UX adjustments based on user testing

---

**Last Updated**: 2025-01-08
**Next Steps**: Test all features and refine mobile UX (Phase 5-6)

---

## What's Working Now

### ✅ Fully Functional
1. **Firebase Integration** - Loading books from all collections
2. **Google Maps** - Full map with terrain view, controls
3. **Book Markers** - Color-coded markers with initials
4. **Search** - Fuzzy search across all fields
5. **Collection Switching** - Switch between newbooks/books/small_books
6. **Location Navigation** - Dropdown + manual geocoding + random location
7. **Map Controls** - Zoom, map type, location selector
8. **Hamburger Menu** - Settings, collection selector, clustering toggle
9. **Bottom Sheet** - Swipeable drawer for search results and book details
10. **Loading States** - Spinner during data fetch

### 🚧 Needs Testing
- Marker clustering (component created, needs live testing)
- Bottom sheet swipe gestures
- Mobile touch interactions
- Search result display in bottom sheet
- Book details view
- Goodreads links from markers

### ⏳ Not Yet Implemented
- Virtual scrolling for large result sets
- Offline support / PWA features
- Performance optimization
- Production build and deployment
