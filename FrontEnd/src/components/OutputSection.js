import React, { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';

import { CodeHighlighter } from '../utils/textUtils';
import FileItem from './../pages/Messages/FileItem'; // Importing FileItem component
import { useSelection } from '../pages/Messages/SelectionContext';

import './styles/OutputSection.css';
import { apiFetch } from '../utils/authUtils';

const FLASK_PORT = process.env.REACT_APP_THE_THINKER_BACKEND_URL || "http://localhost:5000";

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
 * @return {string} - The modified message, possibly with an extra closing code block.
 */
const ensureMarkdownClosingTags = (message) => {
  const tripleBacktickRegex = /```/g;
  const matches = message.match(tripleBacktickRegex);
  const count = matches ? matches.length : 0;

  // Append closing code block if the count of backticks is odd and not already closed
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
 * @param {string} message - The message string to display. Can contain markdown and code blocks.
 * @param {array} files - An array of file UUIDs to be processed and displayed as FileItem components.
 * @param {string} error - Optional error message to display.
 * @param {boolean} isProcessing - Indicates if the message is currently being streamed/processed.
 * @param {function} onDelete - Callback function to handle file deletion.
 * @param {function} onSelect - Callback function to handle file selection.
 * @param {array} selectedFiles - Array of selected file objects to determine selection state.
 * @returns {JSX.Element|null} - Returns the rendered output or null if no content is available.
 */ 
const OutputSection = ({ message, files, error = '', isProcessing }) => {
  // State to hold detailed file data corresponding to each UUID
  const [fileItems, setFileItems] = useState([]);
  
  // State to manage errors specific to file fetching
  const [fileError, setFileError] = useState('');

  const { 
    selectedFiles,
    toggleFileSelection, 
    removeFile
  } = useSelection();

  /**
   * Fetches file details from the backend using the UUID.
   *
   * @param {string} uuid - The UUID of the file to fetch.
   */
  const fetchFileByUUID = useCallback(async (uuid) => {
    try {
      const response = await apiFetch(`${FLASK_PORT}/read_file/${uuid}`, {
        method: 'GET',
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch file with UUID: ${uuid}`);
      }

      const data = await response.json();
      setFileItems(prevItems => [...prevItems, data.file]);
    } catch (err) {
      console.error(`Error fetching file with UUID ${uuid}:`, err);
      setFileError(`Unable to load file with UUID: ${uuid}. Please try again.`);
    }
  }, []);

  useEffect(() => {
    if (files) {
      // Ensure files is always an array
      const filesArray = Array.isArray(files) ? files : [files];

      if (filesArray.length > 0) {
        filesArray.forEach(id => {
          // Check if the file is already in the state to prevent duplicate fetches

          const exists = fileItems.length === 0 ? false : fileItems.some(item => item?.id === id);
          if (!exists) {
            fetchFileByUUID(id);
          }
        });
      }
    }
  }, [files, fetchFileByUUID]);

  useEffect(() => {
    if (isProcessing) {
      setFileItems([])
    }
  }, [isProcessing]);

  /**
   * Determines the message to display.
   * Prioritizes displaying file-specific errors over general errors.
   */
  const displayMessage = error 
    ? error 
    : (isProcessing ? ensureMarkdownClosingTags(message) : message);

  return (
    <div className="output-section">
      {/* Render the message or error */}
      {fileError && <p className="error-message" role="alert">{fileError}</p>}
      <div className="message-container">
        {error && <p className="error-message" role="alert">{error}</p>}
        {fileError && <p className="error-message" role="alert">{fileError}</p>}
        {displayMessage && (
          <div className="markdown-output">
            <CodeHighlighter>
              {displayMessage}
            </CodeHighlighter>
          </div>
        )}
      </div>

      {/* Render the list of FileItem components based on fetched fileItems */}
      {fileItems && fileItems.length > 0 && fileItems[0] && (
        <div className="file-items-container">
          <h3>Generated Files</h3>
          {fileItems
            .filter(file => file) // This filters out undefined or null entries
            .map(file => (
              <FileItem
                key={file.id}
                file={file}
                onDelete={removeFile}
                onSelect={toggleFileSelection}
                isSelected={selectedFiles?.some(selectedFile => selectedFile.id === file.id)}
              />
            ))
          }
        </div>
      )}


      {/* Optionally, display a loading indicator while processing */}
      {isProcessing && (
        <div className="loading-indicator">
          <p>Processing...</p>
        </div>
      )}
    </div>
  );
};

OutputSection.propTypes = {
  message: PropTypes.string,
  files: PropTypes.arrayOf(PropTypes.string).isRequired, // Array of file UUIDs
  error: PropTypes.string,
  isProcessing: PropTypes.bool.isRequired,
  onDelete: PropTypes.func.isRequired,
  onSelect: PropTypes.func.isRequired,
  selectedFiles: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.number.isRequired,
    // ... other file properties as needed
  })),
};

export default React.memo(OutputSection);
