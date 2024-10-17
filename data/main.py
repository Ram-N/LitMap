
import streamlit as st
from pprint import pprint
import firebase_admin
from firebase_admin import credentials, firestore
import json
from collections import defaultdict

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

    def get_document_by_id(self, collection_name: str, doc_id: str, verbose: bool = False) -> dict:
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


# Initialize Firebase client
service_account_key = "litmap-88358-firebase-adminsdk-9w1l9-73ca515ce7.json"
firebase_client = FirebaseClient(service_account_key)


# Streamlit App UI
st.title("LitMap Firestore Manager")

# Sidebar: Collection selection
collection_name = st.sidebar.selectbox(
    "Collection",
    ("books", "midbooks", "newbooks")
)

all_books = firebase_client.get_all_documents(collection_name)

# Sidebar: Search options
search_option = st.sidebar.selectbox("Search by", ("Author", "Book Title", "Genre"))

# Text input for the selected search option
search_input = st.sidebar.text_input(f"Enter {search_option}")

# Button to trigger search
search_button = st.sidebar.button("Search")


# Search logic and display results
if search_button:

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

# Button to get the document count for the selected collection
if st.sidebar.button("NumDocs"):
    doc_count = firebase_client.get_document_count(collection_name)
    st.write(f"Number of documents in '{collection_name}': {doc_count}")

# Sidebar: File uploader
uploaded_file = st.sidebar.file_uploader("Choose a JSON file", type="json")


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


# Add a dropdown to the sidebar
print_option = st.sidebar.selectbox(
    "Select a Print Option",
    ("Select an option", "Get All Titles", 
    "Get All Authors",
    "List All Locations",
    "Find Duplicates",
    ),
    label_visibility="hidden"
)

st.write(f"{print_option}")

if print_option == "Get All Titles":
    # Extract and sort all titles
    all_titles = sorted([book['title'] for book in all_books if 'title' in book])

    # Display the sorted titles
    st.write("### All Titles (Sorted Alphabetically):")
    for title in all_titles:
        st.write(title)

if print_option == "Get All Authors":

    # Extract and sort unique authors
    all_authors = sorted(set(book['author'] for book in all_books if 'author' in book))
    # Display the sorted authors
    st.write("### All Unique Authors (Sorted Alphabetically):")
    for author in all_authors:
        st.write(author)


if print_option == "List All Locations":

    # Extract all unique cities from the 'locations' field of each book
    unique_places = set()

    for book in all_books:
        if 'locations' in book:
            for location in book['locations']:
                if 'city' in location:
                    unique_places.add(location['city'])
                if 'place' in location:
                    unique_places.add(location['place'])

    # Display the unique cities using st.write()
    st.write("### Unique Cities Mentioned in Books:")
    for city in sorted(unique_places):
        st.write(city)

    print(book['locations'])


if print_option == "Find Duplicates":

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
                print(book)

    if not found_duplicates:
        st.write("No duplicate books found.")

# pprint(all_books)

if 0:
    # Example: Add a new document
    new_doc_id = firebase_client.add_new_document(collection_name, {'title': 'Dummy Book', 'author': 'Dummy Author Name'}, verbose=True)

    # Example: Delete a document by its ID
    firebase_client.delete_document_by_id(collection_name, doc_id)



    # Example: Get documents by title with case variants
    title = 'An Area of Darkness'
    books_by_title = firebase_client.get_book_by_title('newbooks', title)
    pprint(books_by_title)

    # Example: Get books by author
    author_name = 'Chimamanda Ngozi Adichie'
    books_by_author = firebase_client.get_books_by_author('newbooks', author_name)
    pprint(books_by_author)