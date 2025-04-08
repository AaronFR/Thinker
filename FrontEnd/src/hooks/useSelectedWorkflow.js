import { useState } from 'react';
import { apiFetch } from '../utils/authUtils';
import { selectWorkflowEndpoint } from '../constants/endpoints';

/*
 * Hook for selecting a workflow based on user prompt and tags.
 * @returns {Object} Contains state and function to select workflow.
 */
const useSelectedWorkflow = () => {
  const [automaticallySelectedWorkflow, setSelectedWorkflow] = useState(null);
  const [workflowIsLoading, setWorkflowIsLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Function to select a workflow by sending user_prompt and tags to the backend.
   * @param {string} userPrompt - The user's prompt/input.
   * @param {Array|string} tags - Relevant tags associated with the prompt.
   */
  const selectWorkflow = async (userPrompt, tags) => {
    setWorkflowIsLoading(true);
    setError(null);

    try {
      const response = await apiFetch(selectWorkflowEndpoint, {
        method: 'POST',
        body: JSON.stringify({
          user_prompt: userPrompt,
          tags: tags
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to select workflow');
      }

      const data = await response.json();
      
      console.log("Selected workflow:", data.workflow);
      setSelectedWorkflow(data.workflow);

    } catch (error) {
      console.error("Error in selecting workflow:", error);
      setError(error.message);
    } finally {
      setWorkflowIsLoading(false);
    }
  };

  return { automaticallySelectedWorkflow, workflowIsLoading, error, selectWorkflow };
};

export default useSelectedWorkflow;
