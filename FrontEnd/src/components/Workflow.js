import React from "react";
import PropTypes from "prop-types";
import ExpandableElement from "../utils/expandableElement";
import './styles/Workflow.css';

import blankImage from './styles/blank.png';

/**
 * Workflow Component
 * 
 * Displays the details of a workflow including its status and steps.
 * 
 * Props:
 * - workflowData (object): The data related to the workflow.
 *   - workflow_name (string): The name of the workflow.
 *   - version (string): The version of the workflow.
 *   - status (string): The current status of the workflow.
 *   - steps (array): A list of steps in the workflow, each containing:
 *     - step_id (number): The unique identifier for the step.
 *     - module (string): The module associated with the step.
 *     - status (string): The status of the step.
 *     - description (string): A short description of the step.
 *     - parameters (object): Optional parameters for the step.
 *     - response (object): The response generated by the step.
 */
const Workflow = ({ workflowData }) => {
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
    </div>
  );
};

/**
 * StepDetail Component
 * 
 * Renders individual step details within the workflow.
 * 
 * Props:
 * - step (object): The data related to the workflow step, expected to contain:
 *   - step_id (number): The unique identifier for the step.
 *   - module (string): The module name.
 *   - status (string): The current status of the step.
 *   - description (string): A descriptive text for the step.
 *   - parameters (object): Optional parameters.
 *   - response (object): The generated response data.
 */
const StepDetail = ({ step }) => {
  const { step_id, module, status, description = "No description available", parameters, response, sites } = step;

  return (
    <div className={`step ${status}`}>
      <div className="step-details">
        <p className="step-index">{`Step ${step_id}`}</p>
        <p className="module"><strong>{module}</strong></p>
        <p className={`status ${status}`}>{status}</p>
      </div>
      <p>{description}</p>
      {parameters && (
        <div className="parameters">
          {Object.entries(parameters).map(([key, value]) => (
            <div key={key}>
              <strong>{key}</strong>: {value}
            </div>
          ))}
        </div>
      )}
      {sites && Object.keys(sites).length > 0 && (
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
                    onError={(e) => { e.target.src = blankImage; }}
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
      )}
      {response && Object.keys(response).length > 0 && (
        <ExpandableElement
          className="response"
          minContent={"Response Generated"}
          maxContent={
            <>
              <h4>Response</h4>
              <pre className="parameters">{step.response}</pre>
            </>
          }
          initiallyExpanded={false}
        />
      )}
    </div>
  );
};

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
