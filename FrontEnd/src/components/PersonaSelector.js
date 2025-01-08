import React, {useCallback} from 'react';
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
const PersonaSelector = React.memo(({ selectedPersona, setSelectedPersona, autoDetectedPersona }) => {
    const personas = [
        { value: "auto", label: `Auto - ${autoDetectedPersona || 'Not detected'}` },
        { value: "coder", label: "💻 Coder" },
        { value: "writer", label: "✍ Writer" },
        // Additional personas can be added here
    ];

    const handleChange = useCallback((event) => {
        setSelectedPersona(event.target.value);
    }, [setSelectedPersona]);
    
    return (
        <div className="persona-selector">
            <select 
                id="persona-select"
                value={selectedPersona} 
                onChange={handleChange}
                className="dropdown"
                aria-label="Select a persona"
            >
                {personas.map((persona) => (
                    <option key={persona.value} value={persona.value}>
                        {persona.label}
                    </option>
                ))}
            </select>
        </div>
    );
});

PersonaSelector.propTypes = {
    selectedPersona: PropTypes.string.isRequired,
    setSelectedPersona: PropTypes.func.isRequired,
    autoDetectedPersona: PropTypes.string.isRequired,
};

export default PersonaSelector;
