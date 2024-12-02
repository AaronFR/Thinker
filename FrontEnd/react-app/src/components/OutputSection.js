import React from 'react';

import { CodeHighlighter } from '../utils/textUtils';

import './styles/OutputSection.css';


const OutputSection = ({ message, error = '', isProcessing }) => {
  return (
    <div className="markdown-output">
      <CodeHighlighter>
        {error ? error : message}
      </CodeHighlighter>
    </div>
  );
};

export default OutputSection;
