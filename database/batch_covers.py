"""Batch workflow for finding and downloading book cover images.

Step 1: Export a CSV of books missing covers
Step 2: User fills in cover URLs manually
Step 3: Import the CSV to download covers and update manifest/GeoJSON

Usage:
    cd database
    python batch_covers.py export                    # All missing books
    python batch_covers.py export --limit 10         # First 10 only
    python batch_covers.py export --output my.csv    # Custom output path
    python batch_covers.py import                    # Process filled-in CSV
    python batch_covers.py import --input my.csv     # Custom input path
"""

import argparse
import csv
import json
import sys
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image

GEOJSON_PATH = Path(__file__).parent / "../vue-app/public/litmap-data.geojson"
COVERS_DIR = Path(__file__).parent / "../vue-app/public/covers"
MANIFEST_PATH = COVERS_DIR / "manifest.json"
DEFAULT_CSV = Path(__file__).parent / "covers_batch.csv"
REVIEW_HTML = Path(__file__).parent / "covers_review.html"

MIN_IMAGE_SIZE = (10, 10)


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


def download_cover_from_url(url, book_id):
    """Download image from URL, validate, and save as JPEG.

    Returns (success: bool, message: str).
    """
    headers = {"User-Agent": "LitMap/1.0 (book cover downloader)"}
    resp = requests.get(url, timeout=15, headers=headers)
    resp.raise_for_status()
    img = Image.open(BytesIO(resp.content))
    if img.width < MIN_IMAGE_SIZE[0] or img.height < MIN_IMAGE_SIZE[1]:
        return False, "Image too small (likely a placeholder)"
    img = img.convert("RGB")
    save_path = COVERS_DIR / f"{book_id}.jpg"
    img.save(str(save_path), "JPEG", quality=85)
    return True, str(save_path)


def update_geojson_has_cover(book_ids):
    """Set hasCover=true in GeoJSON for all features matching any of the given book IDs."""
    book_id_set = set(book_ids)
    with open(GEOJSON_PATH) as f:
        geojson = json.load(f)
    updated = 0
    for feat in geojson["features"]:
        if feat["properties"].get("bookId") in book_id_set:
            feat["properties"]["hasCover"] = True
            updated += 1
    with open(GEOJSON_PATH, "w") as f:
        json.dump(geojson, f, indent=2)
    return updated


def generate_review_html(results, output_path):
    """Generate a static HTML page for visual review of processed covers."""
    covers_rel = "../vue-app/public/covers"

    rows_html = []
    for r in results:
        if r["success"]:
            img_tag = f'<img src="{covers_rel}/{r["book_id"]}.jpg" alt="{r["title"]}">'
            status = '<span class="ok">saved</span>'
        else:
            img_tag = '<div class="no-img">No image</div>'
            status = f'<span class="fail">{r["error"]}</span>'

        rows_html.append(f"""
      <div class="card {"card-fail" if not r["success"] else ""}">
        {img_tag}
        <div class="title">{r["title"]}</div>
        <div class="author">{r["author"]}</div>
        <div class="status">{status}</div>
      </div>""")

    success_count = sum(1 for r in results if r["success"])
    fail_count = len(results) - success_count

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Batch Cover Review</title>
<style>
  body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #f5f5f5; }}
  h1 {{ margin-bottom: 0.5rem; }}
  .summary {{ color: #555; margin-bottom: 1.5rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 1rem; }}
  .card {{ background: #fff; border-radius: 8px; padding: 0.75rem; text-align: center;
           box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  .card-fail {{ border: 2px solid #e74c3c; }}
  .card img {{ max-width: 120px; max-height: 180px; display: block; margin: 0 auto 0.5rem; }}
  .no-img {{ width: 120px; height: 160px; background: #eee; display: flex; align-items: center;
             justify-content: center; margin: 0 auto 0.5rem; color: #999; font-size: 0.85rem; }}
  .title {{ font-weight: 600; font-size: 0.85rem; margin-bottom: 0.25rem;
            overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
  .author {{ font-size: 0.8rem; color: #666; margin-bottom: 0.25rem;
             overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
  .ok {{ color: #27ae60; font-size: 0.8rem; }}
  .fail {{ color: #e74c3c; font-size: 0.8rem; }}
</style>
</head>
<body>
<h1>Batch Cover Review</h1>
<p class="summary">{len(results)} books processed &mdash; {success_count} saved, {fail_count} failed</p>
<div class="grid">
{"".join(rows_html)}
</div>
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html)


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_export(args):
    """Export CSV of books missing covers."""
    books = load_books_from_geojson()
    print(f"Loaded {len(books)} unique books from GeoJSON")

    # Filter to missing covers
    missing = {
        bid: b for bid, b in books.items()
        if not (COVERS_DIR / f"{bid}.jpg").exists()
    }
    print(f"Found {len(missing)} books without covers")

    # Sort by title for easier browsing
    sorted_books = sorted(missing.values(), key=lambda b: b["title"].lower())

    if args.limit:
        sorted_books = sorted_books[:args.limit]
        print(f"Limiting to first {args.limit} books")

    output_path = Path(args.output)
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["book_id", "title", "author", "isbn", "url"])
        for book in sorted_books:
            writer.writerow([book["id"], book["title"], book["author"], book["isbn"], ""])

    print(f"Wrote {len(sorted_books)} rows to {output_path}")
    print("Next: fill in the 'url' column, then run: python batch_covers.py import")


def cmd_import(args):
    """Import CSV with cover URLs, download covers, update manifest and GeoJSON."""
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"CSV file not found: {input_path}")
        sys.exit(1)

    # Read CSV
    rows = []
    with open(input_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = (row.get("url") or "").strip()
            if url:
                rows.append(row)

    if not rows:
        print("No rows with URLs found in CSV. Nothing to do.")
        return

    print(f"Found {len(rows)} rows with URLs to process")

    COVERS_DIR.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest()
    results = []
    success_ids = []

    for i, row in enumerate(rows):
        book_id = (row.get("book_id") or "").strip()
        title = (row.get("title") or "").strip()
        author = (row.get("author") or "").strip()
        url = (row.get("url") or "").strip()

        print(f"[{i+1}/{len(rows)}] {title}... ", end="", flush=True)

        try:
            success, msg = download_cover_from_url(url, book_id)
            if success:
                manifest[book_id] = f"{book_id}.jpg"
                success_ids.append(book_id)
                print("OK")
                results.append({"book_id": book_id, "title": title, "author": author, "success": True})
            else:
                print(f"SKIP: {msg}")
                results.append({"book_id": book_id, "title": title, "author": author, "success": False, "error": msg})
        except Exception as e:
            print(f"FAIL: {e}")
            results.append({"book_id": book_id, "title": title, "author": author, "success": False, "error": str(e)})

    # Save manifest
    save_manifest(manifest)

    # Update GeoJSON for all successful downloads at once
    if success_ids:
        feat_count = update_geojson_has_cover(success_ids)
        print(f"\nUpdated hasCover on {feat_count} GeoJSON features")

    # Generate review HTML
    generate_review_html(results, REVIEW_HTML)
    print(f"Review page: {REVIEW_HTML}")

    # Summary
    success_count = len(success_ids)
    fail_count = len(rows) - success_count
    print(f"\nDownloaded {success_count}/{len(rows)} covers ({fail_count} failed)")


def cmd_status(args):
    """Show a quick dashboard of book data completeness."""
    books = load_books_from_geojson()
    total = len(books)

    missing_cover = sum(1 for bid in books if not (COVERS_DIR / f"{bid}.jpg").exists())
    has_cover = total - missing_cover

    missing_isbn = sum(1 for b in books.values() if not (b["isbn"] or "").strip())
    has_isbn = total - missing_isbn

    # Both missing
    missing_both = sum(
        1 for bid, b in books.items()
        if not (COVERS_DIR / f"{bid}.jpg").exists() and not (b["isbn"] or "").strip()
    )

    print(f"LitMap Book Dashboard")
    print(f"{'='*35}")
    print(f"Total books:       {total:>5}")
    print(f"{'─'*35}")
    print(f"Covers:   {has_cover:>5} have  │ {missing_cover:>5} missing")
    print(f"ISBNs:    {has_isbn:>5} have  │ {missing_isbn:>5} missing")
    print(f"{'─'*35}")
    print(f"Missing both:      {missing_both:>5}")


def main():
    parser = argparse.ArgumentParser(description="Batch book cover workflow")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # status subcommand
    subparsers.add_parser("status", help="Show book data completeness dashboard")

    # export subcommand
    export_parser = subparsers.add_parser("export", help="Export CSV of books missing covers")
    export_parser.add_argument("--limit", type=int, help="Limit number of books exported")
    export_parser.add_argument("--output", default=str(DEFAULT_CSV), help="Output CSV path")

    # import subcommand
    import_parser = subparsers.add_parser("import", help="Import CSV with cover URLs")
    import_parser.add_argument("--input", default=str(DEFAULT_CSV), help="Input CSV path")

    args = parser.parse_args()
    if args.command == "status":
        cmd_status(args)
    elif args.command == "export":
        cmd_export(args)
    elif args.command == "import":
        cmd_import(args)


if __name__ == "__main__":
    main()
