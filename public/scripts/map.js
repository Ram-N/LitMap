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
