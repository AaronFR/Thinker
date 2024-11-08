import React from 'react';
import { MarkdownRenderer } from '../utils/textUtils';

import './styles/PromptAugmentation.css';

const PromptAugmentation = ({ augmentedPromptsEnabled, augmentedPrompt, error="", isAugmenting, copyAugmentedPrompt }) => {
  if (!augmentedPromptsEnabled) return null;

  return (
    <div className="augmented-container">
      <MarkdownRenderer 
        markdownText={error ? error : augmentedPrompt} 
        className="markdown-augmented" 
        isLoading={isAugmenting}
      />
      {augmentedPrompt && (
        <button 
          className="augment-button" 
          onClick={copyAugmentedPrompt} 
          disabled={isAugmenting}
        >
          {isAugmenting ? 'Augmenting...' : 'Copy'}
        </button>
      )}
    </div>
  );
};

export default PromptAugmentation;
