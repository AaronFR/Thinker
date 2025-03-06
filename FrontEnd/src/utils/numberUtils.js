


/**
 * Converts a price value into a formatted string for display.
 *
 * @param {number} price - The price value to format.
 * @returns {string} The formatted price string.
 */
export function formatPrice(price) {
  const scale = 100
  if (price < 1) {
      const cents = Math.round(price * 100 * scale) / scale
      return `¢ ${cents}`;
  } else {
      const roundedPrice = parseFloat(price.toPrecision(4))
      return `$${roundedPrice}`;
  }
}

/**
 * Converts a time format into a convient time string for display
 *
 * @param {number} price - The time value to format.
 * @returns {string} The formatted time string.
 */
export function formatTime(number) {
  const scale = 100
  const duration = Math.round(number * scale) / scale
  return `${duration}s`;
}
