// public/scripts/map.js

let map;
let geocoder;


// Predefined locations (latitude, longitude)
const locations = {
  new_york: { lat: 40.7128, lng: -74.0060 },
  london: { lat: 51.5074, lng: -0.1278 },
  tokyo: { lat: 35.6762, lng: 139.6503 },
  sydney: { lat: -33.8688, lng: 151.2093 }
};






async function initMap() {
  // map = new google.maps.Map(document.getElementById("map"), {
  //     center: { lat: 20.5937, lng: 78.9629 }, // Centered on India
  //     zoom: 5,
  // });

  map = new google.maps.Map(document.getElementById("map"), {
    zoom: 4,                      // Zoom level
    center: { lat: 51.5074, lng: -0.1278 },  // Centered on London
    mapTypeId: 'terrain',          // Show terrain view
  });

  // Initialize the geocoder
  geocoder = new google.maps.Geocoder();

  // Populate zoom level dropdown
  populateZoomDropdown();

  // Function to get the appropriate icon based on book type
  function getIcon(booktype) {
    switch (booktype) {
      case 'Fiction':
        return 'images/icons/red_book.png';
      case 'Non-Fiction':
        return 'images/icons/blue_book.png';
      case 'Travel Book':
        return 'images/icons/brown_book.png';
      case 'Science Fiction':
        return 'images/icons/purple_book.png';
      default:
        return 'images/icons/default.png'; // Fallback icon
    }
  }


  // Access locations from the global window object
  const bookLocations = window.bookLocations;

  // Add markers with info windows
  bookLocations.forEach(location => {
    const marker = new google.maps.Marker({
      position: { lat: location.lat, lng: location.lng },
      map: map,
      title: location.title,
      icon: {
        url: getIcon(location.booktype), // Path to your icon
        scaledSize: new google.maps.Size(32, 32) // Adjust size here
      }
    });

    const infoWindowContent = `
    <div style="width: 200px;">
      <h3>${location.title}</h3>
      <p><strong>Author:</strong> ${location.author}</p>
      <p>${location.description}</p>
      ${location.image ? `<img src="${location.image}" alt="${location.title}" style="width: 100%;">` : ''}
    </div>
  `;

    const infoWindow = new google.maps.InfoWindow({
      content: infoWindowContent
    });

    marker.addListener('click', () => {
      infoWindow.open(map, marker);
    });
  });

  // Other event listeners ---------------------------------
  // Add event listener for map type dropdown
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


window.initMap = initMap; // Expose the function to global scope for the Google Maps API callback
