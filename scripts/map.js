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


// Function to get background color based on book type
function getBgColor(booktype) {
  switch (booktype) {
    case 'Fiction':
      return "#FBBC04";  // Fiction books get yellow background      
    case 'Nonfiction':
      return '#001FFE';    // Nonfiction books get blue background
    case 'Non-fiction':
      return 'blue';    // Nonfiction books get blue background
    case 'Poetry':
      return 'pink';    // Nonfiction books get blue background
    default:
      return 'gray';    // Default background color if type is unknown
  }
}

// Function to get background color based on book type
function getGlyphColor(booktype) {
  switch (booktype) {
    case 'Poetry':
      return 'pink';    // Nonfiction books get blue background
    default:
      return 'white';
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

//Utility function
function getTitleInitials(title) {
  if (title.length < 4) {
    return title;
  }

  const wordsToIgnore = ['the', 'and', 'of', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'with'];

  const words = title.toLowerCase().split(' ');

  const initials = words
    .filter(word => !wordsToIgnore.includes(word))
    .map(word => word[0].toUpperCase())
    .join('');

  return initials;
}


function toggleHighlight(markerView, book) {
  if (markerView.content.classList.contains("highlight")) {
    markerView.content.classList.remove("highlight");
    markerView.zIndex = null;
  } else {
    markerView.content.classList.add("highlight");
    markerView.zIndex = 1;
  }
}


function buildContent(book) {
  const content = document.createElement("div");

  content.classList.add("bookCard");

  content.innerHTML = `
  ${getTitleInitials(book.title)}
    <div class="details">
      <strong>${book.title}</strong><br>
      <em>${book.author}</em><br>
      <span>${book.booktype}</span>

    </div>
    `;
  return content;
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

            // Get background color based on book type
            // const bgColor = getBgColor(book.booktype);
            // const glyphColor = getGlyphColor(book.booktype);

            // Create the PinElement with dynamic background color and a scale of 0.5
            // const pin = new google.maps.marker.PinElement({
            //   scale: 0.5,
            //   background: bgColor,  // Set the background color based on book type
            //   borderColor: "#137333",
            //   glyphColor: glyphColor,
            //   glyph: "NF",
            // });


            // Create the AdvancedMarkerElement for each location
            const marker = new google.maps.marker.AdvancedMarkerElement({
              position: position,
              map: map,  // Assuming 'map' is your Google map instance
              title: `${book.title} by ${book.author}`,  // Title displayed on hover
              // content: pin.element,  // Attach the PinElement
              content: buildContent(book),
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
            // marker.addListener("click", () => {
            //   infoWindow.open({
            //     anchor: marker,
            //     map
            //   });
            // });

            marker.addListener("click", () => {
              toggleHighlight(marker, book);
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
    console.log(location);
    if (location) {
      geocodeAddress(location);
    }
  });

  document.getElementById('zoomControl').addEventListener('input', function () {
    const zoomValue = document.getElementById('zoomValue');
    zoomValue.textContent = this.value;

    // Assuming map is your Google Map instance
    map.setZoom(parseInt(this.value));
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

