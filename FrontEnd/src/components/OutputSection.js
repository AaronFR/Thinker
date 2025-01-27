import React from 'react';

import { CodeHighlighter } from '../utils/textUtils';

import './styles/OutputSection.css';

/**
 * During streaming code blocks won't be formatted correctly till the final 
 * code block triple backtick is sent (```). 
 * This method naivley assumes that if the number of triple backticks is odd a 
 * code block is being streamed and we can append one to the stream for correct
 * formatting. 
 * This is an acceptable assumption because:
 * 
 * 1. Most LLMs reliably structure code within code blocks.
 * 2. The check occurs mid-stream, so temporary malformations are acceptable.
 * 
 * @param {string} message - The message string to check and possibly modify.
 * @param {boolean} isProcessing - Boolean flag indicating that the message is being streamed.
 * @return {string} - The modified message, possibly with an extra closing code block.
 */
const ensureMarkdownClosingTags = (message) => {
  const tripleBacktickRegex = /```/g;
  const matches = message.match(tripleBacktickRegex);
  const count = matches ? matches.length : 0;

  // Append closing code block if the count of opening and closing backticks is odd
  return (count % 2 !== 0 && !message.endsWith("```")) 
  ? message + "\n```\n" 
  : message;
};

/**
 * OutputSection Component
 * 
 * Renders the output content, handling both error messages and standard messages.
 * Conditionally modifies the message if it's in the middle of streaming a code 
 * block to ensure proper formatting.
 * 
 * @param message: The message string to display. Can contain markdown and code blocks.
 * @param error: Optional error message to display.
 * @param isProcessing: Indicates if the message is currently being streamed/processed.
 * @returns {JSX.Element|null} - Returns the rendered output or null if no content is available.
 */ 
const OutputSection = ({ message, error = '', isProcessing }) => {
  if (!message && !error && !isProcessing) return null

  const displayMessage = error 
    ? error 
    : (isProcessing ? ensureMarkdownClosingTags(message) : message);

  return (
    <div className="markdown-output">
      <CodeHighlighter>
        {displayMessage}
      </CodeHighlighter>
    </div>
  );
};

export default React.memo(OutputSection);
