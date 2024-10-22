import React, { useState, useEffect } from 'react';
import './styles/UserInputForm.css';

import FileUploadButton from './FileUploadButton';

const flask_port = "http://localhost:5000";

const UserInputForm = ({ handleSubmit, handleInputChange, userInput, isProcessing, selectedFile }) => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [fetchError, setFetchError] = useState('');

  const fetchUploadedFiles = async () => {
    try {
      const response = await fetch(`${flask_port}/api/files`, {
        method: "GET",
      });

      if (!response.ok) {
        const errorData = await response.json();
        setFetchError(errorData.message || 'Failed to fetch files.');
        return;
      }

      const data = await response.json();
      // setUploadedFiles(data.files);
    } catch (error) {
      setFetchError('Error fetching files.');
      console.error('Error fetching files:', error);
    }
  };

  useEffect(() => {
    fetchUploadedFiles();

    const interval = setInterval(() => {
      fetchUploadedFiles();
    }, 5000); // Every 5 seconds

    return () => clearInterval(interval); // Cleanup on unmount
  }, []);

  const handleUploadSuccess = (file) => {
    console.log("filename: ", file)
    if (file) {
      setUploadedFiles((prevFiles) => [...prevFiles, file.filename]);
    }
    console.log("uploaded files though upload: ", uploadedFiles)
  };

  useEffect(() => {
    console.log("selectedFile: ", selectedFile)
    if (selectedFile) {
      setUploadedFiles((prevFiles) => [...prevFiles, selectedFile.name]);
    }
    console.log("uploaded files through effect: ", uploadedFiles)
  }, [selectedFile])

  return (
    <div>
      {/* Display Uploaded Files */}
      <div style={{ marginBottom: '20px' }}>
        <h3>Selected Files:</h3>
        {fetchError && <p style={{ color: 'red' }}>{fetchError}</p>}
        {uploadedFiles.length === 0 && !fetchError && <p>No files uploaded yet.</p>}
        <ul style={{ listStyleType: 'none', padding: 0 }}>
          {uploadedFiles.map((file, index) => (
            <li key={index} style={{ padding: '5px 0' }}>
              <span role="img" aria-label="file">📄</span> {file}
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
            handleSubmit();
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
            style={{ resize: 'none', overflowY: 'auto', marginLeft: '10px', marginRight: '10px', width: '300px' }}
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

export default UserInputForm;
