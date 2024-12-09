import React from 'react';
import PropTypes from 'prop-types';
import './styles/ProgressBar.css';

/**
 * ProgressBar Component
 * 
 * Displays a horizontal progress bar indicating upload progress.
 * 
 * Props:
 * - progress (number): The current progress percentage (0-100).
 */
const ProgressBar = ({ progress }) => {
  return (
    <div className="progress-bar-container">
      <div 
        className="progress-bar-fill" 
        style={{ width: `${progress}%` }}
      ></div>
    </div>
  );
};

ProgressBar.propTypes = {
  progress: PropTypes.number.isRequired,
};

export default ProgressBar;
