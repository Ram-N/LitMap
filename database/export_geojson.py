"""Export all Firebase book data to GeoJSON format for static site deployment."""

import json
from collections import Counter
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore

from generate_book_id import generate_book_id

SERVICE_ACCOUNT_KEY = "litmap-88358-firebase-adminsdk-9w1l9-73ca515ce7.json"
COLLECTIONS = ["books", "newbooks"]
OUTPUT_FILE = "../vue-app/public/litmap-data.geojson"
COVERS_DIR = Path(__file__).parent / "../vue-app/public/covers"


def init_firebase():
    cred = credentials.Certificate(SERVICE_ACCOUNT_KEY)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    return firestore.client()


def fetch_all_books(db):
    """Fetch books from all collections, deduplicating by title+author."""
    seen = set()
    books = []

    for collection_name in COLLECTIONS:
        docs = db.collection(collection_name).stream()
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            key = (data.get("title", "").strip().lower(), data.get("author", "").strip().lower())
            if key not in seen:
                seen.add(key)
                # Generate human-readable ID
                readable_id = generate_book_id(
                    data.get("title", ""),
                    data.get("author", ""),
                    data.get("isbn"),
                )
                data["readable_id"] = readable_id if readable_id else data["id"]
                books.append(data)

    # Resolve collisions across all books
    id_counts = Counter()
    for book in books:
        rid = book["readable_id"]
        id_counts[rid] += 1

    seen_ids = Counter()
    for book in books:
        rid = book["readable_id"]
        seen_ids[rid] += 1
        if id_counts[rid] > 1 and seen_ids[rid] > 1:
            book["readable_id"] = f"{rid}-{seen_ids[rid]}"

    return books


def book_to_geojson_features(book):
    """Convert a book with locations into GeoJSON Feature objects.

    Each location becomes a separate Feature so markers map 1:1 with points.
    Book metadata is duplicated across features for the same book.
    """
    features = []
    locations = book.get("locations", [])

    if not locations:
        return features

    # Shared properties for all locations of this book
    props = {
        "title": book.get("title", ""),
        "author": book.get("author", ""),
        "description": book.get("description", ""),
        "booktype": book.get("booktype", ""),
        "genre": book.get("genre", ""),
        "rating": book.get("rating"),
        "pageCount": book.get("pageCount"),
        "isbn": book.get("isbn", ""),
        "language": book.get("language", ""),
        "publisher": book.get("publisher", ""),
        "publicationDate": book.get("publicationDate", ""),
        "coverImageUrl": book.get("cover", "") or book.get("coverImageUrl", ""),
        "hasCover": (COVERS_DIR / f"{book.get('readable_id', book.get('id', ''))}.jpg").exists(),
        "tags": book.get("tags", []),
        "bookId": book.get("readable_id", book.get("id", "")),
    }

    for loc in locations:
        lat = loc.get("latitude")
        lng = loc.get("longitude")

        if lat is None or lng is None:
            continue

        # GeoJSON uses [longitude, latitude] order
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(lng), float(lat)],
            },
            "properties": {
                **props,
                "locationCity": loc.get("city", loc.get("place", "")),
                "locationCountry": loc.get("country", ""),
                "locationDescription": loc.get("description", ""),
            },
        }
        features.append(feature)

    return features


def main():
    db = init_firebase()
    books = fetch_all_books(db)
    print(f"Fetched {len(books)} unique books from {COLLECTIONS}")

    features = []
    books_with_locations = 0
    for book in books:
        book_features = book_to_geojson_features(book)
        if book_features:
            books_with_locations += 1
        features.extend(book_features)

    geojson = {
        "type": "FeatureCollection",
        "features": features,
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(geojson, f, indent=2, default=str)

    print(f"Books with locations: {books_with_locations}")
    print(f"Total location features: {len(features)}")
    print(f"Written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
