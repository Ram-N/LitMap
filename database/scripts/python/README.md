# Travel Book JSON Generator

Automatically generate structured JSON data for travel books using Groq LLM and geocoding.

## Quick Start

### 1. Install Dependencies

Using `uv` (recommended):
```bash
cd database/scripts/python
uv pip install -r requirements.txt
```

### 2. Setup API Key

The script will automatically use the `.env` file in `database/scripts/` directory (parent of this folder).

If you need to create a new `.env` file, copy the example:
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

Get a free API key from: https://console.groq.com/keys

**Note**: The script checks for `.env` in multiple locations:
- `database/scripts/python/.env`
- `database/scripts/.env` ← **Your existing file**
- Current working directory

### 3. Run the Script

**Process a CSV file:**
```bash
python generate_travelbooks_json.py ../data/travel-writers-books.csv
```

**Process a text file:**
```bash
python generate_travelbooks_json.py my_books.txt -o output/my_books.json
```

## Features

✅ **Multiple Input Formats**: CSV or plain text
✅ **Smart Location Extraction**: Uses Groq LLM to identify geographic locations
✅ **Automatic Geocoding**: Fetches latitude/longitude coordinates
✅ **Customizable Prompts**: Edit prompt files without touching code
✅ **Progress Saving**: Resume from interruptions
✅ **Rate Limiting**: Respects API limits

## File Structure

```
database/scripts/python/
├── generate_travelbooks_json.py   # Main script
├── prompts/
│   ├── system_prompt.txt          # LLM behavior definition
│   └── book_extraction_prompt.txt # Book processing template
├── requirements.txt               # Python dependencies
├── .env.example                   # Configuration template
├── script_implementation.md       # Detailed documentation
└── README.md                      # This file
```

## Output Format

Generates JSON matching the LitMap schema with:
- Book metadata (title, author, description, genre, etc.)
- Multiple locations with coordinates
- Publication details
- Tags and categories

## Documentation

See [script_implementation.md](./script_implementation.md) for:
- Architecture details
- Usage examples
- Troubleshooting guide
- Customization options
- Cost estimates

## Customizing Prompts

Edit the prompt files in `prompts/` to adjust:
- Location extraction behavior
- Output format preferences
- When to skip books
- Level of detail

No code changes required!

## Examples

**Basic usage:**
```bash
python generate_travelbooks_json.py books.csv
```

**Custom output location:**
```bash
python generate_travelbooks_json.py books.csv -o output/travel_books.json
```

**Resume from book #20:**
```bash
python generate_travelbooks_json.py books.csv -r 20
```

**Use different model:**
```bash
python generate_travelbooks_json.py books.csv -m mixtral-8x7b-32768
```

## Requirements

- Python 3.8+
- Groq API key (free tier available)
- Internet connection (for LLM API and geocoding)

## Support

For issues or questions, see the [script_implementation.md](./script_implementation.md) troubleshooting section.
