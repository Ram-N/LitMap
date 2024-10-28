# remember to activate the correct env

import streamlit as st
from pprint import pprint
import firebase_admin
from firebase_admin import credentials, firestore
import json, re
from collections import defaultdict
from datetime import datetime
import pandas as pd


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


    def book_exists(self, collection_name: str, book: dict) -> bool:
        """
        Check if a book already exists in the Firestore collection by its title.
        Args:
            collection_name (str): The Firestore collection name.
            book (dict): The book data, containing at least the 'title' key.
        
        Returns:
            bool: True if the book exists, False otherwise.
        """
        db_book = self.get_book_by_title(collection_name, book['title'])
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
            if not self.book_exists(collection_name, book):
                st.success(f"Adding {book['title']}")
                self.add_new_document(collection_name, book, verbose=True)
            else:
                st.warning(f"{book['title']} already exists in db")


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


    # deprecated. No need to access the db more than once
    def get_documents_with_case_variants(self, collection_name: str, field: str, value: str) -> list:
        """
        Get documents from Firestore where a field matches different case variants of a given value.
        Args:
            collection_name (str): The name of the Firestore collection.
            field (str): The field to match.
            value (str): The value to search for in different case variants.
        
        Returns:
            list: A list of dictionaries containing the matching documents' data.
        """
        # Convert the value into different case formats
        original_value = value            # Original case
        lower_value = value.lower()       # Lowercase version of the value
        upper_value = value.upper()       # Uppercase version of the value
        title_value = value.title()       # Title case version (each word capitalized)

        # Query for each case variant
        original_query = self.db.collection(collection_name).where(field, '==', original_value).stream()
        lower_query = self.db.collection(collection_name).where(field, '==', lower_value).stream()
        upper_query = self.db.collection(collection_name).where(field, '==', upper_value).stream()
        title_query = self.db.collection(collection_name).where(field, '==', title_value).stream()

        # List to store document data along with their IDs
        matching_docs = []

        # Set to store document IDs we've already seen
        seen_ids = set()
                # Function to append documents if they are new
        def append_if_new(query):
            for doc in query:
                if doc.id not in seen_ids:  # Check if the document ID is already in the set
                    seen_ids.add(doc.id)    # Add the document ID to the set
                    matching_docs.append({'id': doc.id, **doc.to_dict()})
        # Append documents from each query if they are new
        append_if_new(original_query)
        append_if_new(lower_query)
        append_if_new(upper_query)
        append_if_new(title_query)
        # Print results
        if matching_docs:
            for doc in matching_docs:
                print(f"Document ID: {doc['id']} {doc[field]}")
            if len(matching_docs) > 1:
                print(f"Found {len(matching_docs)} unique documents")

        return matching_docs

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


# Streamlit App UI
st.title("LitMap Firestore Manager")

top_options = {
    0: "Select",
    1: "Document Count",
    2: "Print All Titles",
    3: "Print All Authors",
    4: "List All Locations",
    5: "Find Duplicates",
    6: "Compare 2 Books",
    7: "----",
    8: "BACKUP Collection to file",
    9: "Write Book to JSON",
    10: "Delete Doc by ID",
    11: "PURGE - write file and DELete doc"
}

# Create a dictionary of tooltips/explanations
tooltips = {
    "Select": "Choose an action from the dropdown",
    "Document Count": "Shows the total number of documents in the collection",
    "Print All Titles": "Displays a sorted list of all book titles",
    "Print All Authors": "Shows a list of all authors in the collection",
    "List All Locations": "Displays all unique locations mentioned in books",
    "Find Duplicates": "Identifies potential duplicate books in the collection",
    "Compare 2 Books": "Shows a side-by-side comparison of two selected books",
    "----": "Separator",
    "BACKUP Collection to file": "Creates a backup of the entire collection",
    "Write Book to JSON": "Exports a selected book to JSON format",
    "Delete Doc by ID": "Removes a document using its unique identifier",
    "PURGE - write file and DELete doc": "Backs up and then deletes a document"
}

# Create the HTML for the dropdown label with tooltip
tooltip_html = """
    <div style="display: inline-block; position: relative;">
        Action
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

# Display the label with tooltip
st.sidebar.markdown(tooltip_html, unsafe_allow_html=True)

# Create the selectbox with tooltips for each option
top_action = st.sidebar.selectbox(
    label=" ",  # Empty label since we're using custom HTML above
    options=top_options.values(),
    index=0,
    help="Hover over options for descriptions",
    format_func=lambda x: f"{x} ℹ️" if x in tooltips else x
)

# Display the tooltip for the selected option
if top_action in tooltips:
    st.sidebar.info(tooltips[top_action])

st.sidebar.markdown("----")
st.write(f"{top_action}")

# Sidebar: Collection selection
collection_name = st.sidebar.selectbox(
    "Collection",
    ("books", "midbooks", "newbooks"),
    index=1 #default
)
all_books = firebase_client.get_all_documents(collection_name)

# NUM DOCS
if top_action == top_options[1]:
    doc_count = firebase_client.get_document_count(collection_name)
    st.write(f"Number of documents in '{collection_name}': {doc_count}")

# ALL TITLES

if top_action == top_options[2]:
    all_titles = sorted([book['title'] for book in all_books if 'title' in book])
    print(len(all_titles))
    st.write("### All Titles (Sorted Alphabetically):")
    # Join all titles with line breaks and apply custom CSS
    titles_html = "<div style='line-height: 1; font-size: 14px;'>" + "<br>".join(all_titles) + "</div>"
    st.markdown(titles_html, unsafe_allow_html=True)

# UNQIUE Authors
if top_action == top_options[3]:
    # Extract and sort unique authors
    all_authors = sorted(set(book['author'] for book in all_books if 'author' in book))
    # Display the sorted authors
    st.write("### All Unique Authors (Sorted Alphabetically):")
    st.text("\n".join(all_authors))

# UNIQUE LOCATIONS
if top_action == top_options[4]:
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
        use_container_width=True,
        height=400,
        column_order=("Location",)
    )


###########################################################################

# Sidebar: Search options
search_option = st.sidebar.selectbox("Search by", ("Author", "Book Title", "Genre"))

# Text input for the selected search option
search_input = st.sidebar.text_input(f"Enter {search_option}")

# Button to trigger search
search_button = st.sidebar.button("Search")

# Search logic and display results
if search_button:
    st.write(f"{search_option} {search_input}")
    if search_option == "Author":
        books = firebase_client.get_books_by_author(all_books, search_input)
    elif search_option == "Book Title":
        books = firebase_client.get_book_by_title(all_books, search_input)
    elif search_option == "Genre":
        books = firebase_client.fuzzy_match(all_books, 'genre', search_input)

    # Display results in a nice layout
    if books:
        st.write(f"Found {len(books)} books:")
        for book in books:
            st.markdown(
                f"""
                <div style="border:1px solid #ddd; padding:10px; margin-bottom:10px; border-radius: 5px;">
                    <strong>Title:</strong> {book.get('title', 'N/A')}<br>
                    <strong>Author:</strong> {book.get('author', 'N/A')}<br>
                    <strong>Genre:</strong> {book.get('genre', 'N/A')}<br>
                    <strong>Year:</strong> {book.get('year', 'N/A')}<br>
                    <strong>Publisher:</strong> {book.get('publisher', 'N/A')}<br>
                </div>
                """, unsafe_allow_html=True
            )
    else:
        st.write(f"No books found for {search_option} {search_input}")


# Sidebar: File uploader
uploaded_file = st.sidebar.file_uploader("Choose a JSON file to Upload", type="json")


# Function to read and parse the uploaded JSON file
def read_json_file(file):
    try:
        file_data = json.load(file)
        return file_data
    except Exception as e:
        st.sidebar.error(f"Error reading the file: {file} {e}")
        return None

# Button to upload and add books
if uploaded_file is not None:
    if st.sidebar.button("Upload and Add Books"):
        book_data = read_json_file(uploaded_file)  # Read the JSON file
        
        if book_data:
            if isinstance(book_data, list):  # Check if the JSON is a list of books
                firebase_client.add_books_to_db(collection_name, book_data)  # Add books to Firestore
                st.sidebar.success("Books added to the database successfully!")
            else:
                st.sidebar.error("Invalid format: The JSON file must contain a list of books.")




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


if top_action == "Write Book to JSON":
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



dupe_ids = []

if top_action == "Find Duplicates":

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


# Logic for "Delete Doc by ID"
if top_action == "Delete Doc by ID":
    doc_id = st.sidebar.text_input("Enter Document ID", "")

    if doc_id:
        if st.sidebar.button("Delete Document"):
            try:
                firebase_client.delete_document_by_id(collection_name, doc_id)
                st.write(f"Document with ID '{doc_id}' deleted successfully.")
            except Exception as e:
                st.error(f"Failed to delete document: {e}")


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


# Initialize session state for confirmation
if 'backup_confirmed' not in st.session_state:
    st.session_state.backup_confirmed = False

def reset_confirmation():
    st.session_state.backup_confirmed = False

if top_action == "BACKUP Collection to file":
    if not st.session_state.backup_confirmed:
        # Create a container for the confirmation dialog
        with st.container():
            st.warning("⚠️ Backup Confirmation")
            st.write("You are about to create a backup of the entire collection.")
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
                if st.button("✅ Yes, Backup", type="primary"):
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