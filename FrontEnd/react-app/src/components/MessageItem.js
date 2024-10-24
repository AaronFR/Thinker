import React, { useState } from 'react';
import PropTypes from 'prop-types';

import { shortenText, markedFull, shortenAndMarkupText } from '../utils/textUtils';

const flask_port= "http://localhost:5000"


/**
   * MessageItem Component
   * 
   * Displays an individual message with options to expand/collapse and delete.
   * 
   * Props:
   * - msg (Object): The message object containing id, prompt, response, and time.
   * - onDelete (Function): Callback function to handle message deletion.
   */
const MessageItem = ({ msg, onDelete }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  /**
   * Toggles the expansion state of the message item.
   */
  const toggleExpansion = () => {
    setIsExpanded(!isExpanded);
  };

  /**
   * Handles the deletion of the message by making an API call.
   */
  const handleDelete = async () => {
    try {
      const response = await fetch(`${flask_port}/messages/${msg.id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error("Failed to delete the message.");
      }

      onDelete(msg.id);  // Call the onDelete callback to remove the message from the UI
    } catch (error) {
      console.error("Error deleting the message:", error);
    }
  };

  return (
    <div key={msg.id} className="message-item" onClick={toggleExpansion} style={{ cursor: 'pointer' }}>
      <p><strong>Prompt:</strong> {isExpanded ? msg.prompt : shortenText(msg.prompt)}</p>
      <p><strong>Response:</strong> 
        <span 
          dangerouslySetInnerHTML={{ __html: isExpanded ? markedFull(msg.response) : shortenAndMarkupText(msg.response) }}
        />
      </p>
      <p className='time'>{new Date(msg.time * 1000).toLocaleString()}</p>
      <button onClick={handleDelete} className="delete-button">
        Delete
      </button>
    </div>
  );
};

/**
 * PropTypes for MessageItem Component
 */
MessageItem.propTypes = {
  msg: PropTypes.shape({
    id: PropTypes.number.isRequired,
    prompt: PropTypes.string.isRequired,
    response: PropTypes.string.isRequired,
    time: PropTypes.number.isRequired,
  }).isRequired,
  onDelete: PropTypes.func.isRequired,
};

export default MessageItem;