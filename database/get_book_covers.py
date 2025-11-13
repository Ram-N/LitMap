import firebase_admin
from firebase_admin import credentials, firestore
import requests
import time
from typing import Optional, Dict

class BookCoverFetcher:
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

        # Base URLs for different cover sizes
        self.OPEN_LIBRARY_BASE_URL = "https://covers.openlibrary.org/b"
        self.sizes = {'S': 'S', 'M': 'M', 'L': 'L'}

    def get_cover_url(self, isbn: str, size: str = 'M') -> Optional[str]:
        """Generate and validate Open Library cover URL."""
        if not isbn:
            return None
            
        url = f"{self.OPEN_LIBRARY_BASE_URL}/isbn/{isbn}-{size}.jpg"
        
        # Check if image exists
        response = requests.head(url)
        if response.status_code == 200:
            return url
        return None

    def update_book_covers(self, collection_name) -> None:
        """Update cover URLs for all books in Firestore."""
        # Get all books from Firestore
        books_ref = self.db.collection(collection_name)
        books = books_ref.stream()
        
        for book in books:
            book_data = book.to_dict()
            isbn = book_data.get('isbn')
            
            if not isbn:
                continue
                
            # Get cover URLs for different sizes
            cover_urls = {}
            for size in self.sizes.keys():
                cover_url = self.get_cover_url(isbn, size)
                if cover_url:
                    cover_urls[size] = cover_url
            
            if cover_urls:
                # Update Firestore only if we found at least one cover
                print(f"{book_data['title']}")
                print(f"{cover_urls}")

                books_ref.document(book.id).update({
                    'coverUrls': cover_urls,
                    'coverLastUpdated': firestore.SERVER_TIMESTAMP
                })
            
            # Respect rate limits
            time.sleep(1)

    def process_single_book(self, collection_name, book_id: str) -> Dict:
        """Process a single book and return cover URLs."""
        book_ref = self.db.collection(collection_name).document(book_id)
        book = book_ref.get()
        
        if not book.exists:
            return {}
            
        book_data = book.to_dict()
        isbn = book_data.get('isbn')
        
        if not isbn:
            return {}
            
        cover_urls = {}
        for size in self.sizes.keys():
            cover_url = self.get_cover_url(isbn, size)
            if cover_url:
                cover_urls[size] = cover_url
                
        if cover_urls:
            print(f"{book_data['title']}")
            print(f"{cover_urls}")
            book_ref.update({
                'coverUrls': cover_urls,
                'coverLastUpdated': firestore.SERVER_TIMESTAMP
            })
            
        return cover_urls

# Usage example
if __name__ == "__main__":

    collection_name = 'midbooks'
    # Initialize Firebase client
    service_account_key = "litmap-88358-firebase-adminsdk-9w1l9-73ca515ce7.json"
    fetcher = BookCoverFetcher(service_account_key)
    fetcher.update_book_covers(collection_name)
