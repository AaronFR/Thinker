import { useState, useEffect, useRef } from 'react';
import { prototyping_user_id } from '../utils/loginUtils';
import { io } from 'socket.io-client';

const useSubmitMessage = (flaskPort, concatenatedQA, filesForPrompt) => {
  const [message, setMessage] = useState('');
  const [error, setError] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [totalCost, setTotalCost] = useState(null);
  const socketRef = useRef(null);

  // Initialize WebSocket connection only when the component mounts
  useEffect(() => {
    const socket = io(flaskPort); // Connect to the Flask-SocketIO server
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
      // Emit the data to start streaming on the backend
      if (socketRef.current && socketRef.current.connected) {
        socketRef.current.emit('start_stream', {
          prompt: userInput,
          user_id: prototyping_user_id,
          additionalQA: concatenatedQA,
          files: filesForPrompt,
          persona: selectedPersona,
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

  return { message, setMessage, totalCost, error, isProcessing, handleSubmit };
};

export default useSubmitMessage;
