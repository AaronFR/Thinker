import React, { useState, useEffect, useRef, useCallback } from 'react';
import { apiFetch } from '../utils/authUtils';
import { updateCategoryInstructions } from '../constants/endpoints';
import AutoExpandingTextarea from '../utils/AutoExpandingTextarea';
import { shortenText } from '../utils/textUtils';


const CategoryInstructionsEditor = ({ categoryName, category_instructions, onUpdateInstructions, ...rest }) => {
  const [instructions, setInstructions] = useState(category_instructions);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);

  const typingTimer = useRef(null);
  const debounceDelay = 2000; // 2 seconds debounce period

  const saveInstructions = useCallback(
    async (newInstructions) => {
      setIsSaving(true);
      try {
        const response = await apiFetch(updateCategoryInstructions, {
          method: 'POST',
          body: JSON.stringify({
            category_name: categoryName,
            new_category_instructions: newInstructions,
          }),
        });

        if (!response.ok) {
          throw new Error('Failed to save category instructions');
        }

        // Update the parent's local state after a successful save!
        if (onUpdateInstructions) {
          onUpdateInstructions(categoryName, newInstructions);
        }
        
      } catch (err) {
        console.error('Error while saving category instructions:', err);
        setError(err.message);
      } finally {
        setIsSaving(false);
      }
    },
    [categoryName, onUpdateInstructions]
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
    setInstructions(newValue);

    if (typingTimer.current) {
      clearTimeout(typingTimer.current);
    }

    typingTimer.current = setTimeout(() => {
      saveInstructions(newValue);
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
    <div className="category-instructions category-instructions-editor">
      {isSaving && <div className="saving-indicator">Saving...</div>}
      {error && <div className="error-message">{error}</div>}
      
      {isEditing ? (
        <AutoExpandingTextarea
          value={instructions}
          className="textarea response-textarea"
          onChange={handleInputChange}
          onClick={stopPropagation}
          onBlur={handleBlur}
        />
      ) : (
        <div
          className="instructions-display"
          onClick={handleDisplayClick}
          {...rest}
        >
          {shortenText(instructions, 500) || 'Click to edit category instructions'}
        </div>
      )}
    </div>
  );
};

export default CategoryInstructionsEditor;