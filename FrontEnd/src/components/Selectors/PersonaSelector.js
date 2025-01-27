import React, {useCallback} from 'react';
import PropTypes from 'prop-types';

import { Tooltip } from 'react-tooltip';

import Select, { components } from 'react-select';



/**
 * PersonaSelector Component
 * 
 * Allows users to select a persona from a dropdown list.
 * Provides an option for auto detection of persona with feedback.
 * 
 * @param {string} selectedPersona - Current selected persona.
 * @param {function} setSelectedPersona - Function to update the selected persona.
 */
const PersonaSelector = React.memo(({ selectedPersona, setSelectedPersona }) => {
    const personas = [
        { value: "coder", label: "💻 Coder" },
        { value: "writer", label: "✍ Writer" },
    ];

    const handleChange = useCallback((event) => {
        setSelectedPersona(event.value);
    }, [setSelectedPersona]);

    const customStyles = {
    option: (provided, state) => ({
        ...provided,
        display: 'flex',
        alignItems: 'center',
        color: 'var(--color-input-text)',
        padding: '6px 8px',
        fontSize: '12px',
    }),
    };
    
    return (
        <div 
            className="persona-selector"
            data-tooltip-id="tooltip"
            data-tooltip-content="Select Focus. Focus determines both how the application will respond and 'think' about your response but also how workflows are structured and run against your prompt"
            data-tooltip-place="top"
        >
            <Select
                value={personas.find(personas => personas.value === selectedPersona)}
                options={personas}
                placeholder="Speciality"
                id="persona-select"
                onChange={handleChange}
                styles={customStyles}
                aria-label="Select a persona"
                className="dropdown"
                classNamePrefix="react-select"
            />
        </div>
    );
});

PersonaSelector.propTypes = {
    selectedPersona: PropTypes.string.isRequired,
    setSelectedPersona: PropTypes.func.isRequired,
};

export default PersonaSelector;
