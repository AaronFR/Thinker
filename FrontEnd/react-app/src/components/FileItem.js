import React, { useState } from 'react';
import PropTypes from 'prop-types';

import { shortenText, markedFull } from '../utils/textUtils';

const FLASK_PORT = "http://localhost:5000";

/**
 * FileItem Component
 * 
 * Displays an individual file with options to expand/collapse, select, and delete.
 * 
 * Props:
 * - file (Object): The file object containing id, name, summary, content, category_id, and time.
 * - onDelete (Function): Callback function to handle file deletion.
 * - onSelect (Function): Callback function to handle file selection.
 */
const FileItem = ({ file, onDelete, onSelect }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [content, setContent] = useState(file.content || '');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Toggles the expansion state of the file item.
   * Fetches content if expanding and content is not already loaded.
   */
  const toggleExpansion = async () => {
    if (!isExpanded) {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(`${FLASK_PORT}/file/${file.category_id}/${file.name}`, {
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
    }

    setIsExpanded(prev => !prev);
  };

  /**
   * Handles the deletion of the file by making an API call.
   */
  const handleDelete = async (e) => {
    e.stopPropagation(); // Prevent triggering the toggleExpansion
    if (window.confirm("Are you sure you want to delete this file?")) {
      try {
        const response = await fetch(`${FLASK_PORT}/file/${file.id}`, {
          method: 'DELETE',
          credentials: "include"
        });

        if (!response.ok) {
          throw new Error("Failed to delete the file.");
        }

        onDelete(file.id); // Call the onDelete callback to remove the file from the UI
      } catch (err) {
        console.error("Error deleting the file:", err);
        setError("Unable to delete the file. Please try again.");
      }
    }
  };

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
    >
      <div
        onClick={toggleExpansion}
        className="file-item-header"
      >
        <p><strong>File Name:</strong> {isExpanded ? file.name : shortenText(file.name)}</p>
        
      </div>
      
      {isExpanded && (
        <div className="file-details" style={{ padding: '10px 0' }}>
          <p><strong>Description:</strong> 
            <span 
              dangerouslySetInnerHTML={{ __html: markedFull(file.summary || 'No description available.') }}
            />
          </p>
          <p><strong>Content:</strong> 
            {isLoading ? (
              <span>Loading content...</span>
            ) : error ? (
              <span style={{ color: 'red' }}>{error}</span>
            ) : (
              <span 
                dangerouslySetInnerHTML={{ __html: markedFull(content) }}
              />
            )}
          </p>
          {/* Add more file details if necessary */}
        </div>
      )}
      <div className="message-footer">
        <button
          onClick={handleDelete}
          className="delete-button"
          type="button"
        >
          Delete
        </button>
        <p className='time'>{new Date(file.time * 1000).toLocaleString()}</p>
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
