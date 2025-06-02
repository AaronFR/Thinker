import React from 'react';
import PropTypes from 'prop-types';

import TagSelector from './TagsSelector';
import TooltipConstants from '../../constants/tooltips';



/** 
 * Allows users to select a worker from a dropdown list.
 * Provides an option for auto detection of worker with feedback.
 * 
 * @param {string} selectedWorker - Current selected worker.
 * @param {function} setTags - Function to update the selected worker in the prompts tags.
 */
const WorkerSelector = React.memo(({ selectedWorker, setTags, isLoading }) => {
    const workers = [
        { value: "default", label: "😶 Default" },
        { value: "coder", label: "💻 Coder" },
        { value: "writer", label: "✍ Writer" },
    ];
    
    return (
        <div 
            className={`worker-selector ${isLoading ? 'loading' : ''}`}
            data-tooltip-id="tooltip"
            data-tooltip-content={TooltipConstants.workerSelector}
            data-tooltip-place="top"
        >
            <TagSelector
                selectedValue={selectedWorker}
                setTags={setTags}
                options={workers}
                placeholder="Worker"
                className="dropdown"
            />
        </div>
    );
});

WorkerSelector.propTypes = {
    selectedWorker: PropTypes.string,
    setTags: PropTypes.func.isRequired,
};

export default WorkerSelector;
