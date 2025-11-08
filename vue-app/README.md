# LitMap Vue - Mobile-First Literary Map

A modern, mobile-first reimagining of LitMap built with Vue 3, optimized for touch interactions and small screens.

## Tech Stack

- **Vue 3** - Composition API with `<script setup>`
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **Pinia** - State management
- **Firebase/Firestore** - Database
- **vue3-google-map** - Google Maps integration (coming soon)
- **Lucide Vue** - Icon library

## Getting Started

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update with your API keys:

```bash
cp .env.example .env
```

The Firebase config is already populated from the existing LitMap app. You'll need to add your Google Maps API key:

```env
VITE_GOOGLE_MAPS_API_KEY=your_actual_api_key_here
```

### 3. Run Development Server

```bash
npm run dev
```

The app will open at `http://localhost:5173`

### 4. Build for Production

```bash
npm run build
npm run preview  # Test production build locally
```

## Project Structure

```
src/
├── components/
│   ├── layout/         # TopBar, HamburgerMenu, BottomSheet
│   ├── map/           # GoogleMap, BookMarker, MapControls
│   ├── search/        # SearchBar, BookCard, BookDetails
│   └── shared/        # Reusable components (FAB, Toggle)
├── composables/       # Composable functions (useFirebase, useSearch)
├── stores/            # Pinia stores (books, ui)
├── utils/             # Utilities (firebase config)
├── App.vue           # Root component
├── main.js           # Entry point
└── style.css         # Tailwind imports + custom CSS
```

## Features Implemented

### ✅ Phase 1: Foundation
- Vue 3 + Vite project setup
- Tailwind CSS with mobile-first config
- Pinia stores (books, ui)
- Base layout components

### ✅ Phase 2: Firebase Integration
- Firebase configuration with environment variables
- `useFirebase` composable for data operations
- Book fetching and caching
- Collection switching (newbooks, books, small_books)
- Search functionality with fuzzy matching

### 🚧 Phase 3: Google Maps (In Progress)
- Map initialization
- Book markers
- Clustering
- Map controls

## Mobile-First Design

### Touch Targets
All interactive elements meet the minimum 44px touch target size.

### Safe Areas
The app respects iOS safe areas (notches, home indicators):
```css
.safe-top    /* padding-top: env(safe-area-inset-top) */
.safe-bottom /* padding-bottom: env(safe-area-inset-bottom) */
```

### Gestures
- **Bottom Sheet**: Swipe up/down to expand/collapse
- **Hamburger Menu**: Slide in from left
- **Search**: Tap to expand fullscreen

### Responsive Layout
- **Mobile**: Fullscreen map + bottom sheet + FAB
- **Tablet/Desktop**: Optimized layouts with breakpoints

## State Management

### Books Store (`stores/books.js`)
- `allBooks` - All books from Firestore
- `currentCollection` - Active collection
- `isLoading` - Loading state
- `booksWithLocations` - Computed: books with lat/lng

### UI Store (`stores/ui.js`)
- `bottomSheetState` - 'hidden' | 'half' | 'full'
- `selectedBook` - Currently viewed book
- `searchResults` - Search result array
- `isClusteringEnabled` - Marker clustering toggle
- `mapCenter`, `mapZoom`, `mapType` - Map state

## Development Commands

```bash
npm run dev      # Start dev server
npm run build    # Build for production
npm run preview  # Preview production build
```

## Browser Support

- Chrome (desktop & mobile) ✅
- Safari (desktop & mobile) ✅
- Firefox ✅
- Edge ✅

## Firebase Collections

The app connects to three Firestore collections:
- `newbooks` - ~50 books (newest additions)
- `books` - ~200 books (mid-size collection)
- `small_books` - ~500 books (complete collection)

## Next Steps

1. Integrate vue3-google-map
2. Create BookMarker component with clustering
3. Add map controls (zoom, location selector)
4. Implement random location feature
5. Polish mobile UX and animations
6. Deploy to Vercel

## Contributing

This is a migration of the existing LitMap app. See `/docs/05_Migrating_to_Mobile.md` for the full migration plan and progress.

## License

Same as parent LitMap project.
