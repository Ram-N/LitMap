/**
 * Vintage/Sepia map styling for old-world aesthetic
 * Matches LitMap design system (parchment, teal, copper)
 *
 * Color palette from tailwind.config.js:
 * - Teal deep: #3D6960
 * - Copper warm: #C17A3A
 * - Parchment 50: #F5F1E8
 * - Parchment 100: #E8E3D8
 * - Parchment 200: #E0D9C8
 * - Text primary: #2D3E3C
 * - Text secondary: #6B7C7A
 */

export const vintageMapStyles = [
  // Water features - muted teal/blue-green
  {
    featureType: "water",
    elementType: "geometry",
    stylers: [{ color: "#b8d4d1" }] // Muted teal-green water
  },
  {
    featureType: "water",
    elementType: "labels.text.fill",
    stylers: [{ color: "#6B7C7A" }] // Text secondary
  },
  {
    featureType: "water",
    elementType: "labels.text.stroke",
    stylers: [{ color: "#F5F1E8" }, { weight: 2 }] // Parchment stroke
  },

  // Landscape - parchment base
  {
    featureType: "landscape",
    elementType: "geometry",
    stylers: [{ color: "#E8E3D8" }] // Parchment 100
  },
  {
    featureType: "landscape.natural",
    elementType: "geometry",
    stylers: [{ color: "#E0D9C8" }] // Parchment 200
  },

  // Roads - subtle brown/copper tones
  {
    featureType: "road",
    elementType: "geometry",
    stylers: [{ color: "#D5CFC0" }] // Parchment 300 (darker)
  },
  {
    featureType: "road",
    elementType: "geometry.stroke",
    stylers: [{ color: "#C8C0B0" }] // Even darker parchment
  },
  {
    featureType: "road.highway",
    elementType: "geometry",
    stylers: [{ color: "#D8C8B0" }] // Slightly warmer for highways
  },
  {
    featureType: "road",
    elementType: "labels.text.fill",
    stylers: [{ color: "#6B7C7A" }] // Text secondary
  },
  {
    featureType: "road",
    elementType: "labels.text.stroke",
    stylers: [{ color: "#F5F1E8" }, { weight: 2 }]
  },

  // Administrative borders - copper accent
  {
    featureType: "administrative",
    elementType: "geometry.stroke",
    stylers: [{ color: "#C17A3A" }, { weight: 0.7 }] // Copper warm
  },
  {
    featureType: "administrative.country",
    elementType: "geometry.stroke",
    stylers: [{ color: "#C17A3A" }, { weight: 1.2 }] // Thicker for countries
  },
  {
    featureType: "administrative",
    elementType: "labels.text.fill",
    stylers: [{ color: "#2D3E3C" }] // Text primary
  },

  // Parks and natural features - muted sage green
  {
    featureType: "poi.park",
    elementType: "geometry",
    stylers: [{ color: "#d4dcc9" }] // Muted sage
  },
  {
    featureType: "landscape.natural.terrain",
    stylers: [{ color: "#ddd8cc" }] // Light parchment for terrain
  },

  // Transit - minimize visibility
  {
    featureType: "transit",
    stylers: [{ visibility: "off" }]
  },

  // POIs - selective visibility
  {
    featureType: "poi.business",
    stylers: [{ visibility: "off" }] // Hide business POIs
  },
  {
    featureType: "poi.medical",
    stylers: [{ visibility: "off" }]
  },
  {
    featureType: "poi.school",
    stylers: [{ visibility: "off" }]
  },
  {
    featureType: "poi",
    elementType: "labels.text.fill",
    stylers: [{ color: "#6B7C7A" }]
  },

  // Labels - use design system colors
  {
    featureType: "all",
    elementType: "labels.text.fill",
    stylers: [{ color: "#2D3E3C" }] // Text primary
  },
  {
    featureType: "all",
    elementType: "labels.text.stroke",
    stylers: [{ color: "#F5F1E8" }, { weight: 2 }] // Parchment halo
  },

  // Reduce saturation globally for vintage feel
  {
    featureType: "all",
    stylers: [{ saturation: -20 }, { gamma: 0.85 }]
  }
]

/**
 * Alternative: Lighter sepia style (simpler option)
 * Use this if the main vintage style feels too heavy
 */
export const lightSepiaStyles = [
  {
    featureType: "all",
    stylers: [
      { saturation: -30 },
      { lightness: 10 },
      { gamma: 0.9 }
    ]
  },
  {
    featureType: "water",
    elementType: "geometry",
    stylers: [{ color: "#b8d4d1" }]
  },
  {
    featureType: "landscape",
    stylers: [{ color: "#E8E3D8" }]
  },
  {
    featureType: "road",
    stylers: [{ color: "#D5CFC0" }]
  }
]
