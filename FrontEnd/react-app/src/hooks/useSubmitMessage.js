import { useState, useEffect, useRef } from 'react';
import { io } from 'socket.io-client';

const useSubmitMessage = (flaskPort, concatenatedQA, filesForPrompt, selectedMessages, tags) => {
  const [message, setMessage] = useState('');
  const [error, setError] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [totalCost, setTotalCost] = useState(null);
  const socketRef = useRef(null);

  // Initialize WebSocket connection only when the component mounts
  useEffect(() => {
    const socket = io(flaskPort, {
      withCredentials: true
    });
    socketRef.current = socket;

    socket.on('connect', () => {
      console.log('WebSocket connected');
    });

    socket.on('response', (data) => {
      // Append each content chunk to the message as it arrives
      console.log('Received chunk:', data.content);
      setMessage((prevMessage) => prevMessage + data.content);
    });

    socket.on('connect_error', () => {
      console.log('WebSocket connnect error');
      setError('WebSocket connection failed. Please try again later.');
      setIsProcessing(false);
    });

    socket.on('stream_end', () => {
      console.log('Stream has ended');
      setIsProcessing(false);
    });

    socket.on('error', () => {
      // ToDo: Somne variety of "error encountered" graphic
      console.log('Processing encountered an error');
      setIsProcessing(false);
    });

    return () => {
      // Clean up the WebSocket connection when the component unmounts
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, [flaskPort]);

  const handleSubmit = async (userInput, selectedPersona) => {
    setError(null);
    setIsProcessing(true);
    setMessage('');  // Clear previous messages
    setTotalCost(null);  // Reset cost for new request

    try {
      if (socketRef.current && socketRef.current.connected) {
        socketRef.current.emit('start_stream', {
          prompt: userInput,
          additionalQA: concatenatedQA,
          files: filesForPrompt,
          messages: selectedMessages, // its comidic to the full node representation, to send the id, to get the full message - just send the id
          persona: selectedPersona,
          tags: tags
        });
        console.log('Stream started');
      } else {
        throw new Error('WebSocket not connected');
      }
    } catch (error) {
      console.error('Error starting the stream:', error);
      setError('Error starting the stream. Please try again later.');
    }
  }

  return { message, totalCost, error, isProcessing, handleSubmit };
};

export default useSubmitMessage;
