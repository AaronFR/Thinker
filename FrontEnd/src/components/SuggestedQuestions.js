import React, { useState, useEffect, useCallback, useMemo } from 'react';
import PropTypes from 'prop-types';
import { marked } from 'marked';

import { MarkdownRenderer, withLoadingOpacity } from '../utils/textUtils';
import ExpandableElement from '../utils/expandableElement';
import AutoExpandingTextarea from '../utils/AutoExpandingTextarea';

import './styles/SuggestedQuestions.css';

/**
 * SuggestedQuestions Component
 *
 * Renders a list of suggested questions extracted from a markdown prompt.
 * Allows users to input responses to each question and concatenates the answers.
 *
 * @param {string} questionsForPrompt - Markdown string containing the questions.
 * @param {string} error - Error message to display, if any.
 * @param {boolean} isQuestioning - Indicates if a questioning process is ongoing.
 * @param {function} onFormsFilled - Callback to notify parent when forms are filled.
 * @param {function} setConcatenatedQA - Function to set the concatenated Q&A.
 * @param {any} resetResponsesTrigger - Dependency to trigger resetting responses.
 */
const SuggestedQuestions = ({
  questionsForPrompt,
  error = '',
  isQuestioning,
  onFormsFilled,
  setConcatenatedQA,
  resetResponsesTrigger
}) => {
  const [responses, setResponses] = useState({});

  // Reset responses and concatenatedQA when resetResponsesTrigger changes.
  useEffect(() => {
    setResponses({});
    onFormsFilled(false);
    setConcatenatedQA('');
  }, [resetResponsesTrigger, onFormsFilled, setConcatenatedQA]);

  /**
   * Parses the markdown prompt to extract a list of questions.
   * Assumes questions are listed as bullet points.
   * 
   * @param {string} markdownText - The markdown string containing questions.
   * @returns {Array<string>} - An array of question strings.
   */
  const questions = useMemo(() => {
    if (!questionsForPrompt) return [];

    const tokens = marked.lexer(questionsForPrompt);
    const listToken = tokens.find(token => token.type === 'list');

    return listToken ? listToken.items.map(item => item.text) : [questionsForPrompt];
  }, [questionsForPrompt]);

  const concatenateQA = useCallback((questionsList, answers) => {
    return questionsList
      .map((question, index) =>
        answers[index] ? `${question}: ${answers[index].trim()}` : null
      )
      .filter(Boolean) // Remove nulls.
      .join('\n');
  }, []);

  // Use useCallback to prevent unnecessary re-creations of the function on every render.
  const handleResponseChange = useCallback(
    (index, value) => {
      setResponses(prevResponses => {
        const newResponses = { ...prevResponses, [index]: value };
        const anyFilled = Object.values(newResponses).some(val => val.trim() !== "");
        onFormsFilled(anyFilled); // Notify parent component
        
        // Concatenate questions and answers and send the result upward.
        setConcatenatedQA(concatenateQA(questions, newResponses));
        return newResponses;
      });
    },
    [onFormsFilled, setConcatenatedQA, questions, concatenateQA]
  );

  // Memoize the minimal and max expandable elements.
  const minContent = useMemo(() => (
    <MarkdownRenderer 
      markdownText="Questions and Answers" 
      className="question-text" 
      isLoading={isQuestioning} 
    />
  ), [isQuestioning]);

  const maxContent = useMemo(() => (
    <div className="markdown-questions-for-prompt">
      <ol className="questions-list">
        {questions.map((question, index) => (
          <li key={index} className="question-item">
            <MarkdownRenderer 
              markdownText={question} 
              className="question-text" 
              isLoading={isQuestioning} 
            />
            <form className="response-form">
              <AutoExpandingTextarea
                className="textarea response-textarea"
                placeholder="Your answer"
                disabled={isQuestioning}
                value={responses[index] || ""}
                onChange={e => handleResponseChange(index, e.target.value)}
              />
            </form>
          </li>
        ))}
      </ol>
    </div>
  ), [questions, responses, isQuestioning, handleResponseChange]);

  // Instead of returning early, conditionally render inside the JSX.
  let content;
  if (error) {
    content = (
      <div className="markdown-questions-for-prompt" style={withLoadingOpacity(isQuestioning)}>
        <div role="alert" className="error-message">{error}</div>
      </div>
    );
  } else if (!questionsForPrompt) {
    content = (
      <div style={withLoadingOpacity(isQuestioning)}>
        {isQuestioning ? "Loading questions..." : ""}
      </div>
    );
  } else {
    content = (
      <ExpandableElement
        minContent={minContent}
        maxContent={maxContent}
        initiallyExpanded={true}
        toggleButtonLabel=""
      />
    );
  }

  return content;
};

SuggestedQuestions.propTypes = {
  questionUserPromptsEnabled: PropTypes.bool.isRequired,
  questionsForPrompt: PropTypes.string,
  error: PropTypes.string,
  isQuestioning: PropTypes.bool.isRequired,
  onFormsFilled: PropTypes.func.isRequired,
  setConcatenatedQA: PropTypes.func.isRequired,
  resetResponsesTrigger: PropTypes.any, // Can be made more specific if needed.
};

export default React.memo(SuggestedQuestions);
