# remember to activate the correct env

import streamlit as st
from pprint import pprint
import firebase_admin
from firebase_admin import credentials, firestore
import json, re
from collections import defaultdict
from datetime import datetime
import pandas as pd
from geopy.geocoders import Nominatim
import time


# Helper function to normalize location data for comparison
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


# Geocoding helper function
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


class FirebaseClient:
    def __init__(self, service_account_key: str):
        """
        Initialize the Firebase connection using a service account key.
        Args:
            service_account_key (str): Path to the Firebase service account key JSON file.
        """
        self.cred = credentials.Certificate(service_account_key)
        # Initialize the Firebase app only if it hasn't been initialized
        if not firebase_admin._apps:
            firebase_admin.initialize_app(self.cred)
        
        # Get a reference to Firestore
        self.db = firestore.client()

    def get_document_count(self, collection_name: str) -> int:
        """
        Get the count of documents in a Firestore collection.
        Args:
            collection_name (str): The name of the Firestore collection.
        
        Returns:
            int: The number of documents in the collection.
        """
        collection_ref = self.db.collection(collection_name)
        documents = collection_ref.stream()  # Fetch all documents
        document_count = sum(1 for _ in documents)  # Count the documents
        print(f"Number of documents in the '{collection_name}' collection: {document_count}")
        return document_count

    def get_all_documents(self, collection_name: str) -> list:
        """
        Get all documents from a Firestore collection and store them in a list.
        Args:
            collection_name (str): The name of the Firestore collection.
        
        Returns:
            list: A list of dictionaries representing the documents in the collection.
        """
        collection_ref = self.db.collection(collection_name)
        documents = collection_ref.stream()  # Fetch all documents

        document_list = []
        for doc in documents:
            # Convert the document to a dictionary and append it to the list
            document_data = doc.to_dict()
            document_data['id'] = doc.id   # Add document ID to the data
            document_list.append(document_data)

        return document_list

    def get_document_by_id(self, books, book_id):
        """Fetch a book from all_books using its ID."""

        for book in books:
            if book.get('id') == book_id:
                return book  # Return the matching book

        # If no match is found, return None or an empty dictionary
        st.write(f"No book found with ID: {book_id}")
        return None

    def fb_get_document_by_id(self, collection_name: str, doc_id: str, verbose: bool = False) -> dict:
        """
        Get a document by its ID from a Firestore collection.
        Args:
            collection_name (str): The name of the Firestore collection.
            doc_id (str): The ID of the document to retrieve.
            verbose (bool): If True, prints the document's data.
        
        Returns:
            dict: The document's data if it exists, otherwise an empty dictionary.
        """
        doc_ref = self.db.collection(collection_name).document(doc_id)
        doc = doc_ref.get()

        if doc.exists:
            if verbose:
                pprint(f"Document data: {doc.to_dict()}")
            return doc.to_dict()
        else:
            print(f"No such document {doc_id}!")
            return {}

    def update_document_field(self, collection_name: str, doc_id: str, field: str, new_value):
        """
        Update a specific field in a Firestore document.
        Args:
            collection_name (str): The name of the Firestore collection.
            doc_id (str): The ID of the document to update.
            field (str): The field to update.
            new_value: The new value to set for the field.
        """
        doc_ref = self.db.collection(collection_name).document(doc_id)

        # Update the specific field with the new value
        doc_ref.update({field: new_value})
        print(f"Document with ID {doc_id} updated. Field '{field}' set to '{new_value}'.")

    def update_multiple_fields(self, collection_name: str, doc_id: str, field_updates: dict, verbose: bool = False) -> bool:
        """
        Update multiple fields in a Firestore document at once.
        Args:
            collection_name (str): The name of the Firestore collection.
            doc_id (str): The ID of the document to update.
            field_updates (dict): Dictionary of field-value pairs to update.
            verbose (bool): If True, prints detailed update information.

        Returns:
            bool: True if update successful, False otherwise.
        """
        try:
            doc_ref = self.db.collection(collection_name).document(doc_id)

            # Update all fields at once
            doc_ref.update(field_updates)

            if verbose:
                print(f"Document with ID {doc_id} updated successfully.")
                print(f"Updated fields: {list(field_updates.keys())}")

            return True
        except Exception as e:
            print(f"Error updating document {doc_id}: {e}")
            return False

    def add_new_document(self, collection_name: str, field_value_pairs: dict, verbose: bool = False) -> str:
        """
        Add a new document to a Firestore collection with field-value pairs.
        Args:
            collection_name (str): The name of the Firestore collection.
            field_value_pairs (dict): A dictionary containing field-value pairs.
            verbose (bool): If True, prints the new document's ID.
        
        Returns:
            str: The ID of the newly added document.
        """
        # Add a new document with auto-generated ID
        new_doc_ref = self.db.collection(collection_name).add(field_value_pairs)
        if verbose:
            print(f"New document added with ID: {new_doc_ref[1].id}")
        return new_doc_ref[1].id

    def delete_document_by_id(self, collection_name: str, doc_id: str):
        """
        Delete a document from a Firestore collection by its ID.
        Args:
            collection_name (str): The name of the Firestore collection.
            doc_id (str): The ID of the document to delete.
        """
        doc_ref = self.db.collection(collection_name).document(doc_id)
        doc_ref.delete()
        print(f"Document with ID {doc_id} deleted successfully.")


    def book_exists(self, book: dict) -> bool:
        """
        Check if a book already exists in the Firestore collection by its title.
        Args:
            book (dict): The book data, containing at least the 'title' key.
        
        Returns:
            bool: True if the book exists, False otherwise.
        """
        db_book = self.get_book_by_title(all_books, book['title'])
        if len(db_book) > 0:
            return True
        return False

    def add_books_to_db(self, collection_name: str, to_be_added: list):
        """
        Add a list of books to the Firestore collection, only if they don't already exist.
        Args:
            collection_name (str): The Firestore collection name.
            to_be_added (list): A list of dictionaries, where each dict represents a book.
        """
        st.write(f"Attempting to add {len(to_be_added)} documents")
        st.write(f"Collection: {collection_name}")
        
        for book in to_be_added:
            if not self.book_exists(book):
                st.success(f"Adding {book['title']}")
                self.add_new_document(collection_name, book, verbose=True)
            else:
                st.warning(f"{book['title']} already exists in {collection_name}")


    def compare_books(self, books, book_id1, book_id2):
        # Fetch the two books from Firestore
        book1 = self.get_document_by_id(books, book_id1)
        book2 = self.get_document_by_id(books, book_id2)

        if not book1 or not book2:
            st.write("One or both books were not found.")
            return

        st.write(f"## Comparing Books: `{book_id1}` vs `{book_id2}`")
        st.write("---")  # Horizontal line for visual separation

        # Compare attributes between the two books
        for key, value1 in book1.items():
            if key in book2:
                value2 = book2[key]

                if value1 == value2:
                    # Attributes are the same, print once
                    st.write(f" **{key.capitalize()}**: {value1}")
                else:
                    # Attributes differ, print both values
                    st.write(f" **{key.capitalize()}**:")
                    st.write(f"- Book 1: `{value1}`")
                    st.write(f"- Book 2: `{value2}`")
            else:
                st.write(f"### **{key.capitalize()}** exists only in Book 1: {value1}")

        # Check for any attributes that are in Book 2 but not in Book 1
        for key in book2.keys():
            if key not in book1:
                st.write(f"### **{key.capitalize()}** exists only in Book 2: {book2[key]}")


    def fuzzy_match(self, books, attribute, search_string):
        """
        Perform a fuzzy search on a list of books for a given attribute.
        Note that this search does not hit the firestore db at all.

        Args:
            books (list): A list of book JSON objects.
            attribute (str): The attribute to search for (e.g., 'title', 'author', 'isbn').
            search_string (str): The string to search for within the attribute.

        Returns:
            list: A list of books where the attribute matches (even partially) with the search string.
        """
        # Normalize the search string to lowercase for case-insensitive comparison
        search_string = search_string.lower()
        
        # List to store matching books
        matching_books = []

        # Loop through each book
        for book in books:
            # Check if the book has the specified attribute
            if attribute in book:
                # Get the value of the attribute and normalize it to lowercase
                attribute_value = str(book[attribute]).lower()
                
                # Check if the search string is found within the attribute value (partial match)
                if search_string in attribute_value:
                    matching_books.append(book)

        return matching_books



    # Wrapper methods for specific fields
    def get_book_by_title(self, books: list, title: str) -> list:
        return self.fuzzy_match(books, 'title', title)

    def get_books_by_author(self,  books: list, author_name: str) -> list:
        return self.fuzzy_match(books, 'author', author_name)

    def get_books_by_genre(self, books: list, genre: str) -> list:
        return self.fuzzy_match(books, 'genre', genre)

    def get_books_by_year(self, collection_name: str, year: str) -> list:
        return self.get_documents_with_case_variants(collection_name,  'year', year)

    def get_books_by_publisher(self, collection_name: str, publisher: str) -> list:
        return self.get_documents_with_case_variants(collection_name,  'publisher', publisher)


def sanitize_filename(filename):
    """Remove any characters that are not alphanumeric or underscores."""
    return re.sub(r'[^a-zA-Z0-9_]', '_', filename)

def write_book_json(title=None, book_id=None, verbose=False):
    # Validate inputs
    if not title and not book_id:
        raise ValueError("Please provide either a title or an ID to search for the book.")

    # Search for the book in all_books
    books = []
    if title:
        books = firebase_client.get_book_by_title(all_books, title)
    if book_id:
        books = firebase_client.get_document_by_id(all_books, book_id)

    if not books:
        print(f"No matching Books found {title} {book_id}")
        return

    # Create filename: First 20 chars of title + "_" + book ID + ".json"
    book = books[0]
    truncated_title = sanitize_filename(book['title'][:20])  # Sanitize to avoid illegal characters
    filename = f"{truncated_title}_{book['id']}.json"

    # Write book details to JSON file
    with open(filename, 'w') as f:
        json.dump(books, f, indent=4)

    if verbose:
        print(f"Book details saved to: {filename}")

    st.write(f"Book details saved to: `{filename}`")


###########################################################################
# Initialize Firebase client
service_account_key = "litmap-88358-firebase-adminsdk-9w1l9-73ca515ce7.json"
firebase_client = FirebaseClient(service_account_key)

#firebase_client.book_exists("Absurdistan", collection_name='midbooks')

######## S T R E A M L I T ##########################

# Page configuration
st.set_page_config(layout="wide")

# Streamlit App UI
st.title("LitMap Firestore Manager")

# Define tabs

# Create tabs
view_tab, db_tab, h_tab = st.tabs(["Data Viewer", "DB-Manage", "Help"])

view_options = {
    0: "Select",
    1: "Document Count",
    2: "List All Book Titles",
    3: "List All Authors",
    4: "Show All Locations",
    5: "Find Duplicates",
    6: "Compare 2 Books",
}

db_options = {
    0: "Select DB Action",
    8: "Export Collection to JSON",
    9: "Upload Books to Firebase",
    10: "Edit Book Field",
    12: "Export Single Book to JSON",
    13: "Delete Book by ID",
    11: "Backup & Delete Book"
}


top_options = {
    0: "Select",
    1: "Document Count",
    2: "List All Book Titles",
    3: "List All Authors",
    4: "Show All Locations",
    5: "Find Duplicates",
    6: "Compare 2 Books",
    7: "----",
    8: "Export Collection to JSON",
    9: "Export Single Book to JSON",
    10: "Delete Book by ID",
    11: "Backup & Delete Book"
}


# Create a dictionary of tooltips/explanations
tooltips = {
    "Select": "Choose an action from the dropdown",
    "Document Count": "Shows the total number of books in the collection",
    "List All Book Titles": "Displays a sorted list of all book titles",
    "List All Authors": "Shows a list of all authors in the collection",
    "Show All Locations": "Displays all unique locations mentioned in books",
    "Find Duplicates": "Identifies potential duplicate books in the collection",
    "Compare 2 Books": "Shows a side-by-side comparison of two selected books",
    "----": "Separator",
    "Export Collection to JSON": "Downloads entire collection as a backup JSON file",
    "Upload Books to Firebase": "Import books from JSON files into Firebase database",
    "Edit Book Field": "Modify specific fields (like ISBN) in existing books",
    "Export Single Book to JSON": "Downloads a selected book as a JSON file",
    "Delete Book by ID": "Permanently removes a book using its unique identifier",
    "Backup & Delete Book": "Creates a backup copy then deletes the book from Firebase"
}

# Create the HTML for the dropdown label with tooltip
tooltip_html = """
    <div style="display: inline-block; position: relative;">
        <span style="margin-left: 5px;">
            <div style="visibility: hidden; width: 250px; background-color: #555; color: #fff; 
                        text-align: center; border-radius: 6px; padding: 5px; position: absolute; 
                        z-index: 1; bottom: 125%; left: 50%; margin-left: -125px; opacity: 0; 
                        transition: opacity 0.3s;">
                Hover over each option in the dropdown for more information
            </div>
        </span>
    </div>
"""



# Every Sidebar: Collection selection
collection_name = st.sidebar.selectbox(
    "Collection",
    ("books", "midbooks", "newbooks"),
    index=1 #default
)

all_books = firebase_client.get_all_documents(collection_name)

# Initialize session state
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Viewer"


# Info Tab
with view_tab:
    st.session_state.current_tab = "Viewer"
    # Create the selectbox with tooltips for each option
    view_action = st.selectbox(
        label=" ",  # Empty label
        options=view_options.values(),
        index=0,
    )
    # Display the tooltip for the selected option
    if view_action in tooltips:
        st.sidebar.info(tooltips[view_action])
    st.sidebar.markdown("----")
    st.write(f"{view_action}")

    placeholder_viewer = st.empty()

    with placeholder_viewer.container():

        # NUM DOCS
        if view_action == top_options[1]: #DOC COUNT
            doc_count = firebase_client.get_document_count(collection_name)
            print(doc_count)
            st.write(f"Number of documents in '{collection_name}': {doc_count}")

        # LIST ALL BOOK TITLES
        if view_action == top_options[2]: # List All Book Titles
            all_titles = sorted([book['title'] for book in all_books if 'title' in book])
            print(len(all_titles))
            st.write("### All Titles (Sorted Alphabetically):")
            # Join all titles with line breaks and apply custom CSS
            titles_html = "<div style='line-height: 1; font-size: 14px;'>" + "<br>".join(all_titles) + "</div>"
            st.markdown(titles_html, unsafe_allow_html=True)

        # UNQIUE Authors
        if view_action == top_options[3]: #AUTHORS
            # Extract and sort unique authors
            all_authors = sorted(set(book['author'] for book in all_books if 'author' in book))
            # Display the sorted authors
            st.write("### All Unique Authors (Sorted Alphabetically):")
            st.text("\n".join(all_authors))

        # UNIQUE LOCATIONS
        if view_action == top_options[4]: #LOCATIONS
            # Extract all unique cities from the 'locations' field of each book
            unique_places = set()

            for book in all_books:
                if 'locations' in book:
                    for location in book['locations']:
                        if 'city' in location:
                            unique_places.add(location['city'])
                        if 'place' in location:
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
            st.write("### Compare Two Books")
            st.write("Search for and select two books to compare side-by-side.")

            # Debug: Show collection info
            st.info(f"📚 Currently using collection: **{collection_name}** with **{len(all_books)}** books")

            # Debug: Show sample book structure
            if all_books:
                with st.expander("🔧 Debug: View sample book structure"):
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
            st.markdown("#### 📕 Select First Book")
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
                search_btn1 = st.button("🔍 Search", key="search_btn1")

            # Perform search for Book 1
            if search_btn1 and search_query1:
                st.write(f"🔍 DEBUG: Searching for '{search_query1}'")
                st.write(f"🔍 DEBUG: Total books in collection: {len(all_books)}")

                # Search in both title and author fields
                title_matches = firebase_client.fuzzy_match(all_books, 'title', search_query1)
                author_matches = firebase_client.fuzzy_match(all_books, 'author', search_query1)

                st.write(f"🔍 DEBUG: Title matches: {len(title_matches)}")
                st.write(f"🔍 DEBUG: Author matches: {len(author_matches)}")

                # Log first few title matches for inspection
                if title_matches:
                    st.write(f"🔍 DEBUG: First title match: {title_matches[0].get('title', 'N/A')}")
                if author_matches:
                    st.write(f"🔍 DEBUG: First author match: {author_matches[0].get('title', 'N/A')} by {author_matches[0].get('author', 'N/A')}")

                # Combine and deduplicate results
                combined_results = {book['id']: book for book in title_matches + author_matches}
                st.session_state.search_results1 = list(combined_results.values())[:10]  # Limit to top 10

                st.write(f"🔍 DEBUG: Combined unique results: {len(st.session_state.search_results1)}")

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
                    st.session_state.selected_book1 = firebase_client.get_document_by_id(all_books, book_id1)
                    st.success(f"✅ Book 1 selected: {st.session_state.selected_book1['title']}")

            elif search_query1 and search_btn1:
                st.warning("No books found. Try a different search term.")

            # Show Book 2 selection only if Book 1 is selected
            if st.session_state.selected_book1:
                st.markdown("---")
                st.markdown("#### 📗 Select Second Book")

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
                    search_btn2 = st.button("🔍 Search", key="search_btn2")

                # Perform search for Book 2
                if search_btn2 and search_query2:
                    st.write(f"🔍 DEBUG: Searching for '{search_query2}'")
                    st.write(f"🔍 DEBUG: Total books in collection: {len(all_books)}")

                    # Search in both title and author fields
                    title_matches = firebase_client.fuzzy_match(all_books, 'title', search_query2)
                    author_matches = firebase_client.fuzzy_match(all_books, 'author', search_query2)

                    st.write(f"🔍 DEBUG: Title matches: {len(title_matches)}")
                    st.write(f"🔍 DEBUG: Author matches: {len(author_matches)}")

                    # Log first few matches for inspection
                    if title_matches:
                        st.write(f"🔍 DEBUG: First title match: {title_matches[0].get('title', 'N/A')}")
                    if author_matches:
                        st.write(f"🔍 DEBUG: First author match: {author_matches[0].get('title', 'N/A')} by {author_matches[0].get('author', 'N/A')}")

                    # Combine and deduplicate results
                    combined_results = {book['id']: book for book in title_matches + author_matches}
                    st.session_state.search_results2 = list(combined_results.values())[:10]  # Limit to top 10

                    st.write(f"🔍 DEBUG: Combined unique results: {len(st.session_state.search_results2)}")

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
                        st.session_state.selected_book2 = firebase_client.get_document_by_id(all_books, book_id2)
                        st.success(f"✅ Book 2 selected: {st.session_state.selected_book2['title']}")

                elif search_query2 and search_btn2:
                    st.warning("No books found. Try a different search term.")

            # Display comparison when both books are selected
            if st.session_state.selected_book1 and st.session_state.selected_book2:
                st.markdown("---")
                st.markdown("## 📊 Book Comparison")

                book1 = st.session_state.selected_book1
                book2 = st.session_state.selected_book2

                # Create two columns for side-by-side comparison
                col_left, col_right = st.columns(2)

                with col_left:
                    st.markdown(f"### 📕 {book1['title']}")
                    st.markdown(f"**ID:** `{book1['id']}`")

                with col_right:
                    st.markdown(f"### 📗 {book2['title']}")
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
                    value1 = book1.get(key, "❌ Not present")
                    value2 = book2.get(key, "❌ Not present")

                    # Check if values are the same
                    values_match = value1 == value2

                    # Display field name
                    if values_match and value1 != "❌ Not present":
                        st.markdown(f"**{key.capitalize()}:** ✅ *Same*")
                        # Show the value once since they're the same
                        if isinstance(value1, list):
                            st.json(value1)
                        elif len(str(value1)) > 100:
                            with st.expander(f"View {key}"):
                                st.write(value1)
                        else:
                            st.write(f"  {value1}")
                    else:
                        st.markdown(f"**{key.capitalize()}:** ⚠️ *Different*")

                        col_a, col_b = st.columns(2)

                        with col_a:
                            if value1 == "❌ Not present":
                                st.markdown("*Not present in Book 1*")
                            elif isinstance(value1, list):
                                st.json(value1)
                            elif len(str(value1)) > 100:
                                with st.expander("View full text"):
                                    st.write(value1)
                            else:
                                st.write(value1)

                        with col_b:
                            if value2 == "❌ Not present":
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
                if st.button("🔄 Compare Different Books"):
                    st.session_state.selected_book1 = None
                    st.session_state.selected_book2 = None
                    st.session_state.search_results1 = []
                    st.session_state.search_results2 = []
                    st.rerun()

        if view_action == "Find Duplicates":
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
                    firebase_client.compare_books(all_books, book1_id, book2_id)
                    st.markdown("----")



# Function to read and parse the uploaded JSON file
def read_json_file(file):
    try:
        file_data = json.load(file)
        return file_data
    except Exception as e:
        st.sidebar.error(f"Error reading the file: {file} {e}")
        return None


# Add custom CSS to align the label to the left of the selectbox
st.markdown(
    """
    <style>
    .stSelectbox > label {
        display: inline-block;
        width: 30%; /* Adjust this to control label width */
        text-align: left;
        vertical-align: middle;
        margin-right: 10px;
    }
    .stSelectbox > div {
        display: inline-block;
        width: 65%; /* Adjust to control dropdown size */
    }
    </style>
    """,
    unsafe_allow_html=True
)



def write_all_books_to_json(collection_name, all_books):
    """Writes all books from the specified collection to a JSON file."""
    # Generate filename with current date and time
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    filename = f"backup/{collection_name}_{timestamp}.json"
    
    # Write the list of books to the JSON file
    with open(filename, "w") as json_file:
        json.dump(all_books, json_file, indent=4)

    st.success(f"All books saved to {filename}")
    return filename



def reset_confirmation():
    st.session_state.backup_confirmed = False



# DB-Manage Tab
with db_tab:
    st.session_state.current_tab = "DB"

    # Determine the default index for db_action selectbox
    # If edit_selected_book exists, default to "Edit Book Field"
    if 'edit_selected_book' in st.session_state and st.session_state.edit_selected_book is not None:
        # Find index of "Edit Book Field" in db_options
        edit_field_key = 10  # "Edit Book Field" is at key 10
        default_index = list(db_options.keys()).index(edit_field_key)
    else:
        default_index = 0

    db_action = st.selectbox(
        label="Choose action for DB-Manage",
        options=db_options.values(),
        index=default_index
    )

    st.write("---")  # Horizontal line for visual separation
    search_option = st.selectbox("Search by", ("Author", "Book Title", "Genre"))
    search_input = st.text_input(f"Enter {search_option}")
    search_button = st.button("Search")
    st.write("---")  # Horizontal line for visual separation

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
            books = firebase_client.get_books_by_author(all_books, search_input)
        elif search_option == "Book Title":
            books = firebase_client.get_book_by_title(all_books, search_input)
        elif search_option == "Genre":
            books = firebase_client.fuzzy_match(all_books, 'genre', search_input)

        # Store results in session state so they persist across reruns
        st.session_state.search_results = books
        st.session_state.last_search_query = f"{search_option}: {search_input}"

    # Display search results (from session state, so they persist after Edit button click)
    if st.session_state.search_results:
        books = st.session_state.search_results
        st.write(f"Found {len(books)} books:")

        for book in books:
            # Create two columns: one for book info, one for action button
            col_info, col_action = st.columns([4, 1])

            with col_info:
                # Book information display
                st.markdown(f"**📖 {book.get('title', 'N/A')}**")
                st.caption(f"**By:** {book.get('author', 'N/A')} | **Genre:** {book.get('genre', 'N/A')} | **Year:** {book.get('year', 'N/A')}")
                st.caption(f"**Publisher:** {book.get('publisher', 'N/A')} | **ID:** `{book.get('id', 'N/A')}`")

            with col_action:
                # Edit button - clicking it selects the book for editing
                if st.button("✏️ Edit", key=f"edit_btn_{book.get('id')}", type="primary", width='stretch'):
                    st.session_state.edit_selected_book = book
                    st.success(f"✅ Selected: {book.get('title', 'N/A')}")
                    st.rerun()

            st.markdown("---")  # Separator between books

    elif search_button:
        st.write(f"No books found for {search_option} {search_input}")

    #######################################################



    placeholder_db = st.empty()
    with placeholder_db.container():

        if db_action == db_options[9]: #Upload Books to Firebase

            st.session_state.backup_confirmed = False
            print(st.session_state)
            print('Upload Books to Firebase')            
            # File uploader
            uploaded_file = st.file_uploader("Choose a JSON file to Upload", type="json")
            # Button to upload and add books
            if uploaded_file is not None:
                if st.button("Upload and Add Books"):
                    book_data = read_json_file(uploaded_file)  # Read the JSON file
                    
                    if book_data:
                        if isinstance(book_data, list):  # Check if the JSON is a list of books
                            firebase_client.add_books_to_db(collection_name, book_data)  # Add books to Firestore
                            st.success("Books added to the database successfully!")
                        else:
                            st.error("Invalid format: The JSON file must contain a list of books.")

        if db_action == "Export Collection to JSON":
            print('attempting Export Collection to JSON')
            if not st.session_state.backup_confirmed:
                # Create a container for the confirmation dialog
                with st.container():
                    st.warning("⚠️ Export Confirmation")
                    st.write(f"Export {collection_name} collection to JSON?")
                    st.write("This will:")
                    st.markdown("""
                        - Create a new JSON file with current timestamp
                        - Save all documents from the collection
                        - Store the file in the 'backup' directory
                    """)
                    
                    # Add some space
                    st.write("")
                    
                    # Create columns for buttons
                    col1, col2, col3 = st.columns([1, 1, 3])
                    
                    with col1:
                        if st.button("✅ Yes, Export", type="primary"):
                            st.session_state.backup_confirmed = True
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ No, Cancel"):
                            reset_confirmation()
                            st.write("Backup cancelled.")
            
            else:
                try:
                    # Show progress indicator
                    with st.spinner("Creating backup..."):
                        filename = write_all_books_to_json(collection_name, all_books)
                    
                    # Show success message with file details
                    st.success("Backup Completed Successfully!")
                    st.write(f"📁 File saved as: `{filename}`")
                    
                    # Add option to create another backup
                    if st.button("Create Another Backup"):
                        reset_confirmation()
                        st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Backup Failed: {str(e)}")
                    if st.button("Try Again"):
                        reset_confirmation()
                        st.rerun()

        if db_action == db_options[10]: #"Edit Book Field":
            st.write("### 📝 Edit Book")

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
                # Book already selected from search
                selected_book = st.session_state.edit_selected_book

                # CRITICAL: Initialize locations for THIS book if not already set OR if book changed
                # Use book ID to track if we've switched to a different book
                current_book_id = selected_book.get('id')
                if 'edit_current_book_id' not in st.session_state or st.session_state.edit_current_book_id != current_book_id:
                    # New book selected - reset locations to THIS book's data
                    st.session_state.edit_locations_data = normalize_locations(selected_book.get('locations', []))
                    st.session_state.edit_current_book_id = current_book_id

                st.success(f"✅ **Selected Book:** {selected_book.get('title', 'N/A')} by {selected_book.get('author', 'N/A')}")

                # Show current book data
                with st.expander("📖 View Current Book Data"):
                    st.json(selected_book)

                # Option to clear selection and choose another book
                if st.button("🔄 Select a Different Book", key="clear_selection"):
                    st.session_state.edit_selected_book = None
                    st.session_state.edit_show_preview = False
                    st.session_state.edit_changes = {}
                    st.session_state.edit_locations_data = []
                    st.session_state.edit_current_book_id = None
                    st.rerun()

            else:
                # No book selected yet - show two options
                st.info("💡 **Option 1:** Use the search box above to find and click the ✏️ Edit button on a book")
                st.info("💡 **Option 2:** Enter a Book ID manually below if you already know it")

                # Direct ID input as fallback option
                book_id_input = st.text_input("Enter Book ID to Edit (Optional)", key="edit_book_id",
                                              placeholder="e.g., Sv7LW8CL3htN1Fj9AJf2")

                if book_id_input:
                    # Find the book by ID
                    selected_book = firebase_client.get_document_by_id(all_books, book_id_input)

                    if selected_book:
                        st.session_state.edit_selected_book = selected_book
                        st.success(f"✅ Book found: **{selected_book.get('title', 'N/A')}** by {selected_book.get('author', 'N/A')}")
                        st.rerun()
                    else:
                        st.error(f"❌ No book found with ID: {book_id_input}")

                # Show instruction to search if no book selected
                st.warning("⚠️ Please search for a book above and click the Edit button, or enter a Book ID.")

            # Step 2: Edit Form (only show if book is selected)
            if st.session_state.edit_selected_book:
                st.markdown("---")
                st.markdown("#### Step 2: Edit Book Fields")

                book = st.session_state.edit_selected_book

                # No longer using st.form - using regular widgets with keys for session state
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

                # Location editor is outside the form (Streamlit limitation - forms can't contain data_editor)
                st.markdown("---")
                st.markdown("#### 📍 Manage Locations")

                # Initialize locations in session state (normalized to prevent false change detection)
                if 'edit_locations_data' not in st.session_state:
                    st.session_state.edit_locations_data = normalize_locations(book.get('locations', []))

                current_locations = st.session_state.edit_locations_data

                # Debug info (optional - can be removed later)
                with st.expander("🔧 Debug: Location State Info"):
                    st.write(f"**Current book ID:** {book.get('id')}")
                    st.write(f"**Tracked book ID:** {st.session_state.get('edit_current_book_id', 'Not set')}")
                    st.write(f"**Original locations count:** {len(book.get('locations', []))}")
                    st.write(f"**Session locations count:** {len(st.session_state.edit_locations_data)}")
                    st.write("**Original (normalized):**")
                    st.json(normalize_locations(book.get('locations', [])))
                    st.write("**Session state:**")
                    st.json(st.session_state.edit_locations_data)

                # Display current locations count
                st.write(f"**Current locations:** {len(current_locations)}")

                # Section A: Display Current Locations as Table
                if current_locations:
                    st.markdown("##### Current Locations")

                    # Create DataFrame for display
                    locations_df = pd.DataFrame(current_locations)

                    # Ensure all expected columns exist
                    expected_cols = ['city', 'country', 'latitude', 'longitude', 'description']
                    for col in expected_cols:
                        if col not in locations_df.columns:
                            locations_df[col] = ''

                    # Reorder and display only expected columns
                    display_df = locations_df[expected_cols].fillna('')

                    # Display as editable data editor
                    edited_locations = st.data_editor(
                        display_df,
                        width='stretch',
                        num_rows="dynamic",  # Allow adding/deleting rows
                        column_config={
                            "city": st.column_config.TextColumn("City", required=True, width="medium"),
                            "country": st.column_config.TextColumn("Country", width="medium"),
                            "latitude": st.column_config.NumberColumn("Latitude", min_value=-90, max_value=90, format="%.4f"),
                            "longitude": st.column_config.NumberColumn("Longitude", min_value=-180, max_value=180, format="%.4f"),
                            "description": st.column_config.TextColumn("Description (optional)", width="large")
                        },
                        key="locations_editor"
                    )

                    # Update session state from edited DataFrame
                    if not edited_locations.equals(display_df):
                        # Normalize the locations data to remove numpy types
                        raw_locations = edited_locations.to_dict('records')
                        st.session_state.edit_locations_data = normalize_locations(raw_locations)
                        st.success("✅ Locations table updated!")

                else:
                    st.info("📍 No locations yet. Add one using the form below!")

                # Section B: Quick Add Location Form
                st.markdown("---")
                st.markdown("##### ➕ Quick Add Location")

                # Initialize geocode coordinates in session state if not present
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

                # Display success message if geocoding just completed
                if st.session_state.geocode_success_msg:
                    st.success(st.session_state.geocode_success_msg)
                    st.session_state.geocode_success_msg = None

                col_geo, col_add, col_clear = st.columns([1, 1, 1])

                # Callback function for geocoding button
                def geocode_callback():
                    city = st.session_state.get('quick_add_city', '')
                    country = st.session_state.get('quick_add_country', '')
                    if city and country:
                        time.sleep(0.5)  # Rate limiting for Nominatim
                        geo_result = geocode_location(city, country)
                        if geo_result:
                            st.session_state.quick_add_lat = geo_result['latitude']
                            st.session_state.quick_add_lng = geo_result['longitude']
                            st.session_state.geocode_success_msg = f"✅ Found: {geo_result['latitude']}, {geo_result['longitude']}"
                        else:
                            st.session_state.quick_add_lat = 0.0
                            st.session_state.quick_add_lng = 0.0
                            st.session_state.geocode_success_msg = "❌ Location not found."
                    else:
                        st.session_state.geocode_success_msg = "⚠️ Please enter both City and Country first."

                # Callback function for clearing the form
                def clear_form_callback():
                    st.session_state.quick_add_lat = 0.0
                    st.session_state.quick_add_lng = 0.0
                    st.session_state.quick_add_city = ""
                    st.session_state.quick_add_country = ""
                    st.session_state.quick_add_desc = ""

                # Callback function for adding location
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
                        # Clear the form
                        st.session_state.quick_add_lat = 0.0
                        st.session_state.quick_add_lng = 0.0
                        st.session_state.quick_add_city = ""
                        st.session_state.quick_add_country = ""
                        st.session_state.quick_add_desc = ""
                        st.session_state.geocode_success_msg = f"✅ Added {city}, {country}!"

                with col_geo:
                    st.button("🔍 Auto-Geocode", key="geocode_btn", on_click=geocode_callback, help="Automatically lookup coordinates")

                # Display coordinates (auto-filled or manual entry)
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
                    st.button("➕ Add Location", type="primary", key="add_location_btn", on_click=add_location_callback)

                with col_clear:
                    st.button("🗑️ Clear Form", key="clear_form_btn", on_click=clear_form_callback)

                # Section C: Advanced JSON Editor (Collapsible)
                with st.expander("🔧 Advanced: Edit as JSON"):
                    st.write("For power users: Edit the locations array directly as JSON.")

                    current_locations_json = json.dumps(st.session_state.edit_locations_data, indent=2)

                    edited_json = st.text_area(
                        "Locations JSON",
                        value=current_locations_json,
                        height=200,
                        key="json_editor"
                    )

                    if st.button("💾 Save JSON Changes", key="save_json_btn"):
                        try:
                            parsed_json = json.loads(edited_json)
                            st.session_state.edit_locations_data = parsed_json
                            st.success("✅ JSON saved successfully!")
                            st.rerun()
                        except json.JSONDecodeError as e:
                            st.error(f"❌ Invalid JSON: {e}")

                # NOW show the Preview Changes button after all editing is done
                st.markdown("---")
                st.markdown("#### 📋 Review All Changes")
                st.write("Once you've edited all fields and locations above, click below to preview your changes.")

                if st.button("📋 Preview Changes", type="primary", key="preview_changes_btn"):
                    # Trigger the form submission logic
                    submitted = True
                else:
                    submitted = False

                if submitted:
                        # Get locations from session state (managed by location editor below)
                        new_locations = st.session_state.get('edit_locations_data', book.get('locations', []))

                        # Build the changes dictionary
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

                        # Handle tags (convert comma-separated to array)
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

                        # Compare locations from session state with original book locations
                        # Normalize both to avoid false positives from empty fields or data type differences
                        original_locations_normalized = normalize_locations(book.get('locations', []))
                        new_locations_normalized = normalize_locations(new_locations)
                        if new_locations_normalized != original_locations_normalized:
                            changes['locations'] = new_locations

                        st.session_state.edit_changes = changes
                        st.session_state.edit_show_preview = True
                        st.rerun()

                # Step 3: Preview and Confirm Changes (now at the very end)
                if st.session_state.edit_show_preview and st.session_state.edit_changes:
                    st.markdown("---")
                    st.markdown("#### Step 3: Review and Confirm Changes")

                    changes = st.session_state.edit_changes

                    if not changes:
                        st.info("ℹ️ No changes detected. All fields remain the same.")
                    else:
                        st.warning(f"⚠️ You are about to update **{len(changes)}** field(s):")

                        # Show changes in a nice format
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
                                st.markdown("### →")

                            with col_new:
                                if isinstance(new_value, list):
                                    st.json(new_value)
                                elif len(str(new_value)) > 100:
                                    st.text(str(new_value)[:100] + "...")
                                else:
                                    st.code(new_value)

                        # Confirmation buttons
                        st.markdown("---")
                        col_confirm, col_cancel = st.columns(2)

                        with col_confirm:
                            if st.button("✅ Confirm and Save Changes", type="primary", key="confirm_save"):
                                # Perform the update
                                success = firebase_client.update_multiple_fields(
                                    collection_name,
                                    book['id'],
                                    changes,
                                    verbose=True
                                )

                                if success:
                                    st.success(f"✅ Successfully updated {len(changes)} field(s) for book: {book['title']}")

                                    # Reset state
                                    st.session_state.edit_selected_book = None
                                    st.session_state.edit_show_preview = False
                                    st.session_state.edit_changes = {}
                                    st.session_state.edit_locations_data = []
                                    st.session_state.edit_current_book_id = None

                                    st.balloons()
                                    st.info("💡 Refresh the page to edit another book.")
                                else:
                                    st.error("❌ Failed to update the book. Check console for errors.")

                        with col_cancel:
                            if st.button("❌ Cancel Changes", key="cancel_save"):
                                st.session_state.edit_show_preview = False
                                st.session_state.edit_changes = {}
                                st.rerun()

        if db_action == "Write Book to JSON":
            # Radio button to choose between "Title" and "ID"
            search_type = st.sidebar.radio("Search by:", ("Title", "ID"))

            # Display a text input field based on the selected search type
            if search_type == "Title":
                user_input = st.sidebar.text_input("Enter Book Title", "")
            else:
                user_input = st.sidebar.text_input("Enter Book ID", "")

            # Optional: Display the input value and call your function when the user provides input
            if user_input:
                st.write(f"You entered: {user_input}")

                # Call the write_book_json function based on the search type
                if search_type == "Title":
                    write_book_json(title=user_input, book_id=None, verbose=False)
                    st.write(f"Saving book with Title: {user_input}")
                else:
                    write_book_json(title=None, book_id=user_input, verbose=False)
                    st.write(f"Saving book with ID: {user_input}")

        # Logic for "Delete Book by ID"
        if db_action == "Delete Book by ID":
            doc_id = st.sidebar.text_input("Enter Document ID", "")

            if doc_id:
                if st.sidebar.button("Delete Document"):
                    try:
                        firebase_client.delete_document_by_id(collection_name, doc_id)
                        st.write(f"Document with ID '{doc_id}' deleted successfully.")
                    except Exception as e:
                        st.error(f"Failed to delete document: {e}")


# Help Tab
with h_tab:
    st.session_state.current_tab = "Help"

    # Sidebar content for Help tab
    st.selectbox(
        label="Choose action for Help",
        options=top_options.values(),
    )


    placeholder_h = st.empty()
    with placeholder_h.container():

        st.header("Help")
        st.write("Here are the help docs and resources.")
        st.markdown("""
        - **Getting Started:** [link]
        - **FAQ:** [link]
        - **Support:** [link]
        """)


# Global clear button (outside tabs)
if st.sidebar.button("Clear All Tabs"):
    print('clear')
    placeholder_viewer.empty()
    placeholder_db.empty()
    placeholder_h.empty()   
