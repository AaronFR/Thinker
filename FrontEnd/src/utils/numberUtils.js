


/**
 * Converts a price value into a formatted string for display.
 *
 * @param {number} price - The price value to format.
 * @returns {string} The formatted price string.
 */
export function formatPrice(price) {
  const scale = 100
  if (price < 0.0001) {
    // In the event the price is less than one percent of a cent
    console.log(price)
    const scale = 1000
    const cents = Math.round(price * 100 * scale) / scale
      return `¢ ${cents}`;
  }
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

/**
 * Converts a number of bytes into a more readable number of kilobyes / megabytes
 * 
 * @param {number} size - the number of bytes
 * @returns The size of the file in kilobytes or mb
 */
export function formatBytes(size) {
  const kiloByte = 1024;

  const kiloBytes = size / kiloByte

  if (kiloBytes > kiloByte) {
    return `${(kiloBytes / kiloByte).toFixed(1)} mb`;
  }

  return `${kiloBytes.toFixed(1)} kb`;
}