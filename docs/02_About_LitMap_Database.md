# 02. About LitMap Database

This document provides a comprehensive overview of LitMap's data architecture, storage systems, and management workflows.

## **GeoJSON is the Master Data Source**

**`litmap-data.geojson`** (located at `vue-app/public/litmap-data.geojson`) is the single source of truth. The Vue app reads from it directly, and the Streamlit admin interface reads and writes to it. There is no Firebase dependency.

## GeoJSON Data Structure

The file is a standard GeoJSON `FeatureCollection`. Each **Feature** represents one book–location pair (a book with multiple locations produces multiple features sharing the same `bookId`).

### **Feature Format:**
```json
{
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [-7.9892, 31.6258]
  },
  "properties": {
    "title": "The Great Railway Bazaar",
    "author": "Paul Theroux",
    "description": "A vivid travelogue documenting Theroux's journey by train across Europe, Asia, and the Middle East.",
    "booktype": "Nonfiction",
    "genre": "Travel",
    "rating": 4.1,
    "pageCount": 400,
    "isbn": "9780141189147",
    "language": "English",
    "publisher": "Houghton Mifflin",
    "publicationDate": "1975",
    "coverImageUrl": null,
    "hasCover": true,
    "tags": ["Train", "Asia", "Adventure"],
    "bookId": "9780141189147",
    "locationCity": "Istanbul",
    "locationCountry": "Turkey",
    "locationDescription": "A key stop on Theroux's journey, bridging Europe and Asia.",
    "goodreadsLink": "URL to Goodreads page"
  }
}
```

### **Key Data Fields:**

**Basic Information:**
- `title`, `author`, `description`
- `isbn`, `language`, `publisher`, `publicationDate`
- `rating`, `pageCount`

**Classification:**
- `booktype`: `fiction` | `nonfiction` | `travel` | `poetry`
- `genre`: Travel, Historical Fiction, etc.
- `tags`: Array of descriptive keywords

**Geographic Data (per-feature):**
- `geometry.coordinates`: `[longitude, latitude]` (GeoJSON standard)
- `locationCity`, `locationCountry`: Place name
- `locationDescription`: Context of location in the book

**Book Identity:**
- `bookId`: Unique identifier (ISBN-13 if available, otherwise a title-author slug)

**External Links:**
- `coverImageUrl`: Book cover URL
- `goodreadsLink`: Goodreads page link

## Data Sources

### **Static Data Files in `/database/`:**

**Primary Sources:**
- **`books_master.js`** - Large dataset for bulk imports (230KB+)
- **`locations_master.js`** - Geographic reference data
- **`data.js`** - Formatted data for import

**Individual Book Files in `/database/data/`:**
- **JSON files**: Individual book records for selective import
  - `newdata.json`, `new1.json` through `new5.json`
  - Country-specific: `Guyana.json`, `Az-Bah.json`, etc.
  - Book-specific: `Out_of_Africa_*.json`, etc.
- **CSV files**: Tabular exports
  - `books-Claude-01.csv`, `books-Claude-02.csv`
  - `travel-writers-books.csv`

**Backup Data in `/database/backup/`:**
- Timestamped exports from the admin interface
- `litmap_2024-10-27-14-14.json`

**Important:** These are **source materials** that get imported into the GeoJSON via Streamlit, not authoritative databases.

## Streamlit Admin Interface

### **How to Launch:**
```bash
cd /home/ram/projects/LitMap/database
uv run --with streamlit,pandas,geopy streamlit run main.py
```

### **Interface Layout:**
- **Sidebar:** Info and global controls
- **4 Main Tabs:** Data Viewer, DB-Manage, ISBN Manager, Help

### **Adding Books:**

1. **Prepare Data:**
   - Create JSON file in `/database/data/` directory
   - Follow the book JSON format (title, author, locations with lat/lng)
   - Ensure all locations have `latitude` and `longitude`

2. **Import via Streamlit:**
   - **Tab:** "DB-Manage"
   - **Action:** "Upload Books from JSON"
   - Upload your JSON file
   - System validates and checks for duplicates automatically
   - Confirm to save to GeoJSON

### **Editing Books:**

1. **Find Books:**
   - **Tab:** "Data Viewer"
   - **Actions:**
     - "List All Book Titles" - Browse all books
     - "Find Duplicates" - Locate similar entries
     - "Compare 2 Books" - Side-by-side review

2. **Edit Operations:**
   - **Tab:** "DB-Manage"
   - **Actions:**
     - "Edit Book" - Visual form editor with location management
     - "Edit Existing JSON" - Direct JSON editing with diff preview
     - "Export Single Book" - Export for external editing
     - "Delete Book by ID" - Remove a book

### **Management Functions:**

**Data Viewer Tab:**
- **"Document Count"** - See total number of books
- **"List All Book Titles"** - Alphabetical book list
- **"List All Authors"** - Unique author list
- **"Show All Locations"** - Geographic coverage
- **"Find Duplicates"** - Data quality check
- **"Compare 2 Books"** - Detailed comparison

**DB-Manage Tab:**
- **"Upload Books from JSON"** - Import with validation and duplicate checking
- **"Edit Book"** - Visual multi-field editor with location management
- **"Edit Existing JSON"** - Advanced JSON editing with diff preview
- **"Export Collection (Full Backup)"** - Export all books to timestamped JSON
- **"Export Single Book"** - Export one book to JSON
- **"Delete Book by ID"** - Remove a book from the GeoJSON
- **"Backup & Delete Book"** - Safe delete with backup

**ISBN Manager Tab:**
- View ISBN status across all books (valid/missing/invalid)
- Edit ISBNs with real-time validation
- Open Library lookup for missing ISBNs
- Save ISBN changes directly to GeoJSON

## Data Flow Summary

```
Source Files ──┐
               │
JSON/CSV ──────┼──► Streamlit ──► litmap-data.geojson ──► Vue App
               │     Admin         (Master Data)           (Frontend)
Backup ────────┘        │
                        │
                        ▼
                   Export/Backup
```

### **Workflow Steps:**

1. **Content Creation:**
   - Create book JSON files in `/database/data/`
   - Include complete location data with coordinates

2. **Quality Assurance:**
   - Use Streamlit to check for duplicates
   - Validate data format and completeness

3. **Import to GeoJSON:**
   - Use "Upload Books from JSON" in Streamlit
   - Monitor import success/warnings

4. **Production Update:**
   - Commit and push the updated `litmap-data.geojson`
   - GitHub Pages serves the Vue app with the new data

5. **Maintenance:**
   - Regular backups via "Export Collection (Full Backup)"
   - Duplicate cleanup as needed
   - ISBN validation and enrichment

## Data Validation Rules

### **Required Fields:**
- `title`, `author` (essential)
- `locations` array with `latitude`, `longitude` (for mapping)
- `booktype` (fiction|nonfiction|travel|poetry)

### **Data Quality:**
- **Coordinates:** Must be valid lat/lng for map display
- **Duplicates:** System checks title/author similarity
- **Format:** JSON structure must match schema
- **Book IDs:** Auto-generated from ISBN or title-author slug

## Summary

**`litmap-data.geojson` is the single source of truth.** All JSON/CSV files are staging/source data that flows into the GeoJSON through the Streamlit admin interface. The Vue web application reads directly from this file via GitHub Pages.
