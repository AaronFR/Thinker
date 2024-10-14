import React from 'react';
import './styles/UserInputForm.css';

const UserInputForm = ({ handleSubmit, handleInputChange, userInput, isProcessing }) => {
  return (
    <form 
      onSubmit={handleSubmit}
      onKeyDown={(e) => {
        if (e.key === 'Enter' && e.shiftKey) {
          e.preventDefault();
          const { selectionStart, selectionEnd, value } = e.target;
          
          e.target.value = 
            value.substring(0, selectionStart) + '\n' + value.substring(selectionEnd);
          
          e.target.selectionStart = e.target.selectionEnd = selectionStart + 1;
        } else if (e.key === 'Enter') {
          e.preventDefault();
          handleSubmit();
        }
      }}
      style={{ marginTop: '20px' }}
    >
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <textarea
          value={userInput}
          onChange={handleInputChange}
          placeholder='Enter your prompt'
          className="prompt-input"
          rows="2"
          style={{ resize: 'none', overflowY: 'auto' }}
        ></textarea>
        <button 
          type="submit"
          className="submit-button"
          disabled={isProcessing}
        >
          {isProcessing ? 'Processing...' : 'Enter'}
        </button>
      </div>
    </form>
  );
};

export default UserInputForm;
