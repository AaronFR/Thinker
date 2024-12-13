import { marked } from 'marked';
import DOMPurify from 'dompurify';
import React, { useEffect, useRef, useMemo } from 'react';
import hljs from 'highlight.js';
import he from 'he';

/**
 * Strips the folder path from a given file path and returns the basename with extension.
 *
 * @param {string} filePath - The full path of the file.
 * @returns {string} The basename of the file (i.e., the file name with extension).
 */
export const getBasename = (filePath) => {
  return filePath.replace(/^.*[\\/]/, '')
};

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
   * ToDo: Custom rendering for markdown elements e.g. lists headings titles..
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

/**
 * Renders a button that copies the code text to the clipboard.
 *
 * :param code: The code text to be copied.
 */
const CopyCodeButton = ({ code }) => {
  const handleCopy = async () => {
      try {
          await navigator.clipboard.writeText(code);
      } catch (err) {
          console.error('Failed to copy code:', err);
      }
  };

  return (
    <button 
      onClick={handleCopy} 
      style={{ position: 'absolute', top: 8, right: 8 }}
      aria-label="Copy code to clipboard"
    >
      📋
    </button>
  );
};

/**
 * CodeBlock component for rendering highlighted code with a copy button.
 *
 * :param lang: The language of the code block.
 * :param code: The actual code to highlight.
 * :param index: The index for unique key generation.
 */
const CodeBlock = ({ lang, code, index }) => {
  const codeRef = useRef();

  useEffect(() => {
      if (codeRef.current.dataset.highlighted) {
        // Un-set the highlighted attribute -if a streamed code block needs to be re-rendered
        delete codeRef.current.dataset.highlighted;
      }
      hljs.highlightElement(codeRef.current);
  }, [code]);

  const escapedCode = he.encode(code); // for neutering potentially maliscious code before render

  return (
    <div style={{ position: 'relative' }}>
      <CopyCodeButton code={code} />
      <pre>
        <code 
          ref={codeRef} 
          className={lang ? `language-${lang} hljs` : ''}
          dangerouslySetInnerHTML={{ __html: escapedCode }}
        />
      </pre>
    </div>
  );
};

/**
 * Renders a standard text block.
 *
 * :param text: The text to render as HTML.
 */
const TextBlock = ({ text }) => (
  <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked(text)) }} />
);

/**
 * CodeHighlighter Component
 *
 * Detects code blocks in the children prop, applies syntax highlighting to them,
 * and processes non-code text with Markdown formatting.
 * 
 * ToDo: User customization setting for specific hljs stylesheets
 *  - Light mode should set to 'github.css' for one
 * ToDo: You would want to ensure scripts can't be run through code elements
 * ToDo utilise isSupported in DomPurify to affect if this is allowed or not
 *
 * @param {object} props - The component props.
 * @param {string} props.children - The markdown text containing code blocks and regular text.
 */
export const CodeHighlighter = ({ children }) => {
  const parts = useMemo(() => {
    const elements = [];
    let lastIndex = 0;
    let match;
    const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
    while ((match = codeBlockRegex.exec(children)) !== null) {
      const [fullMatch, lang, code] = match;
      const index = match.index;

      // Handle previous text segments
      if (lastIndex < index) {
          const text = children.substring(lastIndex, index);
          elements.push(<TextBlock key={`text-${lastIndex}`} text={text} />);
      }

      // Handle code block
      elements.push(<CodeBlock key={`code-${lastIndex}`} lang={lang} code={code} index={lastIndex} />);
      
      lastIndex = index + fullMatch.length;
  }

  // Add any remaining text after the last code block
  if (lastIndex < children.length) {
      const text = children.substring(lastIndex);
      elements.push(<TextBlock key={`text-end`} text={text} />);
  }

  return elements;
}, [children]);

return <div>{parts}</div>;
};



export const withLoadingOpacity = (isLoading) => ({ opacity: isLoading ? 0.5 : 1 });
