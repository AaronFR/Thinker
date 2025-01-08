import React, { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';

import { shortenText, getBasename, MarkdownRenderer, CodeHighlighter } from '../utils/textUtils';
import { apiFetch } from '../utils/authUtils';

const FLASK_PORT = process.env.REACT_APP_THE_THINKER_BACKEND_URL || "http://localhost:5000";

/**
 * FileItem Component
 * 
 * Displays an individual file with options to expand/collapse, select, and delete.
 *
 * @param file: The file object containing id, name, summary, content, category_id, and time. * 
 * @param onDelete: Callback function to handle file deletion. * 
 * @param onSelect: Callback function to handle file selection.
 */
const FileItem = ({ file, onDelete, onSelect }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [content, setContent] = useState(file.content || '');
  const [isLoading, setIsLoading] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isExpanded && !content) {
      fetchContent();
    }
  }, [isExpanded]);

  /**
   * Fetches file content and handles errors.
   * Sets the content state or handles errors accordingly.
   */
  const fetchContent = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${FLASK_PORT}/file/${file.category_id}/${getBasename(file.name)}`, {
        method: 'GET',
        credentials: "include"
      });

      if (!response.ok) {
        throw new Error("Failed to fetch file content.");
      }

      const data = await response.json();
      setContent(data.content);
    } catch (err) {
      console.error("Error fetching file content:", err);
      setError("Unable to load content. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Toggles the expansion state of the file item.
   */
  const toggleExpansion = useCallback(() => {
    setIsExpanded(prev => !prev);
  }, []);

  /**
     * Handles the deletion of the file by making an API call.
     * Prevents multiple deletions and provides user feedback.
     * 
     * @param e: Event object.
     */
  const handleDelete = useCallback(async (e) => {
    e.stopPropagation(); // Prevent triggering the toggleExpansion
    if (isDeleting) return; // Prevent multiple deletions

    if (!window.confirm('Are you sure you want to delete this file?')) return;

    setIsDeleting(true);
    setError(null);

    try {
        const response = await apiFetch(`${FLASK_PORT}/file/${file.id}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            throw new Error('Failed to delete the file.');
        }

        onDelete(file.id); // Remove the file from the UI
    } catch (err) {
        console.error('Error deleting the file:', err);
        setError('Unable to delete the file. Please try again.');
    } finally {
        setIsDeleting(false);
    }
}, []);

  /**
   * Handles the selection of the file.
   */
  const handleSelect = () => {
    onSelect(file);
  };

  return (
    <div
      className="file-item"
      onClick={handleSelect}
      style={{ cursor: 'pointer', opacity: isLoading ? 0.5 : 1 }}
      role="button"
      aria-pressed={isExpanded}
      tabIndex={0}
      onKeyPress={(e) => {
          if (e.key === 'Enter') toggleExpansion();
      }}
    >
      <div
        onClick={toggleExpansion}
        className="file-item-header"
        aria-expanded={isExpanded}
        role="button"
        tabIndex={0}
        onKeyPress={(e) => {
            if (e.key === 'Enter') toggleExpansion();
        }}
      >
        <p>
          {isExpanded
            ? getBasename(file.name)
            : shortenText(getBasename(file.name))}
        </p>
      </div>
      
      {isExpanded && (
        <div className="file-details" style={{ padding: '10px 0' }}>
          <p><strong>Description:</strong> 
            <MarkdownRenderer>
              {file.summary || 'No description available.'}
            </MarkdownRenderer>
          </p>

          <p>
            <strong>Content:</strong>{' '}
            {isLoading ? <span>Loading content...</span> 
              : error ? <span className="error">{error}</span> 
              : <div className="markdown-output">
                  <CodeHighlighter>{content}</CodeHighlighter>
                </div>}
          </p>
        </div>
      )}

      <div className="message-footer">
      <button
        onClick={handleDelete}
        className="button delete-button"
        type="button"
        disabled={isDeleting}
        aria-label={isDeleting ? 'Deleting file' : 'Delete this file'}
      >
        {isDeleting ? 'Deleting...' : 'Delete'}
      </button>
        <p className="time">
          {new Date(file.time * 1000).toLocaleString()
        }</p>
      </div>
    </div>
  );
};

FileItem.propTypes = {
  file: PropTypes.shape({
    id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
    summary: PropTypes.string,
    content: PropTypes.string,
    category_id: PropTypes.number.isRequired,
    time: PropTypes.number.isRequired,
  }).isRequired,
  onDelete: PropTypes.func.isRequired,
  onSelect: PropTypes.func.isRequired,
};

export default FileItem;
