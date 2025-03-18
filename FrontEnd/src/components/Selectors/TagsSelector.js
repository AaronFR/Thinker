import React, { useCallback, useMemo } from 'react';
import PropTypes from 'prop-types';
import Select from 'react-select';
import Creatable from 'react-select/creatable';

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
 * @param {boolean} creatable - (Optional) Allow creating new options. Defaults to false
 */
const TagSelector = React.memo(({
  selectedValue,
  setTags,
  options,
  placeholder,
  CustomOption,
  className = '',
  creatable = false,
}) => {
  const handleChange = useCallback(
    (selectedOption) => {
      setTags((prevTags) => ({ ...prevTags, [placeholder.toLowerCase()]: selectedOption?.value || '' })); // handles null/undefined selectedOption
    },
    [setTags, placeholder]
  );

  const customStyles = useMemo(() => ({
    option: (provided, state) => ({
      ...provided,
      display: 'flex',
      alignItems: 'center',
      color: 'var(--color-input-text)',
      padding: '6px 8px',
      fontSize: '12px',
    }),
  }), []); // Empty dependency array since styles don't depend on component state

  const value = useMemo(() => {
    return options.find(option => option.value === selectedValue)
  }, [options, selectedValue]);

  const selectProps = useMemo(() => ({
    value: value,
    onChange: handleChange,
    options: options,
    placeholder: placeholder,
    styles: customStyles,
    className: `dropdown ${className}`,
    classNamePrefix: 'react-select',
  }), [value, handleChange, options, placeholder, customStyles, className]);

  const SelectComponent = creatable ? Creatable : Select;


  return (
    <div className={`${placeholder.toLowerCase()}-selector`}>
      <SelectComponent
        {...selectProps}
        components={CustomOption ? { Option: CustomOption } : undefined} // Conditionally set components
      />
    </div>
  );
});

TagSelector.propTypes = {
  selectedValue: PropTypes.string.isRequired,
  setTags: PropTypes.func.isRequired,
  options: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    })
  ).isRequired,
  placeholder: PropTypes.string.isRequired,
  CustomOption: PropTypes.elementType,
  className: PropTypes.string,
  creatable: PropTypes.bool,
};

export default TagSelector;
