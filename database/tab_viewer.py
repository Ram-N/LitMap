# Data Viewer tab logic

import streamlit as st
import pandas as pd
from collections import defaultdict

from book_detail import generate_book_detail_html


def render_viewer_tab(tab, geojson_client, all_books):
    """Render the Data Viewer tab contents."""

    view_options = {
        0: "Select",
        1: "Document Count",
        2: "List All Book Titles",
        3: "List All Authors",
        4: "Show All Locations",
        5: "Find Duplicates",
        6: "Compare 2 Books",
        7: "View Book Detail",
    }

    with tab:
        st.session_state.current_tab = "Viewer"
        # Create the selectbox with tooltips for each option
        view_action = st.selectbox(
            label=" ",  # Empty label
            options=view_options.values(),
            index=0,
        )

        tooltips = {
            "Select": "Choose an action from the dropdown",
            "Document Count": "Shows the total number of books in the dataset",
            "List All Book Titles": "Displays a sorted list of all book titles",
            "List All Authors": "Shows a list of all authors in the dataset",
            "Show All Locations": "Displays all unique locations mentioned in books",
            "Find Duplicates": "Identifies potential duplicate books in the dataset",
            "Compare 2 Books": "Shows a side-by-side comparison of two selected books",
            "View Book Detail": "View detailed information about a single book with map",
        }

        # Display the tooltip for the selected option
        if view_action in tooltips:
            st.sidebar.info(tooltips[view_action])
        st.sidebar.markdown("----")
        st.write(f"{view_action}")

        placeholder_viewer = st.empty()

        with placeholder_viewer.container():

            # NUM DOCS
            if view_action == view_options[1]:  # DOC COUNT
                doc_count = geojson_client.get_book_count()
                print(doc_count)
                st.write(f"Number of books: {doc_count}")

            # LIST ALL BOOK TITLES
            if view_action == view_options[2]:  # List All Book Titles
                all_titles = sorted([book['title'] for book in all_books if 'title' in book])
                print(len(all_titles))
                st.write("### All Titles (Sorted Alphabetically):")
                # Join all titles with line breaks and apply custom CSS
                titles_html = "<div style='line-height: 1; font-size: 14px;'>" + "<br>".join(all_titles) + "</div>"
                st.markdown(titles_html, unsafe_allow_html=True)

            # UNIQUE Authors
            if view_action == view_options[3]:  # AUTHORS
                # Extract and sort unique authors
                all_authors = sorted(set(book['author'] for book in all_books if 'author' in book))
                # Display the sorted authors
                st.write("### All Unique Authors (Sorted Alphabetically):")
                st.text("\n".join(all_authors))

            # UNIQUE LOCATIONS
            if view_action == view_options[4]:  # LOCATIONS
                # Extract all unique cities from the 'locations' field of each book
                unique_places = set()

                for book in all_books:
                    if 'locations' in book:
                        for location in book['locations']:
                            if location.get('city'):
                                unique_places.add(location['city'])
                            if location.get('place'):
                                unique_places.add(location['place'])

                locations_df = pd.DataFrame(sorted(unique_places), columns=['Location'])
                st.write(f"### Unique Cities Mentioned in Books ({len(unique_places)} total):")

                # Display the DataFrame
                st.dataframe(
                    locations_df,
                    hide_index=True,
                    column_config={
                        "Location": st.column_config.TextColumn(
                            "Location",
                            width="medium"
                        )
                    },
                    width='stretch',
                    height=400,
                    column_order=("Location",)
                )

            if view_action == "Compare 2 Books":
                _render_compare_books(geojson_client, all_books)

            if view_action == "Find Duplicates":
                _render_find_duplicates(geojson_client, all_books)

            if view_action == "View Book Detail":
                _render_book_detail(geojson_client, all_books)

    return placeholder_viewer


def _render_book_detail(geojson_client, all_books):
    """Render the View Book Detail sub-action."""
    st.write("### View Book Detail")
    st.write("Search for a book to view its full details with an embedded map.")

    # Search interface
    col_search, col_btn = st.columns([3, 1])

    with col_search:
        detail_query = st.text_input(
            "Search by title or author",
            key="detail_search",
            placeholder="Enter book title or author name..."
        )

    with col_btn:
        st.write("")  # Spacing
        st.write("")  # Spacing
        detail_search_btn = st.button("Search", key="detail_search_btn")

    # Initialize session state
    if 'detail_search_results' not in st.session_state:
        st.session_state.detail_search_results = []

    # Perform search
    if detail_search_btn and detail_query:
        title_matches = geojson_client.fuzzy_match(all_books, 'title', detail_query)
        author_matches = geojson_client.fuzzy_match(all_books, 'author', detail_query)
        combined = {book['id']: book for book in title_matches + author_matches}
        st.session_state.detail_search_results = list(combined.values())[:10]

    # Display search results
    if st.session_state.detail_search_results:
        results = st.session_state.detail_search_results
        st.write(f"**Found {len(results)} result(s):**")

        book_options = {
            f"{book['title']} by {book.get('author', 'Unknown')} (ID: {book['id']})": book['id']
            for book in results
        }

        selected_display = st.selectbox(
            "Select a book to view:",
            options=list(book_options.keys()),
            key="detail_select"
        )

        if selected_display:
            book_id = book_options[selected_display]
            book = geojson_client.get_document_by_id(all_books, book_id)

            if book:
                html = generate_book_detail_html(book)
                st.components.v1.html(html, height=900, scrolling=True)

    elif detail_search_btn and detail_query:
        st.warning("No books found. Try a different search term.")


def _render_compare_books(geojson_client, all_books):
    """Render the Compare 2 Books sub-action."""
    st.write("### Compare Two Books")
    st.write("Search for and select two books to compare side-by-side.")

    # Debug: Show collection info
    st.info(f"Currently loaded **{len(all_books)}** books from GeoJSON")

    # Debug: Show sample book structure
    if all_books:
        with st.expander("Debug: View sample book structure"):
            sample_book = all_books[0]
            st.write(f"**Sample book fields:** {list(sample_book.keys())}")
            st.write(f"**Sample title:** {sample_book.get('title', 'N/A')}")
            st.write(f"**Sample author:** {sample_book.get('author', 'N/A')}")
            st.write(f"**Sample ID:** {sample_book.get('id', 'N/A')}")

    # Initialize session state for book selections
    if 'selected_book1' not in st.session_state:
        st.session_state.selected_book1 = None
    if 'selected_book2' not in st.session_state:
        st.session_state.selected_book2 = None
    if 'search_results1' not in st.session_state:
        st.session_state.search_results1 = []
    if 'search_results2' not in st.session_state:
        st.session_state.search_results2 = []

    # Book 1 Selection
    st.markdown("#### Select First Book")
    col1_search, col1_btn = st.columns([3, 1])

    with col1_search:
        search_query1 = st.text_input(
            "Search by title or author (Book 1)",
            key="search1",
            placeholder="Enter book title or author name..."
        )

    with col1_btn:
        st.write("")  # Spacing
        st.write("")  # Spacing
        search_btn1 = st.button("Search", key="search_btn1")

    # Perform search for Book 1
    if search_btn1 and search_query1:
        st.write(f"DEBUG: Searching for '{search_query1}'")
        st.write(f"DEBUG: Total books: {len(all_books)}")

        # Search in both title and author fields
        title_matches = geojson_client.fuzzy_match(all_books, 'title', search_query1)
        author_matches = geojson_client.fuzzy_match(all_books, 'author', search_query1)

        st.write(f"DEBUG: Title matches: {len(title_matches)}")
        st.write(f"DEBUG: Author matches: {len(author_matches)}")

        # Log first few title matches for inspection
        if title_matches:
            st.write(f"DEBUG: First title match: {title_matches[0].get('title', 'N/A')}")
        if author_matches:
            st.write(f"DEBUG: First author match: {author_matches[0].get('title', 'N/A')} by {author_matches[0].get('author', 'N/A')}")

        # Combine and deduplicate results
        combined_results = {book['id']: book for book in title_matches + author_matches}
        st.session_state.search_results1 = list(combined_results.values())[:10]  # Limit to top 10

        st.write(f"DEBUG: Combined unique results: {len(st.session_state.search_results1)}")

        # Print to console as well
        print(f"\n=== BOOK 1 SEARCH DEBUG ===")
        print(f"Query: {search_query1}")
        print(f"Total books: {len(all_books)}")
        print(f"Title matches: {len(title_matches)}")
        print(f"Author matches: {len(author_matches)}")
        print(f"Combined results: {len(st.session_state.search_results1)}")
        if st.session_state.search_results1:
            print(f"First result: {st.session_state.search_results1[0].get('title', 'N/A')}")
        print("=" * 30)

    # Display search results for Book 1
    if st.session_state.search_results1:
        st.write(f"**Found {len(st.session_state.search_results1)} result(s):**")

        # Create radio buttons for selection
        book_options1 = {
            f"{book['title']} by {book.get('author', 'Unknown')} (ID: {book['id']})": book['id']
            for book in st.session_state.search_results1
        }

        selected_display1 = st.radio(
            "Select a book:",
            options=list(book_options1.keys()),
            key="radio1"
        )

        if selected_display1:
            book_id1 = book_options1[selected_display1]
            st.session_state.selected_book1 = geojson_client.get_document_by_id(all_books, book_id1)
            st.success(f"Book 1 selected: {st.session_state.selected_book1['title']}")

    elif search_query1 and search_btn1:
        st.warning("No books found. Try a different search term.")

    # Show Book 2 selection only if Book 1 is selected
    if st.session_state.selected_book1:
        st.markdown("---")
        st.markdown("#### Select Second Book")

        col2_search, col2_btn = st.columns([3, 1])

        with col2_search:
            search_query2 = st.text_input(
                "Search by title or author (Book 2)",
                key="search2",
                placeholder="Enter book title or author name..."
            )

        with col2_btn:
            st.write("")  # Spacing
            st.write("")  # Spacing
            search_btn2 = st.button("Search", key="search_btn2")

        # Perform search for Book 2
        if search_btn2 and search_query2:
            st.write(f"DEBUG: Searching for '{search_query2}'")
            st.write(f"DEBUG: Total books: {len(all_books)}")

            # Search in both title and author fields
            title_matches = geojson_client.fuzzy_match(all_books, 'title', search_query2)
            author_matches = geojson_client.fuzzy_match(all_books, 'author', search_query2)

            st.write(f"DEBUG: Title matches: {len(title_matches)}")
            st.write(f"DEBUG: Author matches: {len(author_matches)}")

            # Log first few matches for inspection
            if title_matches:
                st.write(f"DEBUG: First title match: {title_matches[0].get('title', 'N/A')}")
            if author_matches:
                st.write(f"DEBUG: First author match: {author_matches[0].get('title', 'N/A')} by {author_matches[0].get('author', 'N/A')}")

            # Combine and deduplicate results
            combined_results = {book['id']: book for book in title_matches + author_matches}
            st.session_state.search_results2 = list(combined_results.values())[:10]  # Limit to top 10

            st.write(f"DEBUG: Combined unique results: {len(st.session_state.search_results2)}")

            # Print to console as well
            print(f"\n=== BOOK 2 SEARCH DEBUG ===")
            print(f"Query: {search_query2}")
            print(f"Total books: {len(all_books)}")
            print(f"Title matches: {len(title_matches)}")
            print(f"Author matches: {len(author_matches)}")
            print(f"Combined results: {len(st.session_state.search_results2)}")
            if st.session_state.search_results2:
                print(f"First result: {st.session_state.search_results2[0].get('title', 'N/A')}")
            print("=" * 30)

        # Display search results for Book 2
        if st.session_state.search_results2:
            st.write(f"**Found {len(st.session_state.search_results2)} result(s):**")

            # Create radio buttons for selection
            book_options2 = {
                f"{book['title']} by {book.get('author', 'Unknown')} (ID: {book['id']})": book['id']
                for book in st.session_state.search_results2
            }

            selected_display2 = st.radio(
                "Select a book:",
                options=list(book_options2.keys()),
                key="radio2"
            )

            if selected_display2:
                book_id2 = book_options2[selected_display2]
                st.session_state.selected_book2 = geojson_client.get_document_by_id(all_books, book_id2)
                st.success(f"Book 2 selected: {st.session_state.selected_book2['title']}")

        elif search_query2 and search_btn2:
            st.warning("No books found. Try a different search term.")

    # Display comparison when both books are selected
    if st.session_state.selected_book1 and st.session_state.selected_book2:
        st.markdown("---")
        st.markdown("## Book Comparison")

        book1 = st.session_state.selected_book1
        book2 = st.session_state.selected_book2

        # Create two columns for side-by-side comparison
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown(f"### {book1['title']}")
            st.markdown(f"**ID:** `{book1['id']}`")

        with col_right:
            st.markdown(f"### {book2['title']}")
            st.markdown(f"**ID:** `{book2['id']}`")

        st.markdown("---")

        # Get all unique keys from both books
        all_keys = set(book1.keys()) | set(book2.keys())
        # Remove 'id' as we've already displayed it
        all_keys.discard('id')

        # Sort keys for consistent display
        sorted_keys = sorted(all_keys)

        # Compare each field
        for key in sorted_keys:
            value1 = book1.get(key, "Not present")
            value2 = book2.get(key, "Not present")

            # Check if values are the same
            values_match = value1 == value2

            # Display field name
            if values_match and value1 != "Not present":
                st.markdown(f"**{key.capitalize()}:** *Same*")
                # Show the value once since they're the same
                if isinstance(value1, list):
                    st.json(value1)
                elif len(str(value1)) > 100:
                    with st.expander(f"View {key}"):
                        st.write(value1)
                else:
                    st.write(f"  {value1}")
            else:
                st.markdown(f"**{key.capitalize()}:** *Different*")

                col_a, col_b = st.columns(2)

                with col_a:
                    if value1 == "Not present":
                        st.markdown("*Not present in Book 1*")
                    elif isinstance(value1, list):
                        st.json(value1)
                    elif len(str(value1)) > 100:
                        with st.expander("View full text"):
                            st.write(value1)
                    else:
                        st.write(value1)

                with col_b:
                    if value2 == "Not present":
                        st.markdown("*Not present in Book 2*")
                    elif isinstance(value2, list):
                        st.json(value2)
                    elif len(str(value2)) > 100:
                        with st.expander("View full text"):
                            st.write(value2)
                    else:
                        st.write(value2)

            st.markdown("---")

        # Add reset button
        if st.button("Compare Different Books"):
            st.session_state.selected_book1 = None
            st.session_state.selected_book2 = None
            st.session_state.search_results1 = []
            st.session_state.search_results2 = []
            st.rerun()


def _render_find_duplicates(geojson_client, all_books):
    """Render the Find Duplicates sub-action."""
    dupe_ids = []
    # Dictionary to track books by title
    books_by_title = defaultdict(list)

    # Group books by their title
    for book in all_books:
        title = book.get('title', '').strip().lower()  # Normalize the title
        books_by_title[title].append(book)

    # Find and display duplicates
    st.write("### Duplicate Books (Same Title)")

    found_duplicates = False
    for title, books in books_by_title.items():
        if len(books) > 1:  # If more than one book shares the same title
            found_duplicates = True
            st.write(f"**Title:** {title.capitalize()}")
            for book in books:
                st.write(f"- Book ID: {book.get('id', 'N/A')}")
                dupe_ids.append(book['id'])
                print(book)

    if not found_duplicates:
        st.write("No duplicate books found.")

    if len(dupe_ids) > 1:
        for i in range(0, len(dupe_ids) - 1, 2):
            book1_id = dupe_ids[i]
            book2_id = dupe_ids[i+1]
            geojson_client.compare_books(all_books, book1_id, book2_id)
            st.markdown("----")
