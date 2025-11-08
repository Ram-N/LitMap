# LitMap Vue - Quick Start Guide

Get the Vue mobile-first version of LitMap running in minutes!

## Prerequisites

- Node.js (v18 or higher)
- npm or yarn
- Firebase credentials (already configured)
- Google Maps API key (already configured)

## Installation

### 1. Navigate to the Vue app directory

```bash
cd vue-app
```

### 2. Install dependencies

```bash
npm install
```

This will install:
- Vue 3
- Vite
- Tailwind CSS
- Pinia
- Firebase SDK
- vue3-google-map
- Lucide icons
- @vueuse/core

### 3. Environment Setup

The `.env` file is already configured with:
- ✅ Firebase credentials (from existing LitMap)
- ✅ Google Maps API key

No additional setup needed!

### 4. Start the development server

```bash
npm run dev
```

The app will open at `http://localhost:5173`

## What to Expect

### On First Load

1. **Loading Spinner** - App fetches books from Firebase
2. **Map Appears** - Centered on India with terrain view
3. **Book Markers** - Colored pins with title initials
4. **Top Bar** - Logo, hamburger menu, search icon

### Features to Test

#### 1. Map Navigation

- **Dropdown**: Select a preset location (New York, London, etc.)
- **Manual Search**: Type a location and press Enter
- **Zoom Controls**: +/- buttons to zoom in/out
- **Random Location**: Click the FAB (shuffle icon) at bottom-right

#### 2. Search

- **Click search icon** (top-right) → Fullscreen search opens
- **Enter a query**: Try "Paris", "Hemingway", "Adventure"
- **Select search type**: Title, Author, Location, Keyword, or Any
- **Click Search** → Bottom sheet slides up with results

#### 3. Bottom Sheet

- **Swipe up** → Expand to full screen
- **Swipe down** → Collapse to half or close
- **Tap a book card** → View full details
- **Tap "View on Goodreads"** → Opens Goodreads page

#### 4. Hamburger Menu

- **Click hamburger icon** (top-left) → Sidebar opens
- **Switch collection**: newbooks, books, or small_books
- **Toggle clustering**: Group nearby markers
- **Change map type**: Roadmap, Satellite, Hybrid, Terrain

#### 5. Book Markers

- **Unhighlighted state**: Small colored pin with initials
- **Hover**: Info tooltip appears
- **Click**: Marker expands to show book details
- **Click cover** (when highlighted): Opens Goodreads
- **Click "Close"**: Return to unhighlighted state

## Project Structure

```
vue-app/
├── src/
│   ├── components/
│   │   ├── layout/        # TopBar, Menu, BottomSheet
│   │   ├── map/          # GoogleMap, Markers, Controls
│   │   ├── search/       # SearchBar, BookCard, BookDetails
│   │   └── shared/       # Reusable components
│   ├── composables/      # Composable functions
│   ├── stores/           # Pinia state management
│   ├── utils/            # Utilities and helpers
│   └── App.vue          # Root component
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## Common Issues & Solutions

### Map Not Loading

**Problem**: Blank map or API error

**Solution**: Check that `VITE_GOOGLE_MAPS_API_KEY` is set in `.env`

### No Books Showing

**Problem**: Markers not appearing

**Solutions**:
1. Check browser console for Firebase errors
2. Verify Firebase credentials in `.env`
3. Check if books loaded: Open dev tools → Pinia store → books

### Bottom Sheet Not Working

**Problem**: Bottom sheet doesn't slide up

**Solution**: Click search icon, enter query, and click "Search" button (not just close)

### Search Returns No Results

**Problem**: Search doesn't find books

**Solutions**:
1. Try "Any" field search instead of specific field
2. Use shorter search terms (e.g., "Paris" instead of "A Moveable Feast")
3. Check if books are loaded (console log)

## Development Commands

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Testing on Mobile

### Using Local Network

1. Find your local IP address:
   ```bash
   # On Mac/Linux
   ifconfig | grep inet

   # On Windows
   ipconfig
   ```

2. Update `vite.config.js`:
   ```js
   server: {
     host: '0.0.0.0',
     port: 5173
   }
   ```

3. On mobile, navigate to: `http://YOUR_IP:5173`

### Using Browser DevTools

1. Open Chrome DevTools (F12)
2. Click "Toggle device toolbar" (Ctrl+Shift+M)
3. Select a mobile device (iPhone, Android)
4. Test touch interactions

## Next Steps

### Phase 5: Testing & Refinement
- [ ] Test all search types
- [ ] Test bottom sheet gestures
- [ ] Verify mobile touch targets
- [ ] Test on real devices (iOS, Android)

### Phase 6: Mobile UX Polish
- [ ] Refine bottom sheet animations
- [ ] Add haptic feedback (if supported)
- [ ] Test landscape orientation
- [ ] Verify safe area insets on notched devices

### Phase 7: Performance
- [ ] Profile render performance
- [ ] Optimize marker rendering for large datasets
- [ ] Add virtual scrolling for search results
- [ ] Implement lazy loading

### Phase 8: Production
- [ ] Build production version
- [ ] Deploy to Vercel
- [ ] Set up environment variables on Vercel
- [ ] Test live deployment

## Helpful Tips

1. **State Inspection**: Install Vue DevTools extension to inspect Pinia stores
2. **Console Logs**: Watch console for helpful logs about books loaded, search results, etc.
3. **Network Tab**: Check Firebase requests to verify data loading
4. **Performance**: Use Chrome DevTools Performance tab to profile

## Support

- **Documentation**: See `/docs/05_Migrating_to_Mobile.md` for full migration details
- **Component Docs**: See `/vue-app/src/components/map/README.md` for map components
- **Issues**: Check console for errors and warnings

---

**Ready to start?** Run `npm install && npm run dev` and enjoy! 🚀
