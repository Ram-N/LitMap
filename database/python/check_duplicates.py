#!/usr/bin/env python3
"""
Duplicate Book Checker
Standalone script to check for duplicate books using ISBN, exact matching, and fuzzy matching.

Supports multiple input formats: JSON, CSV, and TXT

Usage:
    python check_duplicates.py input_books.json
    python check_duplicates.py input_books.csv
    python check_duplicates.py input_books.txt --backup backup/books_20250107.json
    python check_duplicates.py input_books.json --threshold 90 --output results.json
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Any, Set, Tuple
from datetime import datetime

try:
    from rapidfuzz import fuzz
except ImportError:
    print("❌ Error: rapidfuzz library not found.")
    print("   Install it with: uv pip install rapidfuzz")
    exit(1)

try:
    import pandas as pd
except ImportError:
    print("❌ Error: pandas library not found.")
    print("   Install it with: uv pip install pandas")
    exit(1)


class DuplicateChecker:
    """Check for duplicate books using three-tier detection system."""

    def __init__(self, similarity_threshold: float = 85.0):
        """
        Initialize the duplicate checker.

        Args:
            similarity_threshold: Minimum similarity score (0-100) for fuzzy matching
        """
        self.similarity_threshold = similarity_threshold

        # Storage for existing books
        self.existing_books_by_title_author: Set[Tuple[str, str]] = set()
        self.existing_books_by_isbn: Set[str] = set()
        self.existing_books_data: List[Dict[str, Any]] = []

        # Results storage
        self.isbn_matches: List[Dict[str, Any]] = []
        self.exact_matches: List[Dict[str, Any]] = []
        self.fuzzy_matches: List[Dict[str, Any]] = []

        # Statistics
        self.stats = {
            "total_checked": 0,
            "isbn_duplicates": 0,
            "exact_duplicates": 0,
            "fuzzy_duplicates": 0,
            "unique_books": 0
        }

    def _get_latest_backup_file(self, backup_dir: Optional[Path] = None) -> Optional[Path]:
        """
        Find the latest backup JSON file.

        Args:
            backup_dir: Directory to search (defaults to database/backup/)

        Returns:
            Path to latest backup file, or None if not found
        """
        if backup_dir is None:
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
            backup_file: Path to backup file. If None, uses latest from database/backup/
        """
        if backup_file:
            backup_path = Path(backup_file)
        else:
            backup_path = self._get_latest_backup_file()

        if not backup_path or not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        print(f"📚 Loading existing books from: {backup_path}")

        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)

            # Build indexes for all three detection tiers
            for book in existing_data:
                # Extract normalized fields
                title = book.get('title', '').lower().strip()
                author = book.get('author', '').lower().strip()
                isbn_raw = book.get('isbn', '')
                isbn = isbn_raw.strip() if isbn_raw else ''

                # Tier 1: ISBN index
                if isbn:
                    self.existing_books_by_isbn.add(isbn.lower())

                # Tier 2: Title + Author exact match index
                if title and author:
                    self.existing_books_by_title_author.add((title, author))

                # Tier 3: Store full data for fuzzy matching
                self.existing_books_data.append({
                    'title': title,
                    'author': author,
                    'isbn': isbn.lower() if isbn else '',
                    'original_title': book.get('title', ''),
                    'original_author': book.get('author', ''),
                    'original_isbn': isbn
                })

            print(f"✅ Loaded {len(self.existing_books_data)} existing books")
            print(f"   • {len(self.existing_books_by_isbn)} books with ISBN")
            print(f"   • {len(self.existing_books_by_title_author)} books with title+author")

        except Exception as e:
            raise Exception(f"Error loading existing books: {e}")

    def _normalize_title(self, title: str) -> str:
        """
        Normalize title by extracting main title (before colon/dash subtitle).

        Args:
            title: Original title

        Returns:
            Normalized main title
        """
        title = title.lower().strip()

        # Split on common subtitle separators and take the first part
        for separator in [':', ' - ', ' – ', ' — ']:
            if separator in title:
                title = title.split(separator)[0].strip()
                break

        return title

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

    def _check_isbn_duplicate(self, isbn: str) -> bool:
        """
        Check if ISBN already exists (Tier 1 - exact ISBN match).

        Args:
            isbn: Book ISBN

        Returns:
            True if ISBN exists, False otherwise
        """
        if not isbn:
            return False

        isbn_normalized = isbn.strip().lower()
        return isbn_normalized in self.existing_books_by_isbn

    def _check_exact_duplicate(self, title: str, author: str) -> bool:
        """
        Check if book already exists using exact match (Tier 2 - case-insensitive).

        Args:
            title: Book title
            author: Book author

        Returns:
            True if book exists (exact match), False otherwise
        """
        title_lower = title.lower().strip()
        author_lower = author.lower().strip()

        return (title_lower, author_lower) in self.existing_books_by_title_author

    def _find_similar_books(self, title: str, author: str) -> List[Dict[str, Any]]:
        """
        Find existing books with similar title and author using fuzzy matching (Tier 3).
        Also checks normalized titles (without subtitles) for better matching.

        Args:
            title: Book title to search for
            author: Book author to search for

        Returns:
            List of matching books with similarity scores
        """
        similar_books = []
        title_lower = title.lower().strip()
        author_lower = author.lower().strip()

        # Also get normalized title (main title without subtitle)
        normalized_title = self._normalize_title(title)

        for existing_book in self.existing_books_data:
            title_similarity = self._calculate_similarity(title_lower, existing_book['title'])
            author_similarity = self._calculate_similarity(author_lower, existing_book['author'])

            # Also check normalized titles (handles subtitle differences)
            normalized_existing = self._normalize_title(existing_book['title'])
            normalized_similarity = self._calculate_similarity(normalized_title, normalized_existing)

            # Use the BEST title similarity score (either full title or normalized)
            best_title_similarity = max(title_similarity, normalized_similarity)

            # Both title and author must meet threshold
            if best_title_similarity >= self.similarity_threshold and author_similarity >= self.similarity_threshold:
                similar_books.append({
                    'existing_title': existing_book['original_title'],
                    'existing_author': existing_book['original_author'],
                    'existing_isbn': existing_book['original_isbn'],
                    'title_similarity': round(best_title_similarity, 2),
                    'author_similarity': round(author_similarity, 2)
                })

        return similar_books

    def check_book(self, book: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check a single book for duplicates using three-tier system.

        Args:
            book: Book dictionary with title, author, and optionally isbn

        Returns:
            Dictionary with duplicate status and details
        """
        title = book.get('title', '')
        author = book.get('author', '')
        isbn = book.get('isbn', '')

        result = {
            'title': title,
            'author': author,
            'isbn': isbn,
            'is_duplicate': False,
            'duplicate_type': None,
            'matches': []
        }

        # Tier 1: Check ISBN
        if isbn and self._check_isbn_duplicate(isbn):
            result['is_duplicate'] = True
            result['duplicate_type'] = 'isbn'
            # Find the matching book(s) by ISBN
            for existing_book in self.existing_books_data:
                if existing_book['isbn'] == isbn.lower().strip():
                    result['matches'].append({
                        'existing_title': existing_book['original_title'],
                        'existing_author': existing_book['original_author'],
                        'existing_isbn': existing_book['original_isbn'],
                        'match_type': 'ISBN exact match'
                    })
            self.stats['isbn_duplicates'] += 1
            self.isbn_matches.append(result)
            return result

        # Tier 2: Check exact title + author match
        if self._check_exact_duplicate(title, author):
            result['is_duplicate'] = True
            result['duplicate_type'] = 'exact'
            # Find the matching book(s)
            title_lower = title.lower().strip()
            author_lower = author.lower().strip()
            for existing_book in self.existing_books_data:
                if existing_book['title'] == title_lower and existing_book['author'] == author_lower:
                    result['matches'].append({
                        'existing_title': existing_book['original_title'],
                        'existing_author': existing_book['original_author'],
                        'existing_isbn': existing_book['original_isbn'],
                        'match_type': 'Title + Author exact match (case-insensitive)'
                    })
            self.stats['exact_duplicates'] += 1
            self.exact_matches.append(result)
            return result

        # Tier 3: Check fuzzy match
        similar_books = self._find_similar_books(title, author)
        if similar_books:
            result['is_duplicate'] = True
            result['duplicate_type'] = 'fuzzy'
            for match in similar_books:
                result['matches'].append({
                    'existing_title': match['existing_title'],
                    'existing_author': match['existing_author'],
                    'existing_isbn': match['existing_isbn'],
                    'match_type': f"Fuzzy match (Title: {match['title_similarity']}%, Author: {match['author_similarity']}%)",
                    'title_similarity': match['title_similarity'],
                    'author_similarity': match['author_similarity']
                })
            self.stats['fuzzy_duplicates'] += 1
            self.fuzzy_matches.append(result)
            return result

        # No duplicates found
        self.stats['unique_books'] += 1
        return result

    def check_books(self, books: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Check multiple books for duplicates.

        Args:
            books: List of book dictionaries

        Returns:
            List of result dictionaries for each book
        """
        results = []

        print(f"\n🔍 Checking {len(books)} books for duplicates...")
        print(f"   Similarity threshold: {self.similarity_threshold}%\n")

        for idx, book in enumerate(books, 1):
            self.stats['total_checked'] += 1

            title = book.get('title', 'Unknown')
            author = book.get('author', 'Unknown')

            print(f"[{idx}/{len(books)}] Checking: {title} by {author}")

            result = self.check_book(book)
            results.append(result)

            # Print result
            if result['is_duplicate']:
                if result['duplicate_type'] == 'isbn':
                    print(f"   🔴 ISBN DUPLICATE")
                elif result['duplicate_type'] == 'exact':
                    print(f"   🟠 EXACT DUPLICATE (Title + Author)")
                elif result['duplicate_type'] == 'fuzzy':
                    print(f"   🟡 FUZZY DUPLICATE (Similarity match)")

                for match in result['matches']:
                    print(f"      → {match['existing_title']} by {match['existing_author']}")
                    if 'title_similarity' in match:
                        print(f"        Similarity: Title {match['title_similarity']}%, Author {match['author_similarity']}%")
            else:
                print(f"   ✅ UNIQUE (No duplicates found)")
            print()

        return results

    def print_summary(self) -> None:
        """Print summary statistics."""
        print("\n" + "="*70)
        print("📊 DUPLICATE CHECK SUMMARY")
        print("="*70)
        print(f"Total books checked:     {self.stats['total_checked']}")
        print(f"🔴 ISBN duplicates:       {self.stats['isbn_duplicates']}")
        print(f"🟠 Exact duplicates:      {self.stats['exact_duplicates']}")
        print(f"🟡 Fuzzy duplicates:      {self.stats['fuzzy_duplicates']}")
        print(f"✅ Unique books:          {self.stats['unique_books']}")
        print("="*70)

        total_duplicates = (self.stats['isbn_duplicates'] +
                           self.stats['exact_duplicates'] +
                           self.stats['fuzzy_duplicates'])

        if total_duplicates > 0:
            print(f"\n⚠️  Found {total_duplicates} potential duplicate(s)")
            print("   Review the detailed results in the output JSON file.")

    def save_results(self, output_file: str, results: List[Dict[str, Any]]) -> None:
        """
        Save duplicate check results to JSON file.

        Args:
            output_file: Path to output JSON file
            results: List of result dictionaries
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_data = {
            'timestamp': datetime.now().isoformat(),
            'similarity_threshold': self.similarity_threshold,
            'statistics': self.stats,
            'results': {
                'all_books': results,
                'isbn_duplicates': self.isbn_matches,
                'exact_duplicates': self.exact_matches,
                'fuzzy_duplicates': self.fuzzy_matches
            }
        }

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

            print(f"\n💾 Results saved to: {output_path}")
        except Exception as e:
            print(f"\n❌ Error saving results: {e}")


def save_filtered_books(books: List[Dict[str, Any]], output_file: str, input_format: str) -> None:
    """
    Save filtered unique books to file in the same format as input.

    Args:
        books: List of unique book dictionaries
        output_file: Path to output file
        input_format: Format to save in ('json', 'csv', or 'txt')
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if input_format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(books, f, indent=2, ensure_ascii=False)
            print(f"💾 Unique books saved to JSON: {output_path}")

        elif input_format == 'csv':
            df = pd.DataFrame(books)
            # Reorder columns: put title, author first, then other columns
            column_order = []
            if 'title' in df.columns:
                column_order.append('title')
            if 'author' in df.columns:
                column_order.append('author')
            # Add any remaining columns (preserving original order if possible)
            for col in df.columns:
                if col not in column_order:
                    column_order.append(col)

            df = df[column_order]
            # Capitalize column names for CSV (to match typical CSV format)
            df.columns = [col.capitalize() for col in df.columns]
            df.to_csv(output_path, index=False)
            print(f"💾 Unique books saved to CSV: {output_path}")

        elif input_format == 'txt':
            with open(output_path, 'w', encoding='utf-8') as f:
                for book in books:
                    title = book.get('title', '')
                    author = book.get('author', 'Unknown')

                    # Format: "Title by Author"
                    if author and author != 'Unknown':
                        f.write(f"{title} by {author}\n")
                    else:
                        f.write(f"{title}\n")
            print(f"💾 Unique books saved to TXT: {output_path}")

    except Exception as e:
        print(f"❌ Error saving filtered books: {e}")


def load_input_books(input_file: str) -> tuple[List[Dict[str, Any]], str]:
    """
    Load books from input file (JSON, CSV, or TXT).

    Args:
        input_file: Path to input JSON, CSV, or TXT file

    Returns:
        Tuple of (list of book dictionaries, format string)
    """
    input_path = Path(input_file)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    print(f"📖 Loading books from: {input_path}")

    # Detect file format
    file_ext = input_path.suffix.lower()

    if file_ext == '.txt':
        # Read TXT file - support multiple formats
        import re

        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split by double newlines (paragraph-separated)
        entries = [e.strip() for e in content.split('\n\n') if e.strip()]

        # If no double newlines, try single newlines
        if len(entries) <= 1:
            entries = [e.strip() for e in content.split('\n') if e.strip()]

        # Filter out separator lines like "---", "===", "***", etc.
        entries = [e for e in entries if not re.match(r'^[-=*_]{3,}$', e)]

        books = []
        for entry in entries:
            book = {'title': '', 'author': '', 'isbn': ''}

            # Parse different formats:
            # 1. "Author - Title"
            # 2. "Title by Author"
            # 3. Just "Title"

            if ' - ' in entry:
                # Format: "Author - Title"
                parts = entry.split(' - ', 1)
                book['author'] = parts[0].strip()
                book['title'] = parts[1].strip()
            elif ' by ' in entry.lower():
                # Format: "Title by Author"
                by_index = entry.lower().index(' by ')
                book['title'] = entry[:by_index].strip()
                book['author'] = entry[by_index + 4:].strip()
            else:
                # Format: just "Title"
                book['title'] = entry.strip()
                book['author'] = 'Unknown'

            # Clean up title/author: remove year info like "(1988)" or "(born 1956)"
            if book['title']:
                book['title'] = re.sub(r'\s*\(\d{4}\)\s*$', '', book['title'])
                book['title'] = re.sub(r'\s*\(born\s+\d{4}\)\s*$', '', book['title'])
                book['title'] = book['title'].strip()

            if book['author']:
                book['author'] = re.sub(r'\s*\(\d{4}-\d{4}\)\s*$', '', book['author'])
                book['author'] = re.sub(r'\s*\(born\s+\d{4}\)\s*$', '', book['author'])
                book['author'] = book['author'].strip()

            if book['title']:
                books.append(book)

        print(f"✅ Loaded {len(books)} books from TXT\n")
        return books, 'txt'

    elif file_ext == '.csv':
        # Read CSV file
        df = pd.read_csv(input_path)

        # Convert DataFrame to list of dictionaries
        # Preserve all columns from CSV
        books = []
        for _, row in df.iterrows():
            book = {}

            # First, preserve all original columns
            for col in df.columns:
                if pd.notna(row[col]):
                    book[col.lower()] = str(row[col]).strip()

            # Ensure we have standardized keys for duplicate checking
            # Map title (try common variations)
            if 'title' not in book:
                for title_col in ['Title', 'Book', 'book']:
                    if title_col.lower() in book:
                        book['title'] = book[title_col.lower()]
                        break

            # Map author (try common variations)
            if 'author' not in book:
                for author_col in ['Author', 'Authors', 'authors']:
                    if author_col.lower() in book:
                        book['author'] = book[author_col.lower()]
                        break

            # Map ISBN (try common variations)
            if 'isbn' not in book:
                for isbn_col in ['ISBN', 'Isbn', 'ISBN13', 'isbn13']:
                    if isbn_col.lower() in book:
                        book['isbn'] = book[isbn_col.lower()]
                        break

            # Set defaults if missing
            if 'isbn' not in book:
                book['isbn'] = ''
            if 'author' not in book:
                book['author'] = 'Unknown'

            # Only add book if it has at least a title
            if 'title' in book:
                books.append(book)

        print(f"✅ Loaded {len(books)} books from CSV\n")
        return books, 'csv'

    elif file_ext == '.json':
        # Read JSON file
        with open(input_path, 'r', encoding='utf-8') as f:
            books = json.load(f)

        print(f"✅ Loaded {len(books)} books from JSON\n")
        return books, 'json'

    else:
        raise ValueError(f"Unsupported file format: {file_ext}. Please use .json, .csv, or .txt files.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check for duplicate books using ISBN, exact matching, and fuzzy matching. Supports JSON, CSV, and TXT input files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check books from JSON file against latest backup (auto-detected)
  python check_duplicates.py new_books.json

  # Check books from CSV file
  python check_duplicates.py new_books.csv --backup ../backup/books_20250107.json

  # Check books from TXT file (one book per line: "Title by Author" or "Author - Title")
  python check_duplicates.py new_books.txt

  # Use stricter similarity threshold (90% instead of default 85%)
  python check_duplicates.py new_books.json --threshold 90

  # Save results to custom location
  python check_duplicates.py new_books.json --output results/duplicates.json

  # Combine options
  python check_duplicates.py new_books.csv --backup custom_backup.json --threshold 92 --output my_results.json
        """
    )

    parser.add_argument(
        "input_file",
        help="Input file with books to check for duplicates (JSON, CSV, or TXT)"
    )
    parser.add_argument(
        "--backup",
        default=None,
        help="Backup JSON file to check against (default: latest from database/backup/)"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON file for duplicate report (default: output/duplicate_check_YYYY-MM-DD-HHMMSS.json)"
    )
    parser.add_argument(
        "--filtered-output",
        default=None,
        help="Output file for unique books only, in same format as input (default: auto-generated from input filename)"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=85.0,
        help="Similarity threshold for fuzzy matching (0-100, default: 85.0)"
    )

    args = parser.parse_args()

    # Validate threshold
    if not 0 <= args.threshold <= 100:
        print("❌ Error: Threshold must be between 0 and 100")
        return 1

    # Generate default output filename with timestamp if not provided
    if args.output is None:
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        args.output = f"output/duplicate_check_{timestamp}.json"

    # Generate default filtered output filename if not provided
    input_path = Path(args.input_file)
    if args.filtered_output is None:
        input_stem = input_path.stem
        input_ext = input_path.suffix
        args.filtered_output = f"output/{input_stem}_unique{input_ext}"

    print("="*70)
    print("🔍 DUPLICATE BOOK CHECKER")
    print("="*70)
    print(f"Input:               {args.input_file}")
    print(f"Backup:              {args.backup or 'Auto-detect latest'}")
    print(f"Similarity threshold: {args.threshold}%")
    print(f"Duplicate report:    {args.output}")
    print(f"Filtered output:     {args.filtered_output}")
    print("="*70)

    try:
        # Load input books
        books, input_format = load_input_books(args.input_file)

        # Initialize checker
        checker = DuplicateChecker(similarity_threshold=args.threshold)

        # Load existing books
        checker.load_existing_books(args.backup)

        # Check for duplicates
        results = checker.check_books(books)

        # Print summary
        checker.print_summary()

        # Save duplicate check results
        checker.save_results(args.output, results)

        # Extract unique books (not duplicates)
        unique_books = [
            books[i] for i, result in enumerate(results)
            if not result['is_duplicate']
        ]

        # Save filtered unique books in same format as input
        if unique_books:
            save_filtered_books(unique_books, args.filtered_output, input_format)
            print(f"\n✅ {len(unique_books)} unique book(s) saved to filtered output file")
        else:
            print(f"\n⚠️  No unique books found - all books were duplicates!")

        print(f"\n✅ Duplicate check complete!")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
