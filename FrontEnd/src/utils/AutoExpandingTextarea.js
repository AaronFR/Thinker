import React, { useRef, useLayoutEffect, useCallback } from 'react';
import PropTypes from 'prop-types';

/**
 * Component that renders a textarea which automatically
 * expands its height as the user types, eliminating the need for scrolling.
 *
 * @param {string} value - The current value of the textarea.
 * @param {function} onChange - Callback function to handle changes to the textarea's value.
 * @param props - Additional props to be passed to the textarea element.
 */
const AutoExpandingTextarea = React.memo(
  ({ value, onChange, style, ...rest }) => {
    const textareaRef = useRef(null);

    // Adjust the textarea height to match its scrollHeight.
    const adjustHeight = useCallback(() => {
      const ta = textareaRef.current;
      if (ta) {
        ta.style.height = 'auto'; // Reset the height.
        ta.style.height = `${ta.scrollHeight}px`; // Set to new height.
      }
    }, []);

    // Update height after render based on the current value.
    useLayoutEffect(() => {
      adjustHeight();
    }, [value, adjustHeight]);

    const handleChange = (e) => {
      if (onChange) {
        onChange(e);
      }
      adjustHeight();
    };

    return (
      <textarea
        ref={textareaRef}
        value={value}
        onChange={handleChange}
        style={{ overflow: 'hidden', resize: 'none', ...style }}
        {...rest}
      />
    );
  }
);

AutoExpandingTextarea.propTypes = {
  value: PropTypes.string,
  onChange: PropTypes.func,
  style: PropTypes.object,
};

AutoExpandingTextarea.defaultProps = {
  value: '',
  onChange: () => {},
  style: {},
};

export default AutoExpandingTextarea;
