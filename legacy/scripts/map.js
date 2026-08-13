// public/scripts/map.js
let map;
let geocoder;
let markerClusterer = null;


import { MarkerClusterer } from "https://cdn.skypack.dev/@googlemaps/markerclusterer@2.3.1";

// Predefined locations (latitude, longitude)
const presetLocations = {
  //cities
  new_york: { lat: 40.7128, lng: -74.0060 },
  london: { lat: 51.5074, lng: -0.1278 },
  tokyo: { lat: 35.6762, lng: 139.6503 },
  sydney: { lat: -33.8688, lng: 151.2093 },
  // Countries
  india: { lat: 20.5937, lng: 78.9629 },
  uk: { lat: 55.3781, lng: -3.4360 },
  usa: { lat: 37.0902, lng: -95.7129 },

  // Continents
  africa: { lat: 8.7832, lng: 34.5085 },
  south_america: { lat: -8.7832, lng: -55.4915 },

  // Regions
  sub_saharan_africa: { lat: 2.4604, lng: 21.7093 },
  middle_east: { lat: 29.2985, lng: 42.5510 },
  eastern_europe: { lat: 54.5260, lng: 25.2551 }

};

// Assuming you have a presetLocations object like this
const presetRandomLocations = {
  'New York': { lat: 40.7128, lng: -74.0060 },
  'London': { lat: 51.5074, lng: -0.1278 },
  'Tokyo': { lat: 35.6762, lng: 139.6503 },
  'Sydney': { lat: -33.8688, lng: 151.2093 },
  'Rio de Janeiro': { lat: -22.9068, lng: -43.1729 },
  'Cairo': { lat: 30.0444, lng: 31.2357 },
  'Moscow': { lat: 55.7558, lng: 37.6173 },
  'Paris': { lat: 48.8566, lng: 2.3522 },
  'Dubai': { lat: 25.2048, lng: 55.2708 },
  'Toronto': { lat: 43.6532, lng: -79.3832 },
  'Mexico City': { lat: 19.4326, lng: -99.1332 },
  'Beijing': { lat: 39.9042, lng: 116.4074 },
  'Mumbai': { lat: 19.0760, lng: 72.8777 },
  'Johannesburg': { lat: -26.2041, lng: 28.0473 },
  'Berlin': { lat: 52.5200, lng: 13.4050 },
  'Rome': { lat: 41.9028, lng: 12.4964 },
  'Bangkok': { lat: 13.7563, lng: 100.5018 },
  'Buenos Aires': { lat: -34.6037, lng: -58.3816 },
  'Los Angeles': { lat: 34.0522, lng: -118.2437 },
  'Seoul': { lat: 37.5665, lng: 126.9780 },
  'Istanbul': { lat: 41.0082, lng: 28.9784 },
  'Singapore': { lat: 1.3521, lng: 103.8198 },
  'Madrid': { lat: 40.4168, lng: -3.7038 },
  'Lagos': { lat: 6.5244, lng: 3.3792 },
  'Chicago': { lat: 41.8781, lng: -87.6298 },
  'Lima': { lat: -12.0464, lng: -77.0428 },
  'Jakarta': { lat: -6.2088, lng: 106.8456 },
  'Nairobi': { lat: -1.2921, lng: 36.8219 },
  'Hong Kong': { lat: 22.3193, lng: 114.1694 },
  'Athens': { lat: 37.9838, lng: 23.7275 }
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




function getZoomLevelForLocationType(types) {
  if (types.includes('continent')) return 3;
  if (types.includes('country')) return 5;
  if (types.includes('administrative_area_level_1')) return 7;
  if (types.includes('administrative_area_level_2')) return 9;
  if (types.includes('locality') || types.includes('postal_town')) return 11;
  if (types.includes('neighborhood') || types.includes('sublocality')) return 13;
  if (types.includes('route')) return 15;
  return 10; // default zoom level
}

// Function to geocode a location and center the map
function geocodeAddress(location) {
  geocoder.geocode({ address: location }, (results, status) => {
    if (status === "OK") {
      const result = results[0];
      const resultLocation = result.geometry.location;

      // Ensure the resultLocation exists and is valid before setting it on the map
      if (resultLocation) {
        map.setCenter(resultLocation);

        // Get the appropriate zoom level based on the result type
        const zoomLevel = getZoomLevelForLocationType(result.types);
        map.setZoom(zoomLevel);
        document.getElementById('zoomValue').textContent = zoomLevel;


        console.log(`Location: ${location}, Type: ${result.types[0]}, Zoom: ${zoomLevel}`);
      } else {
        alert("No valid location found.");
      }
    } else {
      alert("Geocode was not successful for the following reason: " + status);
    }
  });
}


//Utility function - thanks to Claude
function getTitleInitials(title) {
  // Handle titles shorter than 4 characters
  if (title.length < 4) {
    return title;
  }

  // Remove everything after colon, if present
  const titleBeforeColon = title.split(':')[0];

  // Words to ignore, excluding 'on' and 'of'
  const wordsToIgnore = ['the', 'and', 'a', 'an', 'in', 'at', 'to', 'for', 'with'];

  const words = titleBeforeColon.toLowerCase().split(' ');

  const initials = words
    .filter(word => !wordsToIgnore.includes(word))
    .map(word => {
      // For 'on' and 'of', return the whole word
      if (word === 'on' || word === 'of') {
        return word.toLowerCase();
      }
      // If the word is a number, return the entire number
      if (!isNaN(word)) {
        return word;
      }
      // For other words, return the first character uppercase
      return word[0].toUpperCase();
    })
    .join('');

  return initials;
}

// Keep track of the currently highlighted marker
let currentlyHighlightedMarker = null;

export function openHighlight(markerView, book) {
  // First, remove any existing event listeners to prevent duplicates
  const existingHandler = markerView.content._clickHandler;
  if (existingHandler) {
    markerView.content.removeEventListener('click', existingHandler);
  }

  // Create the click handler function
  const clickHandler = (e) => {
    if (markerView.content.classList.contains('highlight') &&
      !e.target.classList.contains('close-button') &&
      (e.target.classList.contains('image') || e.target.tagName.toLowerCase() === 'img')) {
      const goodreadsUrl = `https://www.goodreads.com/book/isbn/${book.isbn}`;
      window.open(goodreadsUrl, '_blank');
      console.log('opening', book.title);
    }
  };

  // Store the handler reference so we can remove it later
  markerView.content._clickHandler = clickHandler;

  // Add the close button dynamically when highlighting
  const closeButton = document.createElement('div');
  closeButton.className = 'close-button';
  closeButton.textContent = 'Close';
  markerView.content.insertBefore(closeButton, markerView.content.firstChild);

  markerView.content.classList.add("highlight");
  markerView.zIndex = 1;

  // Update the currently highlighted marker
  currentlyHighlightedMarker = markerView;

  // Add click handler for close button
  closeButton.addEventListener('click', (e) => {
    e.stopPropagation();
    closeHighlight(markerView);
  });

  // Add the new click handler
  markerView.content.addEventListener('click', clickHandler);
}

// Also modify closeHighlight to clean up the event listener
export function closeHighlight(markerView) {
  // Remove the click handler if it exists
  const existingHandler = markerView.content._clickHandler;
  if (existingHandler) {
    markerView.content.removeEventListener('click', existingHandler);
    markerView.content._clickHandler = null;
  }

  // Remove the close button when un-highlighting
  const closeButton = markerView.content.querySelector('.close-button');
  if (closeButton) {
    closeButton.remove();
  }

  markerView.content.classList.remove("highlight");
  markerView.zIndex = null;

  // Clear the reference if this was the currently highlighted marker
  if (currentlyHighlightedMarker === markerView) {
    currentlyHighlightedMarker = null;
  }
}

export function buildContent(book, location) {
  const content = document.createElement("div");
  content.classList.add("bookCard");
  content.style.backgroundColor = generateBookColor(book);

  // If a location has a desc, use it. If not, use book's
  const descriptionToShow = location.description || book.description;
  // Generate the cover image HTML
  const coverHTML = book.isbn
    ? `<img src="https://covers.openlibrary.org/b/isbn/${book.isbn}-M.jpg"
      alt="Cover of ${book.title}"
      class="image"
      onerror="this.innerHTML='Book Cover'; this.className='image';">`
    : `<div class="image">Book Cover</div>`;

  content.innerHTML = `
  ${getTitleInitials(book.title)}
  <div class='book-info'>
      <div class="left-column">
        ${coverHTML}
        <div class="location-label">${location.city}</div>
      </div>
      <div class="content">
        <div class = 'top-content'>
            <div class = 'title'>
              ${book.title}
            </div>
            <div class = 'author'>
              ${book.author}
            </div>
        </div>
        <div class="description">
            <div class="bk-desc">
            ${descriptionToShow}
            </div>
        </div>
        <div class = 'location'>
        ${book.booktype}
        </div>
      </div>
    </div>
  </div>
    `;
  return content;
}

//Rendering ALL books on the Explore Map
// Store markers globally so they can be accessed by clustering functions
let allMarkers = [];

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
          const lng = location.lng || location.longitude;

          // Check if lat and lng are defined
          if (lat && lng) {
            // Create the position using the latitude and longitude
            const position = new google.maps.LatLng(lat, lng);

            // Create the AdvancedMarkerElement for each location
            const marker = new google.maps.marker.AdvancedMarkerElement({
              position: position,
              map: map,  // Assuming 'map' is your Google map instance
              title: `${book.title} by ${book.author}`,  // Title displayed on hover
              // content: pin.element,  // Attach the PinElement
              content: buildContent(book, location),
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

            // In your map setup where you create markers:
            marker.addListener("click", () => {
              // If this marker isn't already highlighted
              if (!marker.content.classList.contains("highlight")) {
                // If there's a currently highlighted marker, close it
                if (currentlyHighlightedMarker) {
                  closeHighlight(currentlyHighlightedMarker);
                }
                // Open this marker and update the currently highlighted marker
                openHighlight(marker, book);
                currentlyHighlightedMarker = marker;
              }
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


    const smoothZoom = (map, targetZoom, currentZoom) => {
      if (currentZoom >= targetZoom) {
        return;
      }
      const nextZoom = Math.min(currentZoom + 1, targetZoom);
      google.maps.event.addListenerOnce(map, 'zoom_changed', () => {
        smoothZoom(map, targetZoom, nextZoom);
      });
      setTimeout(() => {
        map.setZoom(nextZoom);
      }, 150);
    };

    // Store markers in global variable for clustering functions
    allMarkers = markers;

    const clusterToggle = document.getElementById('clusterToggle');

    function toggleClustering() {
      console.log('toggleClustering called, checked:', clusterToggle.checked);
      console.log('allMarkers array length:', allMarkers.length);
      if (clusterToggle.checked) {
        enableClustering(allMarkers);
      } else {
        disableClustering();
      }
    }

    function enableClustering(markers) {
      console.log('enableClustering called with markers:', markers.length);
      markerClusterer = new MarkerClusterer({
        map: map,
        markers: markers,
        zoomOnClick: false,
        gridSize: 50,
        maxZoom: 15,
      });
      console.log('Clustering enabled, markerClusterer:', markerClusterer);
    }

    function disableClustering() {
      console.log('disableClustering called');
      console.log('markerClusterer exists?', !!markerClusterer);
      console.log('allMarkers length:', allMarkers.length);
      console.log('map object:', map);

      if (markerClusterer) {
        markerClusterer.clearMarkers();
        console.log('Cleared markers from clusterer');
        markerClusterer = null;
      }
      // Re-add all markers to the map individually
      allMarkers.forEach((marker, index) => {
        console.log(`Setting marker ${index} on map:`, marker);
        marker.setMap(map);
        console.log(`Marker ${index} map after setMap:`, marker.map);
      });
      console.log('All markers should now be on the map');
    }
    // Initial clustering state
    toggleClustering();

    // Add event listener for the toggle
    clusterToggle.addEventListener('change', toggleClustering);


    google.maps.event.addListener(markerClusterer, 'clusterclick', function (cluster) {
      var bounds = cluster.getBounds();
      google.maps.event.addListenerOnce(map, 'zoom_changed', function () {
        if (map.getZoom() > 10)
          map.setZoom(10);
        console.log('Max zoom reached');
      });
      map.fitBounds(bounds);
    });

  }
}


async function initMap() {

  const { Map, InfoWindow } = await google.maps.importLibrary("maps");
  const { AdvancedMarkerElement, PinElement } = await google.maps.importLibrary(
    "marker",
  );

  const london = { lat: 51.5074, lng: -0.1278 };
  const india = { lat: 20.5074, lng: 65.1278 };


  map = new Map(document.getElementById("map"), {
    zoom: 4,
    center: india,
    mapId: "9846f743a351d898",
    mapTypeId: 'terrain',          // Show terrain view

  });

  // Initialize zoom level
  let currentZoom = 4;
  const minZoom = 2;
  const maxZoom = 17;


  // Initialize the geocoder
  geocoder = new google.maps.Geocoder();


  // Map type dropdown
  document.getElementById('mapTypeSelect').addEventListener('change', (event) => {
    const selectedMapType = event.target.value;
    map.setMapTypeId(selectedMapType);
  });

  // Listen for changes in the location dropdown
  document.getElementById('locationSelect').addEventListener('change', function () {
    const selectedOption = this.options[this.selectedIndex];
    const zoomLevelAttr = selectedOption.getAttribute('data-zoom');
    const locationName = selectedOption.value;

    // Parse zoom level and ensure it's a valid number
    let zoomLevel = parseInt(zoomLevelAttr, 10);
    if (isNaN(zoomLevel)) {
      console.error(`Invalid zoom level: ${zoomLevelAttr} for location: ${locationValue}`);
      zoomLevel = 10; // Set a default zoom level
    }

    console.log(`Selected location: ${locationName}, Zoom level: ${zoomLevel}`);

    // Update the zoom control
    // If a valid location is selected, center the map
    if (presetLocations[locationName]) {
      const { lat, lng } = presetLocations[locationName];
      console.log(`Setting view to: lat ${lat}, lng ${lng}, zoom ${zoomLevel}`);

      // Update map view
      try {
        document.getElementById('zoomValue').textContent = zoomLevel;
        map.setCenter(presetLocations[locationName]);
        map.setZoom(zoomLevel); // Adjust zoom level of map
      } catch (error) {
        console.error('Error setting map view:', error);
      }
    } else {
      console.error(`Coordinates not found for location: ${locationName}`);
    }


  });

  //Manually entering Location
  document.getElementById('locationInput').addEventListener('keypress', function (event) {
    if (event.key === 'Enter') {
      event.preventDefault(); // Prevent form submission if it's within a form
      const location = this.value.trim();
      if (location) {
        geocodeAddress(location);
      }
    }
  });


  // Function to update zoom
  function updateZoom(newZoom) {
    currentZoom = Math.max(minZoom, Math.min(maxZoom, newZoom));
    document.getElementById('zoomValue').textContent = currentZoom;

    // Update map zoom
    map.setZoom(currentZoom);
  }

  // Zoom out button
  document.getElementById('zoomOutButton').addEventListener('click', function () {
    currentZoom = document.getElementById('zoomValue').textContent;
    currentZoom = parseInt(currentZoom);
    updateZoom(currentZoom - 1);
  });

  // Zoom in button
  document.getElementById('zoomInButton').addEventListener('click', function () {
    currentZoom = document.getElementById('zoomValue').textContent;
    currentZoom = parseInt(currentZoom);
    console.log('current zoom ', currentZoom);
    updateZoom(currentZoom + 1);
  });

  // Add event listener to the random location button
  document.getElementById('random-btn').addEventListener('click', function () {
    // Get an array of location names
    const locationNames = Object.keys(presetRandomLocations);

    // Select a random location
    const randomLocationName = locationNames[Math.floor(Math.random() * locationNames.length)];
    const randomLocation = presetRandomLocations[randomLocationName];

    // Generate a random zoom level (adjust range as needed)
    const minZ = 5;
    const maxZ = 9;
    const randomZoomLevel = Math.floor(Math.random() * (maxZ - minZ + 1)) + minZ; // Random zoom between 5 and 10

    try {
      // Update zoom display
      document.getElementById('zoomValue').textContent = randomZoomLevel;

      // Center map on random location
      map.setCenter(randomLocation);

      // Set random zoom level
      map.setZoom(randomZoomLevel);

      // Optional: Update any location display if you have one
      console.log(`Random location: ${randomLocationName}, Zoom level: ${randomZoomLevel}`);
    } catch (error) {
      console.error('Error setting random map view:', error);
    }
  });



  renderBooksOnMap(); // This function will render books on the map once they're ready
  updateZoom(currentZoom);
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
// window.buildContent = buildContent;