import React from 'react';
import PropTypes from 'prop-types';

import TagSelector from './TagsSelector';
import TooltipConstants from '../../constants/tooltips';



/** 
 * Allows users to select a persona from a dropdown list.
 * Provides an option for auto detection of persona with feedback.
 * 
 * @param {string} selectedPersona - Current selected persona.
 * @param {function} setTags - Function to update the selected persona in the prompts tags.
 */
const PersonaSelector = React.memo(({ selectedPersona, setTags, isLoading }) => {
    const personas = [
        { value: "coder", label: "💻 Coder" },
        { value: "writer", label: "✍ Writer" },
    ];
    
    return (
        <div 
            className={`persona-selector ${isLoading ? 'loading' : ''}`}
            data-tooltip-id="tooltip"
            data-tooltip-content={TooltipConstants.personaSelector}
            data-tooltip-place="top"
        >
            <TagSelector
                selectedValue={selectedPersona}
                setTags={setTags}
                options={personas}
                placeholder="Persona"
                className="dropdown"
            />
        </div>
    );
});

PersonaSelector.propTypes = {
    selectedPersona: PropTypes.string,
    setTags: PropTypes.func.isRequired,
};

export default PersonaSelector;
