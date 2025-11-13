# 3. Maintaining the Database

This document explains how to manage the LitMap Firebase database using the Streamlit admin interface and how to deploy changes to Firebase.

## Prerequisites

- Python environment with required packages
- Firebase service account credentials
- Access to Firebase Console for rule updates

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
uv pip install streamlit firebase-admin pandas

# Navigate to database directory
cd database/
```

**Alternative: One-step setup with uv**
```bash
# Navigate to database directory
cd /home/ram/projects/LitMap/database

# Run with uv (automatically manages virtual environment)
uv run --with streamlit,firebase-admin,pandas streamlit run main.py
```

**Traditional pip method (if needed):**
```bash
# Create virtual environment
python3 -m venv litmap-env
source litmap-env/bin/activate
pip install streamlit firebase-admin pandas
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
- **View Collections**: Browse different Firestore collections (`newbooks`, `midbooks`, etc.)
- **Document Count**: See total documents in each collection
- **Search Books**: Find books by title, author, or other attributes
- **Add Books**: Import new books from JSON files or manual entry
- **Edit Books**: Modify existing book records
- **Delete Books**: Remove individual books or bulk operations

#### Data Management
- **Duplicate Detection**: Find and merge duplicate book entries
- **Backup Collections**: Export collection data to JSON files
- **Bulk Operations**: Add multiple books from data files
- **Location Management**: Add/edit geographical locations for books

#### Key Data Files
- `books_master.js` - Main book dataset
- `locations_master.js` - Location reference data
- `data/` - Individual book JSON files
- `backup/` - Collection backups with timestamps

### 4. Database Schema

Books in Firestore contain:
```json
{
  "title": "Book Title",
  "author": "Author Name",
  "description": "Book description",
  "booktype": "fiction|nonfiction|travel|poetry",
  "genre": "Genre",
  "tags": ["tag1", "tag2"],
  "locations": [
    {
      "city": "City Name",
      "country": "Country",
      "lat": 12.3456,
      "lng": 78.9012,
      "description": "Location context in book"
    }
  ],
  "isbn": "ISBN number",
  "rating": 4.2,
  "pageCount": 300,
  "publicationDate": "YYYY-MM-DD",
  "coverImage": "URL to cover image",
  "goodreadsUrl": "Goodreads link"
}
```

## Database Utilities

### Python Scripts

Located in `/database/`:

```bash
# Create JSON from data sources
python create_JSON.py

# Fetch book cover images
python get_book_covers.py

# Test Firebase connection
python firebase-connect.py

# Test database operations
python test.py
```

### JavaScript Data Files

- `books_master.js` - Main book collection
- `locations_master.js` - Location reference data
- `data.js` - Formatted data for import
- `new1.js` - New book additions

## Firebase Deployment

### 1. Frontend Deployment

Deploy the web application to Firebase Hosting:

```bash
# From project root directory
firebase deploy
```

This deploys:
- Static files (HTML, CSS, JS)
- Updated Firestore rules
- Firebase configuration

### 2. Database Rules Deployment

Deploy only Firestore security rules:

```bash
firebase deploy --only firestore:rules
```

### 3. Manual Rule Updates

If Firebase CLI isn't available:

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select project: `litmap-88358`
3. Navigate to **Firestore Database** → **Rules**
4. Update rules manually
5. Click **Publish**

### 4. Firebase Configuration Files

- `firebase.json` - Hosting and Firestore configuration
- `firestore.rules` - Database security rules
- `firestore.indexes.json` - Database indexes
- `.firebaserc` - Project configuration

## Workflow Summary

### Adding New Books

1. **Prepare Data**: Create JSON files in `/database/data/`
2. **Run Streamlit**: `streamlit run main.py`
3. **Import Books**: Use the admin interface to upload new books
4. **Verify Data**: Check for duplicates and validate locations
5. **Deploy**: `firebase deploy` to push changes live

### Updating Existing Books

1. **Edit via Streamlit**: Use the search and edit features
2. **Backup First**: Export collection before major changes
3. **Test Locally**: Verify changes work on localhost
4. **Deploy**: Push updates to production

### Database Maintenance

1. **Regular Backups**: Export collections periodically
2. **Duplicate Cleanup**: Use Streamlit tools to find and merge duplicates
3. **Data Validation**: Ensure all books have proper location coordinates
4. **Security Rules**: Keep Firestore rules updated and secure

## Troubleshooting

### Common Issues

**Permission Errors**:
- Check Firestore rules expiration dates
- Verify service account credentials
- Update rules in Firebase Console

**Streamlit Connection Issues**:
- Verify `litmap-88358-firebase-adminsdk-*.json` exists
- Check Python environment activation
- Ensure Firebase Admin SDK is installed

**Deployment Failures**:
- Verify Firebase CLI authentication
- Check project configuration in `.firebaserc`
- Ensure proper permissions for Firebase project

### Environment Setup

**Using uv (recommended):**
```bash
# Install required packages with uv
uv pip install streamlit firebase-admin pandas

# Or create and use virtual environment
uv venv .venv
source .venv/bin/activate
uv pip install streamlit firebase-admin pandas

# Or run directly with dependencies
uv run --with streamlit,firebase-admin,pandas streamlit run database/main.py
```

**Traditional pip method:**
```bash
# Install required packages
pip install streamlit firebase-admin pandas

# Or from requirements file
pip install -r requirements.txt
```

## Security Notes

- **Service Account Key**: Never commit `litmap-88358-firebase-adminsdk-*.json` to public repos
- **API Keys**: Keep Firebase configuration secure
- **Rules**: Regularly review and update Firestore security rules
- **Backups**: Maintain regular backups before major data operations