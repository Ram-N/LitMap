// Managing the App Tabs -- Map, List of Books, List of places
// Add/Delete to the list


document.addEventListener("DOMContentLoaded", () => {
    const mapTab = document.getElementById("mapTab");
    const bookListTab = document.getElementById("bookListTab");
    const adminTab = document.getElementById("adminTab");

    const mapControls = document.getElementById("mapControls");
    const bookListContent = document.getElementById("bookListContent");
    const adminContent = document.getElementById("adminContent");

    document.getElementById('mapTab').addEventListener('click', function () {
        // Show map controls and hide others
        document.getElementById('mapControls').style.display = 'block';
        document.getElementById('bookListControls').style.display = 'none';
        document.getElementById('adminControls').style.display = 'none';

        // Add 'active' class to the clicked tab and remove from others
        this.classList.add('active');
        document.getElementById('bookListTab').classList.remove('active');
        document.getElementById('adminTab').classList.remove('active');
    });

    document.getElementById('bookListTab').addEventListener('click', function () {
        // Show book list controls and hide others
        document.getElementById('mapControls').style.display = 'none';
        document.getElementById('bookListControls').style.display = 'block';
        document.getElementById('adminControls').style.display = 'none';

        // Add 'active' class to the clicked tab and remove from others
        this.classList.add('active');
        document.getElementById('mapTab').classList.remove('active');
        document.getElementById('adminTab').classList.remove('active');
    });

    document.getElementById('adminTab').addEventListener('click', function () {
        // Show admin controls and hide others
        document.getElementById('mapControls').style.display = 'none';
        document.getElementById('bookListControls').style.display = 'none';
        document.getElementById('adminControls').style.display = 'block';

        // Add 'active' class to the clicked tab and remove from others
        this.classList.add('active');
        document.getElementById('mapTab').classList.remove('active');
        document.getElementById('bookListTab').classList.remove('active');
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

// dynamically update the zoom level display when the range slider is used:
document.getElementById('zoomControl').addEventListener('input', function () {
    const zoomValue = document.getElementById('zoomValue');
    zoomValue.textContent = this.value;

    // Now 'map' is globally accessible
    if (map) {
        map.setZoom(parseInt(this.value));  // Ensure map is defined
    } else {
        console.error('Map is not initialized');
    }
});

