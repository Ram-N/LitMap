// Managing the App Tabs -- Map, List of Books, List of places
// Add/Delete to the list

import { db, fsBooks } from './firebase.js';  // Importing db from firebase.js

document.addEventListener("DOMContentLoaded", () => {
    const mapTab = document.getElementById("mapTab");
    const bookListTab = document.getElementById("bookListTab");
    const adminTab = document.getElementById("adminTab");

    const mapControls = document.getElementById("mapControls");
    const bookListContent = document.getElementById("bookListContent");
    const adminContent = document.getElementById("adminContent");

    document.getElementById('searchTab').addEventListener('click', function () {
        // Show book list controls and hide others
        document.getElementById('searchControls').style.display = 'block';
        document.getElementById('adminControls').style.display = 'none';

        // Add 'active' class to the clicked tab and remove from others
        this.classList.add('active');
        document.getElementById('adminTab').classList.remove('active');
    });

    document.getElementById('adminTab').addEventListener('click', function () {
        // Show admin controls and hide others
        document.getElementById('searchControls').style.display = 'none';
        document.getElementById('adminControls').style.display = 'block';

        // Add 'active' class to the clicked tab and remove from others
        this.classList.add('active');
        document.getElementById('searchTab').classList.remove('active');
    });

});


// Handle form submission
document.getElementById('locationForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const locationInput = document.getElementById('locationInput').value;
    const bookTitle = document.getElementById('bookTitle').value;
    const bookAuthor = document.getElementById('bookAuthor').value;

    // Create a new book object
    const newBook = {
        title: bookTitle,
        author: bookAuthor
    };

    try {
        // Save book and location to Firestore
        await addDoc(collection(db, "locations"), {
            location: { name: locationInput }, // Later you can integrate Geocoding API for lat/lng
            books: [newBook]
        });

        alert("Book added successfully!");
    } catch (e) {
        console.error("Error adding book: ", e);
    }
});

// Toggle advanced search
function toggleAdvancedSearch() {
    const advSearch = document.querySelector('.advanced-search');
    advSearch.style.display = (advSearch.style.display === 'none' || advSearch.style.display === '') ? 'block' : 'none';
}

// Function to handle search logic
function oldsearchBooks() {
    const searchQuery = {
        searchBar: document.getElementById('search-bar').value,
        author: document.getElementById('author').value,
        publishDate: document.getElementById('publish-date').value,
        title: document.getElementById('title').value,
        topic: document.getElementById('topic').value,
        tags: document.getElementById('tags').value,
        genre: document.getElementById('genre').value,
        location: document.getElementById('location').value,
        language: document.getElementById('language').value,
        isbn: document.getElementById('isbn').value
    };

    // Output search query to console (you can replace this with an API call or some other functionality)
    console.log('Search Query:', searchQuery);
}

// Function to show the map and hide the list
function showMap() {
    document.getElementById('map-container').classList.add('active');
    document.getElementById('list-container').classList.remove('active');

    // Disable the Map button and enable the List button
    document.getElementById('map-btn').classList.add('disabled');
    document.getElementById('map-btn').setAttribute('disabled', true);
    document.getElementById('list-btn').classList.remove('disabled');
    document.getElementById('list-btn').removeAttribute('disabled');
}

// Function to show the list and hide the map
function showList() {
    document.getElementById('list-container').classList.add('active');
    document.getElementById('map-container').classList.remove('active');

    // Disable the List button and enable the Map button
    document.getElementById('list-btn').classList.add('disabled');
    document.getElementById('list-btn').setAttribute('disabled', true);
    document.getElementById('map-btn').classList.remove('disabled');
    document.getElementById('map-btn').removeAttribute('disabled');
}

function initializeBookTable() {
    // Check if the table already exists, if not, create it
    let bookTable = document.getElementById('bookTable');

    if (!bookTable) {
        // If the table doesn't exist, create it
        bookTable = document.createElement('table');
        bookTable.id = 'bookTable';  // Assign an ID to the newly created table
        bookTable.className = 'styled-table';  // Add the class for styling
        document.getElementById('list-container').appendChild(bookTable); // Append to the container
    }

    // Create thead and append header row
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');

    // Create and append the table headers
    const headers = ['Title', 'Author', 'Type', 'Location'];
    headers.forEach(headerText => {
        const th = document.createElement('th');
        th.textContent = headerText;
        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    bookTable.appendChild(thead);

    // Create tbody
    const tbody = document.createElement('tbody');
    bookTable.appendChild(tbody);
    // The table is now initialized and ready for data rows to be appended
}

function removeBookTable() {
    const bookTable = document.getElementById('bookTable');
    if (bookTable) {
        bookTable.remove();  // Remove the table element from the DOM
    }
}


// Function to update the book table with filtered or selected books
function updateBookTable(books) {
    const tableBody = document.querySelector('#bookTable tbody');
    tableBody.innerHTML = '';  // Clear any existing rows

    console.log(books.length, "books updateTable");
    books.forEach((book) => {
        // Loop through each book location if there are multiple locations
        book.locations.forEach((location) => {
            const row = document.createElement('tr');

            // Create cells for title, author, type, and location
            const titleCell = document.createElement('td');
            titleCell.textContent = book.title;

            const authorCell = document.createElement('td');
            authorCell.textContent = book.author;

            const typeCell = document.createElement('td');
            typeCell.textContent = book.booktype;

            const locationCell = document.createElement('td');
            locationCell.textContent = `${location.lat || location.latitude}, ${location.lng || location.longitude}`;

            // Append cells to the row
            row.appendChild(titleCell);
            row.appendChild(authorCell);
            row.appendChild(typeCell);
            row.appendChild(locationCell);

            // Append row to the table body
            tableBody.appendChild(row);
        });
    });
}

document.addEventListener('DOMContentLoaded', function () {
    showMap();
    // initializeBookTable();
});


// Listen for the 'booksFetched' event and update the table
// this event happens in firebase.js
document.addEventListener('booksFetched', function (e) {
    const books = e.detail;  // Retrieve the books list from the event
    removeBookTable();
    if (books && books.length > 0) {
        // The array is non-null, is indeed an array, and contains elements
        initializeBookTable();
        updateBookTable(books);  // Call your function to update the table
    } else {
        console.log("Nothing Found");
    }

});

// Attach the function to the window object to make it globally accessible
window.showList = showList;
window.showMap = showMap;
