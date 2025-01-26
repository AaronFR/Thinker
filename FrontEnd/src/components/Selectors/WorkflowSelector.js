// WorkflowSelector.js

import React from 'react';
import PropTypes from 'prop-types';
import TagSelector from '../TagsSelector';

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
    <TagSelector
      selectedValue={selectedWorkflow}
      setTags={setTags}
      options={workflows}
      placeholder="Workflow"
      className="workflow-selector"
    />
  );
});

WorkflowSelector.propTypes = {
  selectedWorkflow: PropTypes.string.isRequired,
  setTags: PropTypes.func.isRequired,
};

export default WorkflowSelector;
