import React, { useState, useEffect } from 'react';
import DOMPurify from 'dompurify';
import { marked } from 'marked';
import './styles/SuggestedQuestions.css';

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

  // Reset responses when resetResponsesTrigger changes
  useEffect(() => {
    setResponses({});
    onFormsFilled(false); // Reset formsFilled state
    setConcatenatedQA(''); // Clear concatenatedQA
  }, [resetResponsesTrigger]);

  if (!questionUserPromptsEnabled) return null;

  if (error) {
    return (
      <div className="markdown-questions-for-prompt" style={{ opacity: isQuestioning ? 0.5 : 1 }}>
        <div className="error-message">{error}</div>
      </div>
    );
  }

  if (!questionsForPrompt) {
    return (
      <div style={{ opacity: isQuestioning ? 0.5 : 1 }}>
        Waiting to question prompt...
      </div>
    );
  }

  // Parse the markdown to extract list items
  const tokens = marked.lexer(questionsForPrompt);
  let questions = [];

  tokens.forEach((token) => {
    if (token.type === 'list') {
      questions = token.items.map((item) => item.text);
    }
  });

  // Handler for textarea changes
  const handleResponseChange = (index, value) => {
    setResponses((prevResponses) => {
      const newResponses = { ...prevResponses, [index]: value };

      const anyFilled = Object.values(newResponses).some((val) => val.trim() !== "");// Determine if any textarea has content
      onFormsFilled(anyFilled); // Notify parent component

      const concatenatedQA = concatenateQA(questions, newResponses);
      console.log(concatenatedQA);
      setConcatenatedQA(concatenatedQA)
      return newResponses;
    });
  };
  

  // Method to concatenate questions and answers
  const concatenateQA = (questionsList, answers) => {
    return questionsList
      .map((question, index) => {
        const answer = answers[index] ? answers[index].trim() : "";
        return answer ? `${question}: ${answer}` : null
      })
      .join('\n');
  };

  return (
    <div className="markdown-questions-for-prompt" style={{ opacity: isQuestioning ? 0.5 : 1 }}>
      <ol className="questions-list">
        {questions.map((question, index) => (
          <li key={index} className="question-item">
            <div
              className="question-text"
              dangerouslySetInnerHTML={{
                __html: DOMPurify.sanitize(marked.parseInline(question)),
              }}
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

export default SuggestedQuestions;
