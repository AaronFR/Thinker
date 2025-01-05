import React from 'react';
import PropTypes from 'prop-types';

import './styles/PersonaSelector.css';

/**
 * PersonaSelector Component
 * 
 * Allows users to select a persona from a dropdown list.
 * Provides an option for auto detection of persona with feedback.
 * 
 * @param {string} selectedPersona - Current selected persona.
 * @param {function} setSelectedPersona - Function to update the selected persona.
 * @param {function} autoDetectedPersona - The auto-detected persona label to display.
 */
const PersonaSelector = ({ selectedPersona, setSelectedPersona, autoDetectedPersona }) => {
    return (
        <div className="persona-selector" style={{ marginBottom: '20px' }}>
            <label htmlFor="persona-select" className="visually-hidden">
                Select Persona:
            </label>
            <select 
                id="persona-select"
                value={selectedPersona} 
                onChange={(e) => setSelectedPersona(e.target.value)}
                className="dropdown"
                aria-label="Select a persona"
            >
                <option value="auto">Auto - {autoDetectedPersona}</option>
                <option value="coder">💻 Coder</option>
                <option value="writer">✍ Writer</option>
                {/* Add more personas as needed */}
            </select>
        </div>
    );
};

PersonaSelector.propTypes = {
    selectedPersona: PropTypes.string.isRequired,
    setSelectedPersona: PropTypes.func.isRequired,
    autoDetectedPersona: PropTypes.string.isRequired,
};

export default PersonaSelector;
