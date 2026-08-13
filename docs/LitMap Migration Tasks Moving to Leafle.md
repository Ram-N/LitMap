# LitMap Migration Tasks: Moving to Leaflet, OSM, and GeoJSON

This set of issues outlines the necessary architectural shift to convert LitMap from a Firebase/Google Maps backend to a pure Static Site Application (SSA) using Leaflet.js for mapping and GeoJSON for data storage.

1. Data Architecture: Export Firebase Data to GeoJSON Format
Goal: Migrate existing literary location data from the Firebase database structure into a single, static GeoJSON file.
Description: To achieve a Static Site Architecture (SSA) suitable for GitHub Pages, we must remove the live database dependency. This task requires exporting all data points, ensuring each point contains coordinates, title, author, book, and the category/genre (for color coding).
Acceptance Criteria (AC):
A new file named litmap-data.geojson exists in the project root or /data directory.
The file adheres strictly to the GeoJSON FeatureCollection format.
Every feature object includes a geometry (Point with [longitude, latitude]) and a properties object containing all necessary metadata (title, author, genre, etc.).

2. Core Library Switch: Replace Google Maps with Leaflet.js
Goal: Remove all Google Maps dependencies and initialize the map using Leaflet.js and OpenStreetMap tiles.
Description: Update the main application component (or base HTML/JS file) to load the Leaflet library and its associated CSS. Replace the Google Maps initialization code with a Leaflet MapContainer instance.
Technical Notes:
Import Leaflet CSS: <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
Import Leaflet JS: <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
Initialize the map, ensuring OpenStreetMap tiles are used:
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);



AC:
The page renders a visible, interactive map using OpenStreetMap tiles.
No Google Maps API keys or scripts are loaded.


3. Data Integration: Load and Render GeoJSON Markers
Goal: Read the static litmap-data.geojson file and render all locations as basic markers on the Leaflet map.
Description: Implement JavaScript (or Vue component logic) to use fetch to load the GeoJSON file. Once loaded, use Leaflet's built-in L.geoJSON() function to parse the data and add it as a layer to the map.
Technical Notes:
The L.geoJSON() method automatically converts GeoJSON points into Leaflet markers.
Implement basic bindPopup to show key information (Title, Author) when a marker is clicked.
AC:
All data points from the GeoJSON file are visible as markers on the map.
Clicking any marker displays a simple pop-up with the location title.


4. UI/UX: Implement Custom Colored Markers based on Genre
Goal: Replicate the visual categorization seen in the inspiration map by color-coding markers based on the genre property in the GeoJSON data.
Description: Instead of using the default blue Leaflet pin, create custom icons or colored circles for each major genre (e.g., Mystery, Fantasy, Poetry). This will involve writing a function to choose an icon or circle color based on the feature's properties.genre.
Technical Notes:
Use Leaflet's pointToLayer option within L.geoJSON to replace default markers with colored circles or custom SVG icons.
Define a color map: { "Mystery": "blue", "Fantasy": "green", ... }.
AC:
Map markers are visually distinct (by color) according to their associated literary genre.


5. Performance: Integrate Marker Clustering for Large Datasets
Goal: Implement the Leaflet Marker Cluster plugin to improve map performance and user experience when displaying many markers.
Description: Large datasets will quickly clutter the map. Add the Leaflet.markercluster plugin to automatically group nearby markers into a single cluster icon that dynamically expands upon zooming.
Technical Notes:
Install/include the Marker Cluster library files.
Replace the direct addition of the GeoJSON layer with adding it to a new L.markerClusterGroup().
AC:
A clear, concise cluster of markers (with a count badge) is visible when viewing a large geographical area.
The cluster expands into individual markers when the map is zoomed in.


6. Feature Reimplementation: Develop Client-Side Search Functionality
Goal: Reimplement the search feature (by Author, Title, or Genre) using client-side JavaScript filtering of the GeoJSON data.
Description: Since the data is loaded statically, search must be handled entirely in the browser. Store the GeoJSON data array in a JavaScript variable, and filter this array based on the user's input. The map view should then update to only display the filtered subset of markers.
AC:
A functional search input is present in the sidebar.
Typing in a search query instantly filters the markers on the map and/or a corresponding list view.


7. Feature Reimplementation: "I'm Feeling Curious" Button
Goal: Implement the "I'm Feeling Curious" button to zoom/pan the map to a randomly selected location.
Description: Create a button that, when clicked, selects a random feature from the loaded GeoJSON data array and uses the Leaflet map.setView() or map.panTo() methods to focus the map on that location.
AC:
A clearly labeled "I'm Feeling Curious" button is available.
Clicking the button moves the map view to a random, visible marker and opens its pop-up.


8. Refactoring: Remove All Firebase Dependencies and Logic
Goal: Cleanly remove all unused code, imports, and configuration related to Firebase.
Description: Now that data is handled by GeoJSON and the map by Leaflet, thoroughly audit the Vue/JS codebase to ensure all remnants of firebase/app, firebase/firestore, and firebase/auth imports, as well as any associated authentication or database calls, are deleted.
AC:
No Firebase SDKs are included in the project.
The application runs without errors related to missing Firebase configuration or credentials.


9. Code Cleanup: Prepare Vue Components for Static Deployment
Goal: Ensure the Vue components (if used) are initialized in a way that is compatible with static deployment and eliminate any reliance on server-side rendering patterns.
Description: For Vue or any framework version: verify that component mounting and initialization happen only after the static data load is complete. Focus on ensuring the data-fetching logic is robustly handled via fetch('litmap-data.geojson').
AC:
The application loads and initializes successfully without any initial build or runtime errors.

10. Deployment Prep: Verify GitHub Pages Configuration
Goal: Ensure the project is ready for smooth and reliable deployment on GitHub Pages.
Description: Review the repository settings. Since this is a pure SSA project, deployment should be straightforward (main branch, root directory). Create a simple README.md explaining the project, and ensure all paths (GeoJSON, Leaflet scripts, custom CSS) are relative to the project root to work correctly under the GitHub Pages subdomain structure (username.github.io/litmap/).

AC:
The repository is configured to deploy from the correct branch/folder.
The final, working code is pushed and successfully viewable at the designated GitHub Pages URL.
