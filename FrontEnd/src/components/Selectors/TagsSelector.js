import React, { useCallback } from 'react';
import PropTypes from 'prop-types';
import Select from 'react-select';

import './styles/Selector.css';

/** 
 * A reusable select component for selecting tags.
 * 
 * @param {string} selectedValue - Currently selected value.
 * @param {function} setTags - Function to update the selected tags.
 * @param {Array} options - Array of options for the select.
 * @param {string} placeholder - Placeholder text for the select.
 * @param {React.Component} CustomOption - (Optional) Custom option component.
 * @param {string} className - (Optional) Additional class name for styling.
 */
const TagSelector = React.memo(({
  selectedValue,
  setTags,
  options,
  placeholder,
  CustomOption,
  className = '',
}) => {
  const handleChange = useCallback(
    (selectedOption) => {
      setTags(prevTags => ({ ...prevTags, [placeholder.toLowerCase()]: selectedOption.value }));
    },
    [setTags, placeholder]
  );

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

  const selectProps = {
    value: options.find(option => option.value === selectedValue),
    onChange: handleChange,
    options: options,
    placeholder: placeholder,
    styles: customStyles,
    className: `dropdown ${className}`,
    classNamePrefix: 'react-select',
  };

  if (CustomOption) {
    selectProps.components = { Option: CustomOption };
  }

  return (
    <div className={`${placeholder.toLowerCase()}-selector`}>
      <Select {...selectProps} />
    </div>
  );
});

TagSelector.propTypes = {
  selectedValue: PropTypes.string.isRequired,
  setTags: PropTypes.func.isRequired,
  options: PropTypes.arrayOf(PropTypes.shape({
    value: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
  })).isRequired,
  placeholder: PropTypes.string.isRequired,
  CustomOption: PropTypes.elementType,
  className: PropTypes.string,
};

export default TagSelector;
