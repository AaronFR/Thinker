import React, { useState, useEffect } from 'react';
import './styles/UserInputForm.css';
import PropTypes from 'prop-types';

import FileUploadButton from './FileUploadButton';

const flask_port = "http://localhost:5000";

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
const UserInputForm = ({ handleSubmit, handleInputChange, userInput, isProcessing, selectedFiles, setSelectedFiles }) => {
  const [fetchError, setFetchError] = useState('');

  /**
   * Fetches the list of uploaded files from the backend API.
   */
  const fetchUploadedFiles = async () => {
    try {
      const response = await fetch(`${flask_port}/list_files`, {
        method: "GET",
      });

      if (!response.ok) {
        const errorData = await response.json();
        setFetchError(errorData.message || 'Failed to fetch files.');
        return;
      }

      const data = await response.json();
      // setUploadedFiles(data.files);  // WIP, would replace with only staged
    } catch (error) {
      setFetchError('Error fetching files.');
      console.error('Error fetching files:', error);
    }
  };

  /**
   * useEffect hook to fetch uploaded files on component mount and set up polling.
   */
  useEffect(() => {
    fetchUploadedFiles();

    const interval = setInterval(() => {
      fetchUploadedFiles();
    }, 5000); // Every 5 seconds

    return () => clearInterval(interval); // Cleanup on unmount
  }, []);

  /**
   * Handles successful file uploads by updating the uploadedFiles state
   * and setting the files for prompting.
   * 
   * @param {Object} file - The uploaded file object.
   */
  const handleUploadSuccess = (file) => {
    if (file) {
      // Ensure the file object is properly structured and append to the selectedFiles array
      // ToDo: This will need to be handled properly
      setSelectedFiles((prevFiles) => [...prevFiles, { name: file.filename }]);
    }
  };

  return (
    <div>
      {/* Display Uploaded Files */}
      <div style={{ marginBottom: '20px' }}>
        {fetchError && <p style={{ color: 'red' }}>{fetchError}</p>}
        {selectedFiles.length === 0 && !fetchError}
        <ul style={{ listStyleType: 'none', padding: 0 }}>
          {selectedFiles.map((file, index) => (
            <li key={index} style={{ padding: '5px 0' }}>
              <span role="img" aria-label="file">📄</span> {file.name}
            </li>
          ))}
        </ul>
      </div>

      {/* User Input Form */}
      <form 
        onSubmit={handleSubmit}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && e.shiftKey) {
            e.preventDefault();
            const { selectionStart, selectionEnd, value } = e.target;
            
            e.target.value = 
              value.substring(0, selectionStart) + '\n' + value.substring(selectionEnd);
            
            e.target.selectionStart = e.target.selectionEnd = selectionStart + 1;
          } else if (e.key === 'Enter') {
            e.preventDefault();
            handleSubmit(e);
          }
        }}
        style={{ marginTop: '20px' }}
      >
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          {/* Pass the callback to handleUploadSuccess */}
          <FileUploadButton onUploadSuccess={handleUploadSuccess} />
          <textarea
            value={userInput}
            onChange={handleInputChange}
            placeholder='Enter your prompt'
            className="prompt-input"
            rows="2"
            style={{ resize: 'none', overflowY: 'auto', marginLeft: '10px', marginRight: '10px', width: '500px' }}
          ></textarea>
          <button 
            type="submit"
            className="submit-button"
            disabled={isProcessing}
            style={{ padding: '10px 20px' }}
          >
            {isProcessing ? 'Processing...' : 'Enter'}
          </button>
        </div>
      </form>
    </div>
  );
};

UserInputForm.propTypes = {
  handleSubmit: PropTypes.func.isRequired,
  handleInputChange: PropTypes.func.isRequired,
  userInput: PropTypes.string.isRequired,
  isProcessing: PropTypes.bool.isRequired,
  selectedFiles: PropTypes.instanceOf(File),
};

export default UserInputForm;
