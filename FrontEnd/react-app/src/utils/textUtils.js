import { marked } from 'marked';
import DOMPurify from 'dompurify';

/**
 * Shortens the provided text to the specified length and appends ellipsis if necessary.
 *
 * @param {string} text - The text to shorten.
 * @param {number} maxLength - The maximum allowed length of the text.
 * @returns {string} - The shortened text with ellipsis if it exceeds maxLength.
 */
export const shortenText = (text, maxLength = 160) => {
  return text.length > maxLength ? `${text.slice(0, maxLength)}...` : text;
};

/**
 * Sanitizes and converts Markdown text to HTML.
 *
 * @param {string} text - The Markdown text to sanitize and convert.
 * @returns {string} - The sanitized HTML string.
 */
export const markedFull = (text) => {
  return DOMPurify.sanitize(marked(text));
};

/**
   * Shortens text and applies Markdown formatting.
   * 
   * @param {string} text - The text to shorten and format.
   * @returns {string} - The sanitized HTML string.
   */
export const shortenAndMarkupText = (text, maxLength = 160) => {
  const shortenedText = text.length > maxLength ? text.slice(0, maxLength) + '...' : text;
  const markedShortened = marked(shortenedText);
  return DOMPurify.sanitize(markedShortened);
};
