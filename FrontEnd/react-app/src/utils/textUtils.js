import { marked } from 'marked';
import DOMPurify from 'dompurify';
import React, { useEffect, useRef } from 'react';
import hljs from 'highlight.js';
import he from 'he';

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

const CopyCodeButton = ({ code }) => {
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
    } catch (err) {
      console.error('Failed to copy code:', err);
    }
  };

  return (
    <>
      <button onClick={handleCopy} style={{ position: 'absolute', top: 8, right: 8 }}>
        📋
      </button>
    </>
  );
};

/**
 * CodeHighlighter Component
 *
 * Detects code blocks in the children prop, applies syntax highlighting to them,
 * and processes non-code text with Markdown formatting.
 * 
 * ToDo: User customization setting for specific hljs stylesheets
 *  - Light mode should set to 'github.css' for one
 *
 * @param {object} props - The component props.
 * @param {string} props.children - The markdown text containing code blocks and regular text.
 */
export const CodeHighlighter = ({ children }) => {
  const codeRefs = useRef([]);

  useEffect(() => {
    // Highlight each code block
    codeRefs.current.forEach((codeEl) => {
      if (codeEl) {
        hljs.highlightElement(codeEl);
      }
    });
  }, [children]);

  // Function to process and render code blocks
  const renderContent = () => {
    // Reset codeRefs.current to empty array for the new render
    codeRefs.current = [];

    // Simple regex to detect code blocks in Markdown format
    const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
    const parts = [];
    let lastIndex = 0;
    let match;
    let codeBlockIndex = 0;

    while ((match = codeBlockRegex.exec(children)) !== null) {
      const [fullMatch, lang, code] = match;
      const index = match.index;
    
      if (lastIndex < index) { // Push previous text segments
        const text = children.substring(lastIndex, index);
        const html = DOMPurify.sanitize(marked(text));
        parts.push(<div key={`text-${index}`} dangerouslySetInnerHTML={{ __html: html }} />);
      }
    
      const decodedCode = he.decode(code); // Decode HTML entities
    
      parts.push( // Push highlighted code block
        <div key={`code-container-${index}`} style={{ position: 'relative' }}>
          <CopyCodeButton code={decodedCode} />
          <pre>
            <code
              ref={(el) => {
                if (el) codeRefs.current.push(el); // Push ref instead of assigning by index
              }}
              className={lang ? `language-${lang} hljs` : ''}
            >
              {decodedCode}
            </code>
          </pre>
        </div>
      );
    
      lastIndex = index + fullMatch.length;
    }

  // Add the remaining content after the last code block
  if (lastIndex < children.length) {
      const text = children.substring(lastIndex);
      const html = DOMPurify.sanitize(marked(text));
      parts.push(<div key={`text-end`} dangerouslySetInnerHTML={{ __html: html }} />);
  }

  return parts;
};

return <div>{renderContent()}</div>;
};



export const withLoadingOpacity = (isLoading) => ({ opacity: isLoading ? 0.5 : 1 });
