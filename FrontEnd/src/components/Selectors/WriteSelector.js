import React, { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import './styles/WriteSelector.css'; // Ensure this path matches your project structure

/**
 * WriteSelector Component
 * 
 * Allows the user to input any alphanumeric filename.
 * Updates the tags with the entered filename in the format { "write": "filename.txt" }.
 * Visually consistent with TagSelector components.
 * 
 * @param {string} write - Current value of the write tag.
 * @param {function} setTags - Function to update the tags.
 */
const WriteSelector = React.memo(({ write, setTags }) => {
    const [isEditing, setIsEditing] = useState(false);
    const [inputValue, setInputValue] = useState(write || '');
    const inputRef = useRef(null);

    /**
     * Focuses on the input field when entering edit mode.
     */
    useEffect(() => {
        if (isEditing && inputRef.current) {
            inputRef.current.focus();
        }
    }, [isEditing]);

    /**
     * Handles input value changes.
     *
     * @param {object} e - Event object.
     */
    const handleChange = (e) => {
        setInputValue(e.target.value);
    };

    /**
     * Commits the input value to the tags.
     */
    const commitValue = () => {
        const trimmedValue = inputValue.trim();
        if (trimmedValue) {
            setTags(prevTags => ({
                ...prevTags,
                write: trimmedValue,
            }));
            setIsEditing(false);
        } else {
            // If input is empty, remove the "write" tag
            setTags(prevTags => {
                const updatedTags = { ...prevTags };
                delete updatedTags.write;
                return updatedTags;
            });
            setIsEditing(false);
        }
    };

    /**
     * Cancels the editing and resets the input value.
     */
    const cancelEdit = () => {
        setInputValue(write || '');
        setIsEditing(false);
    };

    /**
     * Handles key down events for committing or cancelling.
     *
     * @param {object} e - Keyboard event object.
     */
    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            commitValue();
        } else if (e.key === 'Escape') {
            cancelEdit();
        }
    };

    /**
     * Handles the deletion of the write tag.
     */
    const handleDelete = () => {
        setTags(prevTags => {
            const updatedTags = { ...prevTags };
            delete updatedTags.write;
            return updatedTags;
        });
    };

    /**
     * Handles clicking on the tag to enter edit mode.
     */
    const handleTagClick = () => {
        setIsEditing(true);
    };

    /**
     * Renders the input field for editing or adding a write tag.
     */
    const renderInput = () => (
        <div className="write-selector-input-container">
            <input
                type="text"
                placeholder="Enter filename"
                value={inputValue}
                onChange={handleChange}
                onKeyDown={handleKeyDown}
                ref={inputRef}
                className="write-selector-input"
                aria-label="Write Tag Input"
            />
            <button
                onClick={commitValue}
                className="write-selector-submit-button"
                aria-label="Submit Write Tag"
                type="button"
            >
                ✔️
            </button>
            <button
                onClick={cancelEdit}
                className="write-selector-cancel-button"
                aria-label="Cancel Write Tag Editing"
                type="button"
            >
                ❌
            </button>
        </div>
    );

    /**
     * Renders the tag display with edit and delete options.
     */
    const renderTag = () => (
        <div className="write-selector-tag">
            <span className="write-selector-tag-value" onClick={handleTagClick}>
                {write}
            </span>
            <button
                onClick={handleDelete}
                className="write-selector-delete-button"
                aria-label="Delete Write Tag"
                type="button"
            >
                &times;
            </button>
        </div>
    );

    return (
        <div className="write-selector-container">
            {isEditing ? renderInput() : write ? renderTag() : (
                <button
                    onClick={() => setIsEditing(true)}
                    className="write-selector-add-button"
                    type="button"
                    aria-label="Add Write Tag"
                >
                    + Select Filename
                </button>
            )}
        </div>
    );
});

WriteSelector.propTypes = {
    write: PropTypes.string,
    setTags: PropTypes.func.isRequired,
};

WriteSelector.defaultProps = {
    write: '',
};

export default WriteSelector;
