import React, { Component } from 'react';
import PropTypes from 'prop-types';
import "./styles/expandableElement.css"

/**
 * ExpandableElement
 * ==================
 *
 * A modular React component that can be expanded and minimized to show different content.
 *
 * The component allows for separate minimized and maximized views. Child elements retain their
 * functionalities irrespective of the expansion state.
 *
 * Attributes:
 * -----------
 * - `minContent` : React node
 *     Content to display when the component is minimized.
 * - `maxContent` : React node
 *     Content to display when the component is maximized.
 * - `initiallyExpanded` : bool
 *     Determines whether the component is expanded on initial render.
 * - `toggleButtonLabel` : string
 *     Label for the toggle button.
 *
 * Usage:
 * ------
 * 

 * <ExpandableElement
 * minContent={<Header />}
 * maxContent={<DetailedView />}
 * initiallyExpanded={false}
 * toggleButtonLabel="Toggle View"
 * />
 */
class ExpandableElement extends Component {
    /**
     * Initialize the ExpandableElement component.
     *
     * @param {object} props - Component properties.
     */
    constructor(props) {
        super(props);
        this.state = {
            isExpanded: props.initiallyExpanded || true,
        };
        this.toggleExpansion = this.toggleExpansion.bind(this);
    }

    /**
     * Toggle the expansion state of the component.
     *
     * Changes the `isExpanded` state between true and false.
     */
    toggleExpansion() {
        this.setState((prevState) => ({
            isExpanded: !prevState.isExpanded,
        }));
    }

    /**
     * Render the ExpandableElement component.
     *
     * Displays either the minimized or maximized content based on the current state.
     * Includes a button to toggle between states.
     *
     * @returns {JSX.Element} The rendered component.
     */
    render() {
        const { minContent, maxContent, toggleButtonLabel } = this.props;
        const { isExpanded } = this.state;

        return (
            <>
                {isExpanded ? maxContent : minContent}
                <button onClick={this.toggleExpansion} className='min-max-button'>
                    {toggleButtonLabel || (isExpanded ? '-' : '+')}
                </button>
            </>
        );
    }
}

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
