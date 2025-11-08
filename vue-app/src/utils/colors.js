/**
 * Generate a consistent color for a book based on its properties
 * Matches the original map.js generateBookColor function
 */
export function generateBookColor(book) {
  // Combine relevant book properties into a single string
  const bookString = `${book.title}|${book.author}|${book.booktype || ''}`

  // Generate a hash from the string
  let hash = 0
  for (let i = 0; i < bookString.length; i++) {
    const char = bookString.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash // Convert to 32-bit integer
  }

  // Convert the hash to a hex color
  const color = Math.abs(hash).toString(16).substring(0, 6)

  // Ensure the color is 6 digits long
  return '#' + ('000000' + color).slice(-6)
}

/**
 * Get title initials for marker display
 * Matches the original map.js getTitleInitials function
 */
export function getTitleInitials(title) {
  // Handle titles shorter than 4 characters
  if (title.length < 4) {
    return title
  }

  // Remove everything after colon, if present
  const titleBeforeColon = title.split(':')[0]

  // Words to ignore, excluding 'on' and 'of'
  const wordsToIgnore = ['the', 'and', 'a', 'an', 'in', 'at', 'to', 'for', 'with']

  const words = titleBeforeColon.toLowerCase().split(' ')

  const initials = words
    .filter(word => !wordsToIgnore.includes(word))
    .map(word => {
      // For 'on' and 'of', return the whole word
      if (word === 'on' || word === 'of') {
        return word.toLowerCase()
      }
      // If the word is a number, return the entire number
      if (!isNaN(word)) {
        return word
      }
      // For other words, return the first character uppercase
      return word[0].toUpperCase()
    })
    .join('')

  return initials
}
