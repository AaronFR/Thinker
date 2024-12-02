import React from "react";

import './styles/Workflow.css'

const Workflow = ({ workflowData }) => {
  if (!workflowData) {return null}

  return (
    <div className={`workflow ${workflowData.status}`}>
      <h1>{workflowData.workflow_name} (v{workflowData.version})</h1>
      <p>Workflow ID: {workflowData.workflow_id}</p>
      <p>Status: {workflowData.status}</p>
      <div className="steps">
        <h2>Steps:</h2>
        {workflowData.steps.map((step) => (
          <div key={step.step_id} className={`step ${step.status}`}>
            <h3>Step {step.step_id}</h3>
            <p>
              <strong>Module:</strong> {step.module}
            </p>
            <p>
              <strong>Status:</strong> {step.status}
            </p>
            <p>
              <strong>Description:</strong>{" "}
              {workflowData.modules[step.module]?.description || "No description available"}
            </p>
            {step.parameters && (
              <div>
                <h4>Parameters:</h4>
                {Object.entries(step.parameters).map(([key, value]) => (
                  <div>
                    {key}: {value}
                  </div>
                ))}
              </div>
            )}
            {step.response && Object.keys(step.response).length > 0 && (
              <div>
                <h4>Response:</h4>
                <pre>{JSON.stringify(step.response, null, 2)}</pre>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Workflow;
