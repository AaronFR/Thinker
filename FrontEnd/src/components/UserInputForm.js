import React, { useState, useEffect, useContext, useCallback } from 'react';
import PropTypes from 'prop-types';

import FileUploadButton from './FileUploadButton';
import TagsManager from './TagsManager';

import { SettingsContext } from '../pages/Settings/SettingsContext';
import { useSelection } from '../pages/Messages/SelectionContext';

import PersonaSelector from './Selectors/PersonaSelector'
import WorkflowSelector from './Selectors/WorkflowSelector';
import ModelSelector from './Selectors/ModelSelector';
import BestOfSelector from './Selectors/BestOfSelector';
import LoopsSelector from './Selectors/LoopsSelector';
import WriteSelector from './Selectors/WriteSelector';
import PagesSelector from './Selectors/PagesSelector';

import { apiFetch } from '../utils/authUtils';
import { getBasename } from '../utils/textUtils';
import AutoExpandingTextarea from '../utils/AutoExpandingTextarea';
import { Tooltip } from 'react-tooltip';
import TooltipConstants from '../constants/tooltips';

import './styles/UserInputForm.css';


const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

/**
 * UserInputForm Component
 *
 * Renders a form that allows users to input text and upload files.
 * Handles fetching of uploaded files, managing uploaded files state,
 * and integrates the FileUploadButton component for file uploads.
 *
 * @param {function} handleSubmit - Function to handle form submission.
 * @param {function} disconnectFromRequest - Function to abort the form submission stream.
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
  disconnectFromRequest,
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
  const { 
    selectedFiles,
    setSelectedFiles,
    toggleFileSelection, 
    selectedMessages,
    toggleMessageSelection 
  } = useSelection();

  /**
   * fetch uploaded files after successful file upload.
   */
  useEffect(() => {
    if (uploadCompleted) {
    }
  }, [uploadCompleted]);

  /**
   * Handles successful file uploads by updating the selectedFiles state.
   *
   * @param {Object} file - The uploaded file object.
   */
  const handleUploadSuccess = useCallback((file) => {
    if (file && file.size > MAX_FILE_SIZE) {
      setFetchError('File size exceeds the maximum limit of 10MB.');
      return;
    }
    setUploadCompleted(true);

      const existingFileNames = new Set(selectedFiles.map(file => file.name));

      if (!existingFileNames.has(file.filename)) {
        setSelectedFiles(prevFiles => [
          ...prevFiles,
          {'category_id': file.category_id, 'id': file.id, 'name': file.name}
      ]);
      }

      
  }, []);

  /**
   * Handles key down events for the textarea.
   *
   * @param {Event} e - The keyboard event object.
   */
  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  }, [handleSubmit]);

  // Wrap the onChange callback so it gets passed down without inline creation
  const handleChange = useCallback(
    (event) => handleInputChange(event, selectedMessages, selectedFiles, tags),
    [handleInputChange, selectedMessages, selectedFiles, tags]
  );

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
                aria-label="Deselect this message"
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
          onChange={handleChange}
          placeholder='Enter your prompt'
          className="textarea prompt-input"
          rows="2"
          required
          aria-label="User prompt input"
        />

        <div className='palette-container'>
          <div className='palette'>
            <FileUploadButton onUploadSuccess={handleUploadSuccess} />
            {settings.augmentedPromptsEnabled !== 'off' && (
              <button
                type="button"
                className="button submit-button"
                onClick={() => generateAugmentedPrompt(userInput)}
                disabled={isProcessing}
                aria-busy={isProcessing}
                data-tooltip-id="tooltip"
                data-tooltip-html={TooltipConstants.augmentButton}
                data-tooltip-place="bottom"
              >
                Improve prompt
              </button>
            )}
            {settings.questionUserPromptsEnabled !== 'off' && (
              <button
                type="button"
                className="button submit-button"
                onClick={() => generateQuestionsForPrompt(userInput, selectedMessages, selectedFiles)}
                disabled={isProcessing}
                aria-busy={isProcessing}
                data-tooltip-id="tooltip"
                data-tooltip-html={TooltipConstants.questionButton}
                data-tooltip-place="bottom"
              >
                Question
              </button>
            )}
            {isProcessing ? (
              <button
                type="button"
                className="button submit-button"
                onClick={disconnectFromRequest}
                aria-busy={isProcessing}
                data-tooltip-id="tooltip"
                data-tooltip-html={TooltipConstants.submitButton_whileProcessing}
                data-tooltip-place="bottom"
              >
                New
              </button>
            ) : (
              <button
                type="submit"
                className="button submit-button"
                disabled={isProcessing}
                data-tooltip-id="tooltip"
                data-tooltip-html={TooltipConstants.submitButton}
                data-tooltip-place="bottom"
              >
                Enter
              </button>
            )}
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
            {tags.workflow === 'loop' && (
              <LoopsSelector
                selectedNumberOfLoops={tags.loops}
                setTags={setTags}
              />
            )}
            {tags.workflow === 'write' && (
              <WriteSelector
                write={tags.write}
                setTags={setTags}
              />
            )}
            {selectedPersona === 'writer' && tags.workflow === 'write' && (
              <PagesSelector
                pages={tags.pages}
                setTags={setTags}
              />
            )}
            <ModelSelector
              selectedModel={tags.model}
              setTags={setTags}
              forTags={true}
            />
            {settings.bestOfEnabled !== 'off' && (
              <BestOfSelector
                bestOf={tags.bestOf}
                setTags={setTags}
              />
            )}
          </div>
        </div>
        

        {settings.debug === true && (
          <TagsManager tags={tags} setTags={setTags} />
        )}
        <Tooltip id="tooltip" />
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

export default React.memo(UserInputForm);
