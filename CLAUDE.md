# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LitMap is an interactive, crowd-sourced literary map where readers can explore books about real locations worldwide. The application displays book settings on a Google Maps interface with search, filtering, and discovery features.

**Live App**: https://ram-n.github.io/LitMap/

## Tech Stack

- **Frontend**: Vanilla JavaScript, HTML, CSS with Google Maps API
- **Backend**: Firebase (Firestore for data storage, Firebase Hosting)
- **Database Management**: Python with Streamlit for admin interface
- **Package Management**: **uv** (modern Python package manager)
- **Deployment**: GitHub Pages

## Package Management

**IMPORTANT**: This project uses `uv` for Python package management. Do NOT use conda or pip directly.

### Key Commands
```bash
# Install dependencies
uv pip install -r requirements.txt

# Run Python scripts
uv run python script.py

# Activate environment (if using venv with uv)
source .venv/bin/activate
```

## Development Commands

### Frontend Development
```bash
# Serve locally for development (simple HTTP server)
python -m http.server 8000
# Then open http://localhost:8000

# No build process - static files served directly
# Note: Firebase config expects 'public/' directory but files are in root
```

### Common Issues

**Firebase Permission Errors**: 
- Firestore rules may block public access in development
- Check firestore.rules for read permissions
- May need authentication for write operations

**Missing favicon**: Add favicon.ico to root directory to eliminate 404 errors

### Database Management (Streamlit Admin)
```bash
# Navigate to database directory
cd database/

# Run Streamlit admin interface (using uv)
uv run streamlit run main.py

# Alternative: if already in activated venv
streamlit run main.py

# Alternative Python scripts for data processing
uv run python create_JSON.py
uv run python get_book_covers.py
uv run python firebase-connect.py
```

### Firebase Deployment
```bash
# Deploy to Firebase Hosting
firebase deploy

# Initialize Firebase (if needed)
firebase init
```

## Architecture

### Frontend Structure
- **index.html**: Main application entry point with React mount point and fallback UI
- **map.html**: Secondary map view
- **scripts/**: Core JavaScript modules
  - `app.js`: Central application logic and UI interactions
  - `firebase.js`: Firebase configuration and Firestore operations
  - `map.js`: Google Maps integration and marker management
- **styles/**: CSS modules for different UI components

### Database Management (`/database`)
- **main.py**: Streamlit admin interface for managing Firestore database
- **FirebaseClient class**: Provides methods for document operations, search, and data management
- **Key Features**: Add/edit books, manage duplicates, backup collections, search functionality
- **Data Structure**: Books with locations (lat/lng), genres, authors, covers, Goodreads links

### Data Model
Books contain:
- Basic info: title, author, description, publication details
- Classification: booktype (fiction/nonfiction/travel/poetry), genre, tags
- Locations: Array of geographic data with lat/lng coordinates
- Metadata: ISBN, rating, page count, cover images, Goodreads links

## Key Features

- **Interactive Map**: Google Maps with clustering, custom markers, and location-based book discovery
- **Search System**: Multi-field search across titles, authors, genres, and tags with fuzzy matching
- **Admin Interface**: Streamlit-based backend for database management and content moderation
- **Book Discovery**: Random location feature and location-based recommendations
- **Responsive Design**: Mobile-friendly interface with sidebar navigation

## Configuration Files

- **firebase.json**: Firebase hosting and Firestore configuration
- **firestore.rules**: Database security rules
- **firestore.indexes.json**: Database indexing configuration
- **.firebaserc**: Firebase project configuration

## Development Workflow

1. Frontend changes: Edit files directly, test with local server
2. Database changes: Use Streamlit admin interface (`streamlit run database/main.py`)
3. Deploy: Use `firebase deploy` for production updates
4. Data management: Python scripts in `/database` for bulk operations

## Important Notes

- **No build system**: Static files served directly
- **Firebase credentials**: Service account key stored in `database/litmap-88358-firebase-adminsdk-9w1l9-73ca515ce7.json`
- **Python package manager**: **ALWAYS use `uv`** - NOT conda, NOT pip directly
- **Google Maps API**: Requires valid API key for map functionality
- **Data validation**: Location coordinates are critical - must include lat/lng for all book locations