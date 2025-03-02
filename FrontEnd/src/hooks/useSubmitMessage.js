import { useState, useEffect, useRef, useCallback } from 'react';
import { io } from 'socket.io-client';

import { apiFetch } from '../utils/authUtils';
import { refreshSessionEndpoint } from '../constants/endpoints';
import { FLASK_PORT } from '../constants/endpoints';

/**
 * Custom hook to handle message submission through a websocket connection.
 */
const useSubmitMessage = (
  concatenatedQA,
  selectedFiles,
  selectedMessages,
  tags,
  workflow,
  setWorkflow
) => {
  const [message, setMessage] = useState('');
  const [files, setFiles] = useState([]);
  const [error, setError] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [totalCost, setTotalCost] = useState(null);

  const socketRef = useRef(null);

  const userInputRef = useRef('');
  const selectedPersonaRef = useRef(null);
  const pendingSubmitRef = useRef(null);
  const workflowRef = useRef(workflow);

  const updateQueueRef = useRef([]);
  const isProcessingQueueRef = useRef(false); // Flag to prevent multiple concurrent queue processing
  const isRefreshingRef = useRef(false);
  const [refreshCategory, setRefreshCategory] = useState(null);

  /**
   * Update workflowRef whenever workflow state changes.
   */
  useEffect(() => {
    workflowRef.current = workflow;
  }, [workflow]);

  /**
   * Process the workflow update queue to ensure sequential updates.
   */
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

        // Update overall workflow status
        const stepIndex = updateData.step - 1; // 1-indexed to 0-indexed
        if (updateData.type === 'status') {
          return { ...prevWorkflow, status: updateData.status };
        }
        
        if (prevWorkflow.steps[stepIndex]) {
          const currentStep = { ...prevWorkflow.steps[stepIndex], ...updateData };
          return {
            ...prevWorkflow,
            steps: prevWorkflow.steps.map((step, index) =>
              index === stepIndex ? currentStep : step
            ),
          };
        } else {
          console.error(`Invalid workflow step index: ${stepIndex}`);
          return prevWorkflow;
        }
      });
    }

    isProcessingQueueRef.current = false;
  }, []);

  /**
   * Function to initialize the socket connection
   */
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

      socket.on('output_file', (data) => {
        setFiles((prevFiles) => [...prevFiles, data.file]);
      });

      socket.on('connect_error', () => {
        console.log('WebSocket connection error');
        setError('Unable to establish a WebSocket connection. Please check your network and try again.');
        setIsProcessing(false);
        reject(new Error('WebSocket connection failed'));
      });

      /* Workflow Events */

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

      /* End Stream Events */

      socket.on('stream_end', (data) => {
        console.log('Stream has ended');
        setIsProcessing(false);
      });

      socket.on('trigger_refresh', (data) => {
        setRefreshCategory({ name: data.category_name, id: data.category_id });
      });

      socket.on('error', async (data) => {
        console.log('Socket error received:', data);
        if (data.error === 'token_expired' && !isRefreshingRef.current) {
          isRefreshingRef.current = true;
          try {
            const refreshResponse = await apiFetch(refreshSessionEndpoint, {
               method: 'POST'
            });
            if (refreshResponse.ok) {
              console.log('Token refreshed successfully');

              socketRef.current.disconnect();

              await initializeSocket(); // Reinitialize the socket and wait for it to connect
              console.log('Retrying pending submit:', pendingSubmitRef.current);
              if (pendingSubmitRef.current) {
                const { userInput, selectedPersona, selectedMessages, selectedFiles, tags } = pendingSubmitRef.current;
                pendingSubmitRef.current = null; // Clear pending submit after retrying
                await handleSubmit(userInput, selectedPersona, selectedMessages, selectedFiles, tags); // Retry the request
              }
            } else {
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
  }, [processUpdateQueue]);

  /**
   * Initialize the socket connection when the component mounts
   */
  useEffect(() => {
    initializeSocket().catch((err) => {
      console.error('Failed to initialize socket:', err);
    });

    return () => {
      if (socketRef.current) {
        socketRef.current.removeAllListeners();
        socketRef.current.disconnect();
      }
    };
  }, [initializeSocket]);

  /**
   * Function to handle message submission
   */
  const handleSubmit = useCallback(async (userInput, selectedPersona, selectedMessages, selectedFiles, tags) => {
      userInputRef.current = userInput;
      selectedPersonaRef.current = selectedPersona;

      if (isProcessing) {
        console.warn('A submission is already in progress.');
        return;
      }

      setError(null);
      setIsProcessing(true);
      setMessage(''); // Clear previous messages
      setTotalCost(null); // Reset cost for new request
      setWorkflow(null); // Clear the previous workflow diagram

      console.log('Storing pending submit:', { userInput, selectedPersona, tags });

      pendingSubmitRef.current = { userInput, selectedPersona, selectedMessages, selectedFiles, tags };

      try {
        if (!socketRef.current || !socketRef.current.connected) {
          // Reinitialize the socket connection if it's not connected
          await initializeSocket();
        }

        socketRef.current.emit('start_stream', {
          prompt: userInput,
          additionalQA: concatenatedQA,
          files: selectedFiles,
          messages: selectedMessages, // consider sending just IDs if needed
          persona: selectedPersona,
          tags: tags
        });
        console.log('Stream started');
      } catch (err) {
        console.error('Error starting the stream:', err);
        setError('Error starting the stream. Please try again later.');
        setIsProcessing(false);
      }
    },
    [concatenatedQA, selectedMessages, selectedFiles, tags, isProcessing, initializeSocket]
  );

  /**
   * Function to cancel the ongoing request
   */
  const disconnectFromRequest = useCallback(() => {
    if (socketRef.current && socketRef.current.connected) {

      // ToDo: Consider adding msgId for terminating ongoing requests
      socketRef.current.emit('disconnect_from_request', (response) => {
        console.info("Disconnecting from request view", response);
        // Disconnect after acknowledgment
        socketRef.current.disconnect();

        // Reset state variables
        setIsProcessing(false);
        setMessage('');
        setTotalCost(null);
        setWorkflow(null);
        pendingSubmitRef.current = null;
        updateQueueRef.current = [];
      });
    } else {
      console.warn('No active socket connection to disconnect.');
    }
  }, []);


  return { message, files, totalCost, error, isProcessing, handleSubmit, disconnectFromRequest, refreshCategory };
};

export default useSubmitMessage;