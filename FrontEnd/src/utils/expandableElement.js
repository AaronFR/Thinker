import React, { useState } from 'react';
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
 */
const ExpandableElement = React.memo(({
    minContent,
    maxContent,
    initiallyExpanded = false,
    toggleButtonLabel,
}) => {
    const [isExpanded, setIsExpanded] = useState(initiallyExpanded);

    const toggleExpansion = () => {
        setIsExpanded((prev) => !prev);
    };

    const buttonLabel = toggleButtonLabel || (isExpanded ? '-' : '+');

    return (
        <>
            {isExpanded ? maxContent : minContent}
            <button
                onClick={toggleExpansion}
                className="min-max-button"
                aria-expanded={isExpanded}
                aria-label="Toggle content visibility"
            >
                {buttonLabel}
            </button>
        </>
    );
});

ExpandableElement.propTypes = {
    /**
     * Content to display when minimized.
     */
    minContent: PropTypes.node.isRequired,

    /**
     * Content to display when maximized.
     */
    maxContent: PropTypes.node.isRequired,

    /**
     * Determines if the component is expanded on initial render.
     */
    initiallyExpanded: PropTypes.bool,

    /**
     * Label for the toggle button.
     */
    toggleButtonLabel: PropTypes.string,
};

ExpandableElement.defaultProps = {
    initiallyExpanded: false,
    toggleButtonLabel: '',
};

export default ExpandableElement;
