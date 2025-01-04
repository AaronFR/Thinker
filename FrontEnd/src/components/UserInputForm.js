import React, { useState, useEffect } from 'react';
import './styles/UserInputForm.css';
import PropTypes from 'prop-types';

import FileUploadButton from './FileUploadButton';
import TagsManager from './TagsManager';
import { apiFetch } from '../utils/authUtils';
import { getBasename } from '../utils/textUtils'

import AutoExpandingTextarea from '../utils/AutoExpandingTextarea';

const FLASK_PORT = process.env.REACT_APP_THE_THINKER_BACKEND_URL || "http://localhost:5000";

/**
 * UserInputForm Component
 * 
 * Renders a form that allows users to input text and upload files.
 * Handles fetching of uploaded files, managing uploaded files state,
 * and integrates the FileUploadButton component for file uploads.
 * 
 * Props:
 * - handleSubmit (function): Function to handle form submission.
 * - handleInputChange (function): Function to handle changes in user input.
 * - userInput (string): Current value of the user input.
 * - isProcessing (boolean): Indicates if the form is in a processing state.
 * - selectedFiles (File): Currently selected file for upload.
 */
const UserInputForm = ({
  handleSubmit,
  handleInputChange,
  userInput,
  isProcessing,
  selectedFiles,
  setSelectedFiles,
  selectedMessages,
  setSelectedMessages,
  tags,
  setTags
}) => {
  const [fetchError, setFetchError] = useState('');
  const [uploadCompleted, setUploadCompleted] = useState(true)

  /**
   * Fetches the list of uploaded files from the backend API.
   */
  const fetchStagedFiles = async () => {
    try {
        const response = await apiFetch(`${FLASK_PORT}/list_staged_files`, {
            method: "GET",
            credentials: "include"
        });

        if (!response.ok) {
            const errorData = await response.json();
            setFetchError(errorData.message || 'Failed to fetch files.');
            return;
        }

        const data = await response.json();

        const existingFileNames = new Set(selectedFiles.map(file => file.name));
        const newFiles = data.files
            .map(fileName => ({ name: getBasename(fileName) }))
            .filter(file => !existingFileNames.has(file.name)); // Filter out duplicates

        setSelectedFiles(prevFiles => [
            ...prevFiles,
            ...newFiles
        ]);
    } catch (error) {
        setFetchError(`Error fetching files: ${error.message}`);
        console.error(error);
    } finally {
        setUploadCompleted(false);
    }
};

  /**
   * useEffect hook to fetch uploaded files
   */
  useEffect(() => {
    if (uploadCompleted){
      fetchStagedFiles();
    }
  }, [uploadCompleted]);

  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

  /**
   * Handles successful file uploads by updating the uploadedFiles state
   * and setting the files for prompting.
   * 
   * @param {Object} file - The uploaded file object.
   */
  const handleUploadSuccess = (file) => {
    if (file) {
      if (file.size > MAX_FILE_SIZE) {
        setFetchError('File size exceeds the maximum limit of 5MB.');
        return;
      }
      setUploadCompleted(true)
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
        if (e.shiftKey) {
            e.preventDefault();  // Prevent form submission and insert newline.
            const { selectionStart, selectionEnd, value } = e.target;
            e.target.value =
                value.substring(0, selectionStart) + '\n' +
                value.substring(selectionEnd);
            e.target.selectionStart = e.target.selectionEnd = selectionStart + 1;
        } else {
            e.preventDefault(); // Prevent default Enter behavior.
            handleSubmit(e);    // Submit the form.
        }
    }
  };

  return (
    <div>
      {/* Display Selected Messages */}
      <div className='reference-area'>
        {fetchError && <p style={{ color: 'red' }}>{fetchError}</p>}
        {selectedMessages.length === 0 && !fetchError}
        <ul style={{ listStyleType: 'none', padding: 0 }}>
          {selectedMessages.map((message, index) => (
            <li key={index}>
              <span role="img" aria-label="message">✉</span> {message.prompt}
            </li>
          ))}
        </ul>
      </div>

      {/* Display Selected Files */}
      <div className='reference-area'>
        {fetchError && <p className='error-message'>{fetchError}</p>}
        {selectedFiles.length === 0 && !fetchError}
        <ul style={{ listStyleType: 'none', padding: 0 }}>
          {selectedFiles.map((file, index) => (
            <li key={index}>
              <span role="img" aria-label="file">📄</span> {file.name}
            </li>
          ))}
        </ul>
      </div>

      {/* User Input Form */}
      <form className='user-input-form' onSubmit={handleSubmit}>
        <AutoExpandingTextarea
          id='prompt-input'
          value={userInput}
          onKeyDown={handleKeyDown}
          onChange={(event) => handleInputChange(event, selectedMessages, selectedFiles)}
          placeholder='Enter your prompt'
          className="textarea prompt-input"
          rows="2"
          required
          aria-label="User prompt input"
        />

        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '5px'}}>
          <FileUploadButton onUploadSuccess={handleUploadSuccess} />
          <button 
            type="submit"
            className="button submit-button"
            disabled={isProcessing}
            aria-busy={isProcessing}
          >
            {isProcessing ? 'Processing...' : 'Enter'}
          </button>
        </div>

        <TagsManager tags={tags} setTags={setTags}/>
      </form>
    </div>
  );
};

UserInputForm.propTypes = {
  handleSubmit: PropTypes.func.isRequired,
  handleInputChange: PropTypes.func.isRequired,
  userInput: PropTypes.string.isRequired,
  isProcessing: PropTypes.bool.isRequired,
  selectedFiles: PropTypes.arrayOf(
      PropTypes.shape({
          name: PropTypes.string.isRequired,
      })
  ).isRequired,
  setSelectedFiles: PropTypes.func.isRequired,
  selectedMessages: PropTypes.arrayOf(
      PropTypes.shape({
          prompt: PropTypes.string.isRequired,
      })
  ).isRequired,
  setSelectedMessages: PropTypes.func.isRequired,
  tags: PropTypes.arrayOf(PropTypes.string).isRequired,
  setTags: PropTypes.func.isRequired,
};

export default UserInputForm;
