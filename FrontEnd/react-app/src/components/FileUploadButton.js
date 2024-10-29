import React, { useReducer, useCallback } from 'react';
import PropTypes from 'prop-types';

import ProgressBar from './ProgressBar';
import { prototyping_user_id } from '../utils/loginUtils'

import './styles/FileUploadButton.css';

const flask_port = "http://localhost:5000";

const initialState = {
  uploadStatus: '',
  isUploading: false,
  uploadProgress: 0,
};

/**
 * Reducer function to manage upload state transitions.
 * 
 * @param {Object} state - Current state.
 * @param {Object} action - Action object containing type and payload.
 * @returns {Object} - New state.
 */
function uploadReducer(state, action) {
  switch (action.type) {
    case 'UPLOAD_START':
      return { ...state, isUploading: true, uploadStatus: 'Uploading...', uploadProgress: 0 };
    case 'UPLOAD_PROGRESS':
      return { ...state, uploadProgress: action.payload };
    case 'UPLOAD_SUCCESS':
      return { ...state, isUploading: false, uploadStatus: 'File uploaded successfully!', uploadProgress: 0 };
    case 'UPLOAD_FAILURE':
      return { ...state, isUploading: false, uploadStatus: action.payload, uploadProgress: 0 };
    case 'RESET':
      return initialState;
    default:
      return state;
  }
}


/**
 * FileUploadButton Component
 * 
 * Allows users to upload files with real-time progress feedback.
 * 
 * @param {Object} props - Component props.
 * @param {Function} props.onUploadSuccess - Callback invoked upon successful upload.
 */
const FileUploadButton = ({ onUploadSuccess }) => {
  const [state, dispatch] = useReducer(uploadReducer, initialState);

  /**
   * Handles file upload when a user selects a file.
   * Supports multiple file uploads and provides upload progress feedback.
   * 
   * @param {Event} event - The file input change event.
   */
  const handleFileChange = useCallback(async (event) => {
    const files = Array.from(event.target.files);

    if (files.length === 0) {
      dispatch({ type: 'UPLOAD_FAILURE', payload: 'No file selected.' });
      return;
    }
    dispatch({ type: 'UPLOAD_START' });

    for (const file of files) {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('user_id', prototyping_user_id);

      const controller = new AbortController();
      const signal = controller.signal;

      try {
        const response = await fetch(`${flask_port}/file`, {
          method: 'POST',
          body: formData,
          signal,
        });

        if (!response.ok) {
          const errorData = await response.json();
          dispatch({ type: 'UPLOAD_FAILURE', payload: `Upload failed: ${errorData.message || 'Unknown error'}` });
          console.error('Error uploading file:', errorData);
          continue;
        }

        const data = await response.json();
        dispatch({ type: 'UPLOAD_SUCCESS' });
        console.log('Success:', data);
        if (onUploadSuccess) {
          onUploadSuccess(data);
        }
      } catch (error) {
        if (error.name === 'AbortError') {
          console.warn('Upload aborted');
        } else {
          dispatch({ type: 'UPLOAD_FAILURE', payload: 'File upload failed.' });
          console.error('Error uploading file:', error);
        }
      }
    }

    // Reset the file input after upload
    event.target.value = null;
  }, [onUploadSuccess, dispatch]);

  return (
    <div className="file-upload-button">
      <input 
        type="file" 
        id="file-input"
        onChange={handleFileChange} 
        disabled={state.isUploading}
        className='file-input'
        aria-disabled={state.isUploading}
        multiple
        style={{ display: 'none' }}
      />

      {/* Custom Label as a Button */}
      <label htmlFor="file-input" className='custom-file-label'>
      📂 {/* Upload Emoji */}
      </label>

      {state.isUploading && (
        <div className='upload-progress'>
          <ProgressBar progress={state.uploadProgress} />
          <p>{state.uploadProgress}%</p>
        </div>
      )}
    </div>
  );
};

FileUploadButton.propTypes = {
  onUploadSuccess: PropTypes.func.isRequired,
};

export default FileUploadButton;
