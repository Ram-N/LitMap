# Map Components

This directory contains all Google Maps-related components for LitMap.

## Components

### GoogleMap.vue
Main map container component that:
- Initializes Google Maps with vue3-google-map
- Manages map state (center, zoom, type)
- Renders book markers with or without clustering
- Handles map interactions

### BookMarker.vue
Individual book marker component with two states:
- **Unhighlighted**: Small colored pin with book title initials
- **Highlighted**: Expanded card showing cover, title, author, description

Features:
- Hover tooltip (InfoWindow)
- Click to highlight/expand
- Click cover to open Goodreads
- Consistent colors based on book hash

### MapControls.vue
Map controls overlay with:
- Location dropdown (preset locations)
- Manual location search input
- Zoom controls (+/-)

### MarkerCluster.vue
Clustering wrapper component for grouping nearby markers.

**Note**: Currently simplified due to vue3-google-map API. May need custom clustering implementation.

## Usage

```vue
<GoogleMap />
```

The component will automatically:
1. Load books from Pinia store
2. Create markers for all books with locations
3. Apply clustering if enabled in UI store
4. Handle marker clicks and show book details

## State Management

All map state is managed in the UI store (`stores/ui.js`):
- `mapCenter` - Current map center { lat, lng }
- `mapZoom` - Current zoom level (2-17)
- `mapType` - Map type (roadmap/satellite/hybrid/terrain)
- `highlightedMarkerId` - Currently highlighted marker
- `isClusteringEnabled` - Clustering toggle

## Dependencies

- `vue3-google-map` - Vue 3 Google Maps wrapper
- `@googlemaps/markerclusterer` - Marker clustering library
- Google Maps JavaScript API with Map ID support

## Configuration

Requires environment variables:
- `VITE_GOOGLE_MAPS_API_KEY` - Google Maps API key
- `VITE_GOOGLE_MAPS_MAP_ID` - Map ID for Advanced Markers
