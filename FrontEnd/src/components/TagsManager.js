import React, { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import PropTypes from 'prop-types';
import './styles/TagsManager.css';

/**
 * Default tags and their corresponding preferred values.
 */
const DEFAULT_TAGS = {
    model: ['gemini-2.0-flash', 'gemini-2.0-flash-lite-preview', 'o3-mini', 'gpt-4o-mini', 'gpt-4o', 'o1-mini'],
    category: [],
    write: ['example.txt'],
    'best of': [1, 2, 3],
    workflow: ['chat', 'write', 'auto', 'loop'],
};

/**
 * TagsManager component allows adding and deleting tags with optional default values.
 *
 * @param {object} tags - Current tags as a dictionary where keys are tag categories and values are tag values.
 * @param {function} setTags - Function to update tags.
 */
const TagsManager = ({ tags, setTags }) => {
    const [isAdding, setIsAdding] = useState(false);
    const [newTag, setNewTag] = useState({ field: '', value: '' });
    const [fieldSuggestions] = useState(Object.keys(DEFAULT_TAGS));

    const fieldInputRef = useRef(null);
    const valueInputRef = useRef(null);

    // Compute value suggestions based on current newTag.field
    const valueSuggestions = useMemo(() => {
        const trimmedField = newTag.field.trim();
        return DEFAULT_TAGS[trimmedField] || [];
    }, [newTag.field]);

    // Focus the field input when the form is shown
    useEffect(() => {
        if (isAdding) {
            fieldInputRef.current.focus();
        }
    }, [isAdding]);

    const resetAddForm = useCallback(() => {
        setIsAdding(false);
        setNewTag({ field: '', value: '' });
    }, []);

    const handleAddClick = useCallback(() => {
        setIsAdding(true);
    }, []);

    const handleFieldChange = useCallback((e) => {
        const value = e.target.value;
        setNewTag((prev) => ({ ...prev, field: value }));
        // valueSuggestions are computed via useMemo, no need to update state here.
    }, []);

    const handleValueChange = useCallback((e) => {
        setNewTag((prev) => ({ ...prev, value: e.target.value }));
    }, []);

    const handleFieldKeyDown = useCallback((e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            if (newTag.field.trim()) {
                // Ensure suggestions are updated via useMemo and then move focus:
                valueInputRef.current.focus();
            }
        }
    }, [newTag.field]);

    const handleValueKeyDown = useCallback((e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            if (newTag.value.trim()) {
                setTags((prevTags) => ({
                    ...prevTags,
                    [newTag.field.trim()]: newTag.value.trim(),
                }));
                resetAddForm();
            }
        }
    }, [newTag, resetAddForm, setTags]);

    const handleDelete = useCallback((key) => {
        setTags((prevTags) => {
            const updatedTags = { ...prevTags };
            delete updatedTags[key];
            return updatedTags;
        });
    }, [setTags]);

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
                    <div
                        className="add-tag-form"
                        role="dialog"
                        aria-modal="true"
                        aria-labelledby="add-tag-title"
                    >
                        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                            <input
                                type="text"
                                list="field-suggestions"
                                placeholder="Tag"
                                value={newTag.field}
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
                                value={newTag.value}
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
                            <button onClick={resetAddForm} className="button delete-button" type="button">
                                x
                            </button>
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
