import React, { useCallback } from 'react';
import PropTypes from 'prop-types';

import Select, { components } from 'react-select';

import './styles/PersonaSelector.css';
import openAiLogo from './styles/openAiLogo.png';

/**
 * Custom Option component to include images
 */
const CustomOption = (props) => (
  <components.Option {...props}>
    <img
      src={openAiLogo}
      alt="OpenAI Logo"
      style={{ width: '20px', marginRight: '10px', color: 'black', fontSize: "50px" }}
    />
    {props.label}
  </components.Option>
);

/**
 * ModelSelector Component
 * 
 * Allows users to select a model from a dropdown list with images.
 * 
 * @param {string} selectedModel - Current selected model.
 * @param {function} setTags - Function to update the selected tags - remember to only change model values.
 */
const ModelSelector = React.memo(({ selectedModel, setTags }) => {
  const models = [
    { value: "gpt-4o-mini", label: "gpt-4o-mini" },
    { value: "gpt-4o", label: "gpt-4o" },
    { value: "o1-mini", label: "o1-mini" },
    { value: "o1-preview", label: "o1-preview" }
  ];

  const handleChange = useCallback(
    (selectedOption) => {
      setTags(prevTags => ({ ...prevTags, model: selectedOption.value }));
    },
    [setTags]
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
  

  return (
    <div className="model-selector">
      <Select
        value={models.find(model => model.value === selectedModel)}
        onChange={handleChange}
        options={models}
        placeholder="LLM"
        components={{ Option: CustomOption }}
        styles={customStyles}
        aria-label="Select a model"
        className="dropdown"
        classNamePrefix="react-select"
      />
    </div>
  );
});

ModelSelector.propTypes = {
  selectedModel: PropTypes.string.isRequired,
  setTags: PropTypes.func.isRequired,
};

export default ModelSelector;
