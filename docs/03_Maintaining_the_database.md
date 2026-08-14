# 3. Maintaining the Database

This document explains how to manage the LitMap database using the Streamlit admin interface. The data lives in `litmap-data.geojson` — no Firebase connection is needed.

## Prerequisites

- Python environment with required packages
- The GeoJSON file at `vue-app/public/litmap-data.geojson`

## Database Management with Streamlit

### 1. Setup Environment

Using `uv` for fast and reliable Python package management:

```bash
# Navigate to project root
cd /home/ram/projects/LitMap

# Create a virtual environment with uv
uv venv litmap-env

# Activate the environment
source litmap-env/bin/activate

# Install required packages using uv
uv pip install streamlit pandas geopy

# Navigate to database directory
cd database/
```

**Alternative: One-step setup with uv**
```bash
# Navigate to database directory
cd /home/ram/projects/LitMap/database

# Run with uv (automatically manages virtual environment)
uv run --with streamlit,pandas,geopy streamlit run main.py
```

**Traditional pip method (if needed):**
```bash
# Create virtual environment
python3 -m venv litmap-env
source litmap-env/bin/activate
pip install streamlit pandas geopy
cd database/
```

### 2. Run Streamlit Admin Interface

Start the Streamlit admin application:

```bash
streamlit run main.py
```

This will open a web interface (typically at `http://localhost:8501`) with database management tools.

### 3. Streamlit Admin Features

The `main.py` Streamlit app provides the following database management capabilities:

#### Core Functions
- **Document Count**: See total number of books in the dataset
- **Search Books**: Find books by title, author, or other attributes
- **Add Books**: Import new books from JSON files with validation
- **Edit Books**: Modify existing book records via form or JSON editor
- **Delete Books**: Remove individual books

#### Data Management
- **Duplicate Detection**: Find and compare duplicate book entries
- **Backup Data**: Export all books to timestamped JSON files
- **Bulk Operations**: Add multiple books from JSON files
- **Location Management**: Add/edit geographical locations with geocoding support
- **ISBN Management**: Validate, lookup, and update ISBNs

#### Key Data Files
- `books_master.js` - Main book dataset
- `locations_master.js` - Location reference data
- `data/` - Individual book JSON files
- `backup/` - Data backups with timestamps

### 4. Data Schema

Books in the GeoJSON contain these properties per feature:
```json
{
  "title": "Book Title",
  "author": "Author Name",
  "description": "Book description",
  "booktype": "fiction|nonfiction|travel|poetry",
  "genre": "Genre",
  "tags": ["tag1", "tag2"],
  "bookId": "unique-book-id",
  "locationCity": "City Name",
  "locationCountry": "Country",
  "locationDescription": "Location context in book",
  "isbn": "ISBN number",
  "rating": 4.2,
  "pageCount": 300,
  "publicationDate": "YYYY",
  "coverImageUrl": "URL to cover image",
  "goodreadsLink": "Goodreads link"
}
```

The geometry provides coordinates as `[longitude, latitude]`. A single book with multiple locations produces multiple features sharing the same `bookId`.

## Database Utilities

### Python Scripts

Located in `/database/`:

```bash
# Create JSON from data sources
python create_JSON.py

# Fetch book cover images
python get_book_covers.py

# Generate human-readable book IDs
python generate_book_id.py

# Export data to GeoJSON (legacy — from Firebase)
python export_geojson.py
```

### JavaScript Data Files

- `books_master.js` - Main book collection
- `locations_master.js` - Location reference data
- `data.js` - Formatted data for import
- `new1.js` - New book additions

## Deployment

### GitHub Pages

The Vue app and GeoJSON data are deployed via GitHub Pages:

1. Edit data using the Streamlit admin interface
2. Changes are saved directly to `vue-app/public/litmap-data.geojson`
3. Commit and push to deploy:
   ```bash
   git add vue-app/public/litmap-data.geojson
   git commit -m "Update book data"
   git push
   ```
4. GitHub Pages serves the updated data automatically

## Workflow Summary

### Adding New Books

1. **Prepare Data**: Create JSON files in `/database/data/`
2. **Run Streamlit**: `streamlit run main.py`
3. **Import Books**: Use "Upload Books from JSON" — validates and checks duplicates
4. **Verify Data**: Review the validation results before confirming
5. **Deploy**: Commit and push the updated GeoJSON

### Updating Existing Books

1. **Edit via Streamlit**: Use the search and edit features in DB-Manage tab
2. **Backup First**: Export data before major changes
3. **Save**: Changes are written directly to `litmap-data.geojson`
4. **Deploy**: Commit and push

### Database Maintenance

1. **Regular Backups**: Export data periodically via "Export Collection (Full Backup)"
2. **Duplicate Cleanup**: Use the "Find Duplicates" tool to identify and resolve duplicates
3. **Data Validation**: Ensure all books have proper location coordinates
4. **ISBN Enrichment**: Use the ISBN Manager tab to fill in missing ISBNs

## Troubleshooting

### Common Issues

**GeoJSON File Not Found**:
- Verify the file exists at `vue-app/public/litmap-data.geojson`
- Check that you're running Streamlit from the `database/` directory

**Streamlit Startup Issues**:
- Check Python environment activation
- Ensure required packages are installed: `streamlit`, `pandas`, `geopy`

**Changes Not Appearing in App**:
- Verify changes were saved (check the GeoJSON file)
- Commit and push to deploy to GitHub Pages
- Clear browser cache if needed

### Environment Setup

**Using uv (recommended):**
```bash
# Install required packages with uv
uv pip install streamlit pandas geopy

# Or create and use virtual environment
uv venv .venv
source .venv/bin/activate
uv pip install streamlit pandas geopy

# Or run directly with dependencies
uv run --with streamlit,pandas,geopy streamlit run database/main.py
```

**Traditional pip method:**
```bash
# Install required packages
pip install streamlit pandas geopy

# Or from requirements file
pip install -r requirements.txt
```

## Security Notes

- **No credentials needed**: The admin interface reads/writes a local GeoJSON file
- **Git-based access control**: Data changes are tracked via git commits
- **Backups**: Maintain regular backups before major data operations
