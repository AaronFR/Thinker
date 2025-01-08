import { useState } from 'react';
import { apiFetch } from '../utils/authUtils';

const FLASK_PORT = process.env.REACT_APP_THE_THINKER_BACKEND_URL || "http://localhost:5000";

/*
 * Hook for suggesting relevant questions to provide beneficial context in user prompts.
 * @returns {Object} Contains state and function to generate questions.
 */
const useSuggestedQuestions = () => {
  const [questionsForPrompt, setQuestionsForPrompt] = useState('');
  const [isQuestioning, setIsQuestioning] = useState(false);
  const [error, setError] = useState(null);

  const generateQuestionsForPrompt = async (input, selectedMessages, selectedFiles) => {
    console.log("Generating questions for:", input, selectedMessages, selectedFiles);
    setIsQuestioning(true);
    setError(null);

    try {
      const response = await apiFetch(`${FLASK_PORT}/augmentation/question_prompt`, {
        method: 'POST',
        body: JSON.stringify({
          user_prompt: input,
          selected_messages: selectedMessages,
          selected_files: selectedFiles
        }),
      });
  
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to generate questions for prompt');
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
