import React, { useState, useRef, useEffect } from 'react';

/**
 * AutoExpandingTextarea
 *
 * A React component that renders a textarea which automatically
 * expands its height as the user types, eliminating the need for scrolling.
 *
 * :props:
 *     - value (string): The current value of the textarea.
 *     - onChange (function): Callback function to handle changes to the textarea's value.
 *     - ...props: Additional props to be passed to the textarea element.
 */
const AutoExpandingTextarea = ({ value, onChange, ...props }) => {
    const textareaRef = useRef(null)
    const [text, setText] = useState(value || '')

    /**
     * Sync text state with value prop
     */
    useEffect(() => {
        setText(value || '')
    }, [value])

    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto'
            textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
        }
    }, [text])

    /**
     * handleChange
     *
     * Handles the change event for the textarea, updating state and
     * invoking the provided onChange callback if available.
     *
     * :param {Object} e - The event object from the textarea.
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

export default AutoExpandingTextarea
