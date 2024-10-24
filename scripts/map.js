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
      // For other words, return the first character
      return word[0];
    })
    .join('')
    .toUpperCase();

  return initials;
}


function openHighlight(markerView, book) {
  // Add the close button dynamically when highlighting
  const closeButton = document.createElement('div');
  closeButton.className = 'close-button';
  closeButton.textContent = 'Close';  // or '×' if you prefer
  markerView.content.insertBefore(closeButton, markerView.content.firstChild);

  markerView.content.classList.add("highlight");
  markerView.zIndex = 1;

  // Add click handler for close button
  closeButton.addEventListener('click', (e) => {
    e.stopPropagation(); // Prevent event from bubbling up
    closeHighlight(markerView);
  });
}



function closeHighlight(markerView) {
  // Remove the close button when un-highlighting
  const closeButton = markerView.content.querySelector('.close-button');
  if (closeButton) {
    closeButton.remove();
  }

  markerView.content.classList.remove("highlight");
  markerView.zIndex = null;
}



//DEPRECATED by Open and CLoseToggle functions
function toggleHighlight(markerView, book) {
  if (markerView.content.classList.contains("highlight")) {
    markerView.content.classList.remove("highlight");
    markerView.zIndex = null;
  } else {
    markerView.content.classList.add("highlight");
    markerView.zIndex = 1;
  }
}


function buildContent(book, location) {
  const content = document.createElement("div");
  content.classList.add("bookCard");
  content.style.backgroundColor = generateBookColor(book);

  // If a location has a desc, use it. If not, use book's
  const descriptionToShow = location.description || book.description;

  content.innerHTML = `
  ${getTitleInitials(book.title)}
  <div class='book-info'>
      <div class="left-column">
        <div class="image">Book Cover</div>
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

            marker.addListener("click", () => {
              // toggleHighlight(marker, book);
              if (!marker.content.classList.contains("highlight")) {
                openHighlight(marker, book);
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

    const clusterToggle = document.getElementById('clusterToggle');

    function toggleClustering() {
      if (clusterToggle.checked) {
        enableClustering(markers);
      } else {
        disableClustering();
      }
    }

    function enableClustering(markers) {
      markerClusterer = new MarkerClusterer({
        map: map,
        markers: markers,
        zoomOnClick: false,
        gridSize: 50,
        maxZoom: 15,
      });
    }

    function disableClustering() {
      if (markerClusterer) {
        markerClusterer.clearMarkers();
        markerClusterer = null;
      }
      markers.forEach(marker => marker.setMap(map));
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
    mapId: "DEMO_MAP_ID",
    mapTypeId: 'terrain',          // Show terrain view

    // How you would like to style the map. 
    // This is where you would paste any style found on Snazzy Maps.
    // styles: [{ "featureType": "all", "elementType": "geometry.fill", "stylers": [{ "weight": "2.00" }] }, { "featureType": "all", "elementType": "geometry.stroke", "stylers": [{ "color": "#9c9c9c" }] }, { "featureType": "all", "elementType": "labels.text", "stylers": [{ "visibility": "on" }] }, { "featureType": "landscape", "elementType": "all", "stylers": [{ "color": "#f2f2f2" }] }, { "featureType": "landscape", "elementType": "geometry.fill", "stylers": [{ "color": "#ffffff" }] }, { "featureType": "landscape.man_made", "elementType": "geometry.fill", "stylers": [{ "color": "#ffffff" }] }, { "featureType": "poi", "elementType": "all", "stylers": [{ "visibility": "off" }] }, { "featureType": "road", "elementType": "all", "stylers": [{ "saturation": -100 }, { "lightness": 45 }] }, { "featureType": "road", "elementType": "geometry.fill", "stylers": [{ "color": "#eeeeee" }] }, { "featureType": "road", "elementType": "labels.text.fill", "stylers": [{ "color": "#7b7b7b" }] }, { "featureType": "road", "elementType": "labels.text.stroke", "stylers": [{ "color": "#ffffff" }] }, { "featureType": "road.highway", "elementType": "all", "stylers": [{ "visibility": "simplified" }] }, { "featureType": "road.arterial", "elementType": "labels.icon", "stylers": [{ "visibility": "off" }] }, { "featureType": "transit", "elementType": "all", "stylers": [{ "visibility": "off" }] }, { "featureType": "water", "elementType": "all", "stylers": [{ "color": "#46bcec" }, { "visibility": "on" }] }, { "featureType": "water", "elementType": "geometry.fill", "stylers": [{ "color": "#c8d7d4" }] }, { "featureType": "water", "elementType": "labels.text.fill", "stylers": [{ "color": "#070707" }] }, { "featureType": "water", "elementType": "labels.text.stroke", "stylers": [{ "color": "#ffffff" }] }]

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

