"""One-time migration: replace Firebase IDs with human-readable book IDs.

Usage:
    python migrate_ids.py              # Dry run — show mapping, no changes
    python migrate_ids.py --execute    # Perform the migration
"""

import argparse
import json
import os
import shutil
from collections import Counter
from pathlib import Path

from generate_book_id import generate_book_id

GEOJSON_FILE = Path(__file__).parent / "../vue-app/public/litmap-data.geojson"
COVERS_DIR = Path(__file__).parent / "../vue-app/public/covers"
MANIFEST_FILE = COVERS_DIR / "manifest.json"
MAPPING_FILE = Path(__file__).parent / "id_migration_map.json"


def load_geojson():
    with open(GEOJSON_FILE) as f:
        return json.load(f)


def build_id_mapping(geojson):
    """Build old_id -> new_id mapping from GeoJSON features."""
    # Collect unique books by old bookId
    books = {}
    for feat in geojson["features"]:
        props = feat["properties"]
        old_id = props.get("bookId", "")
        if old_id and old_id not in books:
            books[old_id] = {
                "title": props.get("title", ""),
                "author": props.get("author", ""),
                "isbn": props.get("isbn"),
            }

    # Generate new IDs, tracking collisions
    mapping = {}
    seen_new_ids = Counter()

    for old_id, info in books.items():
        new_id = generate_book_id(info["title"], info["author"], info["isbn"])

        if new_id is None:
            # Fall back to original Firebase ID
            print(f"  WARNING: No title/author/isbn for {old_id}, keeping original ID")
            new_id = old_id

        seen_new_ids[new_id] += 1
        count = seen_new_ids[new_id]

        if count > 1:
            suffixed = f"{new_id}-{count}"
            print(f"  COLLISION: {new_id} (book #{count}: '{info['title']}') -> {suffixed}")
            mapping[old_id] = suffixed
        else:
            mapping[old_id] = new_id

    return mapping


def rewrite_geojson(geojson, mapping):
    """Rewrite bookId values and hasCover flags in GeoJSON."""
    for feat in geojson["features"]:
        props = feat["properties"]
        old_id = props.get("bookId", "")
        if old_id in mapping:
            new_id = mapping[old_id]
            props["bookId"] = new_id
            # Update hasCover based on whether the cover file will exist
            cover_path = COVERS_DIR / f"{new_id}.jpg"
            old_cover = COVERS_DIR / f"{old_id}.jpg"
            props["hasCover"] = cover_path.exists() or old_cover.exists()


def rename_covers(mapping, dry_run=True):
    """Rename cover image files from old IDs to new IDs."""
    renamed = 0
    errors = []

    for old_id, new_id in mapping.items():
        if old_id == new_id:
            continue
        old_path = COVERS_DIR / f"{old_id}.jpg"
        new_path = COVERS_DIR / f"{new_id}.jpg"

        if old_path.exists():
            if dry_run:
                print(f"  RENAME: {old_path.name} -> {new_path.name}")
            else:
                try:
                    shutil.move(str(old_path), str(new_path))
                except Exception as e:
                    errors.append((old_path.name, str(e)))
                    continue
            renamed += 1

    return renamed, errors


def rewrite_manifest(mapping):
    """Rewrite manifest.json with new IDs."""
    if not MANIFEST_FILE.exists():
        return

    with open(MANIFEST_FILE) as f:
        manifest = json.load(f)

    new_manifest = {}
    for old_id, filename in manifest.items():
        new_id = mapping.get(old_id, old_id)
        # Update both key and filename
        new_manifest[new_id] = f"{new_id}.jpg"

    with open(MANIFEST_FILE, "w") as f:
        json.dump(new_manifest, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Migrate Firebase IDs to human-readable book IDs")
    parser.add_argument("--execute", action="store_true", help="Perform the migration (default is dry run)")
    args = parser.parse_args()

    dry_run = not args.execute

    if dry_run:
        print("=== DRY RUN (no changes will be made) ===")
        print("Use --execute to perform the migration.\n")
    else:
        print("=== EXECUTING MIGRATION ===\n")

    # Load data
    geojson = load_geojson()
    total_features = len(geojson["features"])
    print(f"Loaded {total_features} features from GeoJSON")

    # Build mapping
    print("\nBuilding ID mapping...")
    mapping = build_id_mapping(geojson)

    # Save mapping file (always, even in dry run)
    with open(MAPPING_FILE, "w") as f:
        json.dump(mapping, f, indent=2)
    print(f"Saved mapping to {MAPPING_FILE}")

    # Statistics
    isbn_based = sum(1 for v in mapping.values() if v.isdigit() and len(v) == 13)
    slug_based = sum(1 for v in mapping.values() if not (v.isdigit() and len(v) == 13))
    unchanged = sum(1 for k, v in mapping.items() if k == v)
    collisions = sum(1 for v in mapping.values() if v.endswith(("-2", "-3", "-4", "-5")))

    print(f"\n--- Summary ---")
    print(f"Total unique books: {len(mapping)}")
    print(f"ISBN-based IDs:     {isbn_based}")
    print(f"Slug-based IDs:     {slug_based}")
    print(f"Unchanged (fallback): {unchanged}")
    print(f"Collisions resolved:  {collisions}")

    # Show some examples
    print(f"\n--- Sample mappings ---")
    items = list(mapping.items())
    for old_id, new_id in items[:10]:
        print(f"  {old_id} -> {new_id}")
    if len(items) > 10:
        print(f"  ... and {len(items) - 10} more")

    # Rename covers (preview)
    print(f"\n--- Cover files ---")
    renamed_count, _ = rename_covers(mapping, dry_run=True)
    print(f"Cover files to rename: {renamed_count}")

    if not dry_run:
        print("\nExecuting migration...")

        # 1. Rename cover files first (before rewriting references)
        print("  Renaming cover files...")
        renamed, errors = rename_covers(mapping, dry_run=False)
        print(f"  Renamed {renamed} cover files")
        if errors:
            print(f"  Errors: {len(errors)}")
            for name, err in errors:
                print(f"    {name}: {err}")

        # 2. Rewrite GeoJSON
        print("  Rewriting GeoJSON...")
        rewrite_geojson(geojson, mapping)
        with open(GEOJSON_FILE, "w") as f:
            json.dump(geojson, f, indent=2)
        print(f"  Written to {GEOJSON_FILE}")

        # 3. Rewrite manifest
        print("  Rewriting manifest...")
        rewrite_manifest(mapping)
        print(f"  Written to {MANIFEST_FILE}")

        print("\nMigration complete!")
    else:
        print("\nDry run complete. Use --execute to apply changes.")


if __name__ == "__main__":
    main()
