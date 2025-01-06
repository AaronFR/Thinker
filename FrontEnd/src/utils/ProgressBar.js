import React from 'react';
import PropTypes from 'prop-types';
import './styles/ProgressBar.css';

/**
 * ProgressBar Component
 * 
 * Displays a horizontal progress bar indicating upload, download, or any other progress.
 * It visually represents the completion percentage and provides accessibility features.
 * 
 * @param {number} progress: The current progress percentage (0-100).
 */
const ProgressBar = ({ progress }) => {
  /**
   * Clamps the progress value between 0 and 100 to ensure valid CSS width.
   */
  const clampedProgress = Math.min(Math.max(progress, 0), 100)

  return (
    <div className="progress-bar-container">
      <div
        className="progress-bar-fill"
        style={{ width: `${clampedProgress}%` }}
        role="progressbar"
        aria-valuenow={clampedProgress}
        aria-valuemin="0"
        aria-valuemax="100"
      ></div>
    </div>
  );
};

ProgressBar.propTypes = {
  progress: PropTypes.number.isRequired,
};

export default ProgressBar;
