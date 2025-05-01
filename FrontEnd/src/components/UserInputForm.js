import React, { useState, useContext, useCallback } from 'react';
import PropTypes from 'prop-types';

import FileUploadButton from './FileUploadButton';
import TagsManager from './TagsManager';

import { SettingsContext } from '../pages/Settings/SettingsContext';
import { useSelection } from '../pages/Messages/SelectionContext';

import WorkerSelector from './Selectors/WorkerSelector'
import WorkflowSelector from './Selectors/WorkflowSelector';
import ModelSelector from './Selectors/ModelSelector';
import BestOfSelector from './Selectors/BestOfSelector';
import LoopsSelector from './Selectors/LoopsSelector';
import WriteSelector from './Selectors/WriteSelector';
import PagesSelector from './Selectors/PagesSelector';

import { shortenText } from '../utils/textUtils';
import AutoExpandingTextarea from '../utils/AutoExpandingTextarea';
import { Tooltip } from 'react-tooltip';
import TooltipConstants from '../constants/tooltips';

import './styles/UserInputForm.css';
import CategorySelector from './Selectors/CategorySelector';



/**
 * Renders a form that allows users to input text and upload files.
 * Handles fetching of uploaded files, managing uploaded files state,
 * and integrates the FileUploadButton component for file uploads.
 *
 * @param {function} handleSubmit - Function to handle form submission.
 * @param {function} disconnectFromRequest - Function to abort the form submission stream.
 * @param {function} handleInputChange - Function to handle changes in user input.
 * @param {string} userInput - Current value of the user input.
 * @param {boolean} isProcessing - Indicates if the form is in a processing state.
 * @param {function} generateAugmentedPrompt - Trigger a new auto-prompt-engineer of the users prompt
 * @param {function} generateQuestionsForPrompt - Trigger a new set of questions against the users prompt
 * @param {Array} tags - Current tags.
 * @param {function} setTags - Set function for tags.
 * @param {function} setRefreshFiles - trigger to refresh files after file upload
 */
const UserInputForm = ({
  handleSubmit,
  disconnectFromRequest,
  handleInputChange,
  userInput,
  isProcessing,
  generateAugmentedPrompt,
  generateQuestionsForPrompt,
  categoryIsLoading,
  workflowIsLoading,
  workerIsLoading,
  tags,
  setTags,
  setRefreshFiles
}) => {
  const [fetchError, setFetchError] = useState('');

  const { settings } = useContext(SettingsContext);
  const {
    selectedFiles,
    setSelectedFiles,
    toggleFileSelection,
    selectedMessages,
    toggleMessageSelection
  } = useSelection();

  /**
   * Handles successful file uploads by updating the selectedFiles state.
   *
   * @param {Object} file - The uploaded file object.
   */
  const handleUploadSuccess = useCallback((response) => {
    if (!response || !response.files || !Array.isArray(response.files)) {
      setFetchError('Failed to upload file');
      return;
    }

    // Build a set of file names we already have
    const existingFileNames = new Set(selectedFiles.map(file => file.name))

    const newFiles = response.files
      .filter(file => !existingFileNames.has(file.name))
      .map(file => ({
        category_id: file.category_id,
        id: file.id,
        name: file.name
      }));

    if (newFiles.length > 0) {
      setSelectedFiles(prevFiles => [
        ...prevFiles,
        ...newFiles
      ]);
      
      // Trigger refresh with the first sent file
      setRefreshFiles(newFiles[0].name);
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
    <div className="user-input-form-container">
      {/* Reference Area */}
      {(selectedMessages.length !== 0 || selectedFiles.length !== 0) &&
      <div className="reference-area">
        {selectedMessages.length !== 0 && 
        <div className="reference-section">
          <ul className="reference-list">
            {selectedMessages.map((message, index) => (
              <li key={index} className="selected-item left">
                <span role="img" aria-label="message">✉</span> {shortenText(message.prompt, 80)}
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
        </div>}

        {selectedFiles.length !== 0 && 
        <div className="reference-section">
          {fetchError && <p className='error-message'>{fetchError}</p>}
          <ul className="reference-list">
            {selectedFiles.map((file, index) => (
              <li key={index} className="selected-item right">
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
        </div>}
      </div>}

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

        {/* Primary Action Buttons */}
        <div className="primary-actions">
          <FileUploadButton
            onUploadSuccess={handleUploadSuccess}
            tags={tags}
          />
          {settings.prompt_improvement?.augmented_prompts_enabled == 'on' && (
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
          {settings.prompt_improvement?.question_user_prompts_enabled == 'on' && (
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

        {/* Selectors */}
        <div className="selectors-grid">
          <div className="selector-group">
            <CategorySelector
              selectedCategory={tags.category}
              setTags={setTags}
              isLoading={categoryIsLoading}
            />
          </div>

          <div className="selector-group workflow-selectors">
            <WorkerSelector
              selectedWorker={tags.worker}
              setTags={setTags}
              isLoading={workerIsLoading}
            />
            <WorkflowSelector
              selectedWorkflow={tags.workflow}
              setTags={setTags}
              isLoading={workflowIsLoading}
            />
            {tags.workflow === 'write' && (
              <>
                <WriteSelector
                  write={tags.write}
                  setTags={setTags}
                />
                {tags.worker === 'writer' && tags.workflow === 'write' && (
                  <PagesSelector
                    pages={tags.pages}
                    setTags={setTags}
                  />
                )}
              </>
            )}
          </div>

          <div className="selector-group">
            <ModelSelector
              selectedModel={tags.model}
              setTags={setTags}
              forTags={true}
            />
            {settings.response_improvement?.multiple_reruns_enabled == 'on' && (
              <BestOfSelector
                bestOf={tags.bestOf}
                setTags={setTags}
              />
            )}
            {settings.response_improvement?.loops_enabled == 'on' && (
              <LoopsSelector
                selectedNumberOfLoops={tags.loops}
                setTags={setTags}
              />
            )}
          </div>
        </div>

        {settings?.interface?.debug === true && (
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
  tags: PropTypes.object.isRequired,
  setTags: PropTypes.func.isRequired,
};

export default React.memo(UserInputForm);
