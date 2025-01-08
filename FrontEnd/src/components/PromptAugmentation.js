import React from 'react';
import PropTypes from 'prop-types';

import { MarkdownRenderer, withLoadingOpacity } from '../utils/textUtils';
import ExpandableElement from '../utils/expandableElement';

import './styles/PromptAugmentation.css';

/**
 * PromptAugmentation Component
 * 
 * Displays augmented prompts and provides an option to copy the augmented prompt.
 * 
 * ToDo: the augmentedPromptsEnabled check should probably be higher up. 
 *  A component should not have to worry about disabling itself
 * 
 * @param {boolean} augmentedPromptsEnabled (boolean): Flag to enable or disable augmented prompts.
 * @param {string} augmentedPrompt (string): The augmented prompt text.
 * @param {string} [error=''] - Optional error message to display.
 * @param {boolean} isAugmenting (boolean): Indicates if the augmentation process is ongoing.
 * @param {function} copyAugmentedPrompt (function): Function to copy the augmented prompt.
 */
const PromptAugmentation = ({
  augmentedPromptsEnabled,
  augmentedPrompt,
  error = '',
  isAugmenting,
  copyAugmentedPrompt,
}) => {
  // Immediately return null if augmented prompts are not enabled or the prompt is empty
  if (!augmentedPromptsEnabled) return null;

  // Display loading message if an augmented prompt is not yet ready
  if (!augmentedPrompt) {
    return (
      <div style={withLoadingOpacity(isAugmenting)}>
        {isAugmenting ? "Engineering prompt..." : ""}
      </div>
    );
  }

  const handleCopyClick = (e) => {
    e.stopPropagation();
    copyAugmentedPrompt();
  };

  const buttonLabel = isAugmenting ? 'Copying augmented prompt...' : 'Copy';
  const buttonText = isAugmenting ? 'Augmenting...' : 'Copy';

  const minContent = (
      <MarkdownRenderer
          markdownText="Augmented Prompt +"
          className="markdown-augmented"
          isLoading={isAugmenting}
      />
  );

  const maxContent = (
    <div>
      {error ? (
        <p className="error-message" role="alert">
          {error}
        </p>
      ) : (
        <div className='augmented-container'>
          <MarkdownRenderer
            markdownText={augmentedPrompt}
            className="markdown-augmented"
            isLoading={isAugmenting}
          />
          <button
            className="button augment-button"
            onClick={handleCopyClick}
            disabled={isAugmenting}
            aria-label={buttonLabel}
          >
            {buttonText}
          </button>
        </div>
      )}
    </div>
  );

  return (
      <div className="augmented-container">
        <ExpandableElement
          minContent={minContent}
          maxContent={maxContent}
          initiallyExpanded={true}
          toggleButtonLabel=""
        />
      </div>
  );
};

PromptAugmentation.propTypes = {
    augmentedPromptsEnabled: PropTypes.bool.isRequired,
    augmentedPrompt: PropTypes.string.isRequired,
    error: PropTypes.string,
    isAugmenting: PropTypes.bool.isRequired,
    copyAugmentedPrompt: PropTypes.func.isRequired,
};

export default PromptAugmentation;
