# 02. About LitMap Database

This document provides a comprehensive overview of LitMap's data architecture, storage systems, and management workflows.

## **Firebase is the Ultimate Master Database** 🔥

**Firebase Firestore** is your authoritative source of truth. Everything else is either:
- Source data for importing into Firebase
- Backup/export data from Firebase
- Development/staging data

## Firebase Database Structure

### **Collections:**
1. **`newbooks`** - Primary/default collection (newest data)
2. **`midbooks`** - Secondary collection 
3. **`books`** - Tertiary collection
4. **`locations`** - Geographic reference data

### **Document Format in Firebase:**
```json
{
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
  "publicationDate": "1975-01-01",
  "tags": ["Train", "Asia", "Adventure"],
  "locations": [
    {
      "city": "Istanbul",
      "latitude": 41.0082,
      "longitude": 28.9784,
      "description": "A key stop on Theroux's journey, bridging Europe and Asia."
    },
    {
      "city": "Delhi",
      "latitude": 28.6139,
      "longitude": 77.2090,
      "description": "A major station on the rail journey through India."
    }
  ],
  "coverImage": "URL to book cover",
  "goodreadsUrl": "URL to Goodreads page"
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

**Geographic Data:**
- `locations`: Array of location objects with:
  - `city`, `country`, `state` (optional)
  - `latitude`, `longitude` (required for mapping)
  - `description`: Context of location in the book
  - `in_book`: Chapter reference (optional)

**External Links:**
- `coverImage`: Book cover URL
- `goodreadsUrl`: Goodreads page link

## Data Sources (Not Masters)

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
- Timestamped Firebase exports
- `books_2024-10-27-14-14.json`
- `midbooks_2024-10-19-10-23.json`

**Important:** These are **source materials** that get imported INTO Firebase via Streamlit, not authoritative databases.

## Streamlit Admin Interface

### **How to Launch:**
```bash
cd /home/ram/projects/LitMap/database
uv run --with streamlit,firebase-admin,pandas streamlit run main.py
```

### **Interface Layout:**
- **Sidebar:** Collection selector (`books`, `midbooks`, `newbooks`)
- **3 Main Tabs:** Data Viewer, DB-Manage, Help

### **Adding Books:**

1. **Prepare Data:**
   - Create JSON file in `/database/data/` directory
   - Follow the document format above
   - Ensure all locations have `latitude` and `longitude`

2. **Import via Streamlit:**
   - **Tab:** "DB-Manage"
   - **Action:** "BULK UPLOAD of docs"
   - Select collection (`newbooks` recommended)
   - Upload your JSON file
   - System checks for duplicates automatically

### **Editing Books:**

1. **Find Books:**
   - **Tab:** "Data Viewer"
   - **Actions:** 
     - "Print All Titles" - Browse all books
     - "Find Duplicates" - Locate similar entries
     - "Compare 2 Books" - Side-by-side review

2. **Edit Operations:**
   - **Tab:** "DB-Manage"
   - **Actions:**
     - "EDIT ISBN" - Modify specific fields
     - "Persist Book to JSON" - Export for editing
     - "PURGE - write file and DELete doc" - Backup then delete

### **Management Functions:**

**Data Viewer Tab:**
- **"Document Count"** - See collection sizes
- **"Print All Titles"** - Alphabetical book list
- **"Print All Authors"** - Unique author list
- **"List All Locations"** - Geographic coverage
- **"Find Duplicates"** - Data quality check
- **"Compare 2 Books"** - Detailed comparison

**DB-Manage Tab:**
- **"BACKUP Collection to file"** - Export entire collection to JSON
- **"BULK UPLOAD of docs"** - Import multiple books from JSON
- **"EDIT ISBN"** - Modify specific document fields
- **"Persist Book to JSON"** - Export single book for editing
- **"Delete Doc by ID"** - Remove specific document
- **"PURGE - write file and DELete doc"** - Safe delete with backup

### **Collection Management:**
- **Default Collection:** `midbooks` (index=1)
- **Primary Collection:** `newbooks` (newest data)
- **Switch Collections:** Use sidebar dropdown
- **Data Isolation:** Each collection is independent

## Data Flow Summary

```
Source Files ──┐
               │
JSON/CSV ──────┼──► Streamlit ──► Firebase ──► Web App
               │     Admin         (Master)     (Frontend)
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

3. **Import to Firebase:**
   - Use "Upload Books to Firebase" in Streamlit
   - Select appropriate collection
   - Monitor import success/warnings

4. **Production Update:**
   - Firebase automatically serves data to web app
   - No additional deployment needed for data changes

5. **Maintenance:**
   - Regular backups via "Export Collection to JSON"
   - Duplicate cleanup as needed
   - Collection management between `books`, `midbooks`, `newbooks`

## Data Validation Rules

### **Required Fields:**
- `title`, `author` (essential)
- `locations` array with `latitude`, `longitude` (for mapping)
- `booktype` (fiction|nonfiction|travel|poetry)

### **Data Quality:**
- **Coordinates:** Must be valid lat/lng for map display
- **Duplicates:** System checks title/author similarity
- **Format:** JSON structure must match schema
- **Collections:** Use `newbooks` for new additions

## Security and Access

- **Firebase Rules:** Controlled by `firestore.rules`
- **Admin Access:** Via service account key in Streamlit
- **Public Access:** Read-only for web application
- **Credentials:** `litmap-88358-firebase-adminsdk-*.json`

## Summary

**Firebase Firestore is your single source of truth.** All JSON/CSV files are staging/source data that flows into Firebase through the Streamlit admin interface. The web application reads directly from Firebase, making it the authoritative database for LitMap.