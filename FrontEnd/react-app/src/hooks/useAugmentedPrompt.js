import { useState } from 'react';

const useAugmentedPrompt = (flaskPort) => {
  const [augmentedPrompt, setAugmentedPrompt] = useState('');
  const [isAugmenting, setIsAugmenting] = useState(false);
  const [error, setError] = useState(null);

  const generateAugmentedPrompt = async (input) => {
    setIsAugmenting(true);
    setError(null);

    try {
      const response = await fetch(`${flaskPort}/augmentation/augment_prompt`, {
        method: 'POST',
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ user_prompt: input })
      });
  
      if (!response.ok) {
        throw new Error('Failed to fetch augmented prompt');
      }
  
      const data = await response.json();
      setAugmentedPrompt(data.message);
  
    } catch (error) {
      console.error("Error in augmenting prompt:", error);
      setError(error.message);
    } finally {
      setIsAugmenting(false);
    }
  };

  return { augmentedPrompt, setAugmentedPrompt, isAugmenting, error, generateAugmentedPrompt };
};

export default useAugmentedPrompt;
