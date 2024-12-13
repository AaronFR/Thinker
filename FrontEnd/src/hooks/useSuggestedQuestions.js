import { useState } from 'react';
import { apiFetch } from '../utils/authUtils';

const FLASK_PORT = process.env.REACT_APP_THE_THINKER_BACKEND_URL || "http://localhost:5000";

/*
 * Suggests releveant questions to the user to help provide additional beneficial context in their prompt
 * ToDo: Needs to be informed of reference file and message content
 */
const useSuggestedQuestions = () => {
  const [questionsForPrompt, setQuestionsForPrompt] = useState('');
  const [isQuestioning, setIsQuestioning] = useState(false);
  const [error, setError] = useState(null);

  const generateQuestionsForPrompt = async (input) => {
    console.log("Generating questions for:", input);
    setIsQuestioning(true);
    setError(null);

    try {
      const response = await apiFetch(`${FLASK_PORT}/augmentation/question_prompt`, {
        method: 'POST',
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ user_prompt: input }),
        credentials: "include"
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
