import React, { useState } from 'react';

const flask_port = "http://localhost:5000";

const FileUploadButton = ({ onUploadSuccess }) => {
  const [uploadStatus, setUploadStatus] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    
    if (!file) {
      setUploadStatus('No file selected.');
      return;
    }

    setUploadStatus('Uploading...');
    setIsUploading(true);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const xhr = new XMLHttpRequest();
      xhr.open("POST", `${flask_port}/api/file`, true);

      // Track upload progress
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const percentComplete = Math.round((event.loaded / event.total) * 100);
          setUploadProgress(percentComplete);
        }
      };

      xhr.onload = () => {
        if (xhr.status === 200) {
          const data = JSON.parse(xhr.responseText);
          setUploadStatus('File uploaded successfully!');
          console.log('Success:', data);
          if (onUploadSuccess) {
            onUploadSuccess(data);
          }
        } else {
          const errorData = JSON.parse(xhr.responseText);
          setUploadStatus(`Upload failed: ${errorData.message || 'Unknown error'}`);
          console.error('Error uploading file:', errorData);
        }
        setIsUploading(false);
        setUploadProgress(0);
      };

      xhr.onerror = () => {
        setUploadStatus('File upload failed.');
        console.error('Error uploading file:', xhr.statusText);
        setIsUploading(false);
        setUploadProgress(0);
      };

      xhr.send(formData);
    } catch (error) {
      setUploadStatus('File upload failed.');
      console.error('Error uploading file:', error);
      setIsUploading(false);
      setUploadProgress(0);
    } finally {
      event.target.value = null; // Reset the file input
    }
  };

  return (
    <div>
      <input 
        type="file" 
        onChange={handleFileChange} 
        disabled={isUploading}
        style={{ cursor: isUploading ? 'not-allowed' : 'pointer' }}
      />
      {uploadStatus && <p>{uploadStatus}</p>}
      {isUploading && (
        <div style={{ width: '100%', backgroundColor: '#f3f3f3', borderRadius: '4px', marginTop: '10px' }}>
          <div 
            style={{ 
              width: `${uploadProgress}%`, 
              height: '10px', 
              backgroundColor: '#4caf50', 
              borderRadius: '4px',
              transition: 'width 0.3s'
            }}
          ></div>
        </div>
      )}
      {isUploading && <p>{uploadProgress}%</p>}
    </div>
  );
};

export default FileUploadButton;
