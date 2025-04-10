import React, { useState, useEffect, useCallback, useContext, useRef } from 'react';
import PropTypes from 'prop-types';

import { apiFetch } from '../../utils/authUtils';
import { withLoadingOpacity, toTitleCase } from '../../utils/textUtils';
import { categoriesEndpoint, messagesForCategoryEndpoint } from '../../constants/endpoints';

import MessageItem from './MessageItem';

import './styles/MessageHistory.css';
import { SettingsContext } from '../Settings/SettingsContext';
import { useCalculateItemsPerRow } from '../../hooks/useCalculateItemsPerRow';
import CategoryInstructionsEditor from '../../components/CategoryInstructionsEditor';
import TooltipConstants from '../../constants/tooltips';

/**
 * MessagePane Component
 * 
 * Displays a list of messages grouped by categories,
 * allowing selection, expansion, and deletion.
 * 
 * @param {boolean} isProcessing - Indicates whether the application is processing data.
 * @param {function} onMessageSelect - Callback function for selecting a message.
 */
const MessagePane = ({ isProcessing, onMessageSelect, selectedMessages, removeMessage, refreshCategory }) => {
  const [categories, setCategories] = useState([]);
  const [error, setError] = useState('');
  const [expandedCategoryId, setExpandedCategoryId] = useState(null);
  const [animating, setAnimating] = useState(false);

  const { settings } = useContext(SettingsContext);

  const messageListRef = useRef(null);

  const [itemsPerRow] = useCalculateItemsPerRow(messageListRef, '.category-item');

  /**
   * Fetches message categories from the backend API.
   * 
   * ToDo: should re-sort alphabetically if the user prefers
   * ToDo: When files and messages are merged by default refactor to make use of CategoryService.js
   * 
   * @returns {Promise<void>}
   */
  const fetchCategories = useCallback(async () => {
    try {
      const response = await apiFetch(categoriesEndpoint, { 
        method: 'GET'
      });

      if (!response.ok) {
        throw new Error("Failed to fetch message categories");
      }

      const data = await response.json();

      // Assign unique IDs and default messages
      const categoriesWithId = data.categories.map((category, index) => ({
        id: category.id,
        name: toTitleCase(category.name),
        colour: category.colour || null,
        instructions: category.instructions || null,
        messages: []
      }));
      setCategories(categoriesWithId);
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
   */
  const fetchMessagesByCategory = useCallback(async (categoryName, categoryId) => {
    try {
      const response = await apiFetch(messagesForCategoryEndpoint(categoryName.toLowerCase()), {
        method: "GET",
      });
      if (!response.ok) {
        throw new Error(`Failed to get messages for category: ${categoryName}`);
      }
      const data = await response.json();
      setCategories(prevCategories =>
        prevCategories.map(category =>
          category.name.toLowerCase() === categoryName.toLowerCase()
            ? { ...category, messages: data.messages }
            : category
        )
      );
    } catch (error) {
      console.error("Error fetching messages:", error);
      setError("Unable to load messages. Please try again.");
    }
  }, []);

  useEffect(() => {
    if (refreshCategory == null) {
      return;
    }

    toggleCategory(refreshCategory?.id, refreshCategory?.name)
  }, [refreshCategory, fetchCategories]);

  /**
   * Handles deletion of a message.
   *
   * @param {number} categoryId - The ID of the category containing the message.
   * @param {number} messageId - The ID of the message to be deleted.
   */
  const handleDeleteMessage = useCallback((categoryId, messageId) => {
    setCategories(prevCategories =>
      prevCategories.map(category =>
        category.id === categoryId
          ? { ...category, messages: category.messages.filter(msg => msg.id !== messageId) }
          : category
      )
    );
    removeMessage(messageId);
  }, [removeMessage]);

  /**
   * Updates the local state of category instructions if the backend has been updated.
   */
  const handleCategoryInstructionsUpdate = useCallback((categoryName, newInstructions) => {
    setCategories(prevCategories =>
      prevCategories.map(category =>
        category.name.toLowerCase() === categoryName.toLowerCase()
          ? { ...category, instructions: newInstructions }
          : category
      )
    );
  }, []);

  /**
   * Toggles the expansion of a category.
   *
   * @param {number} id - The ID of the category.
   * @param {string} name - The name of the category.
   */
  const toggleCategory = useCallback(async (id, name) => {
    if (animating) return;

    setAnimating(true);

    if (expandedCategoryId === id) {
      setExpandedCategoryId(null);
    } else {
      setExpandedCategoryId(id);
      const category = categories.find(cat => cat.name.toLowerCase() === name.toLowerCase());
      
      // Fetch messages only if they have not been loaded yet
      if (!category || !category.messages?.length) {
        await fetchMessagesByCategory(name, id);
      }
    }

    // Allow toggling after animation completes (matches CSS transition duration)
    setTimeout(() => {
      setAnimating(false);
    }, 300);
  }, [categories, expandedCategoryId, fetchMessagesByCategory, animating]);

  // Fetch categories when the component mounts if not processing
  useEffect(() => {
    if (!isProcessing) {
      fetchCategories();
    }
  }, [isProcessing, fetchCategories]);

  return (
    <div className="message-history-container" style={withLoadingOpacity(isProcessing)}>
      <h2>Messages</h2>
      {error && <p className="error-message">{error}</p>}
      <section className="category-list" ref={messageListRef}>
        {categories.length > 0 ? (
          <>
            {categories.map((category) => (
              <div 
                key={category.id} 
                className={`category-item ${expandedCategoryId === category.id ? 'category-item--expanded' : ''}`} 
                style={{ backgroundColor: category.colour }}
              >
                <div
                  onClick={() => toggleCategory(category.id, category.name)}
                  tabIndex={0}
                  role="button"
                  onKeyPress={(e) => { if (e.key === 'Enter') toggleCategory(category.id, category.name); }}
                  aria-expanded={expandedCategoryId === category.id}
                  aria-controls={`category-${category.id}`}
                >
                  <header className="category-title">
                    {category.name}
                  </header>
                  {(
                    (settings?.interface?.display_category_instructions === "always" && expandedCategoryId === category.id) ||
                    (settings?.interface?.display_category_instructions === "when selected" && expandedCategoryId === category.id)
                   ) && (
                      <CategoryInstructionsEditor
                        categoryName={category.name}
                        category_instructions={category.instructions}
                        onUpdateInstructions={handleCategoryInstructionsUpdate}
                        data-tooltip-id="tooltip"
                        data-tooltip-content={TooltipConstants.categorySystemMessage}
                        data-tooltip-place="bottom"
                      />
                  )}
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
            ))}
            {/* Add hidden flex items to fill the last row for proper alignment */}
            {Array.from({
              length:
                itemsPerRow === 0 || categories.length === 0
                  ? 0
                  : (categories.length % itemsPerRow === 0 ? 0 : itemsPerRow - (categories.length % itemsPerRow))
            }).map((_, index) => (
              <div key={`hidden-${index}`} className="hidden-flex-item" />
            ))}
          </>
        ) : (
          <p>No categories yet exist.</p>
        )}
      </section>
    </div>
  );
};

MessagePane.propTypes = {
  isProcessing: PropTypes.bool.isRequired,
  onMessageSelect: PropTypes.func.isRequired,
  selectedMessages: PropTypes.array,
  removeMessage: PropTypes.func.isRequired,
  refreshCategory: PropTypes.any,
};

export default React.memo(MessagePane);
