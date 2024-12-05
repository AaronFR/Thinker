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
 * :param message: The message string to be checked and possibly modified.
 * :param isProcessing: Boolean flag indicating that the message is being 
 *                      streamed currently.
 * :return: The original message, possibly with a triple backtick
 */
const handleIncompleteMessage = (message) => {
  const tripleBacktickRegex = /```/g;
  const matches = message.match(tripleBacktickRegex);
  const count = matches ? matches.length : 0;

  if (count % 2 !== 0) {
    if (!message.endsWith("```")) {
      message += "\n```";
    }
  }
      
  return message;
}

const OutputSection = ({ message, error = '', isProcessing }) => {
  return (
    <div className="markdown-output">
      <CodeHighlighter>
        {error ? error : 
          (isProcessing ? handleIncompleteMessage(message) : message)
        }
      </CodeHighlighter>
    </div>
  );
};

export default OutputSection;
