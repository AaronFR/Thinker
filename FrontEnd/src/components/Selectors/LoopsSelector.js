// LoopsSelector.js

import React from 'react';
import PropTypes from 'prop-types';
import TagSelector from './TagsSelector';

/**
 * LoopsSelector Component
 * 
 * Allows users to select the number of loops for processing.
 * 
 * @param {number} selectedNumberOfLoops - Current selected number of loops.
 * @param {function} setLoops - Function to update the selected number of loops.
 */
const LoopsSelector = React.memo(({ selectedNumberOfLoops, setTags }) => {
  const loopOptions = [
    { value: 2, label: "Two Loops (2)" },
    { value: 3, label: "Three Loops (3)" },
    { value: 4, label: "Four Loops (4)" },
    { value: 5, label: "Five Loops (5)" },
  ];

  return (
    <div 
      className='loops-selector-container'
      data-tooltip-id="tooltip"
      data-tooltip-content="Number of times the loop workflow will iterate over your prompt, reviewing and re-writing it each time."
      data-tooltip-place="bottom"
    >
      <TagSelector
        selectedValue={selectedNumberOfLoops}
        setTags={setTags}
        options={loopOptions}
        placeholder="Loops"
        className="loops-selector"
      />
    </div>
    
  );
});

LoopsSelector.propTypes = {
  selectedNumberOfLoops: PropTypes.number.isRequired,
  setLoops: PropTypes.func.isRequired,
};

export default LoopsSelector;
