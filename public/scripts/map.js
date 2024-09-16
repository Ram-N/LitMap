// public/scripts/map.js
let map;
let geocoder;

import { MarkerClusterer } from "https://cdn.skypack.dev/@googlemaps/markerclusterer@2.3.1";

// Predefined locations (latitude, longitude)
const locations = {
  new_york: { lat: 40.7128, lng: -74.0060 },
  london: { lat: 51.5074, lng: -0.1278 },
  tokyo: { lat: 35.6762, lng: 139.6503 },
  sydney: { lat: -33.8688, lng: 151.2093 }
};

function printAllBooks() {
  window.books.forEach((book, index) => {
    console.log(`Book ${index + 1}:`);
    console.log(`Title: ${book.title}`);
    console.log(`Author: ${book.author}`);
    console.log(`Latitude: ${book.lat}`);
    console.log(`Longitude: ${book.lng}`);
    console.log(`Book Type: ${book.booktype}`);
    console.log('----------------------');
  });
}


// Function to get the appropriate icon based on book type
function getIcon(booktype) {
  switch (booktype) {
    case 'fiction':
      return 'images/icons/red_book.png';
    case 'nonfiction':
      return 'images/icons/blue_book.png';
    case 'travel':
      return 'images/icons/brown_book.png';
    case 'science-fiction':
      return 'images/icons/purple_book.png';
    default:
      return 'images/icons/default.png'; // Fallback icon
  }
}


// Function to populate zoom level dropdown
function populateZoomDropdown() {
  const zoomSelect = document.getElementById('zoomSelect');
  for (let zoom = 17; zoom >= 2; zoom -= 2) {
    const option = document.createElement('option');
    option.value = zoom;
    option.text = `Zoom ${zoom}`;
    zoomSelect.appendChild(option);
  }
}


// Function to geocode a location and center the map
function geocodeAddress(location) {
  geocoder.geocode({ address: location }, (results, status) => {
    if (status === "OK") {
      const resultLocation = results[0].geometry.location;

      // Ensure the resultLocation exists and is valid before setting it on the map
      if (resultLocation) {
        map.setCenter(resultLocation);
        map.setZoom(10);
      } else {
        alert("No valid location found.");
      }
    } else {
      alert("Geocode was not successful for the following reason: " + status);
    }
  });
}

function renderBooksOnMap() {


  if (window.books && window.books.length > 0) {
    const markers = [];

    window.books.forEach((book) => {

      // Create content for the marker
      const content = document.createElement('div');
      content.innerHTML = `<div style="padding: 5px; background-color: white; border-radius: 5px;">
                             <strong>${book.title}</strong><br>
                             <em>${book.author}</em><br>
                             <span>${book.booktype}</span>
                           </div>`;

      // Determine the latitude and longitude based on the presence of the location object
      if (book.locations && Array.isArray(book.locations)) {
        // Loop through each location in the locations array
        book.locations.forEach((location) => {

          // Get the latitude and longitude from the current location
          const lat = location.lat || location.latitude;  // Fallback to latitude if lat is not present
          const lng = location.lng || location.longitude; // Fallback to longitude if lng is not present

          // Check if lat and lng are defined
          if (lat && lng) {
            // Create the position using the latitude and longitude
            const position = new google.maps.LatLng(lat, lng);

            // Create the AdvancedMarkerElement for each location
            const marker = new google.maps.marker.AdvancedMarkerElement({
              position: position,
              map: map,  // Assuming 'map' is your Google map instance
              title: `${book.title} by ${book.author}`,  // Title displayed on hover
              // content: `<div class="marker-content">${book.title}</div>` // Custom content for the marker
            });

            const infoWindowContent = `
          <div style="width: 200px;">
            <h3>${book.title}</h3>
            <p><strong>Author:</strong> ${book.author}</p>
            <p>${book.description}</p>
            ${book.image ? `<img src="${book.image}" alt="${book.title}" style="width: 100%;">` : ''}
          </div>
        `;

            // Create the info window without close button
            const infoWindow = new google.maps.InfoWindow({
              content: infoWindowContent,
              disableAutoPan: true // Optional: Prevents automatic panning of the map when the InfoWindow is shown
            });

            // Attach mouseover event to open info window
            marker.addListener("mouseover", () => {
              infoWindow.open({
                anchor: marker,
                map,
                shouldFocus: true
              });
            });

            // Attach mouseout event to close info window
            marker.addListener("mouseout", () => {
              infoWindow.close();
            });

            // Also, ensure to close any previous InfoWindow if another one is opened.
            marker.addListener("click", () => {
              infoWindow.open({
                anchor: marker,
                map
              });
            });

            // Add the marker to the markers array
            markers.push(marker);


          }
        });
      }
      else {
        console.log("Books data unavailable", book.title);
      }
    });

    // Add a marker clusterer to manage the markers
    new MarkerClusterer({
      markers: markers,
      map: map
    });

  }
}



async function initMap() {

  const { Map, InfoWindow } = await google.maps.importLibrary("maps");
  const { AdvancedMarkerElement, PinElement } = await google.maps.importLibrary(
    "marker",
  );



  const london = { lat: 51.5074, lng: -0.1278 };


  map = new Map(document.getElementById("map"), {
    zoom: 4,
    center: london,
    mapId: "DEMO_MAP_ID",
    mapTypeId: 'terrain',          // Show terrain view
  });


  // Initialize the geocoder
  geocoder = new google.maps.Geocoder();

  // Populate zoom level dropdown
  populateZoomDropdown();

  // Map type dropdown
  document.getElementById('mapTypeSelect').addEventListener('change', (event) => {
    const selectedMapType = event.target.value;
    map.setMapTypeId(selectedMapType);
  });

  // Listen for changes in the location dropdown
  document.getElementById('locationSelect').addEventListener('change', (event) => {
    const selectedLocation = event.target.value;

    // If a valid location is selected, center the map
    if (locations[selectedLocation]) {
      map.setCenter(locations[selectedLocation]);
      map.setZoom(5); // Adjust zoom level as needed
    }
  });

  // Search button event listener for the search box
  document.getElementById('searchButton').addEventListener('click', () => {
    const location = document.getElementById('locationInput').value;
    if (location) {
      geocodeAddress(location);
    }
  });

  // Add event listener for zoom level dropdown
  document.getElementById('zoomSelect').addEventListener('change', (event) => {
    const zoomLevel = parseInt(event.target.value, 10);
    map.setZoom(zoomLevel);
  });

  renderBooksOnMap(); // This function will render books on the map once they're ready
}





// Listen for the custom event 'booksReady'
window.addEventListener('booksReady', () => {
  if (window.books && window.books.length > 0) {
    initMap();
  } else {
    console.log("No books found in window.books.");
  }
});


// window.initMap = initMap; // Expose the function to global scope for the Google Maps API callback

