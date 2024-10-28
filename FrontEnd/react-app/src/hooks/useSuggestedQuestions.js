import { useState } from 'react';

const useSuggestedQuestions = (flaskPort) => {
  const [questionsForPrompt, setQuestionsForPrompt] = useState('');
  const [isQuestioning, setIsQuestioning] = useState(false);
  const [error, setError] = useState(null);

  const generateQuestionsForPrompt = async (input) => {
    console.log("Generating questions for:", input);
    setIsQuestioning(true);
    setError(null);

    try {
      const response = await fetch(`${flaskPort}/augmentation/question_prompt`, {
        method: 'POST',
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ user_prompt: input })
      });
  
      if (!response.ok) {
        throw new Error('Failed to generate questions for prompt');
      }
  
      const data = await response.json();
      console.log("questions against user prompt:", data.message);
      setQuestionsForPrompt(data.message);
  
    } catch (error) {
      console.error("Error in questioning user prompt:", error);
      setError(error.message);
    } finally {
      setIsQuestioning(false);
    }
  };

  return { questionsForPrompt, setQuestionsForPrompt, isQuestioning, error, generateQuestionsForPrompt };
};

export default useSuggestedQuestions;
