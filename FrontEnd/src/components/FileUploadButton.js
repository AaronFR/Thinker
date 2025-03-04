import React, { useReducer, useCallback } from 'react';
import PropTypes from 'prop-types';

import ProgressBar from '../utils/ProgressBar';

import './styles/FileUploadButton.css';

import TooltipConstants from '../constants/tooltips';
import { fileEndpoint, filesEndpoint } from '../constants/endpoints';

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

const BULK_FILE_UPLOAD = true;

/**
 * Upload a list of files individually to the single file endpoint.
 * @param {Array<File>} files - The list of selected files.
 */
async function uploadFilesIndividually(files, dispatch, onUploadSuccess) {
  // Map over the files to generate promises
  const uploadPromises = files.map(async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const controller = new AbortController();
    const signal = controller.signal;

    try {
      const response = await fetch(fileEndpoint, {
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
        console.error('Error uploading file:', error);
      }
    }
  });

  // Await all file upload promises
  await Promise.all(uploadPromises);
}

/**
 * Upload a group of files in one bulk request to the bulk file endpoint.
 * @param {Array<File>} files - The list of selected files.
 */
async function uploadFilesBulk(files, dispatch, onUploadSuccess) {
  const formData = new FormData();
  // Append each file under the same 'files' key to send them all in one request.
  files.forEach(file => formData.append('files', file));

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
 * ToDo: I should be able to click on the edges of the button and upload, currently you 
 *  have to click on the file emoji directly
 *
 * @param {Function} props.onUploadSuccess - Callback invoked upon successful upload.
 */
const FileUploadButton = ({ onUploadSuccess }) => {
  const [state, dispatch] = useReducer(uploadReducer, initialState);

  /**
   * Handles file upload when a user selects a file.
   *
   * @param {Event} event - The file input change event.
   */
  const handleFileChange = useCallback(async (event) => {
    // Convert the FileList into an Array of file objects.
    const files = Array.from(event.target.files);

    // ToDo: this should be BEFORE upload not after
    // if (file && file.size > MAX_FILE_SIZE) {
    //   setFetchError('File size exceeds the maximum limit of 10MB.');
    //   return;
    // }

    if (files.length === 0) {
      dispatch({ type: 'UPLOAD_FAILURE', payload: 'No file selected.' });
      return;
    }

    // Dispatch to indicate the start of the upload process.
    dispatch({ type: 'UPLOAD_START' });

    // Determine which upload method to call based on BULK_FILE_UPLOAD.
    if (BULK_FILE_UPLOAD) {
      await uploadFilesBulk(files, dispatch, onUploadSuccess);
    } else {
      await uploadFilesIndividually(files, dispatch, onUploadSuccess);
    }

    // Reset file input.
    event.target.value = null;
  }, [onUploadSuccess]);

  return (
    <div className="button file-upload-button">
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
      <div className='centered'>
        <label 
          htmlFor="file-input"
          className='custom-file-label'
          role="button"
          tabIndex={0}
          aria-label="Upload files"
          data-tooltip-id="tooltip"
          data-tooltip-content={TooltipConstants.fileUploadButton}
          data-tooltip-place="bottom"
        >
          📂 {/* Upload Emoji */}
        </label>

        {state.isUploading && (
          <div className='upload-progress' aria-live="polite">
            <ProgressBar progress={state.uploadProgress} />
            <p>{state.uploadProgress}%</p>
          </div>
        )}
      </div>

      
    </div>
  );
};

FileUploadButton.propTypes = {
  onUploadSuccess: PropTypes.func.isRequired,
};

export default React.memo(FileUploadButton);
