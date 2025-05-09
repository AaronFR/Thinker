import React, { useMemo } from "react";
import PropTypes from "prop-types";

import ExpandableElement from "../utils/expandableElement";
import { CodeHighlighter } from '../utils/textUtils';
import { formatTime } from "../utils/numberUtils";

import './styles/Workflow.css';

import blankImage from './styles/blank.png';

/** 
 * Displays the details of a workflow including its status and steps.
 * 
 * @param {object} workflowData - The data related to the workflow.
 * @param {string} workflow_name - The name of the workflow.
 * @param {string}version - The version of the workflow.
 * @param {string}status - The current status of the workflow.
 * @param {array}steps - A list of steps in the workflow, each containing:
 * @param {number} step_id - The unique identifier for the step.
 * @param {string} module - The module associated with the step.
 * @param {string} status - The status of the step.
 * @param {string} description - A short description of the step.
 * @param {object} parameters - Optional parameters for the step.
 * @param {object} response - The response generated by the step.
 */
const Workflow = React.memo(({ workflowData }) => {
  if (!workflowData) return null;

  return (
    <div className={`workflow ${workflowData.status}`}>
      <div className="workflow-details">
        <p className="workflow-name">
          {workflowData.workflow_name} (v{workflowData.version})
        </p>
        <p className={`status ${workflowData.status}`}>{workflowData.status}</p>
      </div>
      <div className="steps">
        {workflowData.steps.map((step) => (
          <StepDetail key={step.step_id} step={step} />
        ))}
      </div>
      {workflowData.duration && <div>
        <small>{formatTime(workflowData.duration)}</small>
      </div>}
    </div>
  );
});

/** 
 * Renders individual step details within the workflow.
 * 
 * @param {object} step (object): The data related to the workflow step, expected to contain:
 * @param {number} step_id - The unique identifier for the step.
 * @param {string} module - The module name.
 * @param {string} status - The current status of the step.
 * @param {string} description - A descriptive text for the step.
 * @param {object} parameters - Optional parameters.
 * @param {object} response - The generated response data.
 */
const StepDetail = React.memo(({ step }) => {
  const { step_id, module, status, description = "No description available", parameters, response, sites } = step;

  const parametersMarkup = useMemo(() => {
    if (!parameters) return null;
    return (
      <div className="parameters">
        {Object.entries(parameters).map(([key, value]) => (
          <div key={key}>
            <strong>{key}</strong>: {value}
          </div>
        ))}
      </div>
    );
  }, [parameters]);

  const sitesMarkup = useMemo(() => {
    if (!sites || Object.keys(sites).length === 0) return null;
    return (
      <ExpandableElement
        className="response"
        minContent={"Sites Referenced"}
        maxContent={
          <>
            {Object.entries(sites).map(([key, value]) => (
              <div key={key} className="site-container">
                <img
                  src={`${new URL(value).origin}/favicon.ico`}
                  className="site-image"
                  onError={(e) => {
                    e.target.src = blankImage;
                  }}
                  alt={`${key} favicon`}
                />
                <strong>{key}</strong>:{" "}
                <a
                  href={value}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="site-link"
                >
                  {value}
                </a>
              </div>
            ))}
          </>
        }
        initiallyExpanded={true}
      />
    );
  }, [sites]);

  const responseMarkup = useMemo(() => {
    if (!response || Object.keys(response).length === 0) return null;
    return (
      <ExpandableElement
        className="response"
        minContent={"Response Generated"}
        maxContent={
          <>
            <h4>Response</h4>
            <div className="markdown-output">
              <CodeHighlighter>
                {response}
              </CodeHighlighter>
            </div>
          </>
        }
        initiallyExpanded={false}
      />
    );
  }, [response]);

  return (
    <div className={`step ${status}`}>
      <div className="step-details">
        <p className="step-index">{`Step ${step_id}`}</p>
        <p className="module">
          <strong>{module}</strong>
        </p>
        <p className={`status ${status}`}>{status}</p>
      </div>
      <p>{description}</p>
      {parametersMarkup}
      {sitesMarkup}
      {responseMarkup}
    </div>
  );
});

Workflow.propTypes = {
  workflowData: PropTypes.shape({
    workflow_name: PropTypes.string.isRequired,
    version: PropTypes.string.isRequired,
    status: PropTypes.string.isRequired,
    steps: PropTypes.arrayOf(
      PropTypes.shape({
        step_id: PropTypes.number.isRequired,
        module: PropTypes.string.isRequired,
        status: PropTypes.string.isRequired,
        description: PropTypes.string,
        parameters: PropTypes.object,
        response: PropTypes.string,
      })
    ).isRequired,
  }).isRequired,
};

StepDetail.propTypes = {
  step: PropTypes.shape({
    step_id: PropTypes.number.isRequired,
    module: PropTypes.string.isRequired,
    status: PropTypes.string.isRequired,
    description: PropTypes.string,
    parameters: PropTypes.object,
    response: PropTypes.object,
  }).isRequired,
};

export default Workflow;
