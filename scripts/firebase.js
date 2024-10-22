// firebase.js

import {
    initializeApp,
} from "https://www.gstatic.com/firebasejs/10.13.1/firebase-app.js";

import {
    getFirestore, collection, getDocs,
    query, where,
    addDoc, deleteDoc, doc
} from "https://www.gstatic.com/firebasejs/10.13.1/firebase-firestore.js";




// Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyCjZDAj9fHVNkLCS9n7XxXvdX73rmCz7nQ",
    authDomain: "litmap-88358.firebaseapp.com",
    projectId: "litmap-88358",
    storageBucket: "litmap-88358.appspot.com",
    messagingSenderId: "123861546544",
    appId: "1:123861546544:web:f67ae86b3b2e3279455ff5"
};


// Initialize Firebase
const app = initializeApp(firebaseConfig);
console.log('init');
// init services
export const db = getFirestore()


let currentCollection = 'newbooks'; // Default collection
document.addEventListener('DOMContentLoaded', () => {
    const collectionOptions = document.querySelectorAll('.collection-option');

    collectionOptions.forEach(option => {
        option.addEventListener('click', function () {
            currentCollection = this.getAttribute('data-collection');
            updateActiveCollection(this);
            loadBooks(currentCollection);
            refreshBookCache();
        });
    });

    // Set initial active state
    updateActiveCollection(document.querySelector('[data-collection="newbooks"]'));
});


function updateActiveCollection(selectedOption) {
    document.querySelectorAll('.collection-option').forEach(option => {
        option.classList.remove('active');
    });
    selectedOption.classList.add('active');
}

const fsLocations = collection(db, 'locations');


// deprecated
function addLocationsToFirestore() {
    window.locations.forEach((location) => {
        // Create an object to store all location properties dynamically
        let locationData = {};

        // Loop through each property in the location object
        for (let key in location) {
            if (location.hasOwnProperty(key)) {
                locationData[key] = location[key]; // Add the key-value pair dynamically
            }
        }

        addDoc(fsLocations, locationData)
            .then((docRef) => {
                console.log("Location successfully written with ID: ", docRef.id);
            })
            .catch((error) => {
                console.error("Error adding location: ", error);
            });
    });
}


// Function to get all books from Firestore
async function getAllBooks() {
    const booksRef = collection(db, currentCollection);
    const querySnapshot = await getDocs(booksRef);
    const books = [];

    querySnapshot.forEach((doc) => {
        books.push(doc.data());
    });

    return books;  // Return all books to be filtered in the next step
}


// Extended fuzzy search function with support for a single field or a fieldList
function fuzzyBookSearch(books, searchTerm, field = null, fieldList = null) {
    searchTerm = searchTerm.toLowerCase();  // Normalize the search term to lowercase

    return books.filter(book => {

        // Handle location search
        if (field === 'location') {
            if (book.locations && Array.isArray(book.locations)) {
                return book.locations.some(location => {
                    const city = location.city ? location.city.toLowerCase() : '';
                    const state = location.state ? location.state.toLowerCase() : '';
                    const country = location.country ? location.country.toLowerCase() : '';
                    return city.includes(searchTerm) || state.includes(searchTerm) || country.includes(searchTerm);
                });
            }
            return false;
        }

        // If a specific field is provided, search only in that field
        if (field && book[field]) {
            return book[field].toString().toLowerCase().includes(searchTerm);
        }

        // If a fieldList is provided, search only in those fields
        if (fieldList && Array.isArray(fieldList)) {
            return fieldList.some(field => book[field] && book[field].toString().toLowerCase().includes(searchTerm));
        }

        // Default: Search in title, author, and description
        const title = book.title.toLowerCase();
        const author = book.author.toLowerCase();
        const description = book.description ? book.description.toLowerCase() : '';

        // Check if the search term is in any of the default fields
        return title.includes(searchTerm) || author.includes(searchTerm) || description.includes(searchTerm);
    });
}


let allBooks = null;

// Function to fetch all books from Firestore (called only once)
async function fetchAllBooks() {
    if (allBooks === null) {
        try {
            allBooks = await getAllBooks();  // Your existing function to fetch books from Firestore
            console.log('All books fetched from Firestore');
        } catch (error) {
            console.error('Error fetching all books:', error);
            throw error;
        }
    }
    return allBooks;
}

// Modified search function
async function searchBooks(searchTerm, field = null, fieldList = null) {
    try {
        // Ensure books are fetched (will only query Firestore if not already fetched)
        await fetchAllBooks();

        // Perform fuzzy search on the local cache
        const results = fuzzyBookSearch(allBooks, searchTerm, field, fieldList);
        console.log('Search Results:', results);

        // Dispatch a custom event with the books data
        const event = new CustomEvent('booksFetched', { detail: results });
        document.dispatchEvent(event);  // Trigger the event, app.js will update the UI

    } catch (error) {
        console.error('Error searching books:', searchTerm, error);
    }
}

//Not using this as yet
// Function to refresh the book cache (call this when you need to update the local cache)
async function refreshBookCache() {
    allBooks = null;  // Reset the cache
    await fetchAllBooks();  // Fetch books again
    console.log('Book cache refreshed');
}

// Sidebar -- Search for some books 
// Get references to the form and input elements
const searchForm = document.querySelector('form[name="searchForm"]');
const searchInput = document.getElementById('search_query_main');

// Function to handle the search
function handleSearch(event) {
    event.preventDefault();  // Prevent the default form submission
    console.log('Performing search with query:', searchInput.value);

    // Get the search query
    const searchQuery = searchInput.value.trim();
    console.log('searching', searchQuery);

    // Get the currently selected radio button
    const getSelectedRadio = () => {
        return document.querySelector('input[name="search_field"]:checked');
    };

    const getSelectedValue = () => {
        const selectedRadio = getSelectedRadio();
        return selectedRadio ? selectedRadio.value : null;
    };

    let fieldList;  // Declare fieldList outside the switch statement

    switch (getSelectedValue()) {
        case 'any':
            fieldList = ['author', 'title', 'description'];
            searchBooks(searchQuery, null, fieldList);
            break;
        case 'title':
            searchBooks(searchQuery, 'title', null);
            break;
        case 'author':
            searchBooks(searchQuery, 'author', null);
            break;
        case 'location':
            searchBooks(searchQuery, 'location', null);
            break;
        case 'keyword':
            fieldList = ['tags', 'genre'];
            searchBooks(searchQuery, null, fieldList);
            break;
        default:
            console.log('Invalid search field selected');
            return;  // Exit the function if an invalid option is somehow selected
    }

    //make the Search Results visible
    showSearchResults();

}

// Add event listener for form submission (for the search button)
searchForm.addEventListener('submit', handleSearch);

// Add event listener for the Enter key in the search input
searchInput.addEventListener('keyup', function (event) {
    if (event.key === 'Enter') {
        handleSearch(event);
    }
});


async function loadBooks(collectionName) {
    try {
        const querySnapshot = await getDocs(collection(db, collectionName));
        window.books = [];
        querySnapshot.forEach((doc) => {
            window.books.push({ id: doc.id, ...doc.data() });
        });
        printNumberOfDocs(collectionName);

        // Dispatch a custom event after books are fetched
        const event = new CustomEvent('booksReady');
        console.log('FS books are ready');
        window.dispatchEvent(event);

    } catch (error) {
        console.error("Error loading books: ", error);
    }
}


async function printNumberOfDocs(collectionName) {
    try {
        const querySnapshot = await getDocs(collection(db, collectionName));
        console.log(`'${collectionName}' contains: ${querySnapshot.size}`);
    } catch (error) {
        console.error("Error getting documents: ", error);
    }
}


document.getElementById('uploadBooksButton').addEventListener('click', async () => {
    // Import newbooks from newdata.js
    const script = document.createElement('script');
    script.src = 'scripts/newdata.js';
    document.head.appendChild(script);

    script.onload = () => {
        if (window.newbooks && Array.isArray(window.newbooks)) {
            addBooksToFirestore(window.newbooks);
        } else {
            console.error('newbooks list is not available or not an array.');
        }
    };
});

// Example usage
printNumberOfDocs(currentCollection); // For the 'books' collection
printNumberOfDocs("locations"); // For the 'locations' collection

loadBooks(currentCollection);

