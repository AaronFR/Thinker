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

/**
   * Renders the standard markedown text format with an opacity filter while the operation is being reloaded
   * If no text is present no element will be rendered
   * 
   * @param {string} markdownText - The text to shorten and format
   * @param {string} className - The given CSS class name
   * @param {function} isLoading - The function to determine if opacity should be lowered while being reloaded
   */
export const MarkdownRenderer = ({ markdownText, className = "", isLoading = false }) => (
  <>
    {markdownText ? (
      <div 
        className={className} 
        style={{ opacity: isLoading ? 0.5 : 1 }}
        dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked(markdownText || "")) }}
      />) : (
        ""
      )
    }
  </>
);

export const withLoadingOpacity = (isLoading) => ({ opacity: isLoading ? 0.5 : 1 });
