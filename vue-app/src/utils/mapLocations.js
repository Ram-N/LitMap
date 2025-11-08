// Preset locations for dropdown (matches original map.js)
export const presetLocations = {
  // Cities
  new_york: { lat: 40.7128, lng: -74.0060, zoom: 11 },
  london: { lat: 51.5074, lng: -0.1278, zoom: 11 },
  tokyo: { lat: 35.6762, lng: 139.6503, zoom: 11 },
  sydney: { lat: -33.8688, lng: 151.2093, zoom: 11 },
  paris: { lat: 48.8566, lng: 2.3522, zoom: 11 },
  dubai: { lat: 25.2048, lng: 55.2708, zoom: 11 },
  toronto: { lat: 43.6532, lng: -79.3832, zoom: 11 },
  mexico_city: { lat: 19.4326, lng: -99.1332, zoom: 11 },
  beijing: { lat: 39.9042, lng: 116.4074, zoom: 11 },
  mumbai: { lat: 19.0760, lng: 72.8777, zoom: 11 },

  // Countries
  india: { lat: 20.5937, lng: 78.9629, zoom: 5 },
  uk: { lat: 55.3781, lng: -3.4360, zoom: 6 },
  usa: { lat: 37.0902, lng: -95.7129, zoom: 4 },

  // Continents
  africa: { lat: 8.7832, lng: 34.5085, zoom: 3 },
  south_america: { lat: -8.7832, lng: -55.4915, zoom: 3 },

  // Regions
  sub_saharan_africa: { lat: 2.4604, lng: 21.7093, zoom: 5 },
  middle_east: { lat: 29.2985, lng: 42.5510, zoom: 5 },
  eastern_europe: { lat: 54.5260, lng: 25.2551, zoom: 5 },
}

// Random locations for "Random Location" feature
export const randomLocations = [
  { name: 'New York', lat: 40.7128, lng: -74.0060 },
  { name: 'London', lat: 51.5074, lng: -0.1278 },
  { name: 'Tokyo', lat: 35.6762, lng: 139.6503 },
  { name: 'Sydney', lat: -33.8688, lng: 151.2093 },
  { name: 'Rio de Janeiro', lat: -22.9068, lng: -43.1729 },
  { name: 'Cairo', lat: 30.0444, lng: 31.2357 },
  { name: 'Moscow', lat: 55.7558, lng: 37.6173 },
  { name: 'Paris', lat: 48.8566, lng: 2.3522 },
  { name: 'Dubai', lat: 25.2048, lng: 55.2708 },
  { name: 'Toronto', lat: 43.6532, lng: -79.3832 },
  { name: 'Mexico City', lat: 19.4326, lng: -99.1332 },
  { name: 'Beijing', lat: 39.9042, lng: 116.4074 },
  { name: 'Mumbai', lat: 19.0760, lng: 72.8777 },
  { name: 'Johannesburg', lat: -26.2041, lng: 28.0473 },
  { name: 'Berlin', lat: 52.5200, lng: 13.4050 },
  { name: 'Rome', lat: 41.9028, lng: 12.4964 },
  { name: 'Bangkok', lat: 13.7563, lng: 100.5018 },
  { name: 'Buenos Aires', lat: -34.6037, lng: -58.3816 },
  { name: 'Los Angeles', lat: 34.0522, lng: -118.2437 },
  { name: 'Seoul', lat: 37.5665, lng: 126.9780 },
  { name: 'Istanbul', lat: 41.0082, lng: 28.9784 },
  { name: 'Singapore', lat: 1.3521, lng: 103.8198 },
  { name: 'Madrid', lat: 40.4168, lng: -3.7038 },
  { name: 'Lagos', lat: 6.5244, lng: 3.3792 },
  { name: 'Chicago', lat: 41.8781, lng: -87.6298 },
  { name: 'Lima', lat: -12.0464, lng: -77.0428 },
  { name: 'Jakarta', lat: -6.2088, lng: 106.8456 },
  { name: 'Nairobi', lat: -1.2921, lng: 36.8219 },
  { name: 'Hong Kong', lat: 22.3193, lng: 114.1694 },
  { name: 'Athens', lat: 37.9838, lng: 23.7275 },
]

// Dropdown options with labels
export const locationOptions = [
  { value: '', label: 'Select Location' },
  { value: 'new_york', label: 'New York' },
  { value: 'london', label: 'London' },
  { value: 'tokyo', label: 'Tokyo' },
  { value: 'sydney', label: 'Sydney' },
  { value: 'paris', label: 'Paris' },
  { value: 'dubai', label: 'Dubai' },
  { value: 'toronto', label: 'Toronto' },
  { value: 'mexico_city', label: 'Mexico City' },
  { value: 'beijing', label: 'Beijing' },
  { value: 'mumbai', label: 'Mumbai' },
  { value: 'india', label: 'India' },
  { value: 'uk', label: 'United Kingdom' },
  { value: 'usa', label: 'United States' },
  { value: 'africa', label: 'Africa' },
  { value: 'south_america', label: 'South America' },
  { value: 'sub_saharan_africa', label: 'Sub-Saharan Africa' },
  { value: 'middle_east', label: 'Middle East' },
  { value: 'eastern_europe', label: 'Eastern Europe' },
]

/**
 * Get a random location from the randomLocations array
 */
export function getRandomLocation() {
  const randomIndex = Math.floor(Math.random() * randomLocations.length)
  return randomLocations[randomIndex]
}
