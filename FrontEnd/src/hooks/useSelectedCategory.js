import { useState, useCallback } from 'react';
import { apiFetch  } from '../utils/authUtils';
import { selectedCategoryEndpoint } from '../constants/endpoints';

const useSelectedCategory = () => {
  const [automaticallySelectedCategory, setSelectedCategory] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const selectCategory = async (userPrompt) => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await apiFetch(selectedCategoryEndpoint, {
        method: 'POST',
        body: JSON.stringify({
          user_prompt: userPrompt
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to select category')
      }

      const data = await response.json();

      console.log("Selected category:", data.category)
      setSelectedCategory(data.category)
    } catch (error) {
      console.error("Error in selecting persona:", error)
      setError(error.message)
    } finally {
      setIsLoading(false);
    }
  };
  
  return { automaticallySelectedCategory, isLoading, error, selectCategory };
}

export default useSelectedCategory;
