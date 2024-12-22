import React from 'react';
import { MarkdownRenderer } from '../utils/textUtils';
import ExpandableElement from '../utils/expandableElement';

import './styles/PromptAugmentation.css';

const PromptAugmentation = ({
  augmentedPromptsEnabled,
  augmentedPrompt,
  error = '',
  isAugmenting,
  copyAugmentedPrompt,
}) => {
  if (!augmentedPromptsEnabled) return null;
  if (!augmentedPrompt) return null;

  const minContent = (
      <MarkdownRenderer
          markdownText="Augmented Prompt +"
          className="markdown-augmented"
          isLoading={isAugmenting}
      />
  );

  const maxContent = (
      <>
          <MarkdownRenderer
              markdownText={error || augmentedPrompt}
              className="markdown-augmented"
              isLoading={isAugmenting}
          />
          {augmentedPrompt && (
              <button
                  className="button augment-button"
                  onClick={(e) => {
                      e.stopPropagation();
                      copyAugmentedPrompt();
                  }}
                  disabled={isAugmenting}
              >
                  {isAugmenting ? 'Augmenting...' : 'Copy'}
              </button>
          )}
      </>
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

export default PromptAugmentation;
