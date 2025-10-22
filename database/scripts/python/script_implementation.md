# Travel Book JSON Generator - Implementation Documentation

## Overview

This script processes travel books from CSV or plain text files and generates structured JSON data with location information using the Groq LLM API and geocoding services.

## Architecture

### Components

1. **Main Script**: `generate_travelbooks_json.py`
2. **Prompt Files**:
   - `prompts/system_prompt.txt` - Defines LLM behavior and role
   - `prompts/book_extraction_prompt.txt` - Template for book processing
3. **Configuration**: `.env` file for API keys and settings

### Flow Diagram

```
Input File (CSV/TXT)
    ↓
Read & Parse Books
    ↓
For Each Book:
    ↓
Build Prompt from Template
    ↓
Call Groq LLM API
    ↓
Parse JSON Response
    ↓
Geocode Locations (Nominatim)
    ↓
Save Progress
    ↓
Output: Complete JSON Array
```

## Features

### Input Handling

**CSV Format:**
- Reads columns: `Author`, `Book`, `Country`, `Location`, `ISBN`, `Year`
- Example: `database/data/travel-writers-books.csv`

**Plain Text Format:**
- Supports multiple formats:
  - `Author - Book Title`
  - `Book Title by Author`
  - Just `Book Title` (one per line)
- Paragraph-separated entries (double newline)

### LLM Processing

- **Provider**: Groq (fast inference, cost-effective)
- **Default Model**: `llama-3.3-70b-versatile`
- **Temperature**: 0.3 (balanced creativity and consistency)
- **Max Tokens**: 4096

The LLM extracts:
- Book metadata (title, author, description, genre, etc.)
- Multiple geographic locations
- Location context and descriptions
- Publication details

### Geocoding

- **Service**: OpenStreetMap Nominatim (free, no API key required)
- **Rate Limiting**: 1.5 seconds between calls (respects OSM ToS)
- **Retry Logic**: 3 attempts with exponential backoff
- **Output**: Latitude and longitude rounded to 4 decimal places (~11m accuracy)

### Error Handling

1. **Skip Books**: If LLM cannot determine clear locations
2. **Retry Logic**: API failures retry with exponential backoff
3. **Progress Saving**: Output file updated after each successful book
4. **Resume Support**: Can resume from specific book index

## Configuration

### Environment Variables

Create a `.env` file in the `scripts/python/` directory:

```bash
GROQ_API_KEY=your_actual_api_key_here
```

Get your API key from: https://console.groq.com/keys

### Command-Line Options

```bash
# Basic usage
python generate_travel_books.py input.csv

# Specify output file
python generate_travel_books.py input.csv -o output/my_books.json

# Use different model
python generate_travel_books.py input.csv -m mixtral-8x7b-32768

# Resume from book #10 (after interruption)
python generate_travel_books.py input.csv -r 10

# Adjust rate limiting
python generate_travel_books.py input.csv --rate-limit 2.0 --geocode-delay 2.0
```

### Available Groq Models

- `llama-3.3-70b-versatile` (default, recommended)
- `llama-3.1-70b-versatile`
- `mixtral-8x7b-32768`
- `gemma2-9b-it`

## Usage Examples

### Example 1: Process CSV File

```bash
cd database/scripts/python
python generate_travelbooks_json.py ../data/travel-writers-books.csv
```

Output: `output/travel_books_generated.json`

### Example 2: Process Plain Text File

Create `my_books.txt`:
```
Patrick Leigh Fermor - A Time of Gifts
The Places In Between by Rory Stewart
Arabian Sands
```

Run:
```bash
python generate_travelbooks_json.py my_books.txt -o output/my_books.json
```

### Example 3: Resume After Interruption

If processing stops at book #15:
```bash
python generate_travelbooks_json.py input.csv -r 15
```

## Output Format

The script generates a JSON array matching the LitMap schema:

```json
[
  {
    "title": "Arabian Sands",
    "author": "Wilfred Thesiger",
    "description": "A classic travelogue...",
    "booktype": "Nonfiction",
    "publicationDate": "1959",
    "genre": "Travel Literature",
    "rating": null,
    "pageCount": 330,
    "isbn": "9780141442075",
    "language": "English",
    "publisher": "Longmans",
    "coverImageUrl": null,
    "addedBy": "LitMap_AI",
    "tags": ["Arabian Peninsula", "Desert Exploration"],
    "locations": [
      {
        "city": "Salalah",
        "country": "Oman",
        "latitude": 17.02,
        "longitude": 54.11,
        "description": "Starting point for crossing the Empty Quarter"
      }
    ]
  }
]
```

## Customizing Prompts

### Why Separate Prompt Files?

- **Easy Tweaking**: Modify prompts without touching code
- **Version Control**: Track prompt changes separately
- **Experimentation**: Test different prompt strategies quickly
- **Maintenance**: Non-technical users can improve prompts

### Editing Prompts

**System Prompt** (`prompts/system_prompt.txt`):
- Defines the LLM's role and expertise
- Sets output quality guidelines
- Specifies when to skip books

**Book Extraction Prompt** (`prompts/book_extraction_prompt.txt`):
- Uses template variables: `{title}`, `{author}`, `{additional_info}`
- Defines JSON output structure
- Provides specific instructions for location extraction

### Template Variables

Available in `book_extraction_prompt.txt`:
- `{title}`: Book title
- `{author}`: Author name
- `{additional_info}`: Additional metadata (country, location, ISBN, year)

Example modification:
```text
Analyze the following travel book published in {year}:

Title: {title}
Author: {author}
Region: {additional_info}

Focus on extracting locations the author physically visited...
```

## Rate Limiting & Performance

### Recommended Settings

- **LLM Rate Limit**: 1.0 seconds (default)
  - Prevents API throttling
  - ~3600 books per hour maximum

- **Geocoding Delay**: 1.5 seconds (default)
  - Respects Nominatim usage policy
  - Allows ~2400 locations per hour

### Performance Estimates

For 100 books with 3 locations each:
- LLM calls: ~100 seconds (1.7 minutes)
- Geocoding: ~450 seconds (7.5 minutes)
- **Total**: ~10-12 minutes

## Troubleshooting

### Common Issues

**1. "GROQ_API_KEY not found"**
- Solution: Create `.env` file with your API key
- Check: File is in `scripts/python/` directory

**2. "Could not geocode: City, Country"**
- Cause: Location name not recognized by OpenStreetMap
- Solution: LLM will leave lat/lng as null, geocode manually later
- Note: Script continues processing other locations

**3. "JSON parsing error"**
- Cause: LLM returned invalid JSON
- Solution: Check/improve prompts for clearer instructions
- Tip: Look at response preview in error message

**4. Rate limit errors from Groq**
- Solution: Increase `--rate-limit` delay
- Example: `--rate-limit 2.0`

**5. Geocoding timeout errors**
- Solution: Increase `--geocode-delay`
- Example: `--geocode-delay 2.5`

### Debug Tips

1. **Test with small input**: Start with 2-3 books
2. **Check prompt output**: Add print statements to see LLM responses
3. **Validate JSON**: Use online JSON validators
4. **Monitor API usage**: Check Groq console for quota

## Integration with LitMap

### Upload to Firestore

After generation, use the Streamlit admin interface:

```bash
cd database
streamlit run main.py
```

Use the JSON upload feature to import generated books.

### Manual Review

Recommended checks before upload:
- Verify location coordinates on a map
- Check for duplicate books
- Validate ISBN numbers
- Review genre classifications

## Cost Estimation

### Groq API Costs

Groq offers:
- **Free tier**: Limited requests per day
- **Pay-as-you-go**: Very low cost (~$0.10-0.20 per 1M tokens)

Typical book processing:
- Input: ~200 tokens (prompt)
- Output: ~500 tokens (JSON)
- **Cost per book**: ~$0.00007 (essentially free)

### Geocoding Costs

- **Nominatim**: FREE
- **Usage policy**: 1 request per second maximum
- Alternative: Google Geocoding API (paid, more accurate)

## Advanced Usage

### Batch Processing Multiple Files

```bash
for file in inputs/*.txt; do
    python generate_travelbooks_json.py "$file" -o "output/$(basename $file .txt).json"
done
```

### Using Different Models for Comparison

```bash
# Fast, smaller model
python generate_travelbooks_json.py input.csv -m gemma2-9b-it -o output/gemma.json

# Larger, more accurate model
python generate_travelbooks_json.py input.csv -m llama-3.3-70b-versatile -o output/llama.json
```

### Custom Post-Processing

After generation, you can:
1. Merge multiple JSON outputs
2. Add custom fields
3. Validate against schema
4. Enrich with additional APIs (Goodreads, Google Books)

## Future Enhancements

Potential improvements:
- [ ] Add cover image fetching (Google Books API)
- [ ] Support for JSONL input format
- [ ] Parallel processing for multiple books
- [ ] Interactive mode for manual review
- [ ] Goodreads integration for ratings
- [ ] Web interface (Streamlit app)
- [ ] Caching to avoid re-processing same books

## Contributing

To improve this script:
1. Test with diverse book types
2. Refine prompts for better accuracy
3. Add error recovery mechanisms
4. Improve geocoding fallbacks

## License

Part of the LitMap project - see main repository for license details.

## Support

For issues or questions:
- Check this documentation
- Review prompt files
- Test with example data
- Check Groq API status: https://status.groq.com/
