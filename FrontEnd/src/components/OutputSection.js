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
 * 1. Even cheap LLMs reliably put code in code blocks
 * 2. This method only operates mid-stream so if the response is malformed from
 *  a malformed code block in the response it is only *temporarily* malformed
 * 
 * @param {string} message - The message string to check and possibly modify.
 * @param {boolean} isProcessing - Boolean flag indicating that the message is being streamed.
 * @return {string} - The modified message, possibly with an extra closing code block.
 */
const handleIncompleteMessage = (message) => {
  const tripleBacktickRegex = /```/g;
  const matches = message.match(tripleBacktickRegex);
  const count = matches ? matches.length : 0;

  // Append closing code block if the count of opening and closing backticks is odd
  return (count % 2 !== 0 && !message.endsWith("```")) 
  ? message + "\n```" 
  : message;
};

/**
 * OutputSection Component
 * 
 * Renders the output content, handling both error messages and standard messages.
 * 
 * @param message: The message string to display. Can contain markdown and code blocks.
 * @param error: Optional error message to display.
 * @param isProcessing: Indicates if the message is currently being streamed/processed.
 */ 
const OutputSection = ({ message, error = '', isProcessing }) => {
  if (!message && !error && !isProcessing) return null

  return (
    <div className="markdown-output">
      <CodeHighlighter>
        {error 
          ? error
          : (isProcessing ? handleIncompleteMessage(message) : message)
        }
      </CodeHighlighter>
    </div>
  );
};

export default React.memo(OutputSection);
