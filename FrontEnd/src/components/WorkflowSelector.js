import React, {useCallback} from 'react';
import PropTypes from 'prop-types';

import Select, { components } from 'react-select';

import './styles/PersonaSelector.css';

/**
 * WorkflowSelector Component
 * 
 * Allows users to select a workflow from a dropdown list.
 * 
 * @param {string} selectedWorkflow - Current selected workflow.
 * @param {function} setTags - Function to update the selected tags - remember to only change workflow values.
 */
const WorkflowSelector = React.memo(({ selectedWorkflow, setTags }) => {
    const workflows = [
        { value: "chat", label: "🗣 Chat" },
        { value: "write", label: "✍ Write" },
        { value: "auto", label: "Σ For Each" },
        { value: "loop", label: "➿ Loop"}
    ];

    const handleChange = useCallback((event) => {
        console.log(event, event.target)
        setTags(prevTags => ({ ...prevTags, workflow: event.value }));
    }, [setTags]);
    
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
        <div className="workflow-selector">
            <Select
                value={workflows.find(workflow => workflow.value === selectedWorkflow)}
                id="workflow-select"
                placeholder="Workflow.."
                options={workflows}
                onChange={handleChange}
                styles={customStyles}
                aria-label="Select a workflow"
                assName="dropdown"
                classNamePrefix="react-select"
            />
        </div>
    );
});

WorkflowSelector.propTypes = {
    selectedWorkflow: PropTypes.string.isRequired,
    setTags: PropTypes.func.isRequired,
};

export default WorkflowSelector;
