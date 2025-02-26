import React, { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';

import { apiFetch } from '../../utils/authUtils';
import { withLoadingOpacity, toTitleCase} from '../../utils/textUtils';
import { fetchCategoriesEndpoint, messagesForCategoryEndpoint } from '../../constants/endpoints';

import MessageItem from './MessageItem';

import './styles/MessageHistory.css';

/**
 * MessageHistory Component
 * 
 * Displays a list of messages, allowing selection, expansion, and deletion.
 * 
 * @param {boolean} isProcessing - Indicates if the application is currently processing data.
 * @param {function} onMessageSelect - Callback to handle message selection.
 */
const MessageHistory = ({ isProcessing, onMessageSelect, selectedMessages, refreshCategory }) => {
  const [categories, setCategories] = useState([])
  const [error, setError] = useState('');
  const [expandedCategoryId, setExpandedCategoryId] = useState(null);
  
  /**
   * Fetches message categories from the backend API.
   * 
   * ToDo: should re-sort alphabetically if the user prefers
   * 
   * @returns {Promise<void>}
   */
  const fetchCategories = useCallback(async () => {
    try {
      const response = await apiFetch(fetchCategoriesEndpoint, {
        method: "GET"
      });

      if (!response.ok) {
        throw new Error("Failed to fetch message categories");
      }

      const data = await response.json();
      const categoriesWithId = data.categories.map((category, index) => ({
        id: index + 1, // Assign a unique ID based on the index
        name: toTitleCase(category.name),
        colour: category.colour ? category.colour : null,
        description: category.description ? category.description : null,
        messages: []
      }));

      setCategories(categoriesWithId); // Set the categories in state
    } catch (error) {
      console.error("Error fetching categories:", error);
      setError("Unable to load message categories. Please try again.");
    }
  }, []);

  /**
   * Fetches messages for a specific category from the backend API.
   * 
   * @param {string} categoryName - The name of the category.
   * @param {number} categoryId - The ID of the category.
   * @returns {Promise<void>}
   */
  const fetchMessagesByCategory = useCallback(async (categoryName, categoryId) => {
    try {
      const response = await apiFetch(messagesForCategoryEndpoint(categoryName.toLowerCase()), {
        method: "GET",
      })

      if (!response.ok) {
        throw new Error(`Failed to get messages for category: ${categoryName}`)
      }

      const data = await response.json();

      setCategories(prevCetegories => 
        prevCetegories.map(category =>
          category.name.toLowerCase() == categoryName.toLowerCase() ? { ...category, messages: data.messages } : category
        )
      )
    } catch (error) {
      console.error("Error fetching messages:", error)
      setError("Unable to load messages. Please try again.");
    }
  }, []);

  useEffect(() => {
    if (refreshCategory == null) {
      return
    }

    fetchMessagesByCategory(refreshCategory?.name, refreshCategory?.id)
  }, [refreshCategory])

  /**
   * Handles the deletion of a message.
   * 
   * @param {number} categoryId - The ID of the category containing the message.
   * @param {number} messageId - The ID of the message to delete.
   */
  const handleDeleteMessage = useCallback((categoryId, messageId) => {
    setCategories(prevCategories =>
      prevCategories.map(category =>
        category.id === categoryId 
          ? { ...category, messages: category.messages.filter(msg => msg.id !== messageId) }
          : category
      )
    );
  }, []);
  
  /**
   * Toggles the expansion of a category.
   * If the category is already expanded, it collapses it.
   * Otherwise, it expands the category and fetches its messages if not already loaded.
   * 
   * @param {number} id - The ID of the category.
   * @param {string} name - The name of the category.
   */
  const toggleCategory = useCallback(async (id, name) => {
    if (expandedCategoryId === id) {
      setExpandedCategoryId(null); // Collapse
    } else {
      setExpandedCategoryId(id); // Expand
      const category = categories.find(cat => cat.id === id);

      // Fetch messages only if they haven't been loaded yet
      if (!category.messages.length) {
        await fetchMessagesByCategory(name, id);
      }
    }
  }, [categories, expandedCategoryId, fetchMessagesByCategory]);

  // Fetch categories when the component mounts
  useEffect(() => {
    if (!isProcessing) {
      fetchCategories();
    }
  }, [isProcessing]);

  return (
    <div className="message-history-container" style={withLoadingOpacity(isProcessing)}>
      <h2>Messages</h2>
      {error && <p className="error-message">{error}</p>}
      <section className="category-list">
        {categories.length > 0 ? (
          categories.map((category) => (
            <div key={category.id} className="category-item" style={{ backgroundColor: category.colour}}>
              <div
                onClick={() => toggleCategory(category.id, category.name)}
                tabIndex={0}
                role="button"
                onKeyPress={(e) => { if (e.key === 'Enter') toggleCategory(category.id, category.name); }}
                aria-expanded={expandedCategoryId === category.id}
                aria-controls={`category-${category.id}`}
              >
                <header
                  className="button category-title"
                >
                  {category.name}
                </header>
                <small style={{opacity: '80%'}}>
                  {category.description}
                </small>
              </div>
              
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
                        isSelected={selectedMessages?.some(selectedMessage => selectedMessage.id === msg.id)}
                      />
                    ))
                  )}
                </div>
              )}
            </div>
          ))
        ) : <p>No categories yet exist.</p>}
      </section>
    </div>
  );
};

MessageHistory.propTypes = {
  isProcessing: PropTypes.bool.isRequired,
  onMessageSelect: PropTypes.func.isRequired,
};

export default React.memo(MessageHistory);
