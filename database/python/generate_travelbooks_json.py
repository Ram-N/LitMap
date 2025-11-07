#!/usr/bin/env python3
"""
Travel Book JSON Generator
Processes CSV or plain text files of travel books and generates structured JSON
with location data using Groq LLM and geocoding.
"""

import os
import json
import csv
import time
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from dotenv import load_dotenv
from groq import Groq
from rapidfuzz import fuzz

# Load environment variables from scripts/.env (parent directory)
script_dir = Path(__file__).parent
env_paths = [
    script_dir / '.env',              # scripts/python/.env
    script_dir.parent / '.env',       # scripts/.env
    Path.cwd() / '.env'               # current working directory
]

# Try to load .env from multiple locations
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        break


class TravelBookGenerator:
    """Main class for generating travel book JSON data."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "llama-3.3-70b-versatile",
        rate_limit_delay: float = 1.0,
        geocode_delay: float = 1.5
    ):
        """
        Initialize the generator.

        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            model: Groq model to use
            rate_limit_delay: Delay between LLM API calls (seconds)
            geocode_delay: Delay between geocoding calls (seconds)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")

        self.client = Groq(api_key=self.api_key)
        self.model = model
        self.rate_limit_delay = rate_limit_delay
        self.geocode_delay = geocode_delay

        # Initialize geocoder
        self.geolocator = Nominatim(user_agent="litmap_book_generator")

        # Load prompts
        self.system_prompt = self._load_prompt("prompts/system_prompt.txt")
        self.book_extraction_template = self._load_prompt("prompts/book_extraction_prompt.txt")

        # Statistics
        self.stats = {
            "processed": 0,
            "successful": 0,
            "skipped": 0,
            "duplicates_skipped": 0,
            "potential_duplicates_logged": 0,
            "errors": 0
        }

        # Track failed books
        self.failed_books = []

        # Track potential duplicates for logging
        self.potential_duplicates = []

        # Existing books cache
        self.existing_books = set()

        # Store full book data for fuzzy matching
        self.existing_books_data = []

    def _load_prompt(self, relative_path: str) -> str:
        """Load a prompt from a file."""
        script_dir = Path(__file__).parent
        prompt_path = script_dir / relative_path

        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()

    def _get_latest_backup_file(self) -> Optional[Path]:
        """Find the latest backup JSON file in database/backup/."""
        script_dir = Path(__file__).parent
        backup_dir = script_dir.parent / "backup"

        if not backup_dir.exists():
            print(f"⚠️  Backup directory not found: {backup_dir}")
            return None

        # Find all books_*.json files
        backup_files = list(backup_dir.glob("books_*.json"))

        if not backup_files:
            print(f"⚠️  No backup files found in {backup_dir}")
            return None

        # Return the most recently modified file
        latest_file = max(backup_files, key=lambda p: p.stat().st_mtime)
        return latest_file

    def load_existing_books(self, backup_file: Optional[str] = None) -> None:
        """
        Load existing books from backup JSON file.

        Args:
            backup_file: Optional path to specific backup file.
                        If None, uses latest file from database/backup/
        """
        if backup_file:
            backup_path = Path(backup_file)
        else:
            backup_path = self._get_latest_backup_file()

        if not backup_path or not backup_path.exists():
            print("⚠️  No existing books loaded - will process all books")
            return

        print(f"📚 Loading existing books from: {backup_path}")

        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)

            # Create set of (title, author) tuples in lowercase for case-insensitive matching
            # Also store full book data for fuzzy matching
            for book in existing_data:
                title = book.get('title', '').lower().strip()
                author = book.get('author', '').lower().strip()

                if title and author:
                    self.existing_books.add((title, author))
                    # Store full data for fuzzy matching
                    self.existing_books_data.append({
                        'title': title,
                        'author': author,
                        'original_title': book.get('title', ''),
                        'original_author': book.get('author', '')
                    })

            print(f"✅ Loaded {len(self.existing_books)} existing books")

        except Exception as e:
            print(f"⚠️  Error loading existing books: {e}")
            print("   Will process all books without duplicate checking")

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity score between two strings using Levenshtein distance.

        Args:
            str1: First string
            str2: Second string

        Returns:
            Similarity score from 0-100 (100 = identical)
        """
        return fuzz.ratio(str1.lower().strip(), str2.lower().strip())

    def _find_similar_books(self, title: str, author: str, similarity_threshold: float = 85.0) -> List[Dict[str, Any]]:
        """
        Find existing books with similar title and author using fuzzy matching.

        Args:
            title: Book title to search for
            author: Book author to search for
            similarity_threshold: Minimum similarity score (0-100) for both title and author

        Returns:
            List of matching books with similarity scores
        """
        similar_books = []
        title_lower = title.lower().strip()
        author_lower = author.lower().strip()

        for existing_book in self.existing_books_data:
            title_similarity = self._calculate_similarity(title_lower, existing_book['title'])
            author_similarity = self._calculate_similarity(author_lower, existing_book['author'])

            # Both title and author must meet threshold
            if title_similarity >= similarity_threshold and author_similarity >= similarity_threshold:
                similar_books.append({
                    'existing_title': existing_book['original_title'],
                    'existing_author': existing_book['original_author'],
                    'title_similarity': round(title_similarity, 2),
                    'author_similarity': round(author_similarity, 2)
                })

        return similar_books

    def _is_duplicate(self, title: str, author: str) -> bool:
        """
        Check if book already exists in database using exact match (case-insensitive).
        For fuzzy matching, use _find_similar_books instead.

        Args:
            title: Book title
            author: Book author

        Returns:
            True if book exists (exact match), False otherwise
        """
        title_lower = title.lower().strip()
        author_lower = author.lower().strip()

        return (title_lower, author_lower) in self.existing_books

    def _log_potential_duplicate(self, new_book_title: str, new_book_author: str, similar_books: List[Dict[str, Any]]) -> None:
        """
        Log a potential duplicate for manual review.

        Args:
            new_book_title: Title of the new book being processed
            new_book_author: Author of the new book being processed
            similar_books: List of similar existing books with similarity scores
        """
        duplicate_entry = {
            'timestamp': datetime.now().isoformat(),
            'new_book': {
                'title': new_book_title,
                'author': new_book_author
            },
            'similar_existing_books': similar_books
        }

        self.potential_duplicates.append(duplicate_entry)
        self.stats['potential_duplicates_logged'] += 1

        # Print warning to console
        print(f"   ⚠️  Potential duplicate detected!")
        for match in similar_books:
            print(f"      Similar to: \"{match['existing_title']}\" by {match['existing_author']}")
            print(f"      Similarity: Title {match['title_similarity']}%, Author {match['author_similarity']}%")

    def _save_potential_duplicates(self, output_dir: str = "output") -> None:
        """
        Save potential duplicates to a JSON file for manual review.

        Args:
            output_dir: Directory to save the duplicates file
        """
        if not self.potential_duplicates:
            return

        output_path = Path(output_dir) / "potential_duplicates.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.potential_duplicates, f, indent=2, ensure_ascii=False)

            print(f"\n📋 Potential duplicates logged to: {output_path}")
        except Exception as e:
            print(f"\n⚠️  Error saving potential duplicates: {e}")

    def _detect_input_format(self, file_path: str) -> str:
        """Detect if input is CSV or plain text."""
        if file_path.lower().endswith('.csv'):
            return 'csv'
        return 'txt'

    def _map_csv_column(self, df: pd.DataFrame, possible_names: List[str], default: str = '') -> str:
        """
        Find and return the first matching column name from a list of possibilities.

        Args:
            df: DataFrame to search
            possible_names: List of possible column names (case-insensitive)
            default: Default value if no match found

        Returns:
            The actual column name found in the DataFrame, or None if not found
        """
        # Create case-insensitive mapping
        column_map = {col.lower(): col for col in df.columns}

        for name in possible_names:
            if name.lower() in column_map:
                return column_map[name.lower()]
        return None

    def _read_csv_input(self, file_path: str) -> List[Dict[str, str]]:
        """Read books from CSV file with intelligent column mapping."""
        books = []
        df = pd.read_csv(file_path)

        print(f"   CSV columns detected: {', '.join(df.columns)}")

        # Map column names (try multiple common variations)
        title_col = self._map_csv_column(df, ['Title', 'Book', 'title', 'book'])
        author_col = self._map_csv_column(df, ['Author', 'author', 'Authors', 'authors'])
        isbn_col = self._map_csv_column(df, ['ISBN', 'isbn', 'Isbn', 'ISBN13', 'isbn13'])
        description_col = self._map_csv_column(df, ['Description', 'description', 'Summary', 'summary', 'Synopsis', 'synopsis'])
        country_col = self._map_csv_column(df, ['Country', 'country'])
        location_col = self._map_csv_column(df, ['Location', 'location', 'City', 'city'])
        year_col = self._map_csv_column(df, ['Year', 'year', 'Publication Year', 'publication_year', 'PublicationYear'])

        # Print mapping info
        print(f"   Column mapping:")
        print(f"      Title: {title_col or 'NOT FOUND'}")
        print(f"      Author: {author_col or 'NOT FOUND'}")
        if isbn_col:
            print(f"      ISBN: {isbn_col}")
        if description_col:
            print(f"      Description: {description_col}")
        if country_col:
            print(f"      Country: {country_col}")
        if location_col:
            print(f"      Location: {location_col}")
        if year_col:
            print(f"      Year: {year_col}")
        print()

        for _, row in df.iterrows():
            book = {
                'title': str(row[title_col]).strip() if title_col and pd.notna(row[title_col]) else '',
                'author': str(row[author_col]).strip() if author_col and pd.notna(row[author_col]) else '',
                'isbn': str(row[isbn_col]).strip() if isbn_col and pd.notna(row[isbn_col]) else '',
                'description': str(row[description_col]).strip() if description_col and pd.notna(row[description_col]) else '',
                'country': str(row[country_col]).strip() if country_col and pd.notna(row[country_col]) else '',
                'location': str(row[location_col]).strip() if location_col and pd.notna(row[location_col]) else '',
                'year': str(row[year_col]).strip() if year_col and pd.notna(row[year_col]) else ''
            }
            books.append(book)

        return books

    def _is_structured_format(self, entry: str) -> bool:
        """
        Check if entry uses structured multi-line format.

        Format example:
            Title: Book Title
            Author: Author Name
            Description: Book description...
        """
        lines = entry.split('\n')

        # Need at least 2 lines and should have field labels
        if len(lines) < 2:
            return False

        # Check if first line starts with a field label
        field_labels = ['Title:', 'Author:', 'Description:', 'Country:', 'Location:', 'ISBN:', 'Year:']
        return any(lines[0].strip().startswith(label) for label in field_labels)

    def _parse_structured_entry(self, entry: str) -> Dict[str, str]:
        """
        Parse entry in structured multi-line format.

        Format example:
            Title: Book Title
            Author: Author Name
            Description: Book description...
            Country: Country Name
            Location: Location Name
            ISBN: 1234567890
            Year: 2020
        """
        book = {
            'title': '',
            'author': '',
            'description': '',
            'country': '',
            'location': '',
            'isbn': '',
            'year': ''
        }

        current_field = None
        current_value = []

        for line in entry.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Check if line starts with a field label
            matched_field = None
            for field_name, field_label in [
                ('title', 'Title:'),
                ('author', 'Author:'),
                ('description', 'Description:'),
                ('country', 'Country:'),
                ('location', 'Location:'),
                ('isbn', 'ISBN:'),
                ('year', 'Year:')
            ]:
                if line.startswith(field_label):
                    # Save previous field if exists
                    if current_field:
                        book[current_field] = ' '.join(current_value).strip()

                    # Start new field
                    current_field = field_name
                    current_value = [line[len(field_label):].strip()]
                    matched_field = True
                    break

            # If no field label found and we're in a field, it's a continuation line
            if not matched_field and current_field:
                current_value.append(line)

        # Save last field
        if current_field:
            book[current_field] = ' '.join(current_value).strip()

        return book

    def _read_txt_input(self, file_path: str) -> List[Dict[str, str]]:
        """Read books from plain text file."""
        import re
        books = []

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split by double newlines (paragraph-separated)
        entries = [e.strip() for e in content.split('\n\n') if e.strip()]

        # If no double newlines, try single newlines
        if len(entries) <= 1:
            entries = [e.strip() for e in content.split('\n') if e.strip()]

        # Filter out separator lines like "---", "===", "***", etc.
        entries = [e for e in entries if not re.match(r'^[-=*_]{3,}$', e)]

        for entry in entries:
            # Check if entry is in structured format first
            if self._is_structured_format(entry):
                book = self._parse_structured_entry(entry)
            else:
                # Try to parse "Author - Title: Description" or "Title by Author: Description" format
                book = {'title': '', 'author': '', 'description': ''}

                # Parse based on format
                if ' - ' in entry:
                    # Format: "Author - Title" or "Author - Title: Description"
                    parts = entry.split(' - ', 1)
                    book['author'] = parts[0].strip()

                    # Check if there's a description after the title (look for : after author - title)
                    title_part = parts[1]
                    if ': ' in title_part:
                        # Split at LAST colon to handle titles with colons
                        last_colon_idx = title_part.rfind(': ')
                        book['title'] = title_part[:last_colon_idx].strip()
                        book['description'] = title_part[last_colon_idx + 2:].strip()
                    else:
                        book['title'] = title_part.strip()

                elif ' by ' in entry.lower():
                    # Format: "Title by Author" or "Title by Author: Description"
                    by_index = entry.lower().index(' by ')
                    title_part = entry[:by_index].strip()
                    author_and_desc = entry[by_index + 4:].strip()

                    # Check if there's a description after the author
                    if ': ' in author_and_desc:
                        # Split at FIRST colon after author
                        author_desc_parts = author_and_desc.split(': ', 1)
                        book['author'] = author_desc_parts[0].strip()
                        book['description'] = author_desc_parts[1].strip()
                    else:
                        book['author'] = author_and_desc

                    book['title'] = title_part
                else:
                    # Format: just "Title" or "Title: Description"
                    # Only split if there's a colon and it looks like a description separator
                    # (heuristic: description separator usually has substantial text after it)
                    if ': ' in entry:
                        parts = entry.rsplit(': ', 1)  # Use rsplit to split at last colon
                        # Only treat as description if the part after colon is reasonably long (>20 chars)
                        if len(parts[1]) > 20:
                            book['title'] = parts[0].strip()
                            book['description'] = parts[1].strip()
                        else:
                            book['title'] = entry.strip()
                    else:
                        book['title'] = entry.strip()

            # Clean up title: remove year in parentheses like "(1988)" or "(born 1956)"
            if book['title']:
                book['title'] = re.sub(r'\s*\(\d{4}\)\s*$', '', book['title'])
                book['title'] = re.sub(r'\s*\(born\s+\d{4}\)\s*$', '', book['title'])
                book['title'] = book['title'].strip()

            # Clean up author: remove year info like "(1956-2018)" or "(born 1956)"
            if book['author']:
                book['author'] = re.sub(r'\s*\(\d{4}-\d{4}\)\s*$', '', book['author'])
                book['author'] = re.sub(r'\s*\(born\s+\d{4}\)\s*$', '', book['author'])
                book['author'] = re.sub(r'\s*\(\d{4}-\d{4}\)\s*$', '', book['author'])
                book['author'] = book['author'].strip()

            if book['title']:
                books.append(book)

        return books

    def read_input_file(self, file_path: str) -> List[Dict[str, str]]:
        """Read books from input file (CSV or TXT)."""
        format_type = self._detect_input_format(file_path)

        if format_type == 'csv':
            print(f"📖 Reading CSV file: {file_path}")
            return self._read_csv_input(file_path)
        else:
            print(f"📖 Reading text file: {file_path}")
            return self._read_txt_input(file_path)

    def _build_book_prompt(self, book: Dict[str, str]) -> str:
        """Build the prompt for a specific book."""
        additional_info_parts = []

        if book.get('description'):
            additional_info_parts.append(f"Description: {book['description']}")
        if book.get('country'):
            additional_info_parts.append(f"Country/Region: {book['country']}")
        if book.get('location'):
            additional_info_parts.append(f"Location: {book['location']}")
        if book.get('isbn'):
            additional_info_parts.append(f"ISBN: {book['isbn']}")
        if book.get('year'):
            additional_info_parts.append(f"Publication Year: {book['year']}")

        additional_info = '\n'.join(additional_info_parts) if additional_info_parts else "No additional information provided."

        return self.book_extraction_template.format(
            title=book['title'],
            author=book['author'],
            additional_info=additional_info
        )

    def _call_llm(self, user_prompt: str, max_retries: int = 3) -> Optional[str]:
        """Call Groq LLM with retry logic."""
        for attempt in range(max_retries):
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=4096,
                    top_p=0.9
                )

                return completion.choices[0].message.content

            except Exception as e:
                print(f"⚠️  LLM API error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return None

        return None

    def _geocode_location(self, city: str, country: str, max_retries: int = 3) -> Optional[Dict[str, float]]:
        """Geocode a location to get latitude and longitude."""
        query = f"{city}, {country}"

        for attempt in range(max_retries):
            try:
                location = self.geolocator.geocode(query, timeout=10)

                if location:
                    return {
                        "latitude": round(location.latitude, 4),
                        "longitude": round(location.longitude, 4)
                    }
                else:
                    print(f"   ⚠️  Could not geocode: {query}")
                    return None

            except (GeocoderTimedOut, GeocoderServiceError) as e:
                print(f"   ⚠️  Geocoding error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(self.geocode_delay * (attempt + 1))
                else:
                    return None

        return None

    def _process_book_response(self, response_text: str, book_input: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Process the LLM response and geocode locations."""
        try:
            # Strip markdown code fences if present
            response_text = response_text.strip()
            if response_text.startswith('```'):
                # Remove opening fence (```json or just ```)
                lines = response_text.split('\n')
                if lines[0].startswith('```'):
                    lines = lines[1:]
                # Remove closing fence
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                response_text = '\n'.join(lines).strip()

            # Parse JSON response
            book_data = json.loads(response_text)

            # Check if book should be skipped
            if book_data.get("status") == "SKIP":
                reason = book_data.get("reason", "Unknown reason")
                print(f"   ⏭️  Skipped: {reason}")
                self.stats["skipped"] += 1
                return None

            # Geocode each location
            if "locations" in book_data and book_data["locations"]:
                print(f"   📍 Geocoding {len(book_data['locations'])} locations...")

                for location in book_data["locations"]:
                    city = location.get("city", "")
                    country = location.get("country", "")

                    if city and country:
                        coords = self._geocode_location(city, country)
                        if coords:
                            location["latitude"] = coords["latitude"]
                            location["longitude"] = coords["longitude"]
                            print(f"      ✓ {city}, {country}: {coords['latitude']}, {coords['longitude']}")

                        # Rate limit geocoding
                        time.sleep(self.geocode_delay)

                return book_data
            else:
                print(f"   ⚠️  No valid locations found")
                self.stats["skipped"] += 1
                return None

        except json.JSONDecodeError as e:
            print(f"   ❌ JSON parsing error: {e}")
            print(f"   Response was: {response_text[:200]}...")
            self.stats["errors"] += 1
            return None
        except Exception as e:
            print(f"   ❌ Processing error: {e}")
            self.stats["errors"] += 1
            return None

    def process_book(self, book: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Process a single book and return JSON data."""
        title = book.get('title', 'Unknown')
        author = book.get('author', 'Unknown')

        print(f"\n📚 Processing: {title} by {author}")

        # Build prompt
        user_prompt = self._build_book_prompt(book)

        # Call LLM
        print(f"   🤖 Querying LLM...")
        response = self._call_llm(user_prompt)

        if not response:
            print(f"   ❌ LLM call failed")
            self.stats["errors"] += 1
            self.failed_books.append(book)
            return None

        # Process response
        book_data = self._process_book_response(response, book)

        if book_data:
            print(f"   ✅ Successfully processed")
            self.stats["successful"] += 1
        else:
            # Processing failed (JSON parsing error, no locations, etc.)
            self.failed_books.append(book)

        self.stats["processed"] += 1

        # Rate limit
        time.sleep(self.rate_limit_delay)

        return book_data

    def process_all_books(
        self,
        input_file: str,
        output_file: str,
        resume_from: int = 0
    ) -> List[Dict[str, Any]]:
        """Process all books from input file."""
        # Read input
        books = self.read_input_file(input_file)
        print(f"\n📊 Found {len(books)} books to process")

        # Filter out duplicates (exact match) and check for fuzzy matches
        if self.existing_books or self.existing_books_data:
            print(f"\n🔍 Checking for duplicates...")
            books_to_process = []

            for book in books:
                title = book.get('title', '')
                author = book.get('author', '')

                # Check for exact duplicate first
                if self._is_duplicate(title, author):
                    print(f"⏭️  Already exists (exact match): {title} by {author}")
                    self.stats['duplicates_skipped'] += 1
                    continue

                # Check for fuzzy matches (similarity >= 85%)
                similar_books = self._find_similar_books(title, author, similarity_threshold=85.0)

                if similar_books:
                    # Log potential duplicate and skip processing
                    print(f"⏭️  Potential duplicate (fuzzy match): {title} by {author}")
                    self._log_potential_duplicate(title, author, similar_books)
                    self.stats['duplicates_skipped'] += 1
                else:
                    # No duplicates found, add to processing queue
                    books_to_process.append(book)

            duplicates_count = len(books) - len(books_to_process)
            print(f"\n📊 Filtered out {duplicates_count} duplicate(s)")
            print(f"   • Exact matches: {self.stats['duplicates_skipped'] - self.stats['potential_duplicates_logged']}")
            print(f"   • Fuzzy matches (logged for review): {self.stats['potential_duplicates_logged']}")
            print(f"📊 {len(books_to_process)} new book(s) to process")

            books = books_to_process
        else:
            print("⚠️  No duplicate checking (no existing books loaded)")

        if resume_from > 0:
            print(f"▶️  Resuming from book #{resume_from + 1}")
            books = books[resume_from:]

        results = []

        # Create output directory if it doesn't exist
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Process each book
        for idx, book in enumerate(books, start=resume_from):
            book_data = self.process_book(book)

            if book_data:
                results.append(book_data)

                # Save progress after each successful book
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)

                print(f"   💾 Progress saved ({len(results)} books)")

        # Save potential duplicates log
        output_dir = output_path.parent
        self._save_potential_duplicates(str(output_dir))

        return results

    def print_failed_books(self):
        """Print list of books that failed to process."""
        if not self.failed_books:
            return

        print("\n" + "="*60)
        print("❌ FAILED BOOKS")
        print("="*60)
        print(f"The following {len(self.failed_books)} book(s) failed to generate JSON output:\n")

        for idx, book in enumerate(self.failed_books, 1):
            print(f"{idx}. Title: {book.get('title', 'N/A')}")
            print(f"   Author: {book.get('author', 'N/A')}")

            # Print optional fields if they exist
            if book.get('description'):
                print(f"   Description: {book.get('description')}")
            if book.get('country'):
                print(f"   Country: {book.get('country')}")
            if book.get('location'):
                print(f"   Location: {book.get('location')}")
            if book.get('isbn'):
                print(f"   ISBN: {book.get('isbn')}")
            if book.get('year'):
                print(f"   Year: {book.get('year')}")
            print()

        print("="*60)

    def print_statistics(self):
        """Print processing statistics."""
        print("\n" + "="*60)
        print("📊 PROCESSING STATISTICS")
        print("="*60)
        print(f"Total processed:  {self.stats['processed']}")
        print(f"✅ Successful:     {self.stats['successful']}")
        print(f"⏭️  Skipped:        {self.stats['skipped']}")
        print(f"🔄 Duplicates:     {self.stats['duplicates_skipped']}")
        if self.stats['potential_duplicates_logged'] > 0:
            print(f"   • Fuzzy matches (logged): {self.stats['potential_duplicates_logged']}")
        print(f"❌ Errors:         {self.stats['errors']}")
        print("="*60)

        # Print failed books if any
        self.print_failed_books()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate travel book JSON data using Groq LLM"
    )
    parser.add_argument(
        "input_file",
        help="Input file (CSV or TXT)"
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output JSON file path (default: output_json/YYYY-MM-DD-HHMMSS.json)"
    )
    parser.add_argument(
        "-m", "--model",
        default="llama-3.3-70b-versatile",
        help="Groq model to use (default: llama-3.3-70b-versatile)"
    )
    parser.add_argument(
        "-r", "--resume",
        type=int,
        default=0,
        help="Resume from book index (0-based)"
    )
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=1.0,
        help="Delay between LLM calls in seconds (default: 1.0)"
    )
    parser.add_argument(
        "--geocode-delay",
        type=float,
        default=1.5,
        help="Delay between geocoding calls in seconds (default: 1.5)"
    )

    args = parser.parse_args()

    # Generate default output filename with timestamp if not provided
    if args.output is None:
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        args.output = f"output_json/{timestamp}.json"

    # Validate input file exists
    if not os.path.exists(args.input_file):
        print(f"❌ Error: Input file not found: {args.input_file}")
        return 1

    print("="*60)
    print("🗺️  TRAVEL BOOK JSON GENERATOR")
    print("="*60)
    print(f"Input:  {args.input_file}")
    print(f"Output: {args.output}")
    print(f"Model:  {args.model}")
    print("="*60)

    try:
        # Initialize generator
        generator = TravelBookGenerator(
            model=args.model,
            rate_limit_delay=args.rate_limit,
            geocode_delay=args.geocode_delay
        )

        # Load existing books for duplicate detection
        generator.load_existing_books()

        # Process books
        results = generator.process_all_books(
            args.input_file,
            args.output,
            resume_from=args.resume
        )

        # Print statistics
        generator.print_statistics()

        print(f"\n✅ Processing complete!")
        print(f"📄 Output saved to: {args.output}")
        print(f"📚 Total books generated: {len(results)}")

        return 0

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
