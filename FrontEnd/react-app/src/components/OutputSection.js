import React from 'react';
import DOMPurify from 'dompurify';
import { marked } from 'marked';
import './styles/OutputSection.css';

const OutputSection = ({ message, error = '', isProcessing }) => {
  return (
    <>
      {message ? (
        <div
          style={{ opacity: isProcessing ? 0.5 : 1 }}
          className="markdown-output"
          dangerouslySetInnerHTML={{
            __html: DOMPurify.sanitize(error ? error : marked(message)),
          }}
        />
      ) : (
        ""
      )}
    </>
  );
};

export default OutputSection;
