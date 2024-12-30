import React from "react";

import ExpandableElement from "../utils/expandableElement";

import './styles/Workflow.css'

const Workflow = ({ workflowData }) => {
  if (!workflowData) {return null}

  return (
    <div className={`workflow ${workflowData.status}`}>
      <div className="workflow-details">
        <p className="workflow-name">{workflowData.workflow_name} (v{workflowData.version})</p>
        <p className="workflow-id">{workflowData.workflow_id}</p>
        <p className={`status ${workflowData.status}`}>{workflowData.status}</p>
      </div>
      <div className="steps">
        {workflowData.steps.map((step) => (
          <div key={step.step_id} className={`step ${step.status}`}>
            <div className="step-details">
              <p className="step-index">{`Step ${step.step_id}`}</p>
              <p className="module"><strong>{step.module}</strong></p>
              <p className={`status ${step.status}`}>{step.status}</p>
            </div>
            <p>
              {workflowData.modules[step.module]?.description || "No description available"}
            </p>
            {step.parameters && (
              <div className="parameters">
                {Object.entries(step.parameters).map(([key, value]) => (
                  <div>
                    {key}: {value}
                  </div>
                ))}
              </div>
            )}
            {step.response && Object.keys(step.response).length > 0 && (
                <ExpandableElement
                  className="module"
                  minContent={"Response Generated + "}
                  maxContent={<>
                    <h4>Response</h4>
                    <p className="parameters">{step.response}</p>
                  </>}
                  initiallyExpanded={false}
                />
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Workflow;
