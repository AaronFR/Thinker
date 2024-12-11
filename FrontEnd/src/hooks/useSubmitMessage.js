import { useState, useEffect, useRef, useCallback } from 'react';
import { io } from 'socket.io-client';

import { apiFetch } from '../utils/authUtils';

const FLASK_PORT = process.env.REACT_APP_THE_THINKER_BACKEND_URL || "http://localhost:5000";

const useSubmitMessage = (concatenatedQA, filesForPrompt, selectedMessages, tags, workflow, setWorkflow) => {
  const [message, setMessage] = useState('');
  const [error, setError] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [totalCost, setTotalCost] = useState(null);
  const socketRef = useRef(null);
  const isRefreshingRef = useRef(false);

  // Refs to store the latest userInput and selectedPersona
  const userInputRef = useRef('');
  const selectedPersonaRef = useRef(null);

  const pendingSubmitRef = useRef(null);
  const workflowRef = useRef(workflow);

  const updateQueueRef = useRef([]);
  const isProcessingQueueRef = useRef(false); // Flag to prevent multiple concurrent queue processing

  /**
   * Update workflowRef whenever workflow state changes.
   */
  useEffect(() => {
    workflowRef.current = workflow;
  }, [workflow]);

  const processUpdateQueue = useCallback(() => {
    if (isProcessingQueueRef.current) return; // Prevent re-entrancy
    if (!workflowRef.current) return; // Ensure workflow is set

    isProcessingQueueRef.current = true;

    while (updateQueueRef.current.length > 0) {
      const updateData = updateQueueRef.current.shift(); // Dequeue the first update

      console.log("Processing queued workflow update:", updateData);

      setWorkflow((prevWorkflow) => {
        if (!prevWorkflow || !prevWorkflow.steps) {
          console.error("Workflow is null or malformed. Cannot process the update.");
          return prevWorkflow;
        }

        const updatedWorkflow = { ...prevWorkflow };
        if (updateData.type === 'status') {
          // Update the overall workflow status
          updatedWorkflow.status = updateData.status;
          console.log("Updated workflow status:", updatedWorkflow.status);
          return updatedWorkflow;
        } else {
          const stepIndex = updateData.step - 1; // workflows are 1-indexed
          const newStatus = updateData.status;

          if (updatedWorkflow.steps[stepIndex]) {
            updatedWorkflow.steps[stepIndex] = {
              ...updatedWorkflow.steps[stepIndex],
              status: newStatus
            };
            console.log("Updated workflow step:", updatedWorkflow.steps[stepIndex]);
            return updatedWorkflow;
          } else {
            console.error(`Invalid workflow step index: ${stepIndex}`);
            return prevWorkflow;
          }
        }
      });
    }

    isProcessingQueueRef.current = false;
  }, []);

  // Function to initialize the socket connection
  const initializeSocket = useCallback(() => {
    return new Promise((resolve, reject) => {
      const socket = io(FLASK_PORT, {
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
        console.log('WebSocket connection error');
        setError('Unable to establish a WebSocket connection. Please check your network and try again.');
        setIsProcessing(false);
        reject(new Error('WebSocket connection failed'));
      });

      // Workflows
      socket.on('send_workflow', (data) => {
        console.log("Receiving workflow schema", data.workflow);
        setWorkflow(data.workflow);
        // After setting the workflow, process any queued updates
        processUpdateQueue();
      });

      socket.on('update_workflow', (data) => {
        console.log("Received workflow status update", data);
        updateQueueRef.current.push({ type: 'status', status: data.status });
        processUpdateQueue();
    });

      socket.on('update_workflow_step', (data) => {
        console.log("Receiving workflow step update", data);
        console.log("Current workflow:", workflowRef.current);

        if (!workflowRef.current || !workflowRef.current.steps) {
          console.log("Workflow not ready, queuing update:", data);
          updateQueueRef.current.push(data);
        } else {
          // Enqueue the update and process the queue
          updateQueueRef.current.push(data);
          processUpdateQueue();
        }
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
            const refreshResponse = await apiFetch(FLASK_PORT + '/refresh', { method: 'POST' });
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
  }, [FLASK_PORT, processUpdateQueue]);

  // Initialize the socket connection when the component mounts
  useEffect(() => {
    initializeSocket().catch((err) => {
      console.error('Failed to initialize socket:', err);
    });

    return () => {
      if (socketRef.current) {
        socketRef.current.off('connect');
        socketRef.current.off('response');
        socketRef.current.off('connect_error');
        socketRef.current.off('send_workflow');
        socketRef.current.off('update_workflow');
        socketRef.current.off('update_workflow_step');
        socketRef.current.off('stream_end');
        socketRef.current.off('error');
        socketRef.current.disconnect();
      }
    };
  }, [initializeSocket]);

  // Function to handle message submission
  const handleSubmit = useCallback(async (userInput, selectedPersona) => {
      userInputRef.current = userInput;
      selectedPersonaRef.current = selectedPersona;

      setError(null);
      setIsProcessing(true);
      setMessage(''); // Clear previous messages
      setTotalCost(null); // Reset cost for new request
      setWorkflow(null); // Clear the previous workflow diagram

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
