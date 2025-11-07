# Setup Instructions

## Current Status

✅ Your `.env` file with GROQ_API_KEY is already in `database/scripts/` directory
⚠️ Python dependencies need to be installed

## Installation Steps

### 1. Install Dependencies

Using `uv` (as per LitMap project standards):

```bash
cd database/scripts/python
uv pip install -r requirements.txt
```

This will install:
- `groq` - Groq API client
- `pandas` - CSV processing
- `geopy` - Geocoding
- `python-dotenv` - Environment variable loading

### 2. Verify Setup

After installation, test that everything works:

```bash
python verify_setup.py
```

You should see:
```
✅ Found .env at: /path/to/database/scripts/.env
✅ GROQ_API_KEY is set
✅ groq package installed
✅ pandas package installed
✅ geopy package installed
```

### 3. Test Run

Try processing the test file:

```bash
python generate_travelbooks_json.py test_books.txt -o output/test_output.json
```

This will process 3 sample books and create `output/test_output.json`.

## Troubleshooting

### Issue: "GROQ_API_KEY not found"

**Solution**: The script automatically looks for `.env` in:
1. `database/scripts/python/.env`
2. `database/scripts/.env` ← Your file is here
3. Current working directory

Make sure you're running the script from the correct location or that your `.env` has:
```
GROQ_API_KEY=your_actual_key_here
```

### Issue: "No module named 'groq'" or similar

**Solution**: Install dependencies:
```bash
cd database/scripts/python
uv pip install -r requirements.txt
```

### Issue: Geocoding timeout errors

**Solution**: The script has built-in rate limiting. If you still get errors, increase the delay:
```bash
python generate_travel_books.py input.csv --geocode-delay 2.5
```

## Quick Reference

```bash
# Basic usage
python generate_travelbooks_json.py input.csv

# Specify output location
python generate_travelbooks_json.py input.csv -o output/my_books.json

# Resume from interruption (book index 10)
python generate_travelbooks_json.py input.csv -r 10

# Use different model
python generate_travelbooks_json.py input.csv -m mixtral-8x7b-32768

# Adjust rate limits
python generate_travelbooks_json.py input.csv --rate-limit 2.0 --geocode-delay 2.0
```

## Next Steps

Once setup is complete:
1. Process your `travel-writers-books.csv` file
2. Review the generated JSON output
3. Customize prompts in `prompts/` directory as needed
4. Upload results to Firestore using the Streamlit admin interface

See [script_implementation.md](./script_implementation.md) for detailed documentation.
