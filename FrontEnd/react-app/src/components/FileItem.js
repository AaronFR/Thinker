import React, { useState } from 'react';
import PropTypes from 'prop-types';
import './styles/FileItem.css';

import { shortenText, markedFull } from '../utils/textUtils';

const flask_port= "http://localhost:5000"

const FileItem = React.memo(({ file, onDelete, onSelect }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpansion = async () => {
    if (!isExpanded && !file.content) {
      const response = await fetch(`${flask_port}/content/${file.category_id}/${file.name}`, {
        method: 'GET',
      });

      if (!response.ok) {
        throw new Error("Failed to get file content");
      }

      const data = await response.json();
      file.content = data.content

    }

    setIsExpanded(!isExpanded);
  };

  const handleDelete = async (e) => {
    e.stopPropagation(); // Prevent triggering the toggleExpansion
    try {
      const response = await fetch(`${flask_port}/file/${file.id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error("Failed to delete the file.");
      }

      onDelete(file.id); // Call the onDelete callback to remove the file from the UI
    } catch (error) {
      console.error("Error deleting the file:", error);
      // Optionally, display an error message to the user
    }
  };

  const handleSelect = () => {
    onSelect(file);
  };

  return (
    <div className="file-item" onClick={handleSelect} style={{ cursor: 'pointer' }}>
      <div onClick={toggleExpansion} className="file-item-header">
        <p><strong>File Name:</strong> {isExpanded ? file.name : shortenText(file.name)}</p>
      </div>
      {isExpanded && (
        <div className="file-details">
          <p><strong>Description:</strong> 
            <span 
              dangerouslySetInnerHTML={{ __html: markedFull(file.summary) }}
            />
          </p>
          <p><strong>Content:</strong> 
            <span 
              dangerouslySetInnerHTML={{ __html: markedFull(file.content) }}
            />
          </p>
          
          {/* Add more file details if necessary */}
        </div>
      )}
      <button onClick={handleDelete} className="delete-button">
        Delete
      </button>
      <p className='time'>{new Date(file.time * 1000).toLocaleString()}</p>
    </div>
  );
});

FileItem.propTypes = {
  file: PropTypes.shape({
    id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
    summary: PropTypes.string,
    time: PropTypes.number.isRequired,
  }).isRequired,
  onDelete: PropTypes.func.isRequired,
  onSelect: PropTypes.func.isRequired,
};

export default FileItem;
