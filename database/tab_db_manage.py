# DB-Manage tab logic

import json
import time
import streamlit as st
import pandas as pd

from geojson_client import normalize_locations
from helpers import (
    geocode_location,
    write_book_json,
    read_json_file,
    validate_book_json,
    write_all_books_to_json,
    reset_confirmation,
    compare_json_objects,
    display_json_diff,
)


def render_db_manage_tab(tab, geojson_client, all_books):
    """Render the DB-Manage tab contents."""

    db_options = {
        0: "Select DB Action",
        # Import/Upload Operations
        1: "Upload Books from JSON",
        # Edit Operations
        2: "Edit Book",
        7: "Edit Existing JSON",
        # Export/Backup Operations
        3: "Export Collection (Full Backup)",
        4: "Export Single Book",
        # Delete Operations
        5: "Delete Book by ID",
        6: "Backup & Delete Book"
    }

    tooltips = {
        "Select DB Action": "Choose a database operation to perform",
        "Upload Books from JSON": "Import books from JSON files into GeoJSON with validation and duplicate checking",
        "Edit Book": "Modify book details including title, author, locations, and metadata",
        "Edit Existing JSON": "Advanced: Edit book data directly as JSON with diff preview before saving",
        "Export Collection (Full Backup)": "Download entire dataset as a timestamped backup JSON file",
        "Export Single Book": "Export a single book to JSON file by title or ID",
        "Delete Book by ID": "Permanently remove a book using its unique identifier",
        "Backup & Delete Book": "Create a backup copy then delete the book from the dataset"
    }

    with tab:
        st.session_state.current_tab = "DB"

        # Determine the default index for db_action selectbox
        if 'edit_selected_book' in st.session_state and st.session_state.edit_selected_book is not None:
            edit_field_key = 2  # "Edit Book" is at key 2
            default_index = list(db_options.keys()).index(edit_field_key)
        else:
            default_index = 0

        db_action = st.selectbox(
            label="Choose action for DB-Manage",
            options=db_options.values(),
            index=default_index
        )

        if db_action in tooltips:
            st.sidebar.info(tooltips[db_action])

        # Only show global search for specific actions that need it
        if db_action == db_options[2]:  # "Edit Book"
            st.write("---")
            search_option = st.selectbox("Search by", ("Author", "Book Title", "Genre"))
            search_input = st.text_input(f"Enter {search_option}")
            search_button = st.button("Search")
            st.write("---")

            # Initialize session state for search results
            if 'search_results' not in st.session_state:
                st.session_state.search_results = []
            if 'last_search_query' not in st.session_state:
                st.session_state.last_search_query = ""
            if 'db_action_index' not in st.session_state:
                st.session_state.db_action_index = 0

            # Search logic and store results in session state
            if search_button:
                st.write(f"{search_option} {search_input}")
                if search_option == "Author":
                    books = geojson_client.get_books_by_author(all_books, search_input)
                elif search_option == "Book Title":
                    books = geojson_client.get_book_by_title(all_books, search_input)
                elif search_option == "Genre":
                    books = geojson_client.fuzzy_match(all_books, 'genre', search_input)

                st.session_state.search_results = books
                st.session_state.last_search_query = f"{search_option}: {search_input}"

            # Display search results
            if st.session_state.search_results:
                books = st.session_state.search_results
                st.write(f"Found {len(books)} books:")

                for book in books:
                    col_info, col_action = st.columns([4, 1])

                    with col_info:
                        st.markdown(f"**{book.get('title', 'N/A')}**")
                        st.caption(f"**By:** {book.get('author', 'N/A')} | **Genre:** {book.get('genre', 'N/A')} | **Year:** {book.get('year', 'N/A')}")
                        st.caption(f"**Publisher:** {book.get('publisher', 'N/A')} | **ID:** `{book.get('id', 'N/A')}`")

                    with col_action:
                        if st.button("Edit", key=f"edit_btn_{book.get('id')}", type="primary", width='stretch'):
                            st.session_state.edit_selected_book = book
                            st.success(f"Selected: {book.get('title', 'N/A')}")
                            st.rerun()

                    st.markdown("---")

            elif search_button:
                st.write(f"No books found for {search_option} {search_input}")

        placeholder_db = st.empty()
        with placeholder_db.container():

            if db_action == db_options[1]:  # Upload Books from JSON
                _render_upload_books(geojson_client, all_books)

            if db_action == db_options[3]:  # Export Collection (Full Backup)
                _render_export_collection(all_books)

            if db_action == db_options[2]:  # Edit Book
                _render_edit_book(geojson_client, all_books)

            if db_action == db_options[7]:  # Edit Existing JSON
                _render_edit_json(geojson_client, all_books)

            if db_action == db_options[4]:  # Export Single Book
                _render_export_single(geojson_client, all_books)

            if db_action == db_options[5]:  # Delete Book by ID
                _render_delete_book(geojson_client)

    return placeholder_db


def _render_upload_books(geojson_client, all_books):
    """Render the Upload Books from JSON sub-action."""
    st.session_state.backup_confirmed = False

    # Initialize session state for upload workflow
    if 'upload_validated' not in st.session_state:
        st.session_state.upload_validated = False
    if 'upload_validation_results' not in st.session_state:
        st.session_state.upload_validation_results = None
    if 'upload_file_data' not in st.session_state:
        st.session_state.upload_file_data = None
    if 'upload_confirmed' not in st.session_state:
        st.session_state.upload_confirmed = False

    print(st.session_state)
    print('Upload Books from JSON')

    st.write("### Upload Books from JSON")
    st.write("**Two-step process:** Validate -> Confirm -> Upload")

    # File uploader
    uploaded_file = st.file_uploader("Choose a JSON file to Upload", type="json", key="json_uploader")

    # STEP 1: Validation Phase
    if uploaded_file is not None and not st.session_state.upload_validated:
        st.markdown("---")
        st.markdown("#### Step 1: Validate JSON File")

        if st.button("Validate JSON", type="primary", key="validate_json_btn"):
            book_data = read_json_file(uploaded_file)

            if book_data:
                if isinstance(book_data, list):
                    # Run validation
                    with st.spinner("Validating books..."):
                        validation_results = validate_book_json(book_data, all_books, geojson_client)

                    # Store in session state
                    st.session_state.upload_file_data = book_data
                    st.session_state.upload_validation_results = validation_results
                    st.session_state.upload_validated = True
                    st.rerun()
                else:
                    st.error("Invalid format: The JSON file must contain a list of books.")
            else:
                st.error("Failed to read JSON file. Please check the file format.")

    # STEP 2: Display Validation Results and Confirmation
    if st.session_state.upload_validated and st.session_state.upload_validation_results:
        results = st.session_state.upload_validation_results

        st.markdown("---")
        st.markdown("#### Step 2: Validation Results")

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Valid Books", len(results['valid_books']))
        with col2:
            st.metric("Duplicates", len(results['duplicates']))
        with col3:
            st.metric("Invalid", len(results['invalid_books']))
        with col4:
            total_books = len(results['valid_books']) + len(results['duplicates']) + len(results['invalid_books'])
            st.metric("Total in File", total_books)

        # Display invalid books (blocking errors)
        if results['invalid_books']:
            st.error(f"**{len(results['invalid_books'])} Invalid Book(s) Found** - These will NOT be uploaded:")

            for book, errors in results['invalid_books']:
                with st.expander(f"{book.get('title', 'Unknown Title')} by {book.get('author', 'Unknown Author')}"):
                    st.write("**Errors:**")
                    for error in errors:
                        st.write(f"- {error}")
                    st.json(book)

        # Display duplicates (warnings)
        if results['duplicates']:
            st.warning(f"**{len(results['duplicates'])} Duplicate(s) Found** - These will be SKIPPED:")

            for book, existing_matches in results['duplicates']:
                with st.expander(f"{book.get('title', 'Unknown Title')} - Already exists"):
                    st.write(f"**Found {len(existing_matches)} existing book(s) with this title:**")
                    for match in existing_matches:
                        st.write(f"- ID: `{match.get('id')}` | Author: {match.get('author')} | Year: {match.get('year')}")

        # Display valid books (ready to upload)
        if results['valid_books']:
            st.success(f"**{len(results['valid_books'])} Valid Book(s)** - Ready to upload:")

            for book in results['valid_books']:
                with st.expander(f"{book.get('title')} by {book.get('author')}"):
                    st.write(f"**Genre:** {book.get('genre', 'N/A')} | **Type:** {book.get('booktype', 'N/A')}")
                    st.write(f"**Locations:** {len(book.get('locations', []))} location(s)")

                    # Show warnings if any
                    warnings = [w for b, w in results['warnings'] if b.get('title') == book.get('title')]
                    if warnings:
                        st.caption("Warnings (non-blocking):")
                        for warning_list in warnings:
                            for warning in warning_list:
                                st.caption(f"  - {warning}")

        # STEP 3: Confirmation
        st.markdown("---")

        if results['valid_books']:
            st.markdown("#### Step 3: Confirm Upload")
            st.info(f"**Summary:** Ready to add **{len(results['valid_books'])}** new book(s) to GeoJSON")

            col_confirm, col_cancel = st.columns([1, 1])

            with col_confirm:
                if st.button("Confirm and Upload Books", type="primary", key="confirm_upload_btn"):
                    # Perform the upload
                    with st.spinner(f"Uploading {len(results['valid_books'])} books..."):
                        geojson_client.add_books_to_geojson(results['valid_books'], all_books)

                    st.success(f"Successfully added {len(results['valid_books'])} book(s)!")
                    st.balloons()

                    # Reset session state
                    st.session_state.upload_validated = False
                    st.session_state.upload_validation_results = None
                    st.session_state.upload_file_data = None
                    st.session_state.upload_confirmed = False

                    st.info("Upload complete! You can upload another file by refreshing or selecting a new file.")

            with col_cancel:
                if st.button("Cancel Upload", key="cancel_upload_btn"):
                    st.session_state.upload_validated = False
                    st.session_state.upload_validation_results = None
                    st.session_state.upload_file_data = None
                    st.session_state.upload_confirmed = False
                    st.rerun()
        else:
            st.error("No valid books to upload. Please fix the errors in your JSON file or remove duplicates.")

            if st.button("Start Over", key="reset_upload_btn"):
                st.session_state.upload_validated = False
                st.session_state.upload_validation_results = None
                st.session_state.upload_file_data = None
                st.session_state.upload_confirmed = False
                st.rerun()


def _render_export_collection(all_books):
    """Render the Export Collection sub-action."""
    print('attempting Export to JSON')
    # Initialize backup_confirmed if not exists
    if 'backup_confirmed' not in st.session_state:
        st.session_state.backup_confirmed = False

    if not st.session_state.backup_confirmed:
        with st.container():
            st.warning("Export Confirmation")
            st.write("Export all book data to JSON?")
            st.write("This will:")
            st.markdown("""
                - Create a new JSON file with current timestamp
                - Save all books from the GeoJSON dataset
                - Store the file in the 'backup' directory
            """)

            st.write("")

            col1, col2, col3 = st.columns([1, 1, 3])

            with col1:
                if st.button("Yes, Export", type="primary"):
                    st.session_state.backup_confirmed = True
                    st.rerun()

            with col2:
                if st.button("No, Cancel"):
                    reset_confirmation()
                    st.write("Backup cancelled.")

    else:
        try:
            with st.spinner("Creating backup..."):
                filename = write_all_books_to_json(all_books)

            st.success("Backup Completed Successfully!")
            st.write(f"File saved as: `{filename}`")

            if st.button("Create Another Backup"):
                reset_confirmation()
                st.rerun()

        except Exception as e:
            st.error(f"Backup Failed: {str(e)}")
            if st.button("Try Again"):
                reset_confirmation()
                st.rerun()


def _render_edit_book(geojson_client, all_books):
    """Render the Edit Book sub-action."""
    st.write("### Edit Book")

    # Initialize session state for editor
    if 'edit_selected_book' not in st.session_state:
        st.session_state.edit_selected_book = None
    if 'edit_show_preview' not in st.session_state:
        st.session_state.edit_show_preview = False
    if 'edit_changes' not in st.session_state:
        st.session_state.edit_changes = {}

    # Step 1: Book Selection
    st.markdown("#### Step 1: Find and Select Book")

    # Check if a book was already selected from search results
    if st.session_state.edit_selected_book:
        selected_book = st.session_state.edit_selected_book

        # CRITICAL: Initialize locations for THIS book if not already set OR if book changed
        current_book_id = selected_book.get('id')
        if 'edit_current_book_id' not in st.session_state or st.session_state.edit_current_book_id != current_book_id:
            st.session_state.edit_locations_data = normalize_locations(selected_book.get('locations', []))
            st.session_state.edit_current_book_id = current_book_id

        st.success(f"**Selected Book:** {selected_book.get('title', 'N/A')} by {selected_book.get('author', 'N/A')}")

        # Show current book data
        with st.expander("View Current Book Data"):
            st.json(selected_book)

        # Option to clear selection and choose another book
        if st.button("Select a Different Book", key="clear_selection"):
            st.session_state.edit_selected_book = None
            st.session_state.edit_show_preview = False
            st.session_state.edit_changes = {}
            st.session_state.edit_locations_data = []
            st.session_state.edit_current_book_id = None
            st.rerun()

    else:
        st.info("**Option 1:** Use the search box above to find and click the Edit button on a book")
        st.info("**Option 2:** Enter a Book ID manually below if you already know it")

        book_id_input = st.text_input("Enter Book ID to Edit (Optional)", key="edit_book_id",
                                      placeholder="e.g., glory-in-a-camels-eye-tayler")

        if book_id_input:
            selected_book = geojson_client.get_document_by_id(all_books, book_id_input)

            if selected_book:
                st.session_state.edit_selected_book = selected_book
                st.success(f"Book found: **{selected_book.get('title', 'N/A')}** by {selected_book.get('author', 'N/A')}")
                st.rerun()
            else:
                st.error(f"No book found with ID: {book_id_input}")

        st.warning("Please search for a book above and click the Edit button, or enter a Book ID.")

    # Step 2: Edit Form (only show if book is selected)
    if st.session_state.edit_selected_book:
        st.markdown("---")
        st.markdown("#### Step 2: Edit Book Fields")

        book = st.session_state.edit_selected_book

        st.write("**Edit the fields below. Leave unchanged fields as-is.**")

        # Create columns for better layout
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### Basic Information")
            new_title = st.text_input("Title", value=book.get('title', ''), key="edit_title")
            new_author = st.text_input("Author", value=book.get('author', ''), key="edit_author")
            new_description = st.text_area("Description", value=book.get('description', ''), height=100, key="edit_description")

            new_booktype = st.selectbox(
                "Book Type",
                options=['fiction', 'nonfiction', 'travel', 'poetry', 'other'],
                index=['fiction', 'nonfiction', 'travel', 'poetry', 'other'].index(book.get('booktype', 'fiction')) if book.get('booktype') in ['fiction', 'nonfiction', 'travel', 'poetry', 'other'] else 0,
                key="edit_booktype"
            )

            new_genre = st.text_input("Genre", value=book.get('genre', ''), key="edit_genre")
            new_tags = st.text_input("Tags (comma-separated)", value=', '.join(book.get('tags', [])) if isinstance(book.get('tags'), list) else book.get('tags', ''), key="edit_tags")

        with col2:
            st.markdown("##### Publication Details")
            new_publisher = st.text_input("Publisher", value=book.get('publisher', ''), key="edit_publisher")
            new_year = st.number_input("Year", min_value=1000, max_value=2100, value=int(book.get('year', 2000)) if book.get('year') else 2000, key="edit_year")
            new_isbn = st.text_input("ISBN", value=book.get('isbn', ''), key="edit_isbn")
            new_pageCount = st.number_input("Page Count", min_value=0, max_value=10000, value=int(book.get('pageCount', 0)) if book.get('pageCount') else 0, key="edit_pageCount")

            st.markdown("##### Additional Info")
            new_rating = st.number_input("Rating", min_value=0.0, max_value=5.0, step=0.1, value=float(book.get('rating', 0.0)) if book.get('rating') else 0.0, key="edit_rating")
            new_cover = st.text_input("Cover Image URL", value=book.get('cover', ''), key="edit_cover")
            new_goodreads = st.text_input("Goodreads Link", value=book.get('goodreadsLink', ''), key="edit_goodreads")

        # Location editor
        st.markdown("---")
        st.markdown("#### Manage Locations")

        # Initialize locations in session state
        if 'edit_locations_data' not in st.session_state:
            st.session_state.edit_locations_data = normalize_locations(book.get('locations', []))

        current_locations = st.session_state.edit_locations_data

        # Debug info
        with st.expander("Debug: Location State Info"):
            st.write(f"**Current book ID:** {book.get('id')}")
            st.write(f"**Tracked book ID:** {st.session_state.get('edit_current_book_id', 'Not set')}")
            st.write(f"**Original locations count:** {len(book.get('locations', []))}")
            st.write(f"**Session locations count:** {len(st.session_state.edit_locations_data)}")
            st.write("**Original (normalized):**")
            st.json(normalize_locations(book.get('locations', [])))
            st.write("**Session state:**")
            st.json(st.session_state.edit_locations_data)

        st.write(f"**Current locations:** {len(current_locations)}")

        # Section A: Display Current Locations as Table
        if current_locations:
            st.markdown("##### Current Locations")

            locations_df = pd.DataFrame(current_locations)

            expected_cols = ['city', 'country', 'latitude', 'longitude', 'description']
            for col in expected_cols:
                if col not in locations_df.columns:
                    locations_df[col] = ''

            display_df = locations_df[expected_cols].fillna('')

            edited_locations = st.data_editor(
                display_df,
                width='stretch',
                num_rows="dynamic",
                column_config={
                    "city": st.column_config.TextColumn("City", required=True, width="medium"),
                    "country": st.column_config.TextColumn("Country", width="medium"),
                    "latitude": st.column_config.NumberColumn("Latitude", min_value=-90, max_value=90, format="%.4f"),
                    "longitude": st.column_config.NumberColumn("Longitude", min_value=-180, max_value=180, format="%.4f"),
                    "description": st.column_config.TextColumn("Description (optional)", width="large")
                },
                key="locations_editor"
            )

            if not edited_locations.equals(display_df):
                raw_locations = edited_locations.to_dict('records')
                st.session_state.edit_locations_data = normalize_locations(raw_locations)
                st.success("Locations table updated!")

        else:
            st.info("No locations yet. Add one using the form below!")

        # Section B: Quick Add Location Form
        st.markdown("---")
        st.markdown("##### Quick Add Location")

        if 'quick_add_lat' not in st.session_state:
            st.session_state.quick_add_lat = 0.0
        if 'quick_add_lng' not in st.session_state:
            st.session_state.quick_add_lng = 0.0
        if 'geocode_success_msg' not in st.session_state:
            st.session_state.geocode_success_msg = None

        col_city, col_country = st.columns(2)

        with col_city:
            quick_city = st.text_input("City/Place", key="quick_add_city", placeholder="e.g., Paris")

        with col_country:
            quick_country = st.text_input("Country", key="quick_add_country", placeholder="e.g., France")

        quick_description = st.text_input("Description (optional)", key="quick_add_desc", placeholder="e.g., romantic setting in Chapter 3")

        if st.session_state.geocode_success_msg:
            st.success(st.session_state.geocode_success_msg)
            st.session_state.geocode_success_msg = None

        col_geo, col_add, col_clear = st.columns([1, 1, 1])

        def geocode_callback():
            city = st.session_state.get('quick_add_city', '')
            country = st.session_state.get('quick_add_country', '')
            if city and country:
                time.sleep(0.5)
                geo_result = geocode_location(city, country)
                if geo_result:
                    st.session_state.quick_add_lat = geo_result['latitude']
                    st.session_state.quick_add_lng = geo_result['longitude']
                    st.session_state.geocode_success_msg = f"Found: {geo_result['latitude']}, {geo_result['longitude']}"
                else:
                    st.session_state.quick_add_lat = 0.0
                    st.session_state.quick_add_lng = 0.0
                    st.session_state.geocode_success_msg = "Location not found."
            else:
                st.session_state.geocode_success_msg = "Please enter both City and Country first."

        def clear_form_callback():
            st.session_state.quick_add_lat = 0.0
            st.session_state.quick_add_lng = 0.0
            st.session_state.quick_add_city = ""
            st.session_state.quick_add_country = ""
            st.session_state.quick_add_desc = ""

        def add_location_callback():
            city = st.session_state.get('quick_add_city', '')
            country = st.session_state.get('quick_add_country', '')
            if city and country:
                new_location = {
                    "city": city,
                    "country": country,
                    "latitude": st.session_state.quick_add_lat,
                    "longitude": st.session_state.quick_add_lng,
                    "description": st.session_state.get('quick_add_desc', '')
                }
                st.session_state.edit_locations_data.append(new_location)
                st.session_state.quick_add_lat = 0.0
                st.session_state.quick_add_lng = 0.0
                st.session_state.quick_add_city = ""
                st.session_state.quick_add_country = ""
                st.session_state.quick_add_desc = ""
                st.session_state.geocode_success_msg = f"Added {city}, {country}!"

        with col_geo:
            st.button("Auto-Geocode", key="geocode_btn", on_click=geocode_callback, help="Automatically lookup coordinates")

        col_lat, col_lng = st.columns(2)

        with col_lat:
            quick_lat = st.number_input(
                "Latitude",
                min_value=-90.0,
                max_value=90.0,
                format="%.4f",
                key="quick_add_lat",
                help="Auto-filled after geocoding, or enter manually"
            )

        with col_lng:
            quick_lng = st.number_input(
                "Longitude",
                min_value=-180.0,
                max_value=180.0,
                format="%.4f",
                key="quick_add_lng",
                help="Auto-filled after geocoding, or enter manually"
            )

        with col_add:
            st.button("Add Location", type="primary", key="add_location_btn", on_click=add_location_callback)

        with col_clear:
            st.button("Clear Form", key="clear_form_btn", on_click=clear_form_callback)

        # Section C: Advanced JSON Editor (Collapsible)
        with st.expander("Advanced: Edit as JSON"):
            st.write("For power users: Edit the locations array directly as JSON.")

            current_locations_json = json.dumps(st.session_state.edit_locations_data, indent=2)

            edited_json = st.text_area(
                "Locations JSON",
                value=current_locations_json,
                height=200,
                key="json_editor"
            )

            if st.button("Save JSON Changes", key="save_json_btn"):
                try:
                    parsed_json = json.loads(edited_json)
                    st.session_state.edit_locations_data = parsed_json
                    st.success("JSON saved successfully!")
                    st.rerun()
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON: {e}")

        # Preview Changes button
        st.markdown("---")
        st.markdown("#### Review All Changes")
        st.write("Once you've edited all fields and locations above, click below to preview your changes.")

        if st.button("Preview Changes", type="primary", key="preview_changes_btn"):
            submitted = True
        else:
            submitted = False

        if submitted:
            new_locations = st.session_state.get('edit_locations_data', book.get('locations', []))

            changes = {}

            if new_title != book.get('title'):
                changes['title'] = new_title
            if new_author != book.get('author'):
                changes['author'] = new_author
            if new_description != book.get('description'):
                changes['description'] = new_description
            if new_booktype != book.get('booktype'):
                changes['booktype'] = new_booktype
            if new_genre != book.get('genre'):
                changes['genre'] = new_genre

            new_tags_array = [tag.strip() for tag in new_tags.split(',') if tag.strip()]
            if new_tags_array != book.get('tags', []):
                changes['tags'] = new_tags_array

            if new_publisher != book.get('publisher'):
                changes['publisher'] = new_publisher
            if new_year != book.get('year'):
                changes['year'] = new_year
            if new_isbn != book.get('isbn'):
                changes['isbn'] = new_isbn
            if new_pageCount != book.get('pageCount'):
                changes['pageCount'] = new_pageCount
            if new_rating != book.get('rating'):
                changes['rating'] = new_rating
            if new_cover != book.get('cover'):
                changes['cover'] = new_cover
            if new_goodreads != book.get('goodreads', ''):
                changes['goodreadsLink'] = new_goodreads

            original_locations_normalized = normalize_locations(book.get('locations', []))
            new_locations_normalized = normalize_locations(new_locations)
            if new_locations_normalized != original_locations_normalized:
                changes['locations'] = new_locations

            st.session_state.edit_changes = changes
            st.session_state.edit_show_preview = True
            st.rerun()

        # Step 3: Preview and Confirm Changes
        if st.session_state.edit_show_preview and st.session_state.edit_changes:
            st.markdown("---")
            st.markdown("#### Step 3: Review and Confirm Changes")

            changes = st.session_state.edit_changes

            if not changes:
                st.info("No changes detected. All fields remain the same.")
            else:
                st.warning(f"You are about to update **{len(changes)}** field(s):")

                for field, new_value in changes.items():
                    old_value = book.get(field, 'Not set')

                    st.markdown(f"**{field.capitalize()}:**")
                    col_old, col_arrow, col_new = st.columns([2, 1, 2])

                    with col_old:
                        if isinstance(old_value, list):
                            st.json(old_value)
                        elif len(str(old_value)) > 100:
                            st.text(str(old_value)[:100] + "...")
                        else:
                            st.code(old_value)

                    with col_arrow:
                        st.markdown("### ->")

                    with col_new:
                        if isinstance(new_value, list):
                            st.json(new_value)
                        elif len(str(new_value)) > 100:
                            st.text(str(new_value)[:100] + "...")
                        else:
                            st.code(new_value)

                col_confirm, col_cancel = st.columns(2)

                with col_confirm:
                    if st.button("Confirm and Save Changes", type="primary", key="confirm_save"):
                        success = geojson_client.update_book(
                            book['id'],
                            changes
                        )

                        if success:
                            st.success(f"Successfully updated {len(changes)} field(s) for book: {book['title']}")

                            st.session_state.edit_selected_book = None
                            st.session_state.edit_show_preview = False
                            st.session_state.edit_changes = {}
                            st.session_state.edit_locations_data = []
                            st.session_state.edit_current_book_id = None

                            st.balloons()
                            st.info("Refresh the page to edit another book.")
                        else:
                            st.error("Failed to update the book. Check console for errors.")

                with col_cancel:
                    if st.button("Cancel Changes", key="cancel_save"):
                        st.session_state.edit_show_preview = False
                        st.session_state.edit_changes = {}
                        st.rerun()


def _render_edit_json(geojson_client, all_books):
    """Render the Edit Existing JSON sub-action."""
    st.write("### Edit Existing JSON")
    st.write("**Advanced editing:** Search for a book, edit its JSON directly, and preview changes before saving.")

    # Initialize session state
    if 'json_edit_selected_book' not in st.session_state:
        st.session_state.json_edit_selected_book = None
    if 'json_edit_original' not in st.session_state:
        st.session_state.json_edit_original = None
    if 'json_edit_modified' not in st.session_state:
        st.session_state.json_edit_modified = None
    if 'json_edit_show_diff' not in st.session_state:
        st.session_state.json_edit_show_diff = False
    if 'json_search_results' not in st.session_state:
        st.session_state.json_search_results = []

    # Step 1: Search and Select Book
    if not st.session_state.json_edit_selected_book:
        st.markdown("#### Step 1: Find and Select Book")

        col_search_type, col_search_input = st.columns([1, 3])

        with col_search_type:
            json_search_option = st.selectbox(
                "Search by",
                ("Title", "Author", "ID"),
                key="json_search_type"
            )

        with col_search_input:
            json_search_input = st.text_input(
                f"Enter {json_search_option}",
                key="json_search_input",
                placeholder=f"Search for a book by {json_search_option.lower()}..."
            )

        col_btn1, col_btn2 = st.columns([1, 4])

        with col_btn1:
            json_search_button = st.button("Search", key="json_search_btn", type="primary")

        if json_search_button and json_search_input:
            if json_search_option == "Author":
                books = geojson_client.get_books_by_author(all_books, json_search_input)
            elif json_search_option == "Title":
                books = geojson_client.get_book_by_title(all_books, json_search_input)
            elif json_search_option == "ID":
                book = geojson_client.get_document_by_id(all_books, json_search_input)
                books = [book] if book else []

            st.session_state.json_search_results = books

        if st.session_state.json_search_results:
            books = st.session_state.json_search_results
            st.write(f"**Found {len(books)} book(s):**")

            for book in books:
                col_info, col_select = st.columns([4, 1])

                with col_info:
                    st.markdown(f"**{book.get('title', 'N/A')}**")
                    st.caption(f"**By:** {book.get('author', 'N/A')} | **ID:** `{book.get('id', 'N/A')}`")

                with col_select:
                    if st.button("Select", key=f"json_select_{book.get('id')}", type="primary"):
                        book_copy = book.copy()
                        book_id = book_copy.pop('id', None)

                        st.session_state.json_edit_selected_book = book
                        st.session_state.json_edit_original = json.dumps(book_copy, indent=2)
                        st.session_state.json_edit_modified = None
                        st.session_state.json_edit_show_diff = False
                        st.success(f"Selected: {book.get('title', 'N/A')}")
                        st.rerun()

                st.markdown("---")
        elif json_search_button:
            st.warning(f"No books found for {json_search_option}: {json_search_input}")

    # Step 2: JSON Editor
    if st.session_state.json_edit_selected_book:
        st.markdown("---")
        st.markdown("#### Step 2: Edit JSON")

        book = st.session_state.json_edit_selected_book
        st.info(f"**Editing:** {book.get('title', 'N/A')} (ID: `{book.get('id', 'N/A')}`)")

        if st.button("Select Different Book", key="json_clear_selection"):
            st.session_state.json_edit_selected_book = None
            st.session_state.json_edit_original = None
            st.session_state.json_edit_modified = None
            st.session_state.json_edit_show_diff = False
            st.session_state.json_search_results = []
            st.rerun()

        with st.expander("View Original JSON"):
            st.json(json.loads(st.session_state.json_edit_original))

        st.markdown("##### Edit JSON Below")
        st.caption("Be careful when editing. Invalid JSON will be rejected.")

        edited_json_str = st.text_area(
            "Book JSON",
            value=st.session_state.json_edit_original,
            height=400,
            key="json_text_editor",
            help="Edit the JSON structure. The 'id' field is managed automatically."
        )

        col_validate, col_reset = st.columns([1, 1])

        with col_validate:
            if st.button("Validate & Preview Changes", type="primary", key="json_validate_btn"):
                try:
                    edited_dict = json.loads(edited_json_str)
                    st.session_state.json_edit_modified = edited_json_str
                    st.session_state.json_edit_show_diff = True
                    st.success("JSON is valid! Scroll down to review changes.")
                    st.rerun()
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON syntax: {e}")
                    st.session_state.json_edit_show_diff = False

        with col_reset:
            if st.button("Reset to Original", key="json_reset_btn"):
                st.session_state.json_edit_modified = None
                st.session_state.json_edit_show_diff = False
                st.info("Reverted to original JSON")
                st.rerun()

    # Step 3: Display Diff
    if st.session_state.json_edit_show_diff and st.session_state.json_edit_modified:
        st.markdown("---")
        st.markdown("#### Step 3: Review Changes")

        original_dict = json.loads(st.session_state.json_edit_original)
        modified_dict = json.loads(st.session_state.json_edit_modified)

        diff_data = compare_json_objects(original_dict, modified_dict)

        has_changes = (
            len(diff_data['added']) > 0 or
            len(diff_data['removed']) > 0 or
            len(diff_data['changed']) > 0
        )

        if not has_changes:
            st.info("No changes detected. The JSON is identical to the original.")
        else:
            display_json_diff(diff_data, st.session_state.json_edit_selected_book)

            st.markdown("---")
            st.markdown("#### Step 4: Confirm and Save")

            st.warning(f"You are about to update the book: **{st.session_state.json_edit_selected_book.get('title', 'N/A')}**")

            col_confirm, col_cancel = st.columns([1, 1])

            with col_confirm:
                if st.button("Confirm & Save to GeoJSON", type="primary", key="json_confirm_save"):
                    update_data = {}
                    update_data.update(diff_data['added'])
                    for field, change in diff_data['changed'].items():
                        update_data[field] = change['new']

                    for field in diff_data['removed'].keys():
                        update_data[field] = None

                    book_id = st.session_state.json_edit_selected_book['id']

                    try:
                        success = geojson_client.update_book(
                            book_id,
                            update_data
                        )

                        if success:
                            st.success(f"Successfully updated book: {st.session_state.json_edit_selected_book.get('title', 'N/A')}")
                            st.balloons()

                            st.session_state.json_edit_selected_book = None
                            st.session_state.json_edit_original = None
                            st.session_state.json_edit_modified = None
                            st.session_state.json_edit_show_diff = False
                            st.session_state.json_search_results = []

                            st.info("You can now search for another book to edit.")
                        else:
                            st.error("Failed to update the book. Check the console for errors.")

                    except Exception as e:
                        st.error(f"Error saving to GeoJSON: {e}")

            with col_cancel:
                if st.button("Cancel Changes", key="json_cancel_save"):
                    st.session_state.json_edit_show_diff = False
                    st.session_state.json_edit_modified = None
                    st.info("Changes discarded. You can continue editing or select a different book.")
                    st.rerun()


def _render_export_single(geojson_client, all_books):
    """Render the Export Single Book sub-action."""
    search_type = st.sidebar.radio("Search by:", ("Title", "ID"))

    if search_type == "Title":
        user_input = st.sidebar.text_input("Enter Book Title", "")
    else:
        user_input = st.sidebar.text_input("Enter Book ID", "")

    if user_input:
        st.write(f"You entered: {user_input}")

        if search_type == "Title":
            write_book_json(geojson_client, all_books, title=user_input, book_id=None, verbose=False)
            st.write(f"Saving book with Title: {user_input}")
        else:
            write_book_json(geojson_client, all_books, title=None, book_id=user_input, verbose=False)
            st.write(f"Saving book with ID: {user_input}")


def _render_delete_book(geojson_client):
    """Render the Delete Book by ID sub-action."""
    doc_id = st.sidebar.text_input("Enter Book ID", "")

    if doc_id:
        if st.sidebar.button("Delete Book"):
            try:
                geojson_client.delete_book(doc_id)
                st.write(f"Book with ID '{doc_id}' deleted successfully.")
            except Exception as e:
                st.error(f"Failed to delete book: {e}")
