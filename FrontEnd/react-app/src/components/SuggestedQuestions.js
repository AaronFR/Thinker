import React from 'react';
import DOMPurify from 'dompurify';
import { marked } from 'marked';
import './styles/SuggestedQuestions.css';

const SuggestedQuestions = ({ questionUserPromptsEnabled, questionsForPrompt, error="", isQuestioning }) => {
  if (!questionUserPromptsEnabled) return null;

  return (
    <>
      <div style={{ opacity: isQuestioning ? 0.5 : 1 }}>
        {questionsForPrompt ? (
          <div
            className="markdown-questions-for-prompt"
            dangerouslySetInnerHTML={{
              __html: DOMPurify.sanitize(error ? error : marked(questionsForPrompt)),
            }}
          />
        ) : (
          "Waiting to question prompt..."
        )}
      </div>
    </>
  );
};

export default SuggestedQuestions;
