import React, { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import './styles/TagsManager.css';

/**
 * Default tags and their corresponding preferred values.
 */
const DEFAULT_TAGS = {
    model: ['gpt-4o', 'gpt-4o-mini', 'o1-mini', 'o1-preview'],
    category: [],
    write: ['example.txt']
};

/**
 * TagsManager component allows adding and deleting tags with optional default values.
 *
 * @param {object} tags - Current tags as a dictionary where keys are tag categories and values are tag values.
 * @param {function} setTags - Function to update tags.
 */
const TagsManager = ({ tags, setTags }) => {
    const [isAdding, setIsAdding] = useState(false);
    const [newField, setNewField] = useState('');
    const [newValue, setNewValue] = useState('');
    const [fieldSuggestions] = useState(Object.keys(DEFAULT_TAGS));
    const [valueSuggestions, setValueSuggestions] = useState([]);

    const fieldInputRef = useRef(null);
    const valueInputRef = useRef(null);

    /**
     * Focuses on the field input when adding a new tag.
     */
    useEffect(() => {
        if (isAdding) {
            fieldInputRef.current.focus();
        }
    }, [isAdding]);

    /**
     * Handles the Add button click to initiate tag addition.
     */
    const handleAddClick = () => {
        setIsAdding(true);
    };

    /**
     * Handles key down events for the field input.
     *
     * @param {object} e - The keyboard event object.
     */
    const handleFieldKeyDown = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            if (newField.trim()) {
                const trimmedField = newField.trim();
                if (DEFAULT_TAGS[trimmedField]) {
                    setValueSuggestions(DEFAULT_TAGS[trimmedField]);
                } else {
                    setValueSuggestions([]);
                }
                valueInputRef.current.focus();
            }
        }
    };

    /**
     * Handles key down events for the value input.
     *
     * @param {object} e - Event object.
     */
    const handleValueKeyDown = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            if (newValue.trim()) {
                setTags((prevTags) => ({
                    ...prevTags,
                    [newField.trim()]: newValue.trim(),
                }));
                resetAddForm(); 
            }
        }
    };

    /**
     * Resets the addition form to its initial state.
     */
    const resetAddForm = () => {
        setIsAdding(false);
        setNewField('');
        setNewValue('');
        setValueSuggestions([]);
    };

    /**
     * Handles the deletion of a tag.
     *
     * @param {string} key - Tag key to delete.
     */
    const handleDelete = (key) => {
        const updatedTags = { ...tags };
        delete updatedTags[key];
        setTags(updatedTags);
    };

    /**
     * Handles changes in the field input.
     *
     * @param {object} e - Event object.
     */
    const handleFieldChange = (e) => {
        const value = e.target.value;
        setNewField(value);
        if (DEFAULT_TAGS[value.trim()]) {
            setValueSuggestions(DEFAULT_TAGS[value.trim()]);
        } else {
            setValueSuggestions([]);
        }
    };

    /**
     * Handles changes in the value input.
     *
     * @param {object} e - Event object.
     */
    const handleValueChange = (e) => {
        setNewValue(e.target.value);
    };

    return (
        <div className="tags-manager">
            <ul className="tags-list">
                {Object.entries(tags).map(([key, value]) => (
                    <li key={key} className="tag-item">
                        <span>
                            <strong>{key}:</strong> {value}
                        </span>
                        <button
                            onClick={() => handleDelete(key)}
                            className="button delete-button"
                            aria-label={`Delete ${key} tag`}
                            type="button"
                        >
                            &times;
                        </button>
                    </li>
                ))}

                {!isAdding && (
                    <li className="add-tag-item">
                        <button
                            onClick={handleAddClick}
                            className="add-button"
                            type="button"
                            aria-label="Add new tag"
                        >
                            +
                        </button>
                    </li>
                )}
                {isAdding && (
                <div className="add-tag-form" role="dialog" aria-modal="true" aria-labelledby="add-tag-title">
                    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                        <input
                            type="text"
                            list="field-suggestions"
                            placeholder="Tag"
                            value={newField}
                            onChange={handleFieldChange}
                            onKeyDown={handleFieldKeyDown}
                            ref={fieldInputRef}
                            className="input-field"
                            aria-label="Tag Category"
                            required
                        />
                        <datalist id="field-suggestions">
                            {fieldSuggestions.map((field) => (
                                <option key={field} value={field} />
                            ))}
                        </datalist>
                        <input
                            type="text"
                            list="value-suggestions"
                            placeholder="Content"
                            value={newValue}
                            onChange={handleValueChange}
                            onKeyDown={handleValueKeyDown}
                            ref={valueInputRef}
                            className="input-value"
                            aria-label="Tag Value"
                            required
                        />
                        <datalist id="value-suggestions">
                            {valueSuggestions.map((val) => (
                                <option key={val} value={val} />
                            ))}
                        </datalist>
                        <button onClick={resetAddForm} className="button cancel-button" type="button">x</button>
                    </div>
                </div>
            )}
            </ul>
        </div>
    );
};

TagsManager.propTypes = {
    tags: PropTypes.object.isRequired,
    setTags: PropTypes.func.isRequired,
};

export default TagsManager;
