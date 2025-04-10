import React from 'react';

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
export function Messages() {
  const isProcessing = false;

  // Manage selected file / message context
  const { 
    selectedFiles,
    removeFile,
    toggleFileSelection, 
    selectedMessages,
    removeMessage,
    toggleMessageSelection 
  } = useSelection();

  return (
    <div className="scrollable messages-page-container container">
      <Navigation />
      <h1>Messages and Files</h1>
      <div className="panes-container">
        <FilePane 
          onFileSelect={toggleFileSelection}
          isProcessing={isProcessing}
          selectedFiles={selectedFiles}
          removeFile={removeFile}
        />
        <MessageHistory 
          onMessageSelect={toggleMessageSelection}
          isProcessing={isProcessing}
          selectedMessages={selectedMessages}
          removeMessage={removeMessage}
        />
      </div>
    </div>
  );
};

export default Messages;
