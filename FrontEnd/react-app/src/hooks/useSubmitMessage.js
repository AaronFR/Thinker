import { useState } from 'react';
import { prototyping_user_id } from '../utils/loginUtils'

const useSubmitMessage = (flaskPort, concatenatedQA, filesForPrompt) => {
  const [message, setMessage] = useState('');
  const [error, setError] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleSubmit = async (userInput, selectedPersona) => {
    setError(null);
    setIsProcessing(true);

    try {
      const response = await fetch(`${flaskPort}/message`, {
        method: 'POST',
        headers: {
          "Content-Type": 'application/json'
        },
        body: JSON.stringify({
          prompt: userInput,
          user_id: prototyping_user_id,
          additionalQA: concatenatedQA,
          files: filesForPrompt,
          persona: selectedPersona
        }),
      });
      
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      console.log(data)
      setMessage(data.message);
    } catch (error) {
      setError('Error submitting and fetching the message. Please try again later.');
    } finally {
      setIsProcessing(false);
    }
  };

  return { message, setMessage, error, isProcessing, handleSubmit };
};

export default useSubmitMessage;
