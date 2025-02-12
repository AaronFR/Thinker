// ModelSelector.js

import React from 'react';
import PropTypes from 'prop-types';
import { components } from 'react-select';

import TagSelector from './TagsSelector';

import openAiLogo from './styles/openAiLogo.png';
import TooltipConstants from '../../constants/tooltips';

/**
 * CustomOption Component
 * 
 * Custom option with an image for the select options.
 */
const CustomOption = (props) => (
  <components.Option {...props}>
    <img
      src={openAiLogo}
      alt="OpenAI Logo"
      style={{ width: '20px', marginRight: '10px', color: 'black' }}
    />
    {props.label}
  </components.Option>
);

const ModelSelector = React.memo(({ selectedModel, setTags }) => {
  const models = [
    { value: "gpt-4o-mini", label: "gpt-4o-mini" },
    { value: "gpt-4o", label: "gpt-4o" },
    { value: "o1-mini", label: "o1-mini" },
    { value: "o1-preview", label: "o1-preview" }
  ];

  return (
    <div
      className="model-selector"
      data-tooltip-id="tooltip"
      data-tooltip-html={TooltipConstants.modelSelector}
      data-tooltip-place="top"
    >
      <TagSelector
        selectedValue={selectedModel}
        setTags={setTags}
        options={models}
        placeholder="model"
        CustomOption={CustomOption}
        className="model-selector"
        
      />
    </div>
  );
});

ModelSelector.propTypes = {
  selectedModel: PropTypes.string.isRequired,
  setTags: PropTypes.func.isRequired,
};

export default ModelSelector;
