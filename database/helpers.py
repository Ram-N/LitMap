# Helper functions for LitMap Data Manager

import json
import re
import streamlit as st
from datetime import datetime
from geopy.geocoders import Nominatim


def geocode_location(city, country):
    """
    Geocode a location using OpenStreetMap Nominatim (free, no API key required).

    Args:
        city (str): City or place name
        country (str): Country name

    Returns:
        dict: Location dictionary with lat/lng, or None if not found
    """
    try:
        geolocator = Nominatim(user_agent="litmap_editor_v1")
        # Combine city and country for better results
        query = f"{city}, {country}"
        location = geolocator.geocode(query, timeout=10)

        if location:
            return {
                "city": city,
                "country": country,
                "latitude": round(location.latitude, 4),
                "longitude": round(location.longitude, 4)
            }
        else:
            return None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None


def sanitize_filename(filename):
    """Remove any characters that are not alphanumeric or underscores."""
    return re.sub(r'[^a-zA-Z0-9_]', '_', filename)


def write_book_json(geojson_client, all_books, title=None, book_id=None, verbose=False):
    # Validate inputs
    if not title and not book_id:
        raise ValueError("Please provide either a title or an ID to search for the book.")

    # Search for the book in all_books
    books = []
    if title:
        books = geojson_client.get_book_by_title(all_books, title)
    if book_id:
        book = geojson_client.get_document_by_id(all_books, book_id)
        books = [book] if book else []

    if not books:
        print(f"No matching Books found {title} {book_id}")
        return

    # Create filename: First 20 chars of title + "_" + book ID + ".json"
    book = books[0]
    truncated_title = sanitize_filename(book['title'][:20])
    filename = f"{truncated_title}_{book['id']}.json"

    # Write book details to JSON file
    with open(filename, 'w') as f:
        json.dump(books, f, indent=4)

    if verbose:
        print(f"Book details saved to: {filename}")

    st.write(f"Book details saved to: `{filename}`")


def read_json_file(file):
    try:
        file_data = json.load(file)
        return file_data
    except Exception as e:
        st.sidebar.error(f"Error reading the file: {file} {e}")
        return None


def validate_book_json(books_data, all_books, geojson_client):
    """
    Validate a list of books from JSON upload.

    Returns:
        dict: {
            'valid_books': list of books that pass all checks,
            'duplicates': list of (book, existing_matches) tuples,
            'invalid_books': list of (book, error_messages) tuples,
            'warnings': list of (book, warning_messages) tuples
        }
    """
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
            # Check that at least one location has valid lat/lng
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

        # Check for duplicates by title
        title = book.get('title', '')
        existing_matches = geojson_client.get_book_by_title(all_books, title)

        if existing_matches:
            results['duplicates'].append((book, existing_matches))
        else:
            results['valid_books'].append(book)

        # Store warnings separately
        if warnings:
            results['warnings'].append((book, warnings))

    return results


def write_all_books_to_json(all_books):
    """Writes all books to a JSON backup file."""
    # Generate filename with current date and time
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    filename = f"backup/litmap_{timestamp}.json"

    # Write the list of books to the JSON file
    with open(filename, "w") as json_file:
        json.dump(all_books, json_file, indent=4)

    st.success(f"All books saved to {filename}")
    return filename


def reset_confirmation():
    st.session_state.backup_confirmed = False


def compare_json_objects(old_dict, new_dict):
    """
    Compare two dictionaries and return a structured diff.

    Returns:
        dict: {
            'added': {field: value},
            'removed': {field: value},
            'changed': {field: {'old': old_value, 'new': new_value}},
            'unchanged': {field: value}
        }
    """
    diff = {
        'added': {},
        'removed': {},
        'changed': {},
        'unchanged': {}
    }

    all_keys = set(old_dict.keys()) | set(new_dict.keys())

    for key in all_keys:
        if key not in old_dict:
            diff['added'][key] = new_dict[key]
        elif key not in new_dict:
            diff['removed'][key] = old_dict[key]
        elif old_dict[key] != new_dict[key]:
            diff['changed'][key] = {
                'old': old_dict[key],
                'new': new_dict[key]
            }
        else:
            diff['unchanged'][key] = old_dict[key]

    return diff


def display_json_diff(diff_data, original_book):
    """
    Display the JSON differences with color-coded highlighting.

    Args:
        diff_data: Dictionary from compare_json_objects()
        original_book: The original book dict for context
    """
    st.markdown("### Changes Summary")

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Added", len(diff_data['added']))
    with col2:
        st.metric("Removed", len(diff_data['removed']))
    with col3:
        st.metric("Changed", len(diff_data['changed']))
    with col4:
        st.metric("Unchanged", len(diff_data['unchanged']))

    st.markdown("---")

    # Display added fields
    if diff_data['added']:
        st.markdown("### **Added Fields**")
        for field, value in diff_data['added'].items():
            st.markdown(f"**`{field}`**")
            if isinstance(value, (list, dict)):
                st.json(value)
            else:
                st.success(f"New value: `{value}`")
        st.markdown("---")

    # Display removed fields
    if diff_data['removed']:
        st.markdown("### **Removed Fields**")
        for field, value in diff_data['removed'].items():
            st.markdown(f"**`{field}`**")
            if isinstance(value, (list, dict)):
                st.json(value)
            else:
                st.error(f"Removed value: `{value}`")
        st.markdown("---")

    # Display changed fields
    if diff_data['changed']:
        st.markdown("### **Changed Fields**")
        for field, changes in diff_data['changed'].items():
            st.markdown(f"**`{field}`**")

            col_old, col_arrow, col_new = st.columns([2, 1, 2])

            with col_old:
                st.caption("**Old Value:**")
                if isinstance(changes['old'], (list, dict)):
                    st.json(changes['old'])
                else:
                    st.code(str(changes['old']))

            with col_arrow:
                st.markdown("### ->")

            with col_new:
                st.caption("**New Value:**")
                if isinstance(changes['new'], (list, dict)):
                    st.json(changes['new'])
                else:
                    st.code(str(changes['new']))

            st.markdown("---")

    # Collapsible section for unchanged fields
    if diff_data['unchanged']:
        with st.expander(f"View {len(diff_data['unchanged'])} Unchanged Fields"):
            for field, value in diff_data['unchanged'].items():
                st.markdown(f"**`{field}`**: `{value}`")
                st.markdown("")
