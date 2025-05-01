import { useState } from 'react';
import { apiFetch } from '../utils/authUtils';
import { selectWorkerEndpoint } from '../constants/endpoints';

/*
 * Hook for selecting an appropriate worker for the users given prompt.
 * @returns {Object} Contains state and function to select worker.
 */
const useSelectedWorker = () => {
  const [automaticallySelectedWorker, setSelectedWorker] = useState(null);
  const [workerIsLoading, setWorkerIsLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Function to select a worker by sending user_prompt.
   * @param {string} userPrompt - The user's prompt/input.
   */
  const selectWorker = async (userPrompt) => {
    setWorkerIsLoading(true);
    setError(null);

    try {
      const response = await apiFetch(selectWorkerEndpoint, {
        method: 'POST',
        body: JSON.stringify({
          user_prompt: userPrompt
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to select worker');
      }

      const data = await response.json();
      
      console.log("Selected worker:", data.worker);
      setSelectedWorker(data.worker);

    } catch (error) {
      console.error("Error in selecting worker:", error);
      setError(error.message);
    } finally {
      setWorkerIsLoading(false);
    }
  };

  return { automaticallySelectedWorker, workerIsLoading, error, selectWorker };
};

export default useSelectedWorker;
