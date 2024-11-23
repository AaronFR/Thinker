import { useState, useEffect, useRef, useCallback } from 'react';
import { io } from 'socket.io-client';
import { apiFetch } from '../utils/authUtils';

const flask_port = "http://localhost:5000";

const useSubmitMessage = (flaskPort, concatenatedQA, filesForPrompt, selectedMessages, tags) => {
  const [message, setMessage] = useState('');
  const [error, setError] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [totalCost, setTotalCost] = useState(null);
  const socketRef = useRef(null);
  const isRefreshingRef = useRef(false);

  // Refs to store the latest userInput and selectedPersona
  const userInputRef = useRef('');
  const selectedPersonaRef = useRef(null);

  // Ref to store the pending submit request
  const pendingSubmitRef = useRef(null);

  // Function to initialize the socket connection
  const initializeSocket = useCallback(() => {
    return new Promise((resolve, reject) => {
      const socket = io(flaskPort, {
        withCredentials: true
      });
      socketRef.current = socket;

      // Listen for the 'connect' event to resolve the promise
      socket.on('connect', () => {
        console.log('WebSocket connected');
        resolve();
      });

      socket.on('response', (data) => {
        console.log('Received chunk:', data.content);
        setMessage((prevMessage) => prevMessage + data.content);
      });

      socket.on('connect_error', () => {
        console.log('WebSocket connect error');
        setError('WebSocket connection failed. Please try again later.');
        setIsProcessing(false);
        reject(new Error('WebSocket connection failed'));
      });

      socket.on('stream_end', () => {
        console.log('Stream has ended');
        setIsProcessing(false);
      });

      socket.on('error', async (data) => {
        console.log('Socket error received:', data);
        if (data.error === 'token_expired' && !isRefreshingRef.current) {
          isRefreshingRef.current = true;
          try {
            const refreshResponse = await apiFetch(flask_port + '/refresh', { method: 'POST' });
            if (refreshResponse.ok) {
              console.log('Token refreshed successfully');
              socketRef.current.disconnect();

              // Reinitialize the socket and wait for it to connect
              await initializeSocket();
              console.log('Retrying pending submit:', pendingSubmitRef.current);
              if (pendingSubmitRef.current) {
                const { userInput, selectedPersona } = pendingSubmitRef.current;
                pendingSubmitRef.current = null; // Clear pending submit after retrying
                await handleSubmit(userInput, selectedPersona); // Retry the request
              } else {
                console.log('No pending submit to retry.');
              }
            } else {
              console.log('Token refresh failed');
              setError('Session expired. Please log in again.');
              setIsProcessing(false);
            }
          } catch (err) {
            console.error('Error refreshing token:', err);
            setError('Error refreshing token.');
            setIsProcessing(false);
          } finally {
            isRefreshingRef.current = false;
          }
        }
      });
    });
  }, [flaskPort]);

  // Initialize the socket connection when the component mounts
  useEffect(() => {
    initializeSocket().catch((err) => {
      console.error('Failed to initialize socket:', err);
    });

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, [initializeSocket]);

  // Function to handle message submission
  const handleSubmit = useCallback(
    async (userInput, selectedPersona) => {
      userInputRef.current = userInput;
      selectedPersonaRef.current = selectedPersona;

      setError(null);
      setIsProcessing(true);
      setMessage(''); // Clear previous messages
      setTotalCost(null); // Reset cost for new request

      console.log('Storing pending submit:', { userInput, selectedPersona });
      pendingSubmitRef.current = { userInput, selectedPersona };

      try {
        if (socketRef.current && socketRef.current.connected) {
          socketRef.current.emit('start_stream', {
            prompt: userInput,
            additionalQA: concatenatedQA,
            files: filesForPrompt,
            messages: selectedMessages, // consider sending just IDs if needed
            persona: selectedPersona,
            tags: tags
          });
          console.log('Stream started');
        }
      } catch (err) {
        console.error('Error starting the stream:', err);
        setError('Error starting the stream. Please try again later.');
        setIsProcessing(false);
      }
    },
    [concatenatedQA, filesForPrompt, selectedMessages, tags]
  );

  return { message, totalCost, error, isProcessing, handleSubmit };
};

export default useSubmitMessage;
