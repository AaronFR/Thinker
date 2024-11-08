import React, { useState, useRef, useEffect } from 'react';
import './styles/TagsManager.css';
import PropTypes from 'prop-types';

const TagsManager = ({ tags, setTags }) => {

  const [isAdding, setIsAdding] = useState(false);
  const [newField, setNewField] = useState('');
  const [newValue, setNewValue] = useState('');

  const fieldInputRef = useRef(null);
  const valueInputRef = useRef(null);

  const handleAddClick = () => {
    setIsAdding(true);
  };

  useEffect(() => {
    if (isAdding) {
      fieldInputRef.current.focus();
    }
  }, [isAdding]);

  const handleFieldKeyDown = (e) => {
    if (e.key === 'Enter' && newField.trim() !== '') {
      e.preventDefault()
      e.stopPropagation();
      valueInputRef.current.focus();
    }
  };

  const handleValueKeyDown = (e) => {
    if (e.key === 'Enter' && newValue.trim() !== '') {
      e.preventDefault()
      e.stopPropagation();
      setTags({ ...tags, [newField.trim()]: newValue.trim() });
      setIsAdding(false);
      setNewField('');
      setNewValue('');
    }
  };

  const handleDelete = (key) => {
    const updatedTags = { ...tags };
    delete updatedTags[key];
    setTags(updatedTags);
  };

  return (
    <div className="tags-manager">
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <ul className="tags-list">
          {Object.entries(tags).map(([key, value]) => (
            <li key={key} className="tag-item">
              <span><strong>{key}:</strong> {value}</span>
              <button onClick={() => handleDelete(key)} className="delete-button" aria-label={`Delete ${key} tag`} type="button">
                &times;
              </button>
            </li>
          ))}
          {!isAdding && (
            <li className="add-tag-item">
              <button onClick={handleAddClick} className="add-button" type="button">+</button>
            </li>
          )}
        </ul>
        {isAdding && (
          <div className="add-tag-form">
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
              <input
                type="text"
                placeholder="Field"
                value={newField}
                onChange={(e) => setNewField(e.target.value)}
                onKeyDown={handleFieldKeyDown}
                ref={fieldInputRef}
                className="input-field"
                aria-label="Tag Field"
              />
              <input
                type="text"
                placeholder="Value"
                value={newValue}
                onChange={(e) => setNewValue(e.target.value)}
                onKeyDown={handleValueKeyDown}
                ref={valueInputRef}
                className="input-value"
                aria-label="Tag Value"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

TagsManager.propTypes = {
  tags: PropTypes.object.isRequired,
  setTags: PropTypes.func.isRequired,
};

export default TagsManager;
