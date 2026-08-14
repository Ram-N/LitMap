# Editing Database Fields using Streamlit

This guide explains how to edit book records in the LitMap GeoJSON database using the Streamlit admin interface.

## Overview

The Streamlit admin interface provides a comprehensive multi-field editor that allows you to update book records safely and efficiently. All changes are saved directly to `litmap-data.geojson` — no Firebase connection is needed.

## Prerequisites

1. **Activate the Python environment:**
   ```bash
   cd /home/ram/projects/LitMap/database
   source litmap-env/bin/activate
   ```

2. **Run the Streamlit application:**
   ```bash
   streamlit run main.py
   ```

3. The application will open in your browser (typically at `http://localhost:8501`)

## Accessing the Book Editor

1. Navigate to the **"DB-Manage"** tab
2. Select **"Edit Book"** from the action dropdown menu

## Editing Workflow

The editor uses a three-step process:

### Step 1: Find and Select Book

**Using the Search Function:**
1. Use the search box at the top of the DB-Manage tab
2. Search by:
   - Author name
   - Book title
   - Genre
3. Click the **✏️ Edit** button next to the book you want to edit

**Using Book ID directly:**
1. Enter a Book ID in the "Enter Book ID to Edit" field
2. The system will confirm the book was found and display:
   - Book title and author
   - An expandable section with complete current data

### Step 2: Edit Book Fields

Once a book is selected, a comprehensive edit form appears with all fields organized in two columns:

#### Left Column - Basic Information
- **Title**: The book's title
- **Author**: Author name
- **Description**: Book description/summary
- **Book Type**: Dropdown selection (fiction/nonfiction/travel/poetry/other)
- **Genre**: Book genre/category
- **Tags**: Comma-separated tags (automatically converted to array)

#### Right Column - Publication Details
- **Publisher**: Publishing company name
- **Year**: Publication year (1000-2100)
- **ISBN**: ISBN number
- **Page Count**: Number of pages (0-10000)
- **Rating**: Book rating (0.0-5.0)
- **Cover Image URL**: URL to book cover image
- **Goodreads Link**: Link to Goodreads page

#### Location Management

The location editor provides three ways to manage book locations:

**A. Editable Table:**
- View and edit all locations in a data table
- Add or delete rows directly
- Columns: City, Country, Latitude, Longitude, Description

**B. Quick Add Form:**
- Enter city and country
- Use **🔍 Auto-Geocode** to automatically look up coordinates via OpenStreetMap
- Manually adjust latitude/longitude if needed
- Click **➕ Add Location** to append

**C. Advanced JSON Editor (collapsible):**
- Edit the locations array directly as JSON
- Example format:
  ```json
  [
    {
      "city": "Paris",
      "country": "France",
      "latitude": 48.8566,
      "longitude": 2.3522,
      "description": "Main setting of the novel"
    },
    {
      "city": "London",
      "country": "United Kingdom",
      "latitude": 51.5074,
      "longitude": -0.1278,
      "description": "Opening chapters"
    }
  ]
  ```

**Making Changes:**
1. Edit any fields you want to update
2. Leave unchanged fields as-is (they won't be modified)
3. Click **"📋 Preview Changes"** button at the bottom

### Step 3: Review and Confirm Changes

After clicking "Preview Changes", the system shows:

**Change Summary:**
- Number of fields being updated
- Before → After comparison for each modified field
- Visual formatting:
  - Lists displayed as formatted JSON
  - Long text truncated with preview
  - Short values shown in code blocks

**Confirmation Options:**
- **✅ Confirm and Save Changes**: Applies all changes to the GeoJSON file
- **❌ Cancel Changes**: Discards all edits and returns to form

**After Saving:**
- Success message with number of fields updated
- Celebration animation (balloons!)
- Option to refresh and edit another book

## Edit Existing JSON (Advanced)

For power users, the **"Edit Existing JSON"** action provides direct JSON editing:

1. **Search** for a book by title, author, or ID
2. **Select** the book to load its full JSON
3. **Edit** the JSON directly in a text area
4. **Validate & Preview** — the system parses the JSON and shows a structured diff:
   - Added fields
   - Removed fields
   - Changed fields (old → new)
   - Unchanged fields (collapsible)
5. **Confirm & Save** to write changes to GeoJSON

## Features and Capabilities

### Smart Change Detection
- Only modified fields are updated in the GeoJSON
- Unchanged fields are ignored
- Location changes are normalized to avoid false positives

### Field Type Handling
- **Text fields**: Standard text input
- **Numbers**: Validated numeric input with min/max ranges
- **Dropdowns**: Pre-defined options for categorical fields
- **Arrays**: Automatic conversion from comma-separated strings
- **JSON**: Direct editing for complex nested data (locations)

### Validation
- **Required fields**: Title and author must have values
- **Number ranges**: Year, page count, and rating have validation
- **JSON syntax**: Location array is validated before saving
- **Coordinate validation**: Latitude (-90 to 90), Longitude (-180 to 180)
- **Error messages**: Clear feedback if validation fails

### Safety Features
- **Preview before save**: Always review changes before committing
- **Cancellation**: Can cancel at any time before final save
- **Error handling**: Failed updates don't corrupt existing data
- **Preserves book ID**: Updates in place, no ID changes

## Common Use Cases

### Use Case 1: Fix a Typo
1. Search for the book by title
2. Click ✏️ Edit on the search result
3. Correct the typo in the appropriate field
4. Preview → Confirm → Done!

**Example**: Changing "The Grat Gatsby" to "The Great Gatsby"

### Use Case 2: Add Missing Metadata
1. Find the book with incomplete data
2. Fill in missing fields: ISBN, publisher, page count, cover URL, Goodreads link
3. Preview → Confirm → All fields updated simultaneously

**Example**: Adding ISBN 978-0743273565, publisher "Scribner", and page count 180 to a book

### Use Case 3: Add or Update Locations
1. Select the book
2. Use the Quick Add form with Auto-Geocode, or edit the locations table
3. Preview → Confirm → Location data updated

**Example**: Adding a new city where part of the book takes place

### Use Case 4: Update Tags and Genre
1. Change genre (e.g., "Fiction" → "Historical Fiction")
2. Update tags (e.g., "paris, france, 1920s, expat")
3. Preview → Confirm → Both updated together

**Example**: Reclassifying a book with more specific genre and adding relevant tags

## Technical Details

### Backend Implementation

**GeoJSONClient class** in `database/main.py`:
- `update_book(book_id, changes)` — updates properties on all features matching the bookId, saves the file
- `_update_locations(book_id, new_locations)` — replaces all features for a book when locations change
- `save()` — writes the full GeoJSON back to disk

**Session State Management**:
- `edit_selected_book`: Currently selected book data
- `edit_show_preview`: Whether to display change preview
- `edit_changes`: Dictionary of field changes to apply
- `edit_locations_data`: Current state of the location editor
- `edit_current_book_id`: Tracks which book's locations are loaded

**Change Detection Algorithm**:
1. Compare each form field value with original book data
2. Build dictionary of only changed fields
3. Special handling for type conversions (tags string → array)
4. Normalize locations to avoid false positives from empty fields or type differences
5. Preserve unchanged fields completely

### Error Handling

The editor includes comprehensive error handling:

1. **Book not found**: Clear message if book ID doesn't exist
2. **Invalid JSON**: Validation for locations array with error message
3. **Save errors**: Try-catch block with user-friendly error display
4. **Number validation**: Min/max ranges enforced by Streamlit widgets
5. **Console logging**: Detailed logs for debugging

## Troubleshooting

### Book ID Not Found
**Problem**: "No book found with ID: xyz"
**Solution**:
- Verify the book ID is correct
- Use the search function to find the correct ID
- Book IDs are either ISBN-13 numbers or title-author slugs (e.g., `the-great-gatsby-fitzgerald`)

### Invalid JSON in Locations
**Problem**: "❌ Invalid JSON in locations field"
**Solution**:
- Check for missing commas, brackets, or quotes
- Validate JSON syntax using a JSON validator
- Refer to the location array example format above

### Changes Not Saving
**Problem**: Update appears to fail
**Solution**:
- Check console output for detailed error messages
- Verify the GeoJSON file is writable
- Ensure the file path is correct

### Form Fields Not Pre-populating
**Problem**: Form shows empty fields
**Solution**:
- Ensure the book was found in Step 1
- Check that the book data includes the expected fields
- Use the "View Current Book Data" expander to inspect the book record

## Best Practices

1. **Always preview changes** before confirming to catch mistakes
2. **Use the search function** to find books rather than guessing IDs
3. **Make backups** before major edit sessions (use "Export Collection" in DB-Manage)
4. **Use Auto-Geocode** when adding locations to get accurate coordinates
5. **Validate coordinates** when editing location arrays (lat: -90 to 90, lng: -180 to 180)
6. **Use consistent formatting** for tags and genres
7. **Check the expanded book data** if unsure about current field values
8. **Commit changes** to git after editing to deploy updates

## Related Documentation

- [About LitMap Database](02_About_LitMap_Database.md) - Database structure and data format
- [Maintaining the Database](03_Maintaining_the_database.md) - General maintenance procedures
- [Workflow](Workflow.md) - Overall development workflow
