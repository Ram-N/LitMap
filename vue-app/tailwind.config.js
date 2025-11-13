/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Legacy primary colors (kept for backward compatibility)
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        // New design system colors
        teal: {
          deep: '#3D6960',  // Primary action color
        },
        copper: {
          warm: '#C17A3A',  // Accent color
        },
        parchment: {
          50: '#F5F1E8',   // Light background
          100: '#E8E3D8',  // Medium background
          200: '#E0D9C8',  // Border color
          300: '#D5CFC0',  // Darker background
        },
        text: {
          primary: '#2D3E3C',
          secondary: '#6B7C7A',
          tertiary: '#9CA5A3',
        },
        genre: {
          memoir: '#8B5A8E',
          adventure: '#C17A3A',
          historical: '#A67C52',
          travel: '#3D6960',
        },
      },
      fontFamily: {
        serif: ['Georgia', 'Libre Baskerville', 'serif'],
        sans: ['system-ui', '-apple-system', 'sans-serif'],
      },
      borderRadius: {
        xl: '16px',
        '2xl': '24px',
      },
      height: {
        'screen-90': '90vh',
        'screen-95': '95vh',
      },
      minHeight: {
        'touch': '44px', // Minimum touch target size
      },
    },
  },
  plugins: [],
}
