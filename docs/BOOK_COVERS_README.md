# Book Cover Management Tool

## Overview

`book-covers-admin.html` is a web-based tool for reviewing and updating book covers for all books in your LitMap database.

## Features

- **View all books** from any Firestore collection (books, midbooks, newbooks)
- **See current cover status** for each book with visual preview
- **Fetch alternative covers** from multiple sources:
  - Open Library API (free, no API key needed)
  - Google Books API (optional, requires free API key)
- **Edit and update covers** in bulk with batch operations
- **Filter books** by missing covers or broken images
- **Export to CSV** for offline editing
- **Preview covers** before saving

## How to Use

### 1. Open the Tool

Open `book-covers-admin.html` in your web browser:

```bash
# Option 1: Simple HTTP server
cd /home/ram/projects/LitMap
python -m http.server 8000
# Then visit: http://localhost:8000/book-covers-admin.html

# Option 2: Open directly in browser
open book-covers-admin.html  # macOS
xdg-open book-covers-admin.html  # Linux
```

### 2. Configure (Optional)

**Google Books API Key** (Optional but Recommended):
- Get a free API key from [Google Cloud Console](https://console.cloud.google.com/)
- Enable the "Books API"
- Copy your API key
- Paste it into the "Google Books API Key" field
- Limit: 1000 requests/day (free tier)

### 3. Load Books

1. Select your collection (default: "books")
2. Click **"Load Books"**
3. Wait while the tool:
   - Fetches all books from Firestore
   - Checks Open Library for covers
   - Checks Google Books for covers (if API key provided)
   - Displays results in the table

### 4. Review Covers

The table shows:
- **Book Info**: Title, author, ISBN
- **Current Cover**: Visual preview of existing cover
- **Current URL**: The URL currently stored in Firestore
- **Alternative Sources**: Up to 2-3 alternative covers from different APIs
- **New Cover URL**: Editable field to paste or modify URLs

**Visual Indicators**:
- Yellow background = Missing cover
- Red border on image = Broken/invalid image URL

### 5. Update Covers

**Option 1: Use Alternative Source**
- Click **"Use This"** button under any alternative cover
- The URL will be copied to the "New Cover URL" field
- The book will be auto-selected

**Option 2: Manual URL Entry**
- Find a cover image elsewhere (Google Images, Amazon, etc.)
- Right-click → "Copy Image Address"
- Paste into the "New Cover URL" field
- Check the checkbox to select the book

**Option 3: Edit Existing URL**
- Modify the URL in the "New Cover URL" field
- Check the checkbox to select the book

### 6. Preview (Optional)

Click **"Preview"** button to open the cover URL in a new tab and verify it looks correct.

### 7. Save Changes

1. Select all books you want to update (checkboxes)
2. Click **"Update Selected"** button
3. Confirm the batch update
4. Wait for completion message

The tool will:
- Update the `cover` field in Firestore
- Add a `coverLastUpdated` timestamp
- Show success/error counts

### 8. Export (Optional)

Click **"Export to CSV"** to download a CSV file with:
- Current cover URLs
- New cover URLs
- Book metadata

Useful for:
- Offline review
- Sharing with others
- Backup before bulk changes

## Filters

Use the **Filter** dropdown to show:
- **All Books**: Every book in the collection
- **Missing Covers Only**: Books with no cover URL
- **Broken Images Only**: Books where the cover URL failed to load

## Tips

1. **Start with "Missing Covers Only"** filter to focus on books that need attention
2. **Use Google Books API** for better cover quality and coverage
3. **Preview before saving** to ensure covers are correct
4. **Work in batches** - select 10-20 books at a time
5. **Export to CSV** before making bulk changes as a backup
6. **Check ISBN accuracy** - wrong ISBN = wrong cover

## Troubleshooting

### No alternative covers showing
- **Cause**: Missing or incorrect ISBN
- **Solution**: Update ISBN in Firestore using Streamlit admin tool

### Google Books not working
- **Cause**: No API key or invalid key
- **Solution**: Get API key from Google Cloud Console, ensure Books API is enabled

### Covers not updating in main app
- **Cause**: Frontend uses live Open Library API, not Firestore `cover` field
- **Solution**: Update frontend code to use `book.cover` field from Firestore

### Rate limiting errors
- **Open Library**: Max 100 requests per 5 minutes
- **Google Books**: Max 1000 requests per day (free tier)
- **Solution**: Wait and retry, or work in smaller batches

## Data Model

The tool updates these Firestore fields:

```javascript
{
  "cover": "https://...",  // Main cover URL (updated by this tool)
  "coverUrls": {           // Alternative sizes (not used by this tool)
    "S": "https://...",
    "M": "https://...",
    "L": "https://..."
  },
  "coverLastUpdated": "2025-01-15T10:30:00Z"
}
```

## Next Steps

After updating covers with this tool, you may want to:

1. **Update frontend** to use `book.cover` instead of live API calls
2. **Add cover validation** to prevent broken URLs
3. **Automate cover fetching** for new books
4. **Add more cover sources** (Amazon, LibraryThing, etc.)

## Technical Details

- **Framework**: Vanilla JavaScript with Firebase SDK v10.13.1
- **APIs Used**: Firestore, Open Library, Google Books
- **Rate Limiting**: 100ms delay between API calls
- **Image Validation**: HEAD request to check URL validity
- **Security**: Client-side only, uses Firebase web SDK

---

**Questions or issues?** Check the main LitMap documentation or Firebase console for data debugging.
