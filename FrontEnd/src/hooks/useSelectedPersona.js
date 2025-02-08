import { useState } from 'react';
import { apiFetch } from '../utils/authUtils';
import { selectPersonaEndpoint } from '../constants/endpoints';

/*
 * Hook for selecting an appropriate persona for the users given prompt.
 * @returns {Object} Contains state and function to select persona.
 */
const useSelectedPersona = () => {
  const [automaticallySelectedPersona, setSelectedPersona] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Function to select a persona by sending user_prompt.
   * @param {string} userPrompt - The user's prompt/input.
   */
  const selectPersona = async (userPrompt) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiFetch(selectPersonaEndpoint, {
        method: 'POST',
        body: JSON.stringify({
          user_prompt: userPrompt
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to select persona');
      }

      const data = await response.json();
      
      console.log("Selected persona:", data.persona);
      setSelectedPersona(data.persona);

    } catch (error) {
      console.error("Error in selecting persona:", error);
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return { automaticallySelectedPersona, isLoading, error, selectPersona };
};

export default useSelectedPersona;
