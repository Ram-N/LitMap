// Managing the App Tabs -- Map, List of Books, List of places
// Add/Delete to the list

import { db, fsBooks } from './firebase.js';  // Importing db from firebase.js

// utility function
function generateBookColor(book) {
    // Combine relevant book properties into a single string
    const bookString = `${book.title}|${book.author}|${book.type}.join(',')}`;

    // Generate a hash from the string
    let hash = 0;
    for (let i = 0; i < bookString.length; i++) {
        const char = bookString.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32-bit integer
    }

    // Convert the hash to a hex color
    const color = Math.abs(hash).toString(16).substring(0, 6);

    // Ensure the color is 6 digits long
    return '#' + ('000000' + color).slice(-6);
}


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


// Function to show the map and hide the list
function showMap() {
    document.getElementById('map-container').classList.add('active');
    document.getElementById('list-map-container').classList.remove('active');

    // Disable the Map button and enable the List button
    document.getElementById('map-btn').classList.add('disabled');
    document.getElementById('map-btn').setAttribute('disabled', true);
    document.getElementById('list-btn').classList.remove('disabled');
    document.getElementById('list-btn').removeAttribute('disabled');
}

// Function to show the list and hide the map
function showList() {
    document.getElementById('list-map-container').classList.add('active');
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
        const row = document.createElement('tr');

        // Create cells for title, author, type, and location
        const titleCell = document.createElement('td');
        titleCell.textContent = book.title;

        const authorCell = document.createElement('td');
        authorCell.textContent = book.author;

        const typeCell = document.createElement('td');
        typeCell.textContent = book.booktype;

        const locationCell = document.createElement('td');

        // Initialize an empty array to hold city names
        let cityNames = [];

        // Iterate through the locations of the book
        book.locations.forEach((location) => {
            // Check if the location has a 'city' field
            if (location.city) {
                cityNames.push(location.city);
            }
        });

        // Set the textContent of the cell to the concatenated city names, joined by commas
        locationCell.textContent = cityNames.length > 0 ? cityNames.join(', ') : 'Unknown';

        // Append cells to the row
        row.appendChild(titleCell);
        row.appendChild(authorCell);
        row.appendChild(typeCell);
        row.appendChild(locationCell);

        // Append row to the table body
        tableBody.appendChild(row);
    });
}


async function renderSearchResultsMap(books) {
    const { Map } = await google.maps.importLibrary("maps");
    const { AdvancedMarkerElement, PinElement } = await google.maps.importLibrary("marker");

    // Create a new div element for the second map
    const secondMapDiv = document.createElement('div');
    secondMapDiv.id = 'search-results-map';
    secondMapDiv.style.width = '100%';
    // secondMapDiv.style.height = '400px'; // Adjust as needed
    secondMapDiv.style.height = '100%'; // Adjust as needed

    document.getElementById('map-container2').appendChild(secondMapDiv);

    // Calculate the bounds of all locations
    const bounds = new google.maps.LatLngBounds();
    books.forEach(book => {
        console.log(book.locations, book.title);
        book.locations.forEach(location => {
            const llat = location.lat || location.latitude;  // Fallback to latitude if lat is not present
            const llng = location.lng || location.longitude; // Fallback to longitude if lng is not present
            bounds.extend(new google.maps.LatLng(llat, llng));
        });
    });
    // Create the new map
    const searchResultsMap = new Map(document.getElementById("search-results-map"), {
        mapId: "DEMO_MAP_ID",
        zoom: 10, // This will be adjusted by fitBounds()
        center: bounds.getCenter(), // Center the map on the bounds

    });

    // Add markers for each book location
    books.forEach((book, bookIndex) => {
        const bookColor = generateBookColor(book);
        book.locations.forEach((location, locationIndex) => {
            // Get the latitude and longitude from the current location
            const lat = location.lat || location.latitude;  // Fallback to latitude if lat is not present
            const lng = location.lng || location.longitude; // Fallback to longitude if lng is not present

            const pin = new PinElement({
                background: bookColor,
                scale: 1.5,
                glyph: `${bookIndex + 1}.${locationIndex + 1}`,
            });

            const marker = new AdvancedMarkerElement({
                map: searchResultsMap,
                position: { lat: lat, lng: lng },
                title: `${book.title} - Location ${locationIndex + 1}`,
                content: pin.element,
            });

            // Add click listener to show info window
            marker.addListener("click", () => {
                const infoWindow = new google.maps.InfoWindow({
                    content: `<h3>${book.title}</h3>
                              <p>Author: ${book.author}</p>
                              <p>Location: ${location.name || `Location ${locationIndex + 1}`}</p>`
                });
                infoWindow.open(searchResultsMap, marker);
            });
        });
    });

    // Fit the map to the bounds of all markers with error handling
    try {
        searchResultsMap.fitBounds(bounds);
        // Add a listener for when the bounds_changed event is fired
        google.maps.event.addListenerOnce(searchResultsMap, 'bounds_changed', function () {
            const MAX_ZOOM = 15; // Adjust this value as needed
            if (searchResultsMap.getZoom() > MAX_ZOOM) {
                searchResultsMap.setZoom(MAX_ZOOM);
            }
        });
    } catch (error) {
        console.error("Error in fitBounds:", error.message);
        console.error("Error stack:", error.stack);
        console.log("Bounds object:", bounds);
        console.log("Number of locations:", books.reduce((sum, book) => sum + book.locations.length, 0));

        // Fallback: set a default center and zoom if fitBounds fails
        searchResultsMap.setCenter({ lat: 0, lng: 0 });
        searchResultsMap.setZoom(2);
    }
}

// Example usage:
// const searchResults = [
//     { 
//         title: "Book 1", 
//         author: "Author 1",
//         locations: [
//             { name: "Store A", lat: 40.7128, lng: -74.0060 },
//             { name: "Library B", lat: 40.7580, lng: -73.9855 }
//         ]
//     },
//     { 
//         title: "Book 2", 
//         author: "Author 2",
//         locations: [
//             { name: "Bookshop C", lat: 40.7308, lng: -73.9973 }
//         ]
//     },
// ];
// renderSearchResultsMap(searchResults);

document.addEventListener('DOMContentLoaded', function () {
    showMap();
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
        renderSearchResultsMap(books);
    } else {
        console.log("Nothing Found");
    }

});

// Attach the function to the window object to make it globally accessible
window.showList = showList;
window.showMap = showMap;
