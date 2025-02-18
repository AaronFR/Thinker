import React, { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import TooltipConstants from '../../constants/tooltips';

import './styles/WriteSelector.css'; // Ensure this path matches your project structure

/**
 * PagesSelector Component
 * 
 * Allows the user to input an integer value determining the number of pages.
 * Provides validation to ensure only positive integers are accepted.
 * Incorporates editing functionality similar to WriteSelector.
 * 
 * @param {number} pages - Current number of pages.
 * @param {function} setTags - Function to update the prompts tags.
 */
const PagesSelector = React.memo(({ pages, setTags }) => {
    const [isEditing, setIsEditing] = useState(false);
    const [inputValue, setInputValue] = useState(pages || '');
    const [error, setError] = useState('');
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
     * Handles input value changes and validates the input.
     *
     * @param {object} e - Event object.
     */
    const handleChange = (e) => {
        const { value } = e.target;
        setInputValue(value);

        // Validate input: It should be a positive integer
        if (value === '' || /^[1-9]\d*$/.test(value)) {
            setError(''); // Clear error
        } else {
            setError('Please enter a valid positive integer'); // Set error
        }
    };

    /**
     * Commits the input value if valid to the pages state.
     */
    const commitValue = () => {
        if (error === '' && inputValue !== '') {
            setTags(prevTags => ({
                ...prevTags,
                pages: Number(inputValue),
            }));
            setIsEditing(false);
        }
    };

    /**
     * Cancels the editing and resets the input value.
     */
    const cancelEdit = () => {
        setInputValue(pages || '');
        setError('');
        setIsEditing(false);
    };

    /**
     * Handles submitting the input on Enter key.
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
     * Handles the deletion of the pages tag.
     */
    const handleDelete = () => {
        setTags(prevTags => {
            const updatedTags = { ...prevTags };
            delete updatedTags.pages;
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
     * Renders the input field for editing or adding pages count.
     */
    const renderInput = () => (
        <div className="input-container">
            <input
                type="text"
                placeholder="Enter number of pages"
                value={inputValue}
                onChange={handleChange}
                onKeyDown={handleKeyDown}
                ref={inputRef}
                className={`input ${error ? 'error' : ''}`}
                aria-label="Pages Input"
            />
            <button
                onClick={commitValue}
                className="selector-submit-button"
                aria-label="Submit Pages Count"
                type="button"
            >
                ✔️
            </button>
            <button
                onClick={cancelEdit}
                className="selector-cancel-button"
                aria-label="Cancel Pages Count Editing"
                type="button"
            >
                ❌
            </button>
            {error && <span className="error-message">{error}</span>}
        </div>
    );

    /**
     * Renders the tag display with edit and delete options.
     */
    const renderTag = () => (
        <div className="pages-selector-tag">
            <span className="selector-tag-value" onClick={handleTagClick}>
                {pages} Pages
            </span>
            <button
                onClick={handleDelete}
                className="selector-delete-button"
                aria-label="Delete Pages Count"
                type="button"
            >
                &times;
            </button>
        </div>
    );

    return (
        <div className="selector-container">
            {isEditing ? renderInput() : pages ? renderTag() : (
                <button
                    onClick={() => setIsEditing(true)}
                    className="selector-add-button"
                    type="button"
                    aria-label="Add Pages Count"
                    data-tooltip-id="tooltip"
                    data-tooltip-html={TooltipConstants.pagesSelector}
                    data-tooltip-place="top"
                >
                    + Page Count
                </button>
            )}
        </div>
    );
});

PagesSelector.propTypes = {
    pages: PropTypes.number,
    setTags: PropTypes.func.isRequired,
};

PagesSelector.defaultProps = {
    pages: 0,
};

export default PagesSelector;
