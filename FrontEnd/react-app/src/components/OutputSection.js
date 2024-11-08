import React from 'react';

import { MarkdownRenderer } from '../utils/textUtils';

import './styles/OutputSection.css';

const OutputSection = ({ message, error = '', isProcessing }) => {
  return (
    <MarkdownRenderer
      markdownText={error ? error : message}
      className="markdown-output"
      isLoading={isProcessing}
    />
  );
};

export default OutputSection;
