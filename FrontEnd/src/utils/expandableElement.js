import React, { useState, useCallback } from 'react';
import PropTypes from 'prop-types';

import './styles/expandableElement.css';

/**
 * ExpandableElement
 * ==================
 *
 * A modular React component that can be expanded and minimized to show different content.
 *
 * The component allows for separate minimized and maximized views. Child elements retain their
 * functionalities irrespective of the expansion state.
 *
 * Usage:
 * ------
 *
 * <ExpandableElement
 *   minContent={<Header />}
 *   maxContent={<DetailedView />}
 *   initiallyExpanded={false}
 *   toggleButtonLabel="Toggle View"
 * />
 * 
 * @param {node}minContent - The content to display when the element is minimized.
 * @param {node} maxContent - The content to display when the element is expanded.
 * @param {bool} initiallyExpanded - Determines if the component is initially expanded. Defaults to false.
 * @param {string} toggleButtonLabel - (string): Custom label for the toggle button. Defaults to '-' when expanded and '+' when minimized.
 */
const ExpandableElement = React.memo(({
    minContent,
    maxContent,
    initiallyExpanded = false,
    toggleButtonLabel,
}) => {
    const [isExpanded, setIsExpanded] = useState(initiallyExpanded);

    /**
     * Toggles the expansion state of the component.
     */
    const toggleExpansion = useCallback(() => {
        setIsExpanded((prev) => !prev);
    }, []);

    /**
     * Determines the label for the toggle button.
     * Defaults to '+' when collapsed and '-' when expanded if no custom label is provided.
     */
    const buttonLabel = toggleButtonLabel || (isExpanded ? '-' : '+');

    return (
        <div className='expandable-element'>
            {isExpanded ? maxContent : minContent}
            <button
                className="min-max-button"
                onClick={toggleExpansion}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') toggleExpansion(); }}
                aria-expanded={isExpanded}
                aria-label="Toggle content visibility"
            >
                {buttonLabel}
            </button>
        </div>
    );
});

ExpandableElement.propTypes = {
    minContent: PropTypes.node.isRequired,
    maxContent: PropTypes.node.isRequired,
    initiallyExpanded: PropTypes.bool,
    toggleButtonLabel: PropTypes.string,
};
ExpandableElement.defaultProps = {
    initiallyExpanded: false,
    toggleButtonLabel: '',
};

export default ExpandableElement;
