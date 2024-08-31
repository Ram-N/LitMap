

A Literary map of the world.
Go to any marker (location) in the world and see which books are written about the place.

LitMap/
│
├── public/
│   ├── index.html
│   ├── styles/
│   │   └── style.css
│   ├── scripts/
│   │   ├── app.js
│   │   ├── firebase.js
│   │   └── map.js
│   └── assets/
│
├── firebase.json
└── README.md


## File Descriptions


### 1. public/ Folder:
index.html: Your main HTML file that will load the map and interface for adding books. This is the root file that users will access.

- styles/:
    CSS Files

- scripts/:
    - app.js: Central JavaScript file for app logic. This will include UI interactions (handling form submissions, connecting Google Maps and Firebase).
    - firebase.js: Contains the Firebase configuration and initialization code. This is where you'll paste your Firebase config (from earlier).
    - map.js: Handles Google Maps logic, such as loading the map, adding markers, and interacting with map elements.

- assets/:
Place any images or icons your app might need here (like a logo, custom markers, etc.).

### 2. src/ Folder (optional):
    Use this folder if you plan to use a build tool like Webpack or Parcel.
components/: If you start building more advanced UI features (like modals, book lists, etc.), you can organize reusable components here.

-     utils/: Helper functions, like those for formatting data or handling Firebase queries, can go here.

### 3. Project Files:
- firebase.json & .firebaserc: 
    Auto-generated files to initialize Firebase in your project. Also contain hosting configurations.

- package.json: 
    This file tracks project dependencies (like Firebase SDK, if you're using npm).

## Data Structure

```{json}
{
  "location": {
    "lat": 28.6139,
    "lng": 77.2090,
    "name": "New Delhi"
  },
  "books": [
    {
      "title": "Midnight's Children",
      "author": "Salman Rushdie"
    },
    {
      "title": "The White Tiger",
      "author": "Aravind Adiga"
    }
  ]
}
```

### Working with This Schema

- Adding Books: Whenever a user adds a new book for a location, the book is appended to the books array for that location.
- Displaying Books: When a user clicks on a marker, you can display a list of books in an info window, looping through the books array for that location.
- Fetching Locations: When querying your database, you'll get back locations with all associated books, making it easy to manage multiple books per location.


