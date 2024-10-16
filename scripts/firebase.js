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


// Called when the all radiobutton and Search is pressed
async function searchBooks(searchTerm, field = null, fieldList = null) {
    try {
        const books = await getAllBooks();  // Get all books
        const results = fuzzyBookSearch(books, searchTerm, field, fieldList);  // Perform fuzzy search
        console.log('Search Results:', results);  // Display the results or pass to the table update function

        // Dispatch a custom event with the books data
        const event = new CustomEvent('booksFetched', { detail: results });
        document.dispatchEvent(event);  // Trigger the event, app.js will update the UI

    } catch (error) {
        console.error('Error fetching books:', searchTerm, error);
    }
}

// Sidebar -- Search for some books 
document.querySelector('form[name="searchForm"]').addEventListener('submit', function (event) {
    event.preventDefault();  // Prevent the default form submission

    // Get the search query
    const searchQuery = document.getElementById('search_query_main').value.trim();
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
        case 'all':
            fieldList = ['author', 'title', 'description'];
            searchBooks(searchQuery, null, fieldList);
            break;
        case 'title':
            searchBooks(searchQuery, 'title', null);
            break;
        case 'author':
            searchBooks(searchQuery, 'author', null);
            break;
        case 'keyword':
            fieldList = ['tags', 'genre'];
            searchBooks(searchQuery, null, fieldList);
            break;
        default:
            console.log('Invalid search field selected');
            return;  // Exit the function if an invalid option is somehow selected
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

