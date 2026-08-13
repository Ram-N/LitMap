"""Download book cover images from Open Library and Google Books API.

Searches by ISBN first, then falls back to title+author search on both
Open Library and Google Books. This maximizes coverage for books without
ISBNs or whose ISBNs aren't indexed.

Requires: requests, Pillow
    uv pip install requests Pillow

Usage:
    cd database
    python download_covers.py --all          # Download all covers
    python download_covers.py --missing      # Only books without a local cover file
    python download_covers.py --flagged      # Re-download covers flagged in Firestore
    python download_covers.py --book-id ID   # Download cover for a single book
"""

import argparse
import json
import time
import urllib.parse
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image

GEOJSON_PATH = Path(__file__).parent / "../vue-app/public/litmap-data.geojson"
COVERS_DIR = Path(__file__).parent / "../vue-app/public/covers"
MANIFEST_PATH = COVERS_DIR / "manifest.json"

REQUEST_DELAY = 1.0  # seconds between requests
MIN_IMAGE_SIZE = (10, 10)  # reject placeholder images smaller than this


def load_books_from_geojson():
    """Load unique books from GeoJSON, keyed by bookId."""
    with open(GEOJSON_PATH) as f:
        geojson = json.load(f)

    books = {}
    for feature in geojson["features"]:
        props = feature["properties"]
        book_id = props.get("bookId", "")
        if not book_id or book_id in books:
            continue
        books[book_id] = {
            "id": book_id,
            "title": props.get("title", ""),
            "author": props.get("author", ""),
            "isbn": props.get("isbn", ""),
        }
    return books


def load_flagged_books_from_firestore():
    """Load book IDs that have coverFlagged=True in Firestore."""
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        SERVICE_ACCOUNT_KEY = (
            Path(__file__).parent
            / "litmap-88358-firebase-adminsdk-9w1l9-73ca515ce7.json"
        )
        cred = credentials.Certificate(str(SERVICE_ACCOUNT_KEY))
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        db = firestore.client()

        flagged_ids = set()
        for collection_name in ["books", "newbooks"]:
            docs = (
                db.collection(collection_name)
                .where("coverFlagged", "==", True)
                .stream()
            )
            for doc in docs:
                flagged_ids.add(doc.id)
        return flagged_ids
    except Exception as e:
        print(f"Error connecting to Firestore: {e}")
        print("Make sure Firebase credentials are available.")
        return set()


def is_valid_cover(image_data):
    """Check that downloaded data is a real image, not a tiny placeholder."""
    try:
        img = Image.open(BytesIO(image_data))
        width, height = img.size
        if width < MIN_IMAGE_SIZE[0] or height < MIN_IMAGE_SIZE[1]:
            return False
        if width == 1 and height == 1:
            return False
        return True
    except Exception:
        return False


def fetch_image(url):
    """Download image bytes from a URL, return None if invalid."""
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200 and is_valid_cover(resp.content):
            return resp.content
    except requests.RequestException:
        pass
    return None


# ---------------------------------------------------------------------------
# Source 1: Open Library
# ---------------------------------------------------------------------------

def try_open_library_isbn(isbn):
    """Try Open Library cover by ISBN."""
    return fetch_image(f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg")


def try_open_library_search(title, author):
    """Search Open Library by title+author, download the first result's cover."""
    query = urllib.parse.quote(f"{title} {author}")
    url = f"https://openlibrary.org/search.json?q={query}&limit=3&fields=cover_i,title,author_name"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            return None
        docs = resp.json().get("docs", [])
        for doc in docs:
            cover_id = doc.get("cover_i")
            if cover_id:
                image_data = fetch_image(
                    f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
                )
                if image_data:
                    return image_data
    except requests.RequestException:
        pass
    return None


# ---------------------------------------------------------------------------
# Source 2: Google Books
# ---------------------------------------------------------------------------

def _google_books_cover(query_param):
    """Shared helper: query Google Books API and download the cover thumbnail."""
    url = f"https://www.googleapis.com/books/v1/volumes?q={query_param}&maxResults=3"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            return None
        items = resp.json().get("items", [])
        for item in items:
            image_links = item.get("volumeInfo", {}).get("imageLinks", {})
            cover_url = image_links.get("thumbnail") or image_links.get("smallThumbnail")
            if cover_url:
                cover_url = cover_url.replace("http://", "https://")
                image_data = fetch_image(cover_url)
                if image_data:
                    return image_data
    except requests.RequestException:
        pass
    return None


def try_google_books_isbn(isbn):
    """Try Google Books by ISBN."""
    return _google_books_cover(f"isbn:{isbn}")


def try_google_books_search(title, author):
    """Search Google Books by title+author."""
    q = urllib.parse.quote(f'intitle:{title} inauthor:{author}')
    return _google_books_cover(q)


# ---------------------------------------------------------------------------
# Download orchestration
# ---------------------------------------------------------------------------

def download_cover(book):
    """Try all sources in order. Returns (image_data, source_name) or (None, None).

    Order:
      1. Open Library by ISBN
      2. Google Books by ISBN
      3. Open Library by title+author search
      4. Google Books by title+author search
    """
    isbn = book.get("isbn", "")
    title = book.get("title", "")
    author = book.get("author", "")

    # --- ISBN-based lookups (fast, precise) ---
    if isbn:
        data = try_open_library_isbn(isbn)
        if data:
            return data, "OpenLibrary-ISBN"

        time.sleep(REQUEST_DELAY)

        data = try_google_books_isbn(isbn)
        if data:
            return data, "GoogleBooks-ISBN"

        time.sleep(REQUEST_DELAY)

    # --- Title+author search fallback (broader, works without ISBN) ---
    if title:
        data = try_open_library_search(title, author)
        if data:
            return data, "OpenLibrary-search"

        time.sleep(REQUEST_DELAY)

        data = try_google_books_search(title, author)
        if data:
            return data, "GoogleBooks-search"

    return None, None


def save_cover(book_id, image_data):
    """Save cover image to disk as JPEG."""
    filepath = COVERS_DIR / f"{book_id}.jpg"
    try:
        img = Image.open(BytesIO(image_data))
        img = img.convert("RGB")
        img.save(str(filepath), "JPEG", quality=85)
        return True
    except Exception as e:
        print(f"  Error saving image: {e}")
        return False


def load_manifest():
    """Load existing manifest or return empty dict."""
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH) as f:
            return json.load(f)
    return {}


def save_manifest(manifest):
    """Save manifest to disk."""
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Download book cover images")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="Download all covers")
    group.add_argument(
        "--missing",
        action="store_true",
        help="Only download covers for books without a local file",
    )
    group.add_argument(
        "--flagged",
        action="store_true",
        help="Re-download covers flagged in Firestore",
    )
    group.add_argument("--book-id", type=str, help="Download cover for a single book")
    args = parser.parse_args()

    COVERS_DIR.mkdir(parents=True, exist_ok=True)

    books = load_books_from_geojson()
    manifest = load_manifest()
    print(f"Loaded {len(books)} unique books from GeoJSON")

    # Determine which books to process
    if args.book_id:
        if args.book_id not in books:
            print(f"Book ID '{args.book_id}' not found in GeoJSON")
            return
        target_books = {args.book_id: books[args.book_id]}
    elif args.flagged:
        flagged_ids = load_flagged_books_from_firestore()
        target_books = {bid: books[bid] for bid in flagged_ids if bid in books}
        print(f"Found {len(target_books)} flagged books")
    elif args.missing:
        target_books = {
            bid: b
            for bid, b in books.items()
            if not (COVERS_DIR / f"{bid}.jpg").exists()
        }
        print(f"Found {len(target_books)} books without local covers")
    else:  # --all
        target_books = books

    # Download covers
    success_count = 0
    fail_count = 0
    no_cover_found = []
    sources_used = {}

    for i, (book_id, book) in enumerate(target_books.items()):
        title = book.get("title", "Unknown")
        isbn = book.get("isbn", "")

        label = f"ISBN: {isbn}" if isbn else "no ISBN"
        print(f"[{i+1}/{len(target_books)}] {title} ({label})")

        image_data, source = download_cover(book)
        if image_data:
            if save_cover(book_id, image_data):
                manifest[book_id] = f"{book_id}.jpg"
                success_count += 1
                sources_used[source] = sources_used.get(source, 0) + 1
                print(f"  OK  ({source})")
            else:
                fail_count += 1
        else:
            fail_count += 1
            no_cover_found.append(
                {"id": book_id, "title": title, "isbn": isbn, "reason": "not_found"}
            )
            print(f"  MISS — no cover from any source")

        time.sleep(REQUEST_DELAY)

    # Save manifest
    save_manifest(manifest)

    # Summary
    print(f"\n{'='*60}")
    print(f"Download complete:")
    print(f"  Successful:  {success_count}")
    print(f"  Not found:   {fail_count}")
    print(f"  Total:       {len(target_books)}")
    print(f"  Hit rate:    {success_count*100//max(len(target_books),1)}%")
    if sources_used:
        print(f"\n  Covers by source:")
        for src, count in sorted(sources_used.items(), key=lambda x: -x[1]):
            print(f"    {src}: {count}")
    print(f"\n  Manifest: {MANIFEST_PATH}")

    if no_cover_found:
        log_path = COVERS_DIR / "missing_covers.json"
        with open(log_path, "w") as f:
            json.dump(no_cover_found, f, indent=2)
        print(f"  Missing covers log: {log_path}")


if __name__ == "__main__":
    main()
