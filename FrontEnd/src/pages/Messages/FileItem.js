import React, { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';

import { getBasename, CodeHighlighter } from '../../utils/textUtils';
import { formatBytes } from '../../utils/numberUtils';
import { apiFetch } from '../../utils/authUtils';
import { fileAddressEndpoint, fileIdEndpoint } from '../../constants/endpoints';

import './styles/FileItem.css';

/**
 * Displays an individual file with options to expand/collapse, select, and delete.
 *
 * @param file: The file object containing id, name, summary, content, category_id, and time.
 * @param onDelete: Callback function to handle file deletion.
 * @param onSelect: Callback function to handle file selection.
 */
const FileItem = ({ file, onDelete, onSelect, isSelected }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [content, setContent] = useState(file.content || '');
  const [isLoading, setIsLoading] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState(null);

  const fileExtension = file.name.split('.').pop().toLowerCase();

  const nonCodingExtensions = ['txt', 'md', 'markdown'];

  const getFileIcon = () => {
    switch (fileExtension) {
      case 'c':
      case 'cs':
      case 'cpp':
      case 'rb':
      case 'js':
      case 'jsx':
        return '💾';
      case 'css':
        return '✨';
      case 'java':
        return '☕';
      case 'py':
        return '🐍';
      case 'pdf':
        return '📃';
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
        return "This shouldn't be possible";
      case 'csv':
        return '🗃';
      default:
        return '📄';
    }
  };

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
        throw new Error('Failed to fetch file content.');
      }

      const data = await response.json();
      setContent(data.content);
    } catch (err) {
      if (err.name === 'AbortError') return;
      console.error('Error fetching file content:', err);
      setError('Unable to load content. Please try again.');
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

  const toggleExpansion = useCallback((e) => {
    e.stopPropagation();
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

  const handleSelect = useCallback((e) => {
    e.stopPropagation(); // Prevent expansion when selecting
    onSelect(file);
  }, [file, onSelect]);

  /** 
   * ToDo: Take in the extension, sometimes when guessing what the extension is 
   *  it gets it wrong.
   */
  const getFormattedContent = () => {
    // For non-coding file types, return content as is

    
    if (nonCodingExtensions.includes(fileExtension)) {
      return content;
    }
    return "\n```\n" + content + "\n```\n";
  };

  return (
    <div className={`file-item ${isSelected ? 'selected' : ''}`}>
      <div className="file-item-container" onClick={handleSelect}>
        <div className="file-icon">
          {getFileIcon()}
        </div>

        <div className="file-details">
          <div className="file-name">
            {getBasename(file.name)}
          </div>
          <div className="side-by-side">
            <div className="file-date">
              {new Date(file.time * 1000).toLocaleString()}
            </div>
            <div className="file-size">
              {(!(isSelected) || isExpanded) && formatBytes(file.size)}
            </div>
          </div>
        </div>

        <div className="file-actions">
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
          <button className="button expand-button" onClick={toggleExpansion}>
            {isExpanded ? "▲" : "▼"}
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="file-content">
          {file.summary && (
            <div className="file-summary">
              <p><strong>Summary</strong></p>
              <small>
                <div className="markdown-output">
                  <CodeHighlighter>{file.summary}</CodeHighlighter>
                </div>
              </small>
            </div>
          )}
          {file.summary && <strong>Content</strong>}
          <div className="file-content-text">
            <p>
              {isLoading ? (
                <span>Loading content...</span>
              ) : error ? (
                <span className="error">{error}</span>
              ) : (
                <div className="markdown-output">
                  <CodeHighlighter>{getFormattedContent()}</CodeHighlighter>
                </div>
              )}
            </p>
          </div>
        </div>
      )}
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
