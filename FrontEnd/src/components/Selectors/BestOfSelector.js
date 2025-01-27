// BestOfSelector.js

import React from 'react';
import PropTypes from 'prop-types';
import TagSelector from './TagsSelector';

/**
 * BestOfSelector Component
 * 
 * Allows users to select the number of runs for "Best Of" logic.
 * 
 * @param {number} selectedRuns - Current selected number of runs.
 * @param {function} setTags - Function to update the users tags.
 */
const BestOfSelector = React.memo(({ selectedRuns, setTags }) => {
  const runOptions = [
    { value: 1, label: "Disabled (1 run)" },
    { value: 2, label: "Two (2 runs)" },
    { value: 3, label: "Three (3 runs)" },
    { value: 4, label: "Four (4 runs)" },
    { value: 5, label: "Five (5 runs)" },
  ];

  return (
    <div 
      className='loops-selector-container'
      data-tooltip-id="tooltip"
      data-tooltip-content="If enabled each step will run multiple times, a LLM call will be then used to review the various outputs and select for the best one. You can change the selection criteria system message in the settings"
      data-tooltip-place="top"
    >
      <TagSelector
        selectedValue={selectedRuns}
        setTags={setTags}
        options={runOptions}
        placeholder="Best of"
        className="best-of-selector"
      />
    </div>
  );
});

BestOfSelector.propTypes = {
  selectedRuns: PropTypes.number.isRequired,
  setRuns: PropTypes.func.isRequired,
};

export default BestOfSelector;
