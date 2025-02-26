import React, { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';

import { shortenText, getBasename, CodeHighlighter } from '../../utils/textUtils';
import { apiFetch } from '../../utils/authUtils';
import { fileAddressEndpoint, fileIdEndpoint } from '../../constants/endpoints';

/** 
 * Displays an individual file with options to expand/collapse, select, and delete.
 *
 * @param file: The file object containing id, name, summary, content, category_id, and time. * 
 * @param onDelete: Callback function to handle file deletion. * 
 * @param onSelect: Callback function to handle file selection.
 */
const FileItem = ({ file, onDelete, onSelect, isSelected }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [content, setContent] = useState(file.content || '');
  const [isLoading, setIsLoading] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState(null);

  const fetchContent = useCallback(async (signal) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(
        fileAddressEndpoint(file.category_id, getBasename(file.name)),
        {
          method: 'GET',
          credentials: 'include',
          signal,
        }
      );

      if (!response.ok) {
        throw new Error("Failed to fetch file content.");
      }

      const data = await response.json();
      setContent(data.content);
    } catch (err) {
      if (err.name === 'AbortError') return;

      console.error("Error fetching file content:", err);
      setError("Unable to load content. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }, [file.category_id, file.name]);

  useEffect(() => {
    if (isExpanded && !content) {
      const controller = new AbortController();
      fetchContent(controller.signal);
      
      return () => {
        controller.abort();
      };
    }
  }, [isExpanded, content, fetchContent]);

  const toggleExpansion = useCallback(() => {
    setIsExpanded(prev => !prev);
  }, []);

  const handleDelete = useCallback(async (e) => {
    e.stopPropagation();
    if (isDeleting) return;
    if (!window.confirm('Are you sure you want to delete this file?')) return;

    setIsDeleting(true);
    setError(null);

    try {
      const response = await apiFetch(fileIdEndpoint(file.id), {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error('Failed to delete the file.');
      }
      onDelete(file.id);
    } catch (err) {
      console.error('Error deleting the file:', err);
      setError('Unable to delete the file. Please try again.');
    } finally {
      setIsDeleting(false);
    }
  }, [isDeleting, file.id, onDelete]);

  const handleSelect = useCallback(() => {
    onSelect(file);
  }, [file, onSelect]);

  return (
    <div
      className={`file-item ${isSelected ? 'selected' : ''}`}
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
          {isExpanded ? getBasename(file.name) : shortenText(getBasename(file.name))}
        </p>
      </div>
      
      {isExpanded && (
        <div className="file-details" style={{ padding: '10px 0' }}>
          {file.summary && (
            <div>
              <p><strong>Summary</strong></p>
              <small>{file.summary}</small>
            </div>
          )}
          <p>
            <strong>Content:</strong>{' '}
            {isLoading ? (
              <span>Loading content...</span>
            ) : error ? (
              <span className="error">{error}</span>
            ) : (
              <div className="markdown-output">
                <CodeHighlighter>{content}</CodeHighlighter>
              </div>
            )}
          </p>
        </div>
      )}

      <div className="message-footer">
        {(isSelected || isExpanded) && (
          <button
            onClick={handleDelete}
            className="button delete-button"
            type="button"
            disabled={isDeleting}
            aria-label={isDeleting ? 'Deleting file' : 'Delete this file'}
          >
            {isDeleting ? 'Deleting...' : 'Delete'}
          </button>
        )}
        <p className="time">
          {new Date(file.time * 1000).toLocaleString()}
        </p>
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
  isSelected: PropTypes.bool.isRequired,
};

export default FileItem;