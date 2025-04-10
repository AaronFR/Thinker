import React, { useReducer, useCallback } from 'react';
import PropTypes from 'prop-types';

import ProgressBar from '../utils/ProgressBar';

import './styles/FileUploadButton.css';

import TooltipConstants from '../constants/tooltips';
import { filesEndpoint } from '../constants/endpoints';


// Define initial state for the reducer
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
const uploadReducer = (state, action) => {
  switch (action.type) {
    case 'UPLOAD_START':
      return { ...state, isUploading: true, uploadStatus: 'Uploading...' };
    case 'UPLOAD_SUCCESS':
      return { ...state, isUploading: false, uploadStatus: 'File uploaded successfully!' };
    case 'UPLOAD_FAILURE':
      return { ...state, isUploading: false, uploadStatus: action.payload };
    case 'RESET':
      return initialState;
    default:
      return state;
  }
};

/**
 * Upload a group of files in one bulk request to the bulk file endpoint.
 * @param {Array<File>} files - The list of selected files.
 */
async function uploadFiles(files, dispatch, onUploadSuccess, tags) {
  const formData = new FormData();
  // Append each file under the same 'files' key to send them all in one request.
  files.forEach(file => formData.append('files', file));

  if (tags) {
    formData.append('tags', JSON.stringify(tags));
  }

  const controller = new AbortController();
  const signal = controller.signal;

  try {
    const response = await fetch(filesEndpoint, {
      method: 'POST',
      body: formData,
      signal,
      credentials: 'include'
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Unknown error occurred');
    }

    const data = await response.json();
    dispatch({ type: 'UPLOAD_SUCCESS' });
    if (onUploadSuccess) {
      onUploadSuccess(data);
    }
  } catch (error) {
    if (error.name === 'AbortError') {
      console.warn('Upload aborted');
    } else {
      dispatch({ type: 'UPLOAD_FAILURE', payload: `Upload failed: ${error.message}` });
      console.error('Error uploading files:', error);
    }
  }
}

/**
 * Allows users to upload files
 *
 * @param {Function} props.onUploadSuccess - Callback invoked upon successful upload.
 * @param {Object} props.tags - Object containing current prompt tags to send with the upload.
 */
const FileUploadButton = ({ onUploadSuccess, tags }) => {
  const [state, dispatch] = useReducer(uploadReducer, initialState);

  /**
   * Handles file upload when a user selects a file.
   *
   * @param {Event} event - The file input change event.
   */
  const handleFileChange = useCallback(async (event) => {
    // Convert the FileList into an Array of file objects.
    const files = Array.from(event.target.files);

    if (files.length === 0) {
      dispatch({ type: 'UPLOAD_FAILURE', payload: 'No file selected.' });
      return;
    }

    // Dispatch to indicate the start of the upload process.
    dispatch({ type: 'UPLOAD_START' });

    await uploadFiles(files, dispatch, onUploadSuccess, tags);
    // Reset file input.
    event.target.value = null;
  }, [onUploadSuccess, tags]);

  return (
    <label 
      className="button file-upload-button"
      data-tooltip-id="tooltip"
      data-tooltip-content={TooltipConstants.fileUploadButton}
      data-tooltip-place="bottom"
    >
      <input
        type="file"
        onChange={handleFileChange}
        disabled={state.isUploading}
        className='file-input'
        multiple
      />
      <div className='centered'>
        <span className='custom-file-label' role="button" tabIndex={0} aria-label="Upload files">
          📂
        </span>

        {state.isUploading && (
          <div className='upload-progress' aria-live="polite">
            <ProgressBar progress={state.uploadProgress} />
            <div>{state.uploadProgress}%</div>
          </div>
        )}
      </div>
    </label>
  );
};

FileUploadButton.propTypes = {
  onUploadSuccess: PropTypes.func.isRequired,
  tags: PropTypes.object.isRequired,
};

export default React.memo(FileUploadButton);
