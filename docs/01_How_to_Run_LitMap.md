# How to Run LitMap

This guide covers all the ways to run and work with LitMap locally.

## Prerequisites

- **Python 3.8+** (for database management and admin tools)
- **uv** package manager (Python dependencies)
- **Node.js** (optional, for Firebase CLI)
- **Firebase CLI** (optional, for deployment)
- **Google Maps API key** (for map functionality)

## Quick Start

### Running the Frontend Application

The simplest way to run LitMap locally:

```bash
# From the project root directory
python -m http.server 8000
```

Then open your browser to: **http://localhost:8000**

**Note**: This serves the static HTML/CSS/JS files directly - no build process needed.

### Alternative: Using Firebase Serve

If you have Firebase CLI installed:

```bash
firebase serve
```

This will serve the app at **http://localhost:5000**

## Running the Database Admin Interface

LitMap includes a Streamlit-based admin interface for managing the Firestore database.

### Setup

1. **Install Python dependencies** (using uv):
   ```bash
   uv pip install -r requirements.txt
   ```

2. **Ensure Firebase credentials exist**:
   - Check that `database/litmap-88358-firebase-adminsdk-9w1l9-73ca515ce7.json` exists
   - This service account key is required for database access

### Launch Admin Interface

```bash
# Navigate to database directory
cd database/

# Run Streamlit admin interface
uv run streamlit run main.py
```

The admin interface will open at **http://localhost:8501**

### Admin Interface Features

- Add new books with location data
- Edit existing book information
- Search and filter books
- Manage duplicates
- Backup collections
- Geocode addresses to coordinates

## Python Database Scripts

### Book Cover Fetcher

Download book cover images from Open Library:

```bash
cd database/
uv run python get_book_covers.py
```

### Create JSON Data

Generate JSON files from Firestore data:

```bash
cd database/
uv run python create_JSON.py
```

### Firebase Connection Test

Test Firebase connection and operations:

```bash
cd database/
uv run python firebase-connect.py
```

## Development Workflow

### Frontend Development

1. **Make changes** to HTML, CSS, or JavaScript files
2. **Test locally** using Python's HTTP server:
   ```bash
   python -m http.server 8000
   ```
3. **Refresh browser** to see changes (no build step required)

### Database Development

1. **Launch admin interface**:
   ```bash
   cd database/
   uv run streamlit run main.py
   ```
2. **Make changes** through the Streamlit UI
3. **Changes are saved** directly to Firestore

## Deployment

### Deploy to Firebase Hosting

```bash
firebase deploy
```

This deploys the frontend to Firebase Hosting.

### Deploy to GitHub Pages

The live app is hosted at: https://ram-n.github.io/LitMap/

To update:
1. Push changes to the `main` branch
2. GitHub Pages automatically rebuilds and deploys

## Common Issues & Solutions

### Firebase Permission Errors

**Problem**: Can't read/write to Firestore
**Solution**:
- Check `firestore.rules` for proper read/write permissions
- Verify Firebase service account credentials exist
- Ensure you're using the admin SDK for backend operations

### Missing Favicon

**Problem**: 404 error for favicon.ico
**Solution**: Add a `favicon.ico` file to the project root

### Google Maps Not Loading

**Problem**: Map doesn't display or shows error
**Solution**:
- Verify Google Maps API key is valid in `scripts/firebase.js`
- Check API key has Maps JavaScript API enabled
- Ensure billing is enabled on Google Cloud project

### Package Installation Errors

**Problem**: Can't install Python dependencies
**Solution**:
- **Always use uv**: `uv pip install -r requirements.txt`
- Do NOT use conda or pip directly
- If uv isn't installed: `pip install uv`

## Project Structure

```
LitMap/
├── index.html          # Main application entry
├── map.html           # Secondary map view
├── scripts/           # JavaScript modules
│   ├── app.js        # Core application logic
│   ├── firebase.js   # Firebase configuration
│   └── map.js        # Google Maps integration
├── styles/           # CSS modules
├── database/         # Admin tools & scripts
│   ├── main.py      # Streamlit admin interface
│   └── *.py         # Utility scripts
├── docs/            # Documentation
└── firebase.json    # Firebase configuration
```

## Next Steps

- **Learn about the database structure**: See [02_About_LitMap_Database.md](02_About_LitMap_Database.md)
- **Database maintenance**: See [3_Maintaining_the_database.md](3_Maintaining_the_database.md)
- **Editing fields**: See [04_Editing_Database_Fields.md](04_Editing_Database_Fields.md)

## Need Help?

- Check CLAUDE.md for technical details
- Review Firebase console for database issues
- Verify all prerequisites are installed correctly
