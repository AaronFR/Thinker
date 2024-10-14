import React from 'react';
import DOMPurify from 'dompurify';
import { marked } from 'marked';
import './styles/PromptAugmentation.css';

const PromptAugmentation = ({ augmentedPromptsEnabled, augmentedPrompt, error="", isAugmenting, copyAugmentedPrompt }) => {
  if (!augmentedPromptsEnabled) return null;

  return (
    <>
      <div style={{ opacity: isAugmenting ? 0.5 : 1 }}>
        {augmentedPrompt ? (
          <div
            className="markdown-augmented"
            dangerouslySetInnerHTML={{
              __html: DOMPurify.sanitize(error ? error : marked(augmentedPrompt)),
            }}
          />
        ) : (
          "Waiting to augment prompt.."
        )}
      </div>
      {augmentedPrompt && (
        <button className="augment-button" onClick={copyAugmentedPrompt}>
          {isAugmenting ? 'Augmenting...' : 'Copy Augmented Prompt'}
        </button>
      )}
    </>
  );
};

export default PromptAugmentation;
