import React, { useState, useEffect, useRef, useCallback } from 'react';
import { apiFetch } from '../utils/authUtils';
import { updateCategoryDescription } from '../constants/endpoints';
import AutoExpandingTextarea from '../utils/AutoExpandingTextarea';
import { shortenText } from '../utils/textUtils';


const CategoryDescriptionEditor = ({ categoryName, category_description, onUpdateDescription, ...rest }) => {
  const [description, setDescription] = useState(category_description);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);

  const typingTimer = useRef(null);
  const debounceDelay = 2000; // 2 seconds debounce period

  const saveDescription = useCallback(
    async (newDescription) => {
      setIsSaving(true);
      try {
        const response = await apiFetch(updateCategoryDescription, {
          method: 'POST',
          body: JSON.stringify({
            category_name: categoryName,
            new_category_description: newDescription,
          }),
        });

        if (!response.ok) {
          throw new Error('Failed to save category description');
        }

        // Update the parent's local state after a successful save!
        if (onUpdateDescription) {
          onUpdateDescription(categoryName, newDescription);
        }
        
      } catch (err) {
        console.error('Error while saving category description:', err);
        setError(err.message);
      } finally {
        setIsSaving(false);
      }
    },
    [categoryName, onUpdateDescription]
  );

  useEffect(() => {
    return () => {
      if (typingTimer.current) {
        clearTimeout(typingTimer.current);
      }
    };
  }, []);

  const handleInputChange = (e) => {
    e.stopPropagation();
    const newValue = e.target.value;
    setDescription(newValue);

    if (typingTimer.current) {
      clearTimeout(typingTimer.current);
    }

    typingTimer.current = setTimeout(() => {
      saveDescription(newValue);
    }, debounceDelay);
  };

  const handleDisplayClick = (e) => {
    e.stopPropagation();
    setIsEditing(true);
  };

  const handleBlur = (e) => {
    e.stopPropagation();
    setIsEditing(false);
  };

  const stopPropagation = (e) => {
    e.stopPropagation();
  }

  return (
    <div className="category-description category-description-editor">
      {isSaving && <div className="saving-indicator">Saving...</div>}
      {error && <div className="error-message">{error}</div>}
      
      {isEditing ? (
        <AutoExpandingTextarea
          value={description}
          className="textarea response-textarea"
          onChange={handleInputChange}
          onClick={stopPropagation}
          onBlur={handleBlur}
        />
      ) : (
        <div
          className="description-display"
          onClick={handleDisplayClick}
          {...rest}
        >
          {shortenText(description, 500) || 'Click to edit category description'}
        </div>
      )}
    </div>
  );
};

export default CategoryDescriptionEditor;