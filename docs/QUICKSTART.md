# LitMap Quick Start Guide

Quick reference for getting back into LitMap development.

## Quick Navigation
```bash
cdlit                    # Navigate to project (if you have the alias)
cd ~/projects/LitMap     # Or manually
```

## Your Aliases
```bash
alias cdlit='cd ~/projects/LitMap'           # Navigate to project
alias litenv='source litmap-env/bin/activate' # Activate venv (if needed)
alias runlit='cd ~/projects/LitMap/; wserve'  # Run LitMap locally
alias runstream='uv run streamlit run main.py' # Run Streamlit admin
alias uview='uv run streamlit run viewer.py'   # Run viewer (PhotoScribe)
```

## Common Workflows

### Running LitMap Locally
```bash
runlit                          # Quick way (using alias)
python -m http.server 8000      # Or manually from project root
wserve                          # Or using wserve (if available)
# Then open: http://localhost:8000
```

### Database Admin Interface
```bash
cd database/
runstream                       # Run Streamlit admin (using alias)
# Or manually: uv run streamlit run main.py
# Opens at: http://localhost:8501
```
**What you can do:** Add/edit books, search/filter, manage duplicates, backup collections, geocode addresses

### Adding New Books (LLM Method)
1. **Add books to input file:**
   ```bash
   nano database/input_data/books1.txt  # Edit with book list (one per line or CSV)
   ```
2. **Run the LLM generator:**
   ```bash
   cd database/
   python python/generate_travelbooks_json.py input_data/books1.txt -o output/my-books.json
   ```
3. **Review and import:** Check `database/output/` and import via Streamlit admin

**Requirements:** Groq API key in `database/.env` (see `database/python/README.md`)

## Development Commands

### Frontend Development
```bash
python -m http.server 8000      # From project root
# Make changes to HTML/CSS/JS, refresh browser (no build step)
```

### Database Scripts
```bash
cd database/
uv run python get_book_covers.py          # Get book covers from Open Library
uv run python create_JSON.py              # Generate JSON from Firestore
uv run python firebase-connect.py         # Test Firebase connection
```

### Deployment
```bash
firebase deploy                 # Deploy to Firebase Hosting
# Note: GitHub Pages auto-deploys from main branch
# Live at: https://ram-n.github.io/LitMap/
```

## Project Structure
```
LitMap/
├── index.html              # Main app entry
├── scripts/
│   ├── app.js             # Core logic
│   ├── firebase.js        # Firebase config
│   └── map.js             # Google Maps
├── database/
│   ├── main.py            # Streamlit admin
│   ├── python/            # LLM book generator
│   ├── input_data/        # Input files for processing
│   └── output_json/       # Generated data
└── docs/                  # Documentation
```

## Common Tasks
| Task | Command |
|------|---------|
| Run app locally | `wserve` or `python -m http.server 8000` |
| Database admin | `cd database/ && runstream` |
| Add books (LLM) | `cd database/ && python python/generate_travelbooks_json.py input_data/books1.txt -o output/result.json` |
| Deploy | `firebase deploy` |
| Check Firebase | Check Firebase Console for Firestore data |

## Troubleshooting

**Firebase Permission Errors:** Check `firestore.rules`, verify service account credentials in `database/`

**Package Installation Issues:** Always use `uv` for Python packages. Install: `uv pip install -r requirements.txt`

**Google Maps Not Loading:** Verify API key in `scripts/firebase.js`, check Maps JavaScript API is enabled, ensure billing enabled

**Missing Favicon:** Add `favicon.ico` to project root to eliminate 404 errors

## Important Notes
- **Package Manager**: Always use `uv` for Python, never conda/pip directly
- **No Build Process**: Static files served directly (HTML/CSS/JS)
- **Database Changes**: Use Streamlit admin or Python scripts
- **Credentials**: Firebase service account key in `database/litmap-88358-firebase-adminsdk-*.json`

## Environment Setup (Fresh Start)
```bash
cd ~/projects/LitMap
uv pip install -r requirements.txt
ls database/litmap-88358-firebase-adminsdk-*.json    # Ensure credentials exist
npm install -g firebase-tools                        # Install Firebase CLI if needed
wserve  # or python -m http.server 8000
```

## Next Steps
- **Database details**: `docs/04_Editing_Database_Fields.md`
- **Full setup guide**: `docs/01_How_to_Run_LitMap.md`
- **Technical details**: `CLAUDE.md`
- **LLM script docs**: `database/python/README.md`

---
**Need Help?** Check the docs/ directory or CLAUDE.md for detailed information.
