// src/pages/Messages.js

import React from 'react';
import PropTypes from 'prop-types';

import FilePane from './FilePane';
import MessageHistory from './MessagePane';
import Navigation from '../../components/Navigation';
import { useSelection } from './SelectionContext';

import './styles/Messages.css';


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
  const isProcessing = false;

  // Manage selected file / message context
  const { 
    selectedFiles, 
    toggleFileSelection, 
    selectedMessages,
    toggleMessageSelection 
  } = useSelection();

  return (
    <div className="scrollable messages-page-container">
      <Navigation />
      <h1>Messages and Files</h1>
      <div className="panes-container">
        <FilePane 
          onFileSelect={toggleFileSelection}
          isProcessing={isProcessing}
          selectedFiles={selectedFiles}
        />
        <MessageHistory 
          onMessageSelect={toggleMessageSelection}
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
