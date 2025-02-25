import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import PropTypes from 'prop-types';

import { CodeHighlighter } from '../utils/textUtils';
import FileItem from './../pages/Messages/FileItem';
import { useSelection } from '../pages/Messages/SelectionContext';

import './styles/OutputSection.css';
import { apiFetch } from '../utils/authUtils';
import { fileIdEndpoint } from '../constants/endpoints';

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
 * @param {array} selectedFiles - Array of selected file objects to determine selection state.
 * @returns {JSX.Element|null} - Returns the rendered output or null if no content is available.
 */ 
const OutputSection = ({ message, files, error = '', isProcessing }) => {
  const [fileMap, setFileMap] = useState({});
  const [fileError, setFileError] = useState('');

  const { selectedFiles, toggleFileSelection, removeFile } = useSelection();

  // useRef to track already requested file UUIDs so we avoid duplicate fetches
  const requestedFilesRef = useRef({});

  /**
   * Fetch file details from the backend for the given uuid unless already fetched.
   */
  const fetchFileByUUID = useCallback(async (uuid) => {
    // Avoid duplicate requests
    if (requestedFilesRef.current[uuid]) return;
    requestedFilesRef.current[uuid] = true;

    try {
      const response = await apiFetch(fileIdEndpoint(uuid), { method: 'GET' });

      if (!response.ok) throw new Error(`Failed to fetch file with UUID: ${uuid}`);
      const data = await response.json();

      // Batch update fileMap (and avoid repeatedly copying arrays)
      setFileMap(prev => ({ ...prev, [uuid]: data.file }));
    } catch (err) {
      console.error(`Error fetching file with UUID ${uuid}:`, err);
      setFileError(`Unable to load file with UUID: ${uuid}. Please try again.`);
    }
  }, []);

  // When files change, start fetching new file details.
  useEffect(() => {
    if (!files) return;
    const filesArray = Array.isArray(files) ? files : [files];

    if (filesArray.length) {
      filesArray.forEach(uuid => {
        // Only fetch if the file is not already in our fileMap.
        if (!fileMap[uuid]) {
          fetchFileByUUID(uuid);
        }
      });
    }
    // We intentionally do not depend on fileMap to avoid re-triggering fetch requests.
  }, [files, fetchFileByUUID]);

  // Clear fileMap and requestedFilesRef when processing begins.
  useEffect(() => {
    if (isProcessing) {
      setFileMap({});
      requestedFilesRef.current = {};
    }
  }, [isProcessing]);

  // Compute final message once – if processing then fix incomplete code blocks.
  const displayMessage = useMemo(() => {
    return error 
      ? error 
      : (isProcessing ? ensureMarkdownClosingTags(message) : message);
  }, [error, isProcessing, message]);

  // Convert fileMap into an array for rendering.
  const fileItems = useMemo(() => Object.values(fileMap), [fileMap]);

  const renderFileItem = useCallback(file => (
    <FileItem
      key={file.id}
      file={file}
      onDelete={removeFile}
      onSelect={toggleFileSelection}
      isSelected={selectedFiles?.some(selected => selected.id === file.id)}
    />
  ), [removeFile, selectedFiles, toggleFileSelection]);

  return (
    <div className="output-section">
      {(error || fileError) && (
        <p className="error-message" role="alert">
          {fileError || error}
        </p>
      )}

      <div className="message-container">
        {displayMessage && (
          <div className="markdown-output">
            <CodeHighlighter>
              {displayMessage}
            </CodeHighlighter>
          </div>
        )}
      </div>

      {fileItems && fileItems.length > 0 && fileItems[0] && (
        <div className="file-items-container">
          <h3>Generated Files</h3>
          {fileItems.filter(Boolean).map(renderFileItem)}
        </div>
      )}

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
  files: PropTypes.arrayOf(PropTypes.string).isRequired,
  error: PropTypes.string,
  isProcessing: PropTypes.bool.isRequired,
  selectedFiles: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.string.isRequired,
  })),
};

export default React.memo(OutputSection);
