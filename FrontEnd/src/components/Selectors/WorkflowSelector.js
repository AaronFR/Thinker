// WorkflowSelector.js

import React from 'react';
import PropTypes from 'prop-types';
import TagSelector from './TagsSelector';
import TooltipConstants from '../../constants/tooltips';

/**
 * WorkflowSelector Component
 * 
 * Allows users to select a workflow from a dropdown list.
 * 
 * @param {string} selectedWorkflow - Current selected workflow.
 * @param {function} setTags - Function to update the selected tags.
 */
const WorkflowSelector = React.memo(({ selectedWorkflow, setTags }) => {
  const workflows = [
    { value: "chat", label: "🗣 Chat" },
    { value: "write", label: "✍ Write" },
    { value: "auto", label: "Σ For Each" },
    { value: "loop", label: "➿ Loop" }
  ];

  return (
    <div
      className='workflow-selector-container'
      data-tooltip-id="tooltip"
      data-tooltip-content={TooltipConstants.workflowSelector}
      data-tooltip-place="top"
    >
      <TagSelector
        selectedValue={selectedWorkflow}
        setTags={setTags}
        options={workflows}
        placeholder="Workflow"
        className="workflow-selector"
      />
    </div>
    
  );
});

WorkflowSelector.propTypes = {
  selectedWorkflow: PropTypes.string.isRequired,
  setTags: PropTypes.func.isRequired,
};

export default WorkflowSelector;
