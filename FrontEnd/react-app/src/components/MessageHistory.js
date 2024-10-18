import React, { useState, useEffect } from 'react';
import DOMPurify from 'dompurify';
import { marked } from 'marked';
import './styles/MessageHistory.css';

const flask_port= "http://localhost:5000"

const MessageHistory = ({ isProcessing }) => {
  const [categories, setCategories] = useState(null)
  const [expandedCategory, setExpandedCategory] = useState(null);

  const abridged_text_length = 160

  const toggleCategory = async (id, name) => {
    if (expandedCategory === id) {
      setExpandedCategory(null); // Collapse if already expanded
    } else {
      setExpandedCategory(id); // Expand the clicked category

      // Check if this category already has messages loaded
      const categoryIndex = categories.findIndex(cat => cat.id === id);
      if (categories[categoryIndex].messages && categories[categoryIndex].messages.length > 0) {
        // Messages already loaded, no need to fetch again
        return;
      }

      await fetchMessagesByCategory(name, id);
    }
  };

  function toTitleCase(string) {
    return string
      .toLowerCase()
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  const fetchCategories = async (e) => {
    const response = await fetch(`${flask_port}/categories`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json"
      }
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

  const fetchMessagesByCategory = async (categoryName, categoryId) => {
    try {
      console.log(categoryName.toLowerCase())
      const response = await fetch(`${flask_port}/categories/${categoryName.toLowerCase()}/messages`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json"
        }
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
  }

  useEffect(() => {
    fetchCategories();
  }, []);

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

  const MessageItem = ({ msg, onDelete }) => {
    const [isExpanded, setIsExpanded] = useState(false);
  
    const toggleExpansion = () => {
      setIsExpanded(!isExpanded);
    };
  
    const shortenText = (text) => {
      return text.length > abridged_text_length ? text.slice(0, abridged_text_length) + '...' : text;
    };

    const shortenAndMarkupText = (text) => {
      const shortenedText = text.length > abridged_text_length ? text.slice(0, abridged_text_length) + '...' : text;
      const markedShortened = marked(shortenedText);
      return DOMPurify.sanitize(markedShortened);
    };
  
    const markedFull = (text) => {
      return DOMPurify.sanitize(marked(text));
    };

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

  return (
    <div className="message-history-container" style={{ opacity: isProcessing ? 0.5 : 1 }}>
      <div className="sidebar">
        <h2>Messages</h2>
        <div className="category-list">
          {categories && categories.length > 0 ? (
            categories.map(
              (category) => (
                <div key={category.id} className="category-item">
                  <div className="category-title" onClick={() => toggleCategory(category.id, category.name)}>
                    {category.name}
                  </div>
                  {expandedCategory === category.id && (
                    <div className="message-list">
                      {category.messages.length === 0 ? (
                        <p>Loading messages...</p>
                      ) : (
                        category.messages.map((msg) => (
                          <MessageItem
                            key={msg.id} 
                            msg={msg} 
                            onDelete={() => handleDeleteMessage(category.id, msg.id)} 
                          />
                        ))
                      )}
                    </div>
                  )}
                </div>
              )
            )
          ) : <div />}
        </div>
      </div>
    </div>
  );
};

export default MessageHistory;
