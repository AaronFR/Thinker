import React, { useState } from 'react';

const flask_port = "http://localhost:5000";

const FileUploadButton = () => {
  const [uploadStatus, setUploadStatus] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  // Handle file selection and upload
  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    
    if (!file) {
      setUploadStatus('No file selected.');
      return;
    }

    setUploadStatus('Uploading...');
    setIsUploading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${flask_port}/api/file`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        setUploadStatus(`Upload failed: ${errorData.message || 'Unknown error'}`);
        console.error('Error uploading file:', errorData);
        setIsUploading(false);
        return;
      }

      const data = await response.json();
      setUploadStatus('File uploaded successfully!');
      console.log('Success:', data);
    } catch (error) {
      setUploadStatus('File upload failed.');
      console.error('Error uploading file:', error);
    } finally {
      setIsUploading(false);
      event.target.value = null;
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
    </div>
  );
};

export default FileUploadButton;
