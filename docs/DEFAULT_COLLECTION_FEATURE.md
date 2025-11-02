# Default Collection Feature

## Overview
Added a persistent default collection preference that remembers your preferred collection across app sessions.

## How It Works

### In the Sidebar
1. **Collection Dropdown**: Select your collection (books, midbooks, or newbooks)
2. **Checkbox Below**: "Set '[collection_name]' as default"
   - Check this box to save your preference
   - Uncheck to clear the default

### User Experience

#### Setting a Default Collection
1. Select a collection from the dropdown (e.g., "books")
2. Check the box "Set 'books' as default"
3. See success message: "✅ 'books' set as default!"
4. Next time you open the app, "books" will be automatically selected

#### Changing the Default
1. Select a different collection from the dropdown (e.g., "newbooks")
2. Check the box "Set 'newbooks' as default"
3. The new collection becomes the default
4. Previous default is replaced

#### Clearing the Default
1. With a default collection set, uncheck the checkbox
2. See info message: "ℹ️ Default collection cleared"
3. Next time you open the app, it will default to "midbooks" (fallback default)

## Technical Implementation

### Persistence
- Preferences stored in: `user_preferences.json` (in database directory)
- File structure:
  ```json
  {
    "default_collection": "books"
  }
  ```
- File is excluded from git via `.gitignore`

### Functions Added
- `load_user_preferences()` - Reads from JSON file
- `save_user_preferences()` - Writes to JSON file
- `get_default_collection()` - Retrieves saved default
- `set_default_collection(name)` - Saves a default
- `clear_default_collection()` - Removes the default

### Behavior
- **On app startup**: Loads saved preference and selects that collection
- **If no preference**: Falls back to index 1 (midbooks)
- **Invalid preference**: Falls back to index 1 (midbooks)
- **Real-time updates**: Checkbox state syncs with current selection

## Benefits
1. **Time savings**: No need to change collection every time you open the app
2. **Workflow efficiency**: Frequent users can set their primary working collection
3. **User-friendly**: Simple checkbox interface, clear feedback messages
4. **Persistent**: Preference survives app restarts, system reboots

## Example Workflow

### Scenario: Database Admin who primarily works with "books" collection

**Day 1:**
1. Open Streamlit app (defaults to "midbooks")
2. Change to "books"
3. Check "Set 'books' as default"
4. Work with books collection

**Day 2 onwards:**
1. Open Streamlit app
2. ✅ Automatically on "books" collection
3. Start working immediately (no manual selection needed)

**When testing with "newbooks":**
1. Temporarily switch to "newbooks" (don't check the box)
2. Work with newbooks
3. Refresh app → Returns to "books" (your saved default)

**To stop using default:**
1. Uncheck the "Set 'books' as default" box
2. App will return to "midbooks" on next launch
