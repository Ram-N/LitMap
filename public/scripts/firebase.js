// firebase.js

import {
    initializeApp,
} from "https://www.gstatic.com/firebasejs/10.13.1/firebase-app.js";

import {
    getFirestore, collection, getDocs,
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
const db = getFirestore()
const fsBooks = collection(db, 'books');
const fsLocations = collection(db, 'locations');


// Save books to Firestore (from data.js)
function addBooksToFirestore(newbooks) {
    newbooks.forEach((book) => {
        // Create an object to store all book properties dynamically
        let bookData = {};

        // Loop through each property in the book object
        for (let key in book) {
            if (book.hasOwnProperty(key)) {
                bookData[key] = book[key]; // Add the key-value pair dynamically
            }
        }

        console.log(db);

        // Add the dynamically created bookData object to Firestore
        addDoc(fsBooks, bookData)
            .then((docRef) => {
                console.log("Book successfully written: ", docRef.id, book.title);
            })
            .catch((error) => {
                console.error("Error adding book: ", error);
            });
    });
}


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




async function getBooks() {
    const querySnapshot = await getDocs(fsBooks);
    window.books = [];

    querySnapshot.forEach((doc) => {
        window.books.push({
            id: doc.id,
            ...doc.data()
        });
    });

    // Dispatch a custom event after books are fetched
    const event = new CustomEvent('booksReady');
    console.log('FS books are ready');
    window.dispatchEvent(event);
}

if (0) {
    // Call the functions to save the data to Firestore
    // addBooksToFirestore();
    // addLocationsToFirestore();
    // console.log('books and locations saved')
}


async function printNumberOfDocs(collectionName) {
    try {
        const querySnapshot = await getDocs(collection(db, collectionName));
        console.log(`Number of documents in the '${collectionName}' collection: ${querySnapshot.size}`);
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
printNumberOfDocs("books"); // For the 'books' collection
printNumberOfDocs("locations"); // For the 'locations' collection

// Call the function to fetch books
getBooks();

