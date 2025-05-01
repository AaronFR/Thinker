import { useState } from 'react';
import { apiFetch } from '../utils/authUtils';
import { selectedCategoryEndpoint } from '../constants/endpoints';

const useSelectedCategory = () => {
  const [automaticallySelectedCategory, setSelectedCategory] = useState(null);
  const [categoryIsLoading, setCategoryIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const selectCategory = async (userPrompt) => {
    setCategoryIsLoading(true);
    setError(null);

    try {
      const response = await apiFetch(selectedCategoryEndpoint, {
        method: 'POST',
        body: JSON.stringify({
          user_prompt: userPrompt
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to select category');
      }

      const data = await response.json();
      console.log("Selected category:", data.category);
      setSelectedCategory(data.category);
    } catch (error) {
      console.error("Error in selecting worker:", error);
      setError(error.message);
    } finally {
      setCategoryIsLoading(false);
    }
  };
  
  return { automaticallySelectedCategory, categoryIsLoading, error, selectCategory };
}

export default useSelectedCategory;
