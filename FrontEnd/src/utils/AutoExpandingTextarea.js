import React, { useState, useRef, useLayoutEffect } from 'react';
import PropTypes from 'prop-types'

/**
 * AutoExpandingTextarea
 *
 * A React component that renders a textarea which automatically
 * expands its height as the user types, eliminating the need for scrolling.
 * 
 * ToDo: rescales -except for new line, why?
 *
 * @param {string} value - The current value of the textarea.
 * @param {function} onChange - Callback function to handle changes to the textarea's value.
 * @param props - Additional props to be passed to the textarea element.
 */
const AutoExpandingTextarea = ({ value, onChange, ...props }) => {
    const textareaRef = useRef(null)
    const [text, setText] = useState(value || '')

    /**
     * Synchronizes the internal text state with the value prop
     * and adjusts the textarea height based on content.
     */
    useLayoutEffect(() => {
        setText(value || '')
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto' // Reset height to calculate scrollHeight accurately
            textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
        }
    }, [value])

    /**
     * handleChange
     *
     * Handles the change event for the textarea, updating state and
     * invoking the provided onChange callback if available.
     *
     * @param {Object} e - The event object from the textarea.
     */
    const handleChange = (e) => {
        setText(e.target.value)
        if (onChange) {
            onChange(e)
        }
    }

    return (
        <textarea
            {...props}
            ref={textareaRef}
            value={text}
            onChange={handleChange}
            style={{
                overflow: 'hidden',
                resize: 'none',
            }}
        />
    )
}

AutoExpandingTextarea.propTypes = {
    value: PropTypes.string,
    onChange: PropTypes.func,
}

AutoExpandingTextarea.defaultProps = {
    value: '',
    onChange: null,
}

export default AutoExpandingTextarea
