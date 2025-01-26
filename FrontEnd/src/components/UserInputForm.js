import React, { useState, useEffect, useContext } from 'react';
import PropTypes from 'prop-types';

import FileUploadButton from './FileUploadButton';
import TagsManager from './TagsManager';
import { apiFetch } from '../utils/authUtils';
import { getBasename } from '../utils/textUtils';
import AutoExpandingTextarea from '../utils/AutoExpandingTextarea';
import PersonaSelector from './Selectors/PersonaSelector'
import WorkflowSelector from './Selectors/WorkflowSelector';
import ModelSelector from './Selectors/ModelSelector';

import './styles/UserInputForm.css';

import { SettingsContext } from '../pages/Settings/SettingsContext';
import { useSelection, SelectionProvider } from '../pages/Messages/SelectionContext';
import BestOfSelector from './Selectors/BestOfSelector';
import LoopsSelector from './Selectors/LoopsSelector';
import WriteSelector from './Selectors/WriteSelector';

const FLASK_PORT = process.env.REACT_APP_THE_THINKER_BACKEND_URL || "http://localhost:5000";
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

/**
 * UserInputForm Component
 *
 * Renders a form that allows users to input text and upload files.
 * Handles fetching of uploaded files, managing uploaded files state,
 * and integrates the FileUploadButton component for file uploads.
 *
 * @param {function} handleSubmit - Function to handle form submission.
 * @param {function} handleInputChange - Function to handle changes in user input.
 * @param {string} userInput - Current value of the user input.
 * @param {boolean} isProcessing - Indicates if the form is in a processing state.
 * @param {String} selectedPersona - Currently selected persona.
 * @param {function} setSelectedPersona - Set new persona
 * @param {function} generateAugmentedPrompt - Trigger a new auto-prompt-engineer of the users prompt
 * @param {function} generateQuestionsForPrompt - Trigger a new set of questions against the users prompt
 * @param {Array} tags - Current tags.
 * @param {function} setTags - Set function for tags.
 */
const UserInputForm = ({
  handleSubmit,
  handleInputChange,
  userInput,
  isProcessing,
  selectedPersona,
  setSelectedPersona,
  generateAugmentedPrompt,
  generateQuestionsForPrompt,
  tags,
  setTags
}) => {
  const [fetchError, setFetchError] = useState('');
  const [uploadCompleted, setUploadCompleted] = useState(true)

  const { settings } = useContext(SettingsContext);
  //const { selectedMessages } = useContext(SelectionProvider)
  const { 
    selectedFiles,
    setSelectedFiles,
    toggleFileSelection, 
    selectedMessages,
    toggleMessageSelection 
  } = useSelection();
  
  /**
   * Fetches the list of uploaded files from the backend API.
   */
  const fetchStagedFiles = async () => {
    try {
        const response = await apiFetch(`${FLASK_PORT}/list_staged_files`, {
            method: "GET",
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Failed to fetch files.');
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
   * fetch uploaded files after successful file upload.
   */
  useEffect(() => {
    if (uploadCompleted) {
      fetchStagedFiles();
    }
  }, [uploadCompleted]);

  /**
   * Handles successful file uploads by updating the selectedFiles state.
   *
   * @param {Object} file - The uploaded file object.
   */
  const handleUploadSuccess = (file) => {
    if (file && file.size > MAX_FILE_SIZE) {
      setFetchError('File size exceeds the maximum limit of 10MB.');
      return;
    }
    setUploadCompleted(true);
  };

  /**
   * Handles key down events for the textarea.
   *
   * @param {Event} e - The keyboard event object.
   */
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();  // Prevent form submission
      if (e.shiftKey) {
        const { selectionStart, selectionEnd, value } = e.target;
        e.target.value =
          value.substring(0, selectionStart) + '\n' +
          value.substring(selectionEnd);
        e.target.selectionStart = e.target.selectionEnd = selectionStart + 1;
      } else {
        handleSubmit(e);
      }
    }
  };

  return (
    <div>
      {/* Display Selected Messages */}
      <div className='reference-area'>
        <ul style={{ listStyleType: 'none', padding: 0 }}>
          {selectedMessages.map((message, index) => (
            <li key={index} className="selected-item">
              <span role="img" aria-label="message">✉</span> {message.prompt}
              <button
                className="deselect-button"
                onClick={() => toggleMessageSelection(message)}
                aria-label={`Deselect this message`}
              >
                ✖️
              </button>
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
            <li key={index} className="selected-item">
              <span role="img" aria-label="file">📄</span> {file.name}
              <button
                className="deselect-button"
                onClick={() => toggleFileSelection(file)}
                aria-label={`Deselect this file`}
              >
                ✖️
              </button>
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
          onChange={(event) => handleInputChange(event, selectedMessages, selectedFiles, tags)}
          placeholder='Enter your prompt'
          className="textarea prompt-input"
          rows="2"
          required
          aria-label="User prompt input"
        />

        <div className='palette'>
          <FileUploadButton onUploadSuccess={handleUploadSuccess} />
          {settings.augmentedPromptsEnabled !== 'off' && <button 
            type="button"
            className="button submit-button"
            onClick={() => generateAugmentedPrompt(userInput)}
            disabled={isProcessing}
            aria-busy={isProcessing}
          >
            {'Auto-Engineer'}
          </button>}
          {settings.questionUserPromptsEnabled !== 'off' &&<button // settings.promptQuestioningMessage != 'off'
            type="button"
            className="button submit-button"
            onClick={() => generateQuestionsForPrompt(userInput, selectedMessages, selectedFiles)}
            disabled={isProcessing}
            aria-busy={isProcessing}
          >
            {'Question'}
          </button>}
          <button 
            type="submit"
            className="button submit-button"
            disabled={isProcessing}
            aria-busy={isProcessing}
          >
            {isProcessing ? 'Processing...' : 'Enter'}
          </button>
        </div>

        <div className='palette'>
        <PersonaSelector 
            selectedPersona={selectedPersona} 
            setSelectedPersona={setSelectedPersona}
          />

          <WorkflowSelector
            selectedWorkflow={tags.workflow}
            setTags={setTags}
          />
          {tags.workflow == 'loop' && <LoopsSelector
            selectedNumberOfLoops={tags.loops}
            setTags={setTags}
          />}
          {tags.workflow == 'write' && <WriteSelector
            write={tags.write}
            setTags={setTags}
          />}

          <ModelSelector
            selectedModel={tags.model}
            setTags={setTags}
          />

          <BestOfSelector
            bestOf={tags.bestOf}
            setTags={setTags}
          />
          
        </div>

        {settings.debug === true && <TagsManager tags={tags} setTags={setTags} />}
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
