// firebase.js

import {
    initializeApp,
} from "https://www.gstatic.com/firebasejs/10.13.1/firebase-app.js";

import {
    getFirestore, collection, getDocs
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
const colRef = collection(db, 'books')


// function saveBookToFirestore(book) {
//     db.collection("books").add(book)
//         .then((docRef) => {
//             console.log("Book added with ID: ", docRef.id);
//         })
//         .catch((error) => {
//             console.error("Error adding book: ", error);
//         });
// }

// Example book data (you can dynamically create this)
const newBook = {
    title: "Tale of 2 Cities",
    author: "Charles Dickens",
    location: { lat: 55.5074, lng: -0.1278 }, // Latitude and longitude for London
    booktype: "Fiction"
};

// Call the function to save book
// saveBookToFirestore(newBook);
// console.log('2 saved')



async function getBooks() {
    const querySnapshot = await getDocs(colRef);
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

// Call the function to fetch books
getBooks();



// function loadBooksFromFirestore() {
//     db.collection("books").get().then(
//         (querySnapshot) => {
//             querySnapshot.forEach((doc) => {
//                 const book = doc.data();
//                 console.log(book);

//                 // Create marker for each book
//                 const marker = new google.maps.Marker({
//                     position: book.location,
//                     map: map,
//                     title: book.title,
//                     icon: getIcon(book.booktype)
//                 });

//                 // Add an info window for each marker
//                 const infoWindow = new google.maps.InfoWindow({
//                     content: `<h3>${book.title}</h3><p><strong>Author:</strong> ${book.author}</p>`
//                 });

//                 marker.addListener("click", () => {
//                     infoWindow.open(map, marker);
//                 });
//             });
//         });
// }

// Call this function when the map initializes
// loadBooksFromFirestore();

