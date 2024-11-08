import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { marked } from 'marked';

import { MarkdownRenderer, withLoadingOpacity } from '../utils/textUtils';

import './styles/SuggestedQuestions.css';

/**
 * SuggestedQuestions Component
 * 
 * Renders a list of suggested questions extracted from a markdown prompt.
 * Allows users to input responses to each question and concatenates the answers.
 * 
 * Props:
 * - questionUserPromptsEnabled (boolean): Flag to enable or disable prompting.
 * - questionsForPrompt (string): Markdown string containing the questions.
 * - error (string): Error message to display, if any.
 * - isQuestioning (boolean): Indicates if a questioning process is ongoing.
 * - onFormsFilled (function): Callback to notify parent when forms are filled.
 * - setConcatenatedQA (function): Function to set the concatenated Q&A.
 * - resetResponsesTrigger (any): Dependency to trigger resetting responses.
 */
const SuggestedQuestions = ({
  questionUserPromptsEnabled,
  questionsForPrompt,
  error = "",
  isQuestioning,
  onFormsFilled,
  setConcatenatedQA,
  resetResponsesTrigger
}) => {
  const [responses, setResponses] = useState({});

  /**
   * Resets responses, forms filled state, and concatenated Q&A when triggered.
   */
  useEffect(() => {
    setResponses({});
    onFormsFilled(false); // Reset formsFilled state
    setConcatenatedQA(''); // Clear concatenatedQA
  }, [resetResponsesTrigger]);

  if (!questionUserPromptsEnabled) return null;

  if (error) {
    return (
      <div className="markdown-questions-for-prompt" style={withLoadingOpacity(isQuestioning)}>
        <div className="error-message">{error}</div>
      </div>
    );
  }

  // Display loading message if questions are not yet available
  if (!questionsForPrompt) {
    return (
      <div style={withLoadingOpacity(isQuestioning)}>
        {isQuestioning ? "..." : ""}
      </div>
    );
  }

  /**
   * Parses the markdown prompt to extract a list of questions.
   * Assumes questions are listed as bullet points.
   * 
   * @param {string} markdownText - The markdown string containing questions.
   * @returns {Array<string>} - An array of question strings.
   */
  const parseQuestions = (markdownText) => {

    // Parse the markdown to extract list items
    const tokens = marked.lexer(questionsForPrompt);
    let questions = [];

    tokens.forEach((token) => {
      if (token.type === 'list') {
        questions = token.items.map((item) => item.text);
      }
    });

    return questions;
  }

  const questions = parseQuestions(questionsForPrompt);

  /**
   * Handles changes in the response textareas.
   * Updates the responses state and concatenates Q&A.
   * 
   * @param {number} index - The index of the question.
   * @param {string} value - The user's response.
   */
  const handleResponseChange = (index, value) => {
    setResponses((prevResponses) => {
      const newResponses = { ...prevResponses, [index]: value };

      // Determine if any textarea has content
      const anyFilled = Object.values(newResponses).some((val) => val.trim() !== "");
      onFormsFilled(anyFilled); // Notify parent component

      const concatenatedQA = concatenateQA(questions, newResponses);
      console.log(concatenatedQA);
      setConcatenatedQA(concatenatedQA)
      return newResponses;
    });
  };
  
  /**
   * Concatenates questions and their corresponding answers into a single string.
   * 
   * @param {Array<string>} questionsList - Array of questions.
   * @param {Object} answers - Object mapping question indices to answers.
   * @returns {string} - Concatenated Q&A string.
   */
  const concatenateQA = (questionsList, answers) => {
    return questionsList
      .map((question, index) => {
        const answer = answers[index] ? answers[index].trim() : "";
        return answer ? `${question}: ${answer}` : null
      })
      .filter(Boolean) // Remove nulls
      .join('\n');
  };

  return (
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
              <textarea
                className="response-textarea"
                placeholder="Your answer"
                disabled={isQuestioning}
                value={responses[index] || ""}
                onChange={(e) => handleResponseChange(index, e.target.value)}
              />
            </form>
          </li>
        ))}
      </ol>
    </div>
  );
};

/**
 * PropTypes for SuggestedQuestions Component
 */
SuggestedQuestions.propTypes = {
  questionUserPromptsEnabled: PropTypes.bool.isRequired,
  questionsForPrompt: PropTypes.string,
  error: PropTypes.string,
  isQuestioning: PropTypes.bool.isRequired,
  onFormsFilled: PropTypes.func.isRequired,
  setConcatenatedQA: PropTypes.func.isRequired,
  resetResponsesTrigger: PropTypes.any, // Can be more specific based on usage
};

export default SuggestedQuestions;
