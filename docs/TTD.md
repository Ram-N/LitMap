## To-Do List:




DONE 1. When the search text input or button is clicked, switch to Focus tab

2. H1 List View replace with "7 Books found"
default should be "Search for books"

3. Make the "Enable Clustering" toggle much skinnier

4. Add a "Clear Search" feature -- triggered when a collection is switched. Or if the current results are Zero




# Python Firestore functions
- Check for duplicate books
- Given a city name, get its Lat Lng, using GoogleMapsAPI if needed
- booktypes: should only be fiction, nonfiction, travel, poetry


GenAI
- Generate tons more books


# Learn
Good markers demo
https://storage.googleapis.com/gmp-maps-demos/advanced-markers/index.html#


Things to do:


- Frontend - Javascript, CSS, HTML

- Backend - Firebase

- API's - Google Maps API
    - Might also need GeoCoding API - to convert "New Delhi" into its lat/long

## 2. Set up Google Maps API
Google Cloud Setup: Create an account on Google Cloud, enable the Google Maps API, and get your API key.
Basic Map Display: Start by creating a basic HTML page that loads a world map using Google Maps.
Map Customization: Decide on how you want the map to look—zoom levels, whether to show city names, terrain, satellite, or normal views, etc.

## 3. Front-End Components

- Home Page (Map):

    - Display a world map with markers (flags or pins) showing locations associated with books.
    - Use the Google Maps API to handle interactive map elements like zooming, panning, and clicking on markers.

- Location Input Form:

 - Allow users to type a location name (like "New Delhi").
 - Use Google’s Geocoding API to translate location names into lat/long coordinates.
 - Include form fields for book title and author.
 - Submit the data to be saved in your backend.

- Marker Display:

  - When a location is added, display a marker at the specified lat/long with the book title and author in a tooltip or info window.
  - Consider showing a list of all books linked to the same location when clicking on the marker.

## 4. User Interactions and Features

- Add a Book: Users type a city name, which converts to lat/long, and they input the book title and author.
- Display Books: On the map, show markers or pins where each book is associated.
- Search Feature: Allow users to search for books by city or country and instantly pan to that location on the map.
- User Authentication (Optional): You might want to allow users to create accounts so that entries can be associated with individual users (for crowd-sourcing). Firebase has easy-to-integrate authentication.



