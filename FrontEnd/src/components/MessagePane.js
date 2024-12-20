import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

import { apiFetch } from '../utils/authUtils';
import { withLoadingOpacity, toTitleCase} from '../utils/textUtils';

import MessageItem from './MessageItem';

import './styles/MessageHistory.css';

const FLASK_PORT = process.env.REACT_APP_THE_THINKER_BACKEND_URL || "http://localhost:5000";

/**
 * MessageHistory Component
 * 
 * Displays a list of message categories and their respective messages.
 * Allows users to expand/collapse categories, view message details, select messages, and delete messages.
 * 
 * Props:
 * - isProcessing (boolean): Indicates if the app is currently processing data.
 */
const MessageHistory = ({ isProcessing, onMessageSelect }) => {
  const [categories, setCategories] = useState([])
  const [expandedCategoryId, setExpandedCategoryId] = useState(null);

  /**
   * Toggles the expansion of a category.
   * If the category is already expanded, it collapses it.
   * Otherwise, it expands the category and fetches its messages if not already loaded.
   * 
   * @param {number} id - The ID of the category.
   * @param {string} name - The name of the category.
   */
  const toggleCategory = async (id, name) => {
    if (expandedCategoryId === id) {
      setExpandedCategoryId(null); // Collapse if already expanded
    } else {
      setExpandedCategoryId(id); // Expand the clicked category

      // Check if this category already has messages loaded
      const categoryIndex = categories.findIndex(cat => cat.id === id);
      if (categories[categoryIndex].messages && categories[categoryIndex].messages.length > 0) {
        // Messages already loaded, no need to fetch again
        return;
      }

      await fetchMessagesByCategory(name, id);
    }
  };

  /**
   * Fetches message categories from the backend API.
   * 
   * @returns {Promise<void>}
   */
  const fetchCategories = async () => {
    const response = await apiFetch(`${FLASK_PORT}/categories`, {
      method: "GET",
    });

    if (!response.ok) {
      throw new Error("Failed to get message categories")
    }

    const data = await response.json()

    const categoriesWithId = data.categories.map((category, index) => ({
      id: index + 1, // Assign a unique ID based on the index
      name: toTitleCase(category),
      messages: []
    }));

    setCategories(categoriesWithId)
  }

  /**
   * Fetches messages for a specific category from the backend API.
   * 
   * @param {string} categoryName - The name of the category.
   * @param {number} categoryId - The ID of the category.
   * @returns {Promise<void>}
   */
  const fetchMessagesByCategory = async (categoryName, categoryId) => {
    try {
      console.log(categoryName.toLowerCase())
      const response = await apiFetch(`${FLASK_PORT}/messages/${categoryName.toLowerCase()}`, {
        method: "GET",
      })

      if (!response.ok) {
        throw new Error(`Failed to get messages for category: ${categoryName}`)
      }

      const data = await response.json();
      console.log(data)

      setCategories(prevCetegories => 
        prevCetegories.map(category =>
          category.id === categoryId ? { ...category, messages: data.messages } : category
        )
      )
    } catch (error) {
      console.error("Error fetching messages:", error)
    }
  };

  // Fetch categories when the component mounts
  useEffect(() => {
    if (!isProcessing) {
      fetchCategories();
    }
  }, [isProcessing]);

  /**
   * Handles the deletion of a message.
   * 
   * @param {number} categoryId - The ID of the category containing the message.
   * @param {number} messageId - The ID of the message to delete.
   */
  const handleDeleteMessage = (categoryId, messageId) => {
    // Create a new category list with the updated messages
    const updatedCategories = categories.map((category) => {
      if (category.id === categoryId) {
        // Filter out the deleted message
        const updatedMessages = category.messages.filter((msg) => msg.id !== messageId);
        return { ...category, messages: updatedMessages };
      }
      return category;
    });

    setCategories(updatedCategories);
  };

  return (
    <div className="message-history-container" style={withLoadingOpacity(isProcessing)}>
      <h2>Messages</h2>
      <section className="category-list">
        {categories.length > 0 ? (
          categories.map((category) => (
            <div key={category.id} className="category-item">
              <header
                className="category-title"
                onClick={() => toggleCategory(category.id, category.name)}
                tabIndex={0}
                role="button"
                onKeyPress={(e) => { if (e.key === 'Enter') toggleCategory(category.id, category.name); }}
                aria-expanded={expandedCategoryId === category.id}
                aria-controls={`category-${category.id}`}
              >
                {category.name}
              </header>
              {expandedCategoryId === category.id && (
                <div id={`category-${category.id}`} className="message-list">
                  {category.messages.length === 0 ? (
                    <p>Loading messages...</p>
                  ) : (
                    category.messages.map((msg) => (
                      <MessageItem
                        key={msg.id} 
                        msg={msg} 
                        onDelete={() => handleDeleteMessage(category.id, msg.id)}
                        onSelect={onMessageSelect}
                      />
                    ))
                  )}
                </div>
              )}
            </div>
          ))
        ) : <div />}
      </section>
    </div>
  );
};

MessageHistory.propTypes = {
  isProcessing: PropTypes.bool.isRequired,
};

export default React.memo(MessageHistory);
