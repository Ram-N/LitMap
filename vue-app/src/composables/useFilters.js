import { ref, computed } from 'vue'
import { useBooksStore } from '@/stores/books'

/**
 * Normalize booktype strings to canonical categories.
 */
const BOOKTYPE_MAP = {
  'fiction': 'Fiction',
  'literary fiction': 'Fiction',
  'historical fiction': 'Fiction',
  'crime/mystery': 'Fiction',
  'mystery/thriller': 'Fiction',
  'nonfiction': 'Nonfiction',
  'non-fiction': 'Nonfiction',
  'memoir': 'Nonfiction',
  'nature writing': 'Nonfiction',
  'poetry': 'Poetry',
  'travel essays': 'Travel',
  'travel history': 'Travel',
  'travel literature': 'Travel',
  'travel memoir': 'Travel',
  'travel/history': 'Travel',
}

function normalizeBooktype(raw) {
  if (!raw) return 'Other'
  return BOOKTYPE_MAP[raw.toLowerCase()] || raw
}

/**
 * Map countries to broad regions.
 */
const REGION_MAP = {
  'Africa': [
    'Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cameroon',
    'Cape Verde', 'Central African Republic', 'Chad', 'Comoros', 'Congo', 'Democratic Republic of the Congo',
    'Djibouti', 'Egypt', 'Equatorial Guinea', 'Eritrea', 'Eswatini', 'Ethiopia', 'Gabon',
    'Gambia', 'Ghana', 'Guinea', 'Guinea-Bissau', 'Ivory Coast', 'Kenya', 'Lesotho',
    'Liberia', 'Libya', 'Madagascar', 'Malawi', 'Mali', 'Mauritania', 'Mauritius',
    'Morocco', 'Mozambique', 'Namibia', 'Niger', 'Nigeria', 'Rwanda', 'São Tomé and Príncipe',
    'Senegal', 'Seychelles', 'Sierra Leone', 'Somalia', 'South Africa', 'South Sudan',
    'Sudan', 'Tanzania', 'Togo', 'Tunisia', 'Uganda', 'Zambia', 'Zimbabwe',
  ],
  'Asia': [
    'Afghanistan', 'Armenia', 'Azerbaijan', 'Bahrain', 'Bangladesh', 'Bhutan', 'Brunei',
    'Cambodia', 'China', 'Cyprus', 'Georgia', 'India', 'Indonesia', 'Iran', 'Iraq',
    'Israel', 'Japan', 'Jordan', 'Kazakhstan', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Lebanon',
    'Malaysia', 'Maldives', 'Mongolia', 'Myanmar', 'Nepal', 'North Korea', 'Oman',
    'Pakistan', 'Palestine', 'Philippines', 'Qatar', 'Saudi Arabia', 'Singapore',
    'South Korea', 'Sri Lanka', 'Syria', 'Taiwan', 'Tajikistan', 'Thailand', 'Timor-Leste',
    'Turkey', 'Turkmenistan', 'United Arab Emirates', 'Uzbekistan', 'Vietnam', 'Yemen',
  ],
  'Europe': [
    'Albania', 'Andorra', 'Austria', 'Belarus', 'Belgium', 'Bosnia and Herzegovina',
    'Bulgaria', 'Croatia', 'Czech Republic', 'Czechia', 'Denmark', 'Estonia', 'Finland',
    'France', 'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy', 'Kosovo',
    'Latvia', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Malta', 'Moldova', 'Monaco',
    'Montenegro', 'Netherlands', 'North Macedonia', 'Norway', 'Poland', 'Portugal',
    'Romania', 'Russia', 'San Marino', 'Serbia', 'Slovakia', 'Slovenia', 'Spain',
    'Sweden', 'Switzerland', 'Ukraine', 'United Kingdom', 'Vatican City', 'England',
    'Scotland', 'Wales',
  ],
  'Americas': [
    'Antigua and Barbuda', 'Argentina', 'Bahamas', 'Barbados', 'Belize', 'Bolivia',
    'Brazil', 'Canada', 'Chile', 'Colombia', 'Costa Rica', 'Cuba', 'Dominica',
    'Dominican Republic', 'Ecuador', 'El Salvador', 'Grenada', 'Guatemala', 'Guyana',
    'Haiti', 'Honduras', 'Jamaica', 'Mexico', 'Nicaragua', 'Panama', 'Paraguay',
    'Peru', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Vincent and the Grenadines',
    'Suriname', 'Trinidad and Tobago', 'United States', 'Uruguay', 'Venezuela', 'USA',
  ],
  'Oceania': [
    'Australia', 'Fiji', 'Kiribati', 'Marshall Islands', 'Micronesia', 'Nauru',
    'New Zealand', 'Palau', 'Papua New Guinea', 'Samoa', 'Solomon Islands', 'Tonga',
    'Tuvalu', 'Vanuatu',
  ],
}

// Build reverse lookup: country → region
const countryToRegion = {}
for (const [region, countries] of Object.entries(REGION_MAP)) {
  for (const c of countries) {
    countryToRegion[c] = region
    countryToRegion[c.toLowerCase()] = region
  }
}

function getBookRegions(book) {
  const regions = new Set()
  for (const loc of book.locations || []) {
    const region = countryToRegion[loc.country] || countryToRegion[loc.country?.toLowerCase()]
    if (region) regions.add(region)
  }
  return regions
}

export function useFilters() {
  const booksStore = useBooksStore()

  // Filter state
  const selectedTypes = ref([])
  const selectedRegion = ref(null)
  const selectedGenres = ref([])

  // Available booktypes (normalized, sorted by count)
  const availableTypes = computed(() => {
    const counts = {}
    for (const book of booksStore.allBooks) {
      const type = normalizeBooktype(book.booktype)
      counts[type] = (counts[type] || 0) + 1
    }
    return Object.entries(counts)
      .sort(([, a], [, b]) => b - a)
      .map(([type, count]) => ({ label: type, count }))
  })

  const availableRegions = ['Africa', 'Americas', 'Asia', 'Europe', 'Oceania']

  // Top genres extracted from the dataset (flattened, deduplicated, top 12)
  const availableGenres = computed(() => {
    const counts = {}
    for (const book of booksStore.allBooks) {
      const genres = extractGenres(book)
      for (const g of genres) {
        counts[g] = (counts[g] || 0) + 1
      }
    }
    return Object.entries(counts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 12)
      .map(([genre, count]) => ({ label: genre, count }))
  })

  // Filtered books
  const filteredBooks = computed(() => {
    let books = booksStore.allBooks

    if (selectedTypes.value.length > 0) {
      books = books.filter(b =>
        selectedTypes.value.includes(normalizeBooktype(b.booktype))
      )
    }

    if (selectedRegion.value) {
      books = books.filter(b => getBookRegions(b).has(selectedRegion.value))
    }

    if (selectedGenres.value.length > 0) {
      books = books.filter(b => {
        const bookGenres = extractGenres(b)
        return selectedGenres.value.some(g => bookGenres.includes(g))
      })
    }

    return books
  })

  const hasActiveFilters = computed(() =>
    selectedTypes.value.length > 0 ||
    selectedRegion.value !== null ||
    selectedGenres.value.length > 0
  )

  function toggleType(type) {
    const idx = selectedTypes.value.indexOf(type)
    if (idx >= 0) {
      selectedTypes.value.splice(idx, 1)
    } else {
      selectedTypes.value.push(type)
    }
  }

  function setRegion(region) {
    selectedRegion.value = selectedRegion.value === region ? null : region
  }

  function toggleGenre(genre) {
    const idx = selectedGenres.value.indexOf(genre)
    if (idx >= 0) {
      selectedGenres.value.splice(idx, 1)
    } else {
      selectedGenres.value.push(genre)
    }
  }

  function clearAll() {
    selectedTypes.value = []
    selectedRegion.value = null
    selectedGenres.value = []
  }

  return {
    selectedTypes,
    selectedRegion,
    selectedGenres,
    availableTypes,
    availableRegions,
    availableGenres,
    filteredBooks,
    hasActiveFilters,
    toggleType,
    setRegion,
    toggleGenre,
    clearAll,
  }
}

/**
 * Extract flat genre list from a book (handles string, CSV string, or array).
 */
function extractGenres(book) {
  const results = []

  if (book.genre) {
    if (Array.isArray(book.genre)) {
      results.push(...book.genre)
    } else if (typeof book.genre === 'string') {
      results.push(...book.genre.split(',').map(s => s.trim()).filter(Boolean))
    }
  }

  return results.map(g => g.trim()).filter(Boolean)
}
