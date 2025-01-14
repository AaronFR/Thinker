// src/pages/Messages.js

import React, { useState, useCallback } from 'react';
import PropTypes from 'prop-types';

import FilePane from './FilePane';
import MessageHistory from './MessagePane';

import './styles/Messages.css';
import Navigation from '../../components/Navigation';

/**
 * Messages Page Component
 * 
 * This page consolidates both FilePane and MessageHistory components,
 * allowing users to interact with files and messages within a single interface.
 * It manages the state of selected files and messages and communicates selections back to the main app.
 * 
 * @param {Function} onFileSelect - Callback to handle file selection.
 * @param {Function} onMessageSelect - Callback to handle message selection.
 * @param {boolean} isProcessing - Indicates if the app is currently processing data.
 */
// const Messages = ({ onFileSelect, onMessageSelect }) => {
export function Messages() {
  // State to manage selected files
  const [selectedFiles, setSelectedFiles] = useState([]);
  const isProcessing = false;

  // State to manage selected messages
  const [selectedMessages, setSelectedMessages] = useState([]);


  /**
   * Handles the selection of a file.
   * Adds or removes the file from the selectedFiles state based on its current selection state.
   * Communicates the selection back to the parent component.
   * 
   * @param {Object} file - The file object to select/deselect.
   */
  const handleFileSelect = useCallback((file) => {
    setSelectedFiles((prevFiles) => {
      // ToDo: should filter by id not name
      if (prevFiles.some((f) => f.name === file.name)) {
        // If the file is already selected, filter it out
        return prevFiles.filter((f) => f.name !== file.name);
      } else {
        // Otherwise, add new the new file to the list of selectedFiles
        return [...prevFiles, file];
      }
    });
  }, []);  //onFileSelect

  /**
   * Handles the selection of a message.
   * Adds or removes the message from the selectedMessages state based on its current selection state.
   * Communicates the selection back to the parent component.
   * 
   * @param {Object} message - The message object to select/deselect.
   */
  const handleMessageSelect = useCallback((message) => {
    setSelectedMessages((prevMessages) => {
      // ToDo: should filter by id not prompt
      const messageExists = prevMessages.some((f) => f.prompt === message.prompt);
         return messageExists 
             ? prevMessages.filter((f) => f.prompt !== message.prompt)
             : [...prevMessages, message];
    });
  }, []);  //onMessageSelect

  return (
    <div className="scrollable messages-page-container">
      <Navigation />
      <h1>Messages and Files</h1>
      <div className="panes-container">
        <FilePane 
          onFileSelect={handleFileSelect}
          isProcessing={isProcessing}
          selectedFiles={selectedFiles}
        />
        <MessageHistory 
          onMessageSelect={handleMessageSelect}
          isProcessing={isProcessing}
          selectedMessages={selectedMessages}
        />
      </div>
    </div>
  );
};

Messages.propTypes = {
  onFileSelect: PropTypes.func.isRequired,
  onMessageSelect: PropTypes.func.isRequired,
  isProcessing: PropTypes.bool.isRequired,
};

export default Messages;
