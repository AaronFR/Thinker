// ModelSelector.js

import React, { useMemo } from 'react';
import PropTypes from 'prop-types';
import { components } from 'react-select';
import Select from 'react-select';
import TagSelector from './TagsSelector';

import openAiLogo from './styles/openAiLogo.png';
import googleLogo from './styles/googleLogo.png'; 
import TooltipConstants from '../../constants/tooltips';

import './styles/Selector.css';

/**
 * CustomOption Component
 *
 * Custom option with an image for the select options.  Uses the Gemini logo
 * for options with 'gemini' in their value, otherwise defaults to OpenAI logo.
 */
const CustomOption = (props) => {
  const { data } = props;
  const useGeminiLogo = data.value.includes('gemini'); //check if the value includes gemini

  return (
    <components.Option {...props}>
      <img
        src={useGeminiLogo ? googleLogo : openAiLogo}
        alt={useGeminiLogo ? "Gemini Logo" : "OpenAI Logo"}
        style={{ width: '20px', marginRight: '10px', color: 'black' }}
      />
      {props.label}
    </components.Option>
  );
};

const ModelSelector = React.memo(({ selectedModel, setTags, forTags, economicalMode }) => {
  const economicalModels = useMemo(() => [
    { value: "gemini-2.0-flash", label: "gemini-2.0-flash" },
    { value: "gemini-2.0-flash-lite-preview", label: "gemini-2.0-flash-lite-preview" },
    { value: "gpt-4o-mini", label: "gpt-4o-mini" },
  ], []);

  const allModels = useMemo(() => [
    { value: "gemini-2.0-flash", label: "gemini-2.0-flash" },
    { value: "gemini-2.0-flash-lite-preview", label: "gemini-2.0-flash-lite-preview" },
    { value: "gpt-4o-mini", label: "gpt-4o-mini" },
    { value: "o3-mini", label: "o3-mini" },
    { value: "o1-mini", label: "o1-mini" },
    { value: "gpt-4o", label: "gpt-4o" },
  ], []);

  // Derive the models to display based on economicalMode
  const modelsToDisplay = useMemo(() => (
    economicalMode ? economicalModels : allModels
  ), [economicalMode, economicalModels, allModels]);

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

  const handleChange = (selectedOption) => {
    setTags(selectedOption.value);  // Pass only the value
  };

  return (
    <div
      className="model-selector"
      data-tooltip-id="tooltip"
      data-tooltip-html={TooltipConstants.modelSelector}
      data-tooltip-place="top"
    >
      {forTags ? <TagSelector
        selectedValue={selectedModel}
        setTags={setTags}
        options={modelsToDisplay}
        placeholder="model"
        CustomOption={CustomOption}
        className="model-selector"
        
      /> : <Select
        className="dropdown model-selector"
        classNamePrefix="react-select"
        styles={customStyles}
        value={modelsToDisplay.find(option => option.value === selectedModel)}
        onChange={handleChange}
        options={modelsToDisplay}
        getOptionLabel={(option) => option.label}
        getOptionValue={(option) => option.value}
        placeholder="Select a model..."
        components={{ Option: CustomOption }}
      />
      }
    </div>
  );
});

CustomOption.propTypes = {
  data: PropTypes.shape({
    value: PropTypes.string.isRequired,
  }).isRequired,
};

ModelSelector.propTypes = {
  selectedModel: PropTypes.string.isRequired,
  setTags: PropTypes.func.isRequired,
};


export default ModelSelector;
