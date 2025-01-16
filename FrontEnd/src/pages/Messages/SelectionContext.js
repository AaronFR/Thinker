import React, { createContext, useState, useContext, useCallback, useEffect, useMemo } from 'react';
import PropTypes from 'prop-types';

// Create the SelectionContext
export const SelectionContext = createContext();

/**
 * SelectionProvider
 *
 * This component wraps around parts of the application that need access to
 * the selection state for files and messages. It provides functionalities
 * to add, remove, and toggle selections.
 *
 * @param {Object} props - The component props.
 * @param {React.ReactNode} props.children - The child components.
 * @returns {JSX.Element} The provider component.
 */
export const SelectionProvider = ({ children }) => {
  const [selectedFiles, setSelectedFiles] = useState(() => {
    const savedFiles = localStorage.getItem('selectedFiles');
    return savedFiles ? JSON.parse(savedFiles) : [];
  });

  const [selectedMessages, setSelectedMessages] = useState(() => {
    const savedMessages = localStorage.getItem('selectedMessages');
    return savedMessages ? JSON.parse(savedMessages) : [];
  });

  useEffect(() => {
    console.log("SelectionContext updated:", selectedMessages);

    localStorage.setItem('selectedMessages', JSON.stringify(selectedMessages));

  }, [selectedMessages]);

  useEffect(() => {
    console.log("Selected Files Updated:", selectedFiles);
    localStorage.setItem('selectedFiles', JSON.stringify(selectedFiles));
  }, [selectedFiles]);
  
  useEffect(() => {
    console.log("Selected Messages Updated:", selectedMessages);
    localStorage.setItem('selectedMessages', JSON.stringify(selectedMessages));
  }, [selectedMessages]);
  

  /**
   * Adds a file to the selectedFiles state.
   *
   * @param {Object} file - The file object to add.
   */
  const addFile = useCallback((file) => {
    setSelectedFiles((prevFiles) => {
      // Prevent adding duplicate files based on unique 'id'
      if (!prevFiles.some((f) => f.id === file.id)) {
        return [...prevFiles, file];
      }
      return prevFiles;
    });
  }, []);

  /**
   * Removes a file from the selectedFiles state.
   *
   * @param {string} fileId - The unique identifier of the file to remove.
   */
  const removeFile = useCallback((fileId) => {
    setSelectedFiles((prevFiles) => prevFiles.filter((file) => file.id !== fileId));
  }, []);

  /**
   * Toggles the selection state of a file.
   * Adds the file if not selected, otherwise removes it.
   *
   * @param {Object} file - The file object to toggle.
   */
  const toggleFileSelection = useCallback((file) => {
    setSelectedFiles((prevFiles) => {
      if (prevFiles.some((f) => f.id === file.id)) {
        return prevFiles.filter((f) => f.id !== file.id);
      }
      return [...prevFiles, file];
    });
  }, []);

  /**
   * Adds a message to the selectedMessages state.
   *
   * @param {Object} message - The message object to add.
   */
  const addMessage = useCallback((message) => {
    setSelectedMessages((prevMessages) => {
      // Prevent adding duplicate messages based on unique 'id'
      if (!prevMessages.some((m) => m.id === message.id)) {
        return [...prevMessages, message];
      }
      return prevMessages;
    });
  }, []);

  /**
   * Removes a message from the selectedMessages state.
   *
   * @param {string} messageId - The unique identifier of the message to remove.
   */
  const removeMessage = useCallback((messageId) => {
    setSelectedMessages((prevMessages) => prevMessages.filter((m) => m.id !== messageId));
  }, []);

  /**
   * Toggles the selection state of a message.
   * Adds the message if not selected, otherwise removes it.
   *
   * @param {Object} message - The message object to toggle.
   */
  const toggleMessageSelection = useCallback((message) => {
    setSelectedMessages((prevMessages) => {
      const messageExists = prevMessages.some((f) => f.id === message.id);
      console.log('Selected Messages Updated:', messageExists);

      return messageExists 
          ? prevMessages.filter((f) => f.id !== message.id)
          : [...prevMessages, message];
    });
  }, []);

  const contextValue = useMemo(() => ({
    selectedFiles,
    setSelectedFiles,
    selectedMessages,
    setSelectedMessages,
    addFile,
    removeFile,
    toggleFileSelection,
    addMessage,
    removeMessage,
    toggleMessageSelection,
  }), [selectedFiles, setSelectedFiles, selectedMessages, setSelectedMessages, addFile, removeFile, toggleFileSelection, addMessage, removeMessage, toggleMessageSelection]);

  return (
    <SelectionContext.Provider value={contextValue}>
      {children}
    </SelectionContext.Provider>
  );
};

SelectionProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

/**
 * useSelection
 *
 * Custom hook to consume the SelectionContext.
 *
 * @returns {Object} The context value containing selection states and manipulation functions.
 */
export const useSelection = () => {
  const context = useContext(SelectionContext);
  if (!context) {
    throw new Error('useSelection must be used within a SelectionProvider');
  }
  return context;
};
