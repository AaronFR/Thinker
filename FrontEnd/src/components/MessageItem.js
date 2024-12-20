import React, { useState, memo } from 'react';
import PropTypes from 'prop-types';

import { shortenText, CodeHighlighter } from '../utils/textUtils';

const FLASK_PORT = process.env.REACT_APP_THE_THINKER_BACKEND_URL || "http://localhost:5000";

/**
 * MessageItem Component
 * 
 * Displays an individual message with options to expand/collapse and delete.
 * 
 * Props:
 * - msg (Object): The message object containing id, prompt, response, and time.
 * - onDelete (Function): Callback function to handle message deletion.
 */
const MessageItem = ({ msg, onDelete, onSelect }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Toggles the expansion state of the message item.
   */
  const toggleExpansion = () => {
    setIsExpanded(prev => !prev);
  };

  /**
   * Handles the deletion of the message by making an API call.
   */
  const handleDelete = async (e) => {
    e.stopPropagation(); // Prevent triggering the toggleExpansion
    if (isDeleting) return; // Prevent multiple deletions
    if (!window.confirm("Are you sure you want to delete this message?")) return;

    setIsDeleting(true);
    setError(null);

    try {
      const response = await fetch(`${FLASK_PORT}/messages/${msg.id}`, {
        method: 'DELETE',
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Failed to delete the message.");
      }

      onDelete(msg.id); // Call the onDelete callback to remove the message from the UI
    } catch (err) {
      console.error("Error deleting the message:", err);
      setError("Unable to delete the message. Please try again.");
    } finally {
      setIsDeleting(false);
    }
  };

  /**
   * Handles the selection of the message.
   */
  const handleSelect = () => {
    onSelect(msg);
  };

  return (
    <div 
      className="message-item"
      onClick={handleSelect}
      style={{ cursor: 'pointer' }}
    >
      <div 
        className="message-header"
        onClick={toggleExpansion}
        style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
      >
          
        <div className="markdown-output">
          <CodeHighlighter>
            {isExpanded ? msg.prompt : shortenText(msg.prompt)}
          </CodeHighlighter>
        </div>
        
      </div>
      
      <div className="message-response">
        <p><strong>Response:</strong></p>
        <div className="markdown-output">
          <CodeHighlighter>
            {isExpanded ? msg.response : shortenText(msg.response)}
          </CodeHighlighter>
        </div>
        
      </div>

      {error && <p className="error-message" style={{ color: 'red' }}>{error}</p>}

      <div className="message-footer">
        <button
          onClick={handleDelete}
          className="delete-button"
          type="button"
          disabled={isDeleting}
        >
          {isDeleting ? 'Deleting...' : 'Delete'}
        </button>
        <p className='time'>{new Date(msg.time * 1000).toLocaleString()}</p>
      </div>
    </div>
  );
};

MessageItem.propTypes = {
  msg: PropTypes.shape({
    id: PropTypes.string.isRequired,
    prompt: PropTypes.string.isRequired,
    response: PropTypes.string.isRequired,
    time: PropTypes.number.isRequired,
  }).isRequired,
  onSelect: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
};

export default MessageItem;
