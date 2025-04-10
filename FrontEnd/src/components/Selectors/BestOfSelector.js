import React from 'react';
import PropTypes from 'prop-types';
import TagSelector from './TagsSelector';
import TooltipConstants from '../../constants/tooltips';

/** 
 * Allows users to select the number of runs for "Best Of" logic.
 * 
 * @param {number} selectedRuns - Current selected number of runs.
 * @param {function} setTags - Function to update the users tags.
 */
const BestOfSelector = React.memo(({ selectedRuns, setTags }) => {
  const runOptions = [
    { value: 1, label: "Disabled" },
    { value: 2, label: "2 Responses" },
    { value: 3, label: "3 Responses" },
    { value: 4, label: "4 Responses" },
    { value: 5, label: "5 Responses" },
  ];

  return (
    <div 
      className='loops-selector-container'
      data-tooltip-id="tooltip"
      data-tooltip-html={TooltipConstants.bestOfSelector}
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
  selectedRuns: PropTypes.number,
  setTags: PropTypes.func.isRequired,
};

export default BestOfSelector;
