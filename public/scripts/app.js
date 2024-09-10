// Managing the App Tabs -- Map, List of Books, List of places
// Add/Delete to the list

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

// map.addListener("click", (e) => {
//     const latLng = e.latLng;

//     // Create a marker at the clicked location
//     const marker = new google.maps.Marker({
//         position: latLng,
//         map: map,
//     });

//     // Example: add marker details (book info) here
//     const bookTitle = prompt("Enter the book title:");
//     const bookAuthor = prompt("Enter the book author:");

//     // Attach info window to marker (to show book details)
//     const infoWindow = new google.maps.InfoWindow({
//         content: `<h4>${bookTitle}</h4><p>${bookAuthor}</p>`
//     });

//     marker.addListener("click", () => {
//         infoWindow.open(map, marker);
//     });

    // Optionally, save the marker data to Firestore or local storage
// });



