import React, { useCallback, useMemo } from 'react';
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
 * @param {string} augmentedPrompt (string): The augmented prompt text.
 * @param {string} [error=''] - Optional error message to display.
 * @param {boolean} isAugmenting (boolean): Indicates if the augmentation process is ongoing.
 * @param {function} copyAugmentedPrompt (function): Function to copy the augmented prompt.
 */
const PromptAugmentation = React.memo(({
  augmentedPromptsEnabled,
  augmentedPrompt,
  error = '',
  isAugmenting,
  copyAugmentedPrompt,
}) => {
  // Always call hooks so that they have a consistent order

  const handleCopyClick = useCallback((e) => {
    e.stopPropagation();
    copyAugmentedPrompt();
  }, [copyAugmentedPrompt]);

  const buttonLabel = isAugmenting ? 'Copying augmented prompt...' : 'Copy';
  const buttonText = isAugmenting ? 'Augmenting...' : 'Copy';

  const minContent = useMemo(() => (
    <MarkdownRenderer
      markdownText="Augmented Prompt"
      className="markdown-augmented"
      isLoading={isAugmenting}
    />
  ), [isAugmenting]);

  const maxContent = useMemo(() => (
    <div>
      {error ? (
        <p className="error-message" role="alert">
          {error}
        </p>
      ) : (
        <div className="augmented-container">
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
  ), [error, augmentedPrompt, isAugmenting, handleCopyClick, buttonLabel, buttonText]);

  if (!augmentedPrompt) {
    return (
      <div style={withLoadingOpacity(isAugmenting)}>
        {isAugmenting ? "Engineering prompt..." : ""}
      </div>
    );
  }

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
});

PromptAugmentation.propTypes = {
  augmentedPromptsEnabled: PropTypes.bool.isRequired,
  augmentedPrompt: PropTypes.string.isRequired,
  error: PropTypes.string,
  isAugmenting: PropTypes.bool.isRequired,
  copyAugmentedPrompt: PropTypes.func.isRequired,
};

export default PromptAugmentation;
