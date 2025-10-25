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
            "errors": 0
        }

        # Existing books cache
        self.existing_books = set()

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
            for book in existing_data:
                title = book.get('title', '').lower().strip()
                author = book.get('author', '').lower().strip()

                if title and author:
                    self.existing_books.add((title, author))

            print(f"✅ Loaded {len(self.existing_books)} existing books")

        except Exception as e:
            print(f"⚠️  Error loading existing books: {e}")
            print("   Will process all books without duplicate checking")

    def _is_duplicate(self, title: str, author: str) -> bool:
        """
        Check if book already exists in database (case-insensitive).

        Args:
            title: Book title
            author: Book author

        Returns:
            True if book exists, False otherwise
        """
        title_lower = title.lower().strip()
        author_lower = author.lower().strip()

        return (title_lower, author_lower) in self.existing_books

    def _detect_input_format(self, file_path: str) -> str:
        """Detect if input is CSV or plain text."""
        if file_path.lower().endswith('.csv'):
            return 'csv'
        return 'txt'

    def _read_csv_input(self, file_path: str) -> List[Dict[str, str]]:
        """Read books from CSV file."""
        books = []
        df = pd.read_csv(file_path)

        for _, row in df.iterrows():
            book = {
                'title': row.get('Book', ''),
                'author': row.get('Author', ''),
                'country': row.get('Country', ''),
                'location': row.get('Location', ''),
                'isbn': row.get('ISBN', ''),
                'year': row.get('Year', '')
            }
            books.append(book)

        return books

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

        for entry in entries:
            # Try to parse "Author - Title" or "Title by Author" format
            book = {'title': '', 'author': ''}

            if ' - ' in entry:
                parts = entry.split(' - ', 1)
                book['author'] = parts[0].strip()
                book['title'] = parts[1].strip()
            elif ' by ' in entry.lower():
                parts = entry.lower().split(' by ')
                book['title'] = entry[:entry.lower().index(' by ')].strip()
                book['author'] = entry[entry.lower().index(' by ') + 4:].strip()
            else:
                # Assume entire line is the title
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
            return None

        # Process response
        book_data = self._process_book_response(response, book)

        if book_data:
            print(f"   ✅ Successfully processed")
            self.stats["successful"] += 1

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

        # Filter out duplicates
        if self.existing_books:
            print(f"\n🔍 Checking for duplicates...")
            books_to_process = []

            for book in books:
                title = book.get('title', '')
                author = book.get('author', '')

                if self._is_duplicate(title, author):
                    print(f"⏭️  Already exists: {title} by {author}")
                    self.stats['duplicates_skipped'] += 1
                else:
                    books_to_process.append(book)

            duplicates_count = len(books) - len(books_to_process)
            print(f"\n📊 Filtered out {duplicates_count} duplicate(s)")
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

        return results

    def print_statistics(self):
        """Print processing statistics."""
        print("\n" + "="*60)
        print("📊 PROCESSING STATISTICS")
        print("="*60)
        print(f"Total processed:  {self.stats['processed']}")
        print(f"✅ Successful:     {self.stats['successful']}")
        print(f"⏭️  Skipped:        {self.stats['skipped']}")
        print(f"🔄 Duplicates:     {self.stats['duplicates_skipped']}")
        print(f"❌ Errors:         {self.stats['errors']}")
        print("="*60)


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
        default="output/travel_books_generated.json",
        help="Output JSON file path (default: output/travel_books_generated.json)"
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
