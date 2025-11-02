# Editing Database Fields using Streamlit

This guide explains how to edit book records in the Firebase/Firestore database using the Streamlit admin interface.

## Overview

The Streamlit admin interface provides a comprehensive multi-field editor that allows you to update book records safely and efficiently without the need to export, delete, and re-import data.

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
2. Select **"Edit Book Field"** from the action dropdown menu
3. Choose your collection from the sidebar (books/midbooks/newbooks)

## Editing Workflow

The editor uses a three-step process:

### Step 1: Find and Select Book

**Using the Search Function:**
1. Use the search box at the top of the DB-Manage tab
2. Search by:
   - Author name
   - Book title
   - Genre
3. The search results will display matching books with their IDs

**Selecting the Book:**
1. Copy the Book ID from the search results
2. Paste it into the "Enter Book ID to Edit" field
3. The system will confirm the book was found and display:
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

#### Locations Array Editor
- **Locations (JSON format)**: Edit the locations array directly as JSON
  - Each location should include: `place` or `city`, `lat`, `lng`, and optionally `country`
  - The editor validates JSON syntax
  - Example format:
    ```json
    [
      {
        "city": "Paris",
        "lat": 48.8566,
        "lng": 2.3522,
        "country": "France"
      },
      {
        "place": "Eiffel Tower",
        "lat": 48.8584,
        "lng": 2.2945,
        "country": "France"
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
- **✅ Confirm and Save Changes**: Applies all changes to Firebase
- **❌ Cancel Changes**: Discards all edits and returns to form

**After Saving:**
- Success message with number of fields updated
- Celebration animation (balloons!)
- Option to refresh and edit another book

## Features and Capabilities

### Smart Change Detection
- Only modified fields are sent to Firebase
- Unchanged fields are ignored
- Efficient updates with minimal database writes

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
- **Error messages**: Clear feedback if validation fails

### Safety Features
- **Preview before save**: Always review changes before committing
- **Cancellation**: Can cancel at any time before final save
- **Error handling**: Failed updates don't corrupt existing data
- **Preserves document ID**: Updates in place, no ID changes

## Common Use Cases

### Use Case 1: Fix a Typo
1. Search for the book by title
2. Copy the book ID
3. Correct the typo in the appropriate field
4. Preview → Confirm → Done!

**Example**: Changing "The Grat Gatsby" to "The Great Gatsby"

### Use Case 2: Add Missing Metadata
1. Find the book with incomplete data
2. Fill in missing fields: ISBN, publisher, page count, cover URL, Goodreads link
3. Preview → Confirm → All fields updated simultaneously

**Example**: Adding ISBN 978-0743273565, publisher "Scribner", and page count 180 to a book

### Use Case 3: Update Location Coordinates
1. Select the book
2. Edit the locations JSON array to add/remove/modify coordinates
3. Preview → Confirm → Location data updated

**Example**: Adding a new location or correcting latitude/longitude values

### Use Case 4: Update Tags and Genre
1. Change genre (e.g., "Fiction" → "Historical Fiction")
2. Update tags (e.g., "paris, france, 1920s, expat")
3. Preview → Confirm → Both updated together

**Example**: Reclassifying a book with more specific genre and adding relevant tags

## Advantages Over Export-Delete-Reimport

| Aspect | Old Method (Export/Delete/Import) | New Method (Streamlit Editor) |
|--------|-----------------------------------|-------------------------------|
| **Speed** | Slow (3 steps) | Fast (direct update) |
| **Safety** | Risky (can lose data) | Safe (uses Firestore update) |
| **Document ID** | May change on reimport | Preserved |
| **Preview** | No preview | Full before/after view |
| **Multiple fields** | Edit entire JSON | Visual form with widgets |
| **Validation** | Manual | Automatic |
| **Error recovery** | Can lose data | No data loss on error |
| **User experience** | Technical (JSON editing) | User-friendly (forms) |

## Technical Details

### Backend Implementation

**Batch Update Method**: `update_multiple_fields()`
- Located in: `database/main.py` (FirebaseClient class, lines 112-137)
- Uses Firestore's `update()` method (not `set()`)
- Only modifies specified fields
- Returns success/failure status
- Built-in error handling

**Session State Management**:
- `edit_selected_book`: Currently selected book data
- `edit_show_preview`: Whether to display change preview
- `edit_changes`: Dictionary of field changes to apply

**Change Detection Algorithm**:
1. Compare each form field value with original book data
2. Build dictionary of only changed fields
3. Special handling for type conversions (tags string → array)
4. Preserve unchanged fields completely

### Error Handling

The editor includes comprehensive error handling:

1. **Book not found**: Clear message if book ID doesn't exist
2. **Invalid JSON**: Validation for locations array with error message
3. **Firebase errors**: Try-catch block with user-friendly error display
4. **Number validation**: Min/max ranges enforced by Streamlit widgets
5. **Console logging**: Detailed logs for debugging

## Troubleshooting

### Book ID Not Found
**Problem**: "No book found with ID: xyz"
**Solution**:
- Verify the book ID is correct
- Check you're searching in the right collection (books/midbooks/newbooks)
- Use the search function to find the correct ID

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
- Verify Firebase credentials are valid
- Ensure you have write permissions to the collection
- Check internet connection

### Form Fields Not Pre-populating
**Problem**: Form shows empty fields
**Solution**:
- Ensure the book was found in Step 1
- Check that the book data includes the expected fields
- Use the "View Current Book Data" expander to inspect the book record

## Best Practices

1. **Always preview changes** before confirming to catch mistakes
2. **Use the search function** to find book IDs rather than guessing
3. **Make backups** of collections before major edit sessions
4. **Validate coordinates** when editing location arrays (lat: -90 to 90, lng: -180 to 180)
5. **Use consistent formatting** for tags and genres
6. **Test with a single book** before performing similar edits on multiple books
7. **Check the expanded book data** if unsure about current field values

## Related Documentation

- [About LitMap Database](02_About_LitMap_Database.md) - Database structure and Firebase setup
- [Maintaining the Database](3_Maintaining_the_database.md) - General maintenance procedures
- [Workflow](Workflow.md) - Overall development workflow

## Support

If you encounter issues not covered in this guide:
1. Check the Streamlit console output for error messages
2. Review the Firebase console for database-level issues
3. Consult the [Firebase documentation](https://firebase.google.com/docs/firestore) for Firestore-specific questions
