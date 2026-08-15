# GeoJSON Client — reads/writes book data from litmap-data.geojson

import json
import re
import streamlit as st
import pandas as pd

from generate_book_id import generate_book_id


def normalize_locations(locations):
    """
    Normalize location data by removing empty fields and ensuring consistent structure.
    This prevents false positives when comparing locations.
    """
    if not locations:
        return []

    normalized = []
    for loc in locations:
        # Create a clean dict with only non-empty values
        clean_loc = {}
        for key, value in loc.items():
            # Skip empty strings, None values, and NaN values
            if value not in ['', None] and not (isinstance(value, float) and pd.isna(value)):
                # Convert numpy types to Python types for proper comparison
                if hasattr(value, 'item'):  # numpy types have .item() method
                    clean_loc[key] = value.item()
                else:
                    # Ensure standard Python types (not numpy)
                    if isinstance(value, (int, float)):
                        clean_loc[key] = float(value) if '.' in str(value) or isinstance(value, float) else int(value)
                    else:
                        clean_loc[key] = value

        if clean_loc:  # Only add non-empty locations
            normalized.append(clean_loc)

    return normalized


class GeoJSONClient:
    """Client for reading/writing book data from litmap-data.geojson."""

    def __init__(self, geojson_path: str):
        self.geojson_path = geojson_path
        with open(geojson_path) as f:
            self.geojson = json.load(f)
        self._build_books_list()

    def _build_books_list(self):
        """Extract unique books from GeoJSON features, keyed by bookId."""
        books_by_id = {}
        for feat in self.geojson["features"]:
            props = feat["properties"]
            bid = props.get("bookId", "")
            if bid and bid not in books_by_id:
                book = {}
                # Map GeoJSON properties to the book dict format used by the UI
                book['id'] = bid
                book['title'] = props.get('title', '')
                book['author'] = props.get('author', '')
                book['description'] = props.get('description', '')
                book['booktype'] = props.get('booktype', '')
                book['genre'] = props.get('genre', '')
                book['rating'] = props.get('rating')
                book['pageCount'] = props.get('pageCount')
                book['isbn'] = props.get('isbn')
                book['language'] = props.get('language', '')
                book['publisher'] = props.get('publisher')
                book['year'] = props.get('publicationDate', '')
                book['cover'] = props.get('coverImageUrl', '')
                book['hasCover'] = props.get('hasCover', False)
                book['tags'] = props.get('tags', [])
                book['goodreadsLink'] = props.get('goodreadsLink', '')
                # Collect locations from all features for this book
                book['locations'] = []
                books_by_id[bid] = book

        # Second pass: collect all locations for each book
        for feat in self.geojson["features"]:
            props = feat["properties"]
            bid = props.get("bookId", "")
            if bid in books_by_id:
                coords = feat.get("geometry", {}).get("coordinates", [None, None])
                loc = {
                    "city": props.get("locationCity", ""),
                    "country": props.get("locationCountry", ""),
                    "latitude": coords[1] if coords[1] is not None else 0,
                    "longitude": coords[0] if coords[0] is not None else 0,
                }
                loc_desc = props.get("locationDescription", "")
                if loc_desc:
                    loc["description"] = loc_desc
                books_by_id[bid]['locations'].append(loc)

        self._books_by_id = books_by_id
        self._books_list = list(books_by_id.values())

    def get_all_books(self) -> list:
        """Return list of all unique books."""
        return self._books_list

    def get_book_count(self) -> int:
        return len(self._books_list)

    def get_document_by_id(self, books, book_id):
        """Fetch a book from a book list using its ID."""
        for book in books:
            if book.get('id') == book_id:
                return book
        st.write(f"No book found with ID: {book_id}")
        return None

    def fuzzy_match(self, books, attribute, search_string):
        """
        Perform a fuzzy (substring) search on a list of books for a given attribute.

        Args:
            books (list): A list of book dicts.
            attribute (str): The attribute to search (e.g., 'title', 'author').
            search_string (str): The string to search for.

        Returns:
            list: Books where the attribute contains the search string (case-insensitive).
        """
        search_string = search_string.lower()
        matching_books = []
        for book in books:
            if attribute in book:
                attribute_value = str(book[attribute]).lower()
                if search_string in attribute_value:
                    matching_books.append(book)
        return matching_books

    def get_book_by_title(self, books: list, title: str) -> list:
        return self.fuzzy_match(books, 'title', title)

    def get_books_by_author(self, books: list, author_name: str) -> list:
        return self.fuzzy_match(books, 'author', author_name)

    def get_books_by_genre(self, books: list, genre: str) -> list:
        return self.fuzzy_match(books, 'genre', genre)

    def book_exists(self, book: dict, all_books: list) -> bool:
        """Check if a book already exists by title."""
        matches = self.get_book_by_title(all_books, book['title'])
        return len(matches) > 0

    def compare_books(self, books, book_id1, book_id2):
        book1 = self.get_document_by_id(books, book_id1)
        book2 = self.get_document_by_id(books, book_id2)

        if not book1 or not book2:
            st.write("One or both books were not found.")
            return

        st.write(f"## Comparing Books: `{book_id1}` vs `{book_id2}`")
        st.write("---")

        for key, value1 in book1.items():
            if key in book2:
                value2 = book2[key]
                if value1 == value2:
                    st.write(f" **{key.capitalize()}**: {value1}")
                else:
                    st.write(f" **{key.capitalize()}**:")
                    st.write(f"- Book 1: `{value1}`")
                    st.write(f"- Book 2: `{value2}`")
            else:
                st.write(f"### **{key.capitalize()}** exists only in Book 1: {value1}")

        for key in book2.keys():
            if key not in book1:
                st.write(f"### **{key.capitalize()}** exists only in Book 2: {book2[key]}")

    def update_book(self, book_id: str, changes: dict) -> bool:
        """Update properties for all features matching bookId, then save."""
        try:
            # Map book dict fields back to GeoJSON property names
            field_map = {
                'title': 'title',
                'author': 'author',
                'description': 'description',
                'booktype': 'booktype',
                'genre': 'genre',
                'rating': 'rating',
                'pageCount': 'pageCount',
                'isbn': 'isbn',
                'language': 'language',
                'publisher': 'publisher',
                'year': 'publicationDate',
                'cover': 'coverImageUrl',
                'hasCover': 'hasCover',
                'tags': 'tags',
                'goodreadsLink': 'goodreadsLink',
            }

            # Handle location changes separately
            if 'locations' in changes:
                self._update_locations(book_id, changes['locations'])

            # Update non-location properties on all features for this book
            non_loc_changes = {k: v for k, v in changes.items() if k != 'locations'}
            if non_loc_changes:
                for feat in self.geojson["features"]:
                    if feat["properties"].get("bookId") == book_id:
                        for field, value in non_loc_changes.items():
                            geojson_field = field_map.get(field, field)
                            feat["properties"][geojson_field] = value

            self.save()
            self._build_books_list()
            return True
        except Exception as e:
            print(f"Error updating book {book_id}: {e}")
            return False

    def _update_locations(self, book_id: str, new_locations: list):
        """Replace all features for a bookId with new location features."""
        # Grab a reference feature to copy book-level properties
        ref_props = None
        for feat in self.geojson["features"]:
            if feat["properties"].get("bookId") == book_id:
                ref_props = dict(feat["properties"])
                break

        if ref_props is None:
            return

        # Remove old features for this book
        self.geojson["features"] = [
            f for f in self.geojson["features"]
            if f["properties"].get("bookId") != book_id
        ]

        # Add new features
        for loc in new_locations:
            new_props = dict(ref_props)
            new_props["locationCity"] = loc.get("city", "")
            new_props["locationCountry"] = loc.get("country", "")
            new_props["locationDescription"] = loc.get("description", "")
            lng = loc.get("longitude", 0)
            lat = loc.get("latitude", 0)
            new_feat = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lng, lat]
                },
                "properties": new_props
            }
            self.geojson["features"].append(new_feat)

    def add_book(self, book_dict: dict) -> str:
        """Add a new book to the GeoJSON. Returns the generated bookId."""
        book_id = generate_book_id(
            book_dict.get('title', ''),
            book_dict.get('author', ''),
            book_dict.get('isbn'),
        )
        if not book_id:
            # Fallback: use sanitized title
            book_id = re.sub(r'[^a-zA-Z0-9]', '', book_dict.get('title', 'unknown'))[:20]

        # Ensure uniqueness
        existing_ids = {f["properties"].get("bookId") for f in self.geojson["features"]}
        base_id = book_id
        counter = 1
        while book_id in existing_ids:
            book_id = f"{base_id}-{counter}"
            counter += 1

        locations = book_dict.get('locations', [])
        if not locations:
            locations = [{"city": "", "country": "", "latitude": 0, "longitude": 0}]

        for loc in locations:
            props = {
                "title": book_dict.get('title', ''),
                "author": book_dict.get('author', ''),
                "description": book_dict.get('description', ''),
                "booktype": book_dict.get('booktype', ''),
                "genre": book_dict.get('genre', ''),
                "rating": book_dict.get('rating'),
                "pageCount": book_dict.get('pageCount'),
                "isbn": book_dict.get('isbn'),
                "language": book_dict.get('language', ''),
                "publisher": book_dict.get('publisher'),
                "publicationDate": book_dict.get('year', book_dict.get('publicationDate', '')),
                "coverImageUrl": book_dict.get('cover', book_dict.get('coverImageUrl')),
                "hasCover": book_dict.get('hasCover', False),
                "tags": book_dict.get('tags', []),
                "goodreadsLink": book_dict.get('goodreadsLink', ''),
                "bookId": book_id,
                "locationCity": loc.get('city', ''),
                "locationCountry": loc.get('country', ''),
                "locationDescription": loc.get('description', ''),
            }
            lng = loc.get('longitude', 0)
            lat = loc.get('latitude', 0)
            feat = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lng, lat]
                },
                "properties": props
            }
            self.geojson["features"].append(feat)

        self.save()
        self._build_books_list()
        return book_id

    def add_books_to_geojson(self, to_be_added: list, all_books: list):
        """Add a list of books, skipping duplicates."""
        st.write(f"Attempting to add {len(to_be_added)} book(s)")
        for book in to_be_added:
            if not self.book_exists(book, all_books):
                st.success(f"Adding {book['title']}")
                self.add_book(book)
            else:
                st.warning(f"{book['title']} already exists")

    def delete_book(self, book_id: str):
        """Remove all features with matching bookId, then save."""
        before = len(self.geojson["features"])
        self.geojson["features"] = [
            f for f in self.geojson["features"]
            if f["properties"].get("bookId") != book_id
        ]
        after = len(self.geojson["features"])
        self.save()
        self._build_books_list()
        print(f"Deleted book {book_id}: removed {before - after} feature(s)")

    def save(self):
        """Write GeoJSON back to disk."""
        with open(self.geojson_path, "w") as f:
            json.dump(self.geojson, f, indent=2)
