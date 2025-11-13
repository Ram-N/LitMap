"""
Test script to verify the JSON validation function works correctly.
"""

# Sample test data
test_books = [
    # Valid book
    {
        "title": "Test Book 1",
        "author": "Test Author",
        "description": "A test description",
        "genre": "fiction",
        "booktype": "fiction",
        "locations": [
            {
                "city": "Paris",
                "country": "France",
                "latitude": 48.8566,
                "longitude": 2.3522
            }
        ]
    },
    # Missing required field (author)
    {
        "title": "Test Book 2",
        "description": "Missing author",
        "locations": [
            {
                "city": "London",
                "country": "UK",
                "latitude": 51.5074,
                "longitude": -0.1278
            }
        ]
    },
    # Missing locations
    {
        "title": "Test Book 3",
        "author": "Test Author 3",
        "description": "Missing locations",
    },
    # Invalid coordinates
    {
        "title": "Test Book 4",
        "author": "Test Author 4",
        "locations": [
            {
                "city": "Somewhere",
                "country": "Unknown",
                # Missing lat/lng
            }
        ]
    },
    # Valid but with warnings (missing optional fields)
    {
        "title": "Test Book 5",
        "author": "Test Author 5",
        # Missing description, genre, booktype
        "locations": [
            {
                "city": "Tokyo",
                "country": "Japan",
                "latitude": 35.6762,
                "longitude": 139.6503
            }
        ]
    }
]

# Mock all_books for duplicate checking
mock_all_books = [
    {"title": "test book 1", "author": "Someone Else", "id": "abc123"}  # Duplicate of Test Book 1
]

# Simplified validation function for testing (extracted logic)
def validate_book_json_test(books_data, all_books):
    """Test version of validation function"""
    results = {
        'valid_books': [],
        'duplicates': [],
        'invalid_books': [],
        'warnings': []
    }

    for book in books_data:
        errors = []
        warnings = []

        # Check required fields
        if not book.get('title'):
            errors.append("Missing 'title' field")
        if not book.get('author'):
            errors.append("Missing 'author' field")

        # Check locations
        locations = book.get('locations', [])
        if not locations:
            errors.append("Missing 'locations' array")
        else:
            valid_location_found = False
            for loc in locations:
                if 'latitude' in loc and 'longitude' in loc:
                    try:
                        lat = float(loc['latitude'])
                        lng = float(loc['longitude'])
                        if -90 <= lat <= 90 and -180 <= lng <= 180:
                            valid_location_found = True
                            break
                    except (ValueError, TypeError):
                        pass

            if not valid_location_found:
                errors.append("No valid location with latitude/longitude found")

        # Check for optional but recommended fields
        if not book.get('description'):
            warnings.append("Missing 'description' field")
        if not book.get('genre'):
            warnings.append("Missing 'genre' field")
        if not book.get('booktype'):
            warnings.append("Missing 'booktype' field")

        # If there are critical errors, mark as invalid
        if errors:
            results['invalid_books'].append((book, errors))
            continue

        # Check for duplicates by title (case-insensitive)
        title = book.get('title', '').lower()
        existing_matches = [b for b in all_books if b.get('title', '').lower() == title]

        if existing_matches:
            results['duplicates'].append((book, existing_matches))
        else:
            results['valid_books'].append(book)

        # Store warnings separately
        if warnings:
            results['warnings'].append((book, warnings))

    return results


# Run the test
print("=" * 60)
print("TESTING JSON VALIDATION FUNCTION")
print("=" * 60)

results = validate_book_json_test(test_books, mock_all_books)

print(f"\n✅ Valid Books: {len(results['valid_books'])}")
for book in results['valid_books']:
    print(f"   - {book.get('title')}")

print(f"\n⚠️  Duplicates: {len(results['duplicates'])}")
for book, matches in results['duplicates']:
    print(f"   - {book.get('title')} (matches: {[m.get('title') for m in matches]})")

print(f"\n❌ Invalid Books: {len(results['invalid_books'])}")
for book, errors in results['invalid_books']:
    print(f"   - {book.get('title', 'Unknown')}")
    for error in errors:
        print(f"     * {error}")

print(f"\n⚠️  Warnings: {len(results['warnings'])}")
for book, warnings in results['warnings']:
    print(f"   - {book.get('title')}")
    for warning in warnings:
        print(f"     * {warning}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)

# Expected results:
# Valid: Test Book 5 (has warnings but no errors)
# Duplicates: Test Book 1 (matches mock_all_books)
# Invalid: Test Book 2 (missing author), Test Book 3 (missing locations), Test Book 4 (invalid coordinates)
# Warnings: Test Book 5 (missing description, genre, booktype)
