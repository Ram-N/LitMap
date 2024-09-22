// Managing the App Tabs -- Map, List of Books, List of places
// Add/Delete to the list


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
function searchBooks() {
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

// Default behavior: show the map view on load
window.onload = function () {
    showMap();
};


