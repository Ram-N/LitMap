// Managing the App Tabs -- Map, List of Books, List of places
// Add/Delete to the list

import { db } from './firebase.js';  // Importing db from firebase.js
import { buildContent, openHighlight, closeHighlight } from './map.js';

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
    const suggestTab = document.getElementById("suggestTab");

    const mapControls = document.getElementById("mapControls");
    const bookListContent = document.getElementById("bookListContent");
    const adminContent = document.getElementById("adminContent");

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


// Function to show the map and hide the list
function showMap() {
    document.getElementById('map-container').classList.add('active');
    document.getElementById('focus-container').classList.remove('active');
    document.getElementById('suggest-container').classList.remove('active');


    // Disable the Map button and enable the List button
    document.getElementById('map-btn').classList.add('disabled');
    document.getElementById('map-btn').setAttribute('disabled', true);
    document.getElementById('list-btn').classList.remove('disabled');
    document.getElementById('list-btn').removeAttribute('disabled');
    document.getElementById('suggest-btn').classList.remove('disabled');
    document.getElementById('suggest-btn').removeAttribute('disabled');

}

// Function to show the list and hide the world map (Explore)
function showSearchResults() {
    document.getElementById('focus-container').classList.add('active');
    document.getElementById('map-container').classList.remove('active');
    document.getElementById('suggest-container').classList.remove('active');

    // Disable the List button and enable the Map button
    document.getElementById('list-btn').classList.add('disabled');
    document.getElementById('list-btn').setAttribute('disabled', true);
    document.getElementById('map-btn').classList.remove('disabled');
    document.getElementById('map-btn').removeAttribute('disabled');
    document.getElementById('suggest-btn').classList.remove('disabled');
    document.getElementById('suggest-btn').removeAttribute('disabled');
}


function showSuggestForm() {
    // Hide map and list containers, show suggest container
    document.getElementById('map-container').classList.remove('active');
    document.getElementById('focus-container').classList.remove('active');
    document.getElementById('suggest-container').classList.add('active');

    // Show the suggest controls
    const suggestControls = document.getElementById('suggestControls');
    suggestControls.classList.remove('hidden');
    suggestControls.style.display = ''; // This removes the "display: none" style

    // Enable map and list buttons, disable suggest button
    document.getElementById('map-btn').classList.remove('disabled');
    document.getElementById('map-btn').removeAttribute('disabled');
    document.getElementById('list-btn').classList.remove('disabled');
    document.getElementById('list-btn').removeAttribute('disabled');
    document.getElementById('suggest-btn').classList.add('disabled');
    document.getElementById('suggest-btn').setAttribute('disabled', true);



}


// Function to create and display book cards
function renderCards(books, query) {

    // Get the books-found element
    const booksFoundSection = document.querySelector('#books-found');

    // Remove any existing h3 count display
    const existingCount = booksFoundSection.querySelector('h3');
    if (existingCount) {
        existingCount.remove();
    }

    // Create new h3 element for book count
    const countDisplay = document.createElement('h3');
    countDisplay.textContent = `${books.length} ${books.length === 1 ? 'Book' : 'Books'} Found`;

    // Create new element for query display
    const queryDisplay = document.createElement('p');
    queryDisplay.textContent = query;  // assuming 'query' is your query string
    // Optional: add some styling if you want
    queryDisplay.style.fontStyle = 'italic';  // makes it italic
    // OR use a class if you prefer
    // queryDisplay.className = 'query-display';



    // Create container for cards if it doesn't exist
    let container = document.querySelector('.cards-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'cards-container';
        booksFoundSection.appendChild(container);
        container.appendChild(countDisplay);
        container.appendChild(queryDisplay);
    }

    // Add the new count display at the start of books-found section
    // booksFoundSection.insertBefore(countDisplay, booksFoundSection.firstChild);

    books.forEach(book => {
        const card = document.createElement('div');
        card.className = 'search-card';

        // Create header section with title, author, and type
        const header = document.createElement('div');
        header.className = 'search-card__header';

        const title = document.createElement('h3');
        title.className = 'search-card__title';
        title.textContent = book.title;

        const author = document.createElement('p');
        author.className = 'search-card__author';
        author.textContent = book.author;

        const type = document.createElement('p');
        type.className = 'search-card__type';
        type.textContent = book.type || 'Type not specified';

        header.appendChild(title);
        header.appendChild(author);
        header.appendChild(type);

        // Create locations section
        const locations = document.createElement('div');
        locations.className = 'search-card__locations';

        let locationNames = [];
        if (book.locations && Array.isArray(book.locations)) {
            locationNames = book.locations.map(loc =>
                loc.place || loc.city || 'Location not specified'
            );
        }
        locations.textContent = locationNames.join(', ') || 'No locations specified';

        // Create description section
        const description = document.createElement('p');
        description.className = 'search-card__description';
        if (book.description) {
            description.textContent = book.description.length > 80
                ? book.description.substring(0, 80) + '...'
                : book.description;
        } else {
            description.textContent = 'No description available';
        }

        // Assemble the card
        card.appendChild(header);
        card.appendChild(description);
        card.appendChild(locations);

        // Add the card to the container
        container.appendChild(card);
    });
}

// Function to remove all cards
function removeCards() {
    const container = document.querySelector('.cards-container');
    if (container) {
        container.remove();
    }
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
        console.log(book.locations, book.title, "BC");
        const bookColor = generateBookColor(book);
        book.locations.forEach((location, locationIndex) => {
            console.log(location, book.title, "LOC");
            // Get the latitude and longitude from the current location
            const lat = location.lat || location.latitude;  // Fallback to latitude if lat is not present
            const lng = location.lng || location.longitude; // Fallback to longitude if lng is not present

            const marker = new AdvancedMarkerElement({
                map: searchResultsMap,
                position: { lat: lat, lng: lng },
                title: `${book.title} by ${book.author}`,  // Title displayed on hover
                content: buildContent(book, location)
                // content: pin.element,
            });

            marker.addListener("click", () => {
                // toggleHighlight(marker, book);
                if (!marker.content.classList.contains("highlight")) {
                    openHighlight(marker, book);
                }

            });


            // Add click listener to show info window
            // marker.addListener("click", () => {
            //     const infoWindow = new google.maps.InfoWindow({
            //         content: `<h3>${book.title}</h3>
            //                   <p>Author: ${book.author}</p>
            //                   <p>Location: ${location.name || `Location ${locationIndex + 1}`}</p>`
            //     });
            //     infoWindow.open(searchResultsMap, marker);
            // });
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


// Modified event listener
document.addEventListener('booksFetched', function (e) {

    const books = e.detail.results;     // Access the results
    const query = e.detail.searchQuery; // Access the searchQuery

    removeCards(); // Clear existing cards

    console.log(query, 'bFetched')
    if (books && books.length > 0) {
        renderCards(books, query);
        renderSearchResultsMap(books); // Keeping the map rendering
    } else {
        console.log("No books Found");
        const booksFoundSection = document.querySelector('#books-found');

        // Remove any existing h3 count display
        const existingCount = booksFoundSection.querySelector('h3');
        if (existingCount) {
            existingCount.remove();
        }

        const mapContainer = document.querySelector('#map-container2');
        if (mapContainer) {
            const existingMap = mapContainer.querySelector('#search-results-map');
            if (existingMap) {
                existingMap.remove();
            }
        }

        // Create and append the "no results" message
        const container = document.createElement('div');
        container.className = 'cards-container';
        container.innerHTML = '<div class="search-card">No books found matching your search criteria.</div>';
        booksFoundSection.appendChild(container);
    }
});

// Attach the function to the window object to make it globally accessible
window.showSearchResults = showSearchResults;
window.showMap = showMap;
window.showSuggestForm = showSuggestForm;