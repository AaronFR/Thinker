import React from 'react';
import PropTypes from 'prop-types';

import { MarkdownRenderer } from '../utils/textUtils';
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
 * @param {string} error (string): Error message to display, if any.
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
  if (!augmentedPromptsEnabled || !augmentedPrompt) return null;

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
        <p className="error-message" role="alert">{error}</p>
      ) : (
        <>
          <MarkdownRenderer
            markdownText={augmentedPrompt}
            className="markdown-augmented"
            isLoading={isAugmenting}
          />
          <button
            className="button augment-button"
            onClick={(e) => {
              e.stopPropagation();
              copyAugmentedPrompt();
            }}
            disabled={isAugmenting}
            aria-label={
              isAugmenting
                  ? 'Copying augmented prompt...'
                  : 'Copy augmented prompt'
            }
          >
            {isAugmenting ? 'Augmenting...' : 'Copy'}
          </button>
        </>
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
