import React, { useState } from 'react';
import { marked } from 'marked';
import { Link } from 'react-router-dom';
import DOMPurify from 'dompurify';
import './App.css';


const flask_port= "http://localhost:5000"

function App () {
    const [message, setMessage] = useState(''); // State to hold the message
    const [error, setError] = useState(null); // State to hold error messages
    const [userInput, setUserInput] = useState('') // State to hold user input
    const [isProcessing, setIsProcessing] = useState(false); // State to while processing prompt

    console.log("App component called")
 
    // Handle user input submission
    const handleSubmit = async (e) => {
      console.log("HandleSubmit triggered")
      e.preventDefault();
      setError(null);

      try {
        setIsProcessing(true)
        const response = await fetch(flask_port + '/api/message', {
          method: 'POST',
          headers: {
            "Content-Type": 'application/json'
          },
          body: JSON.stringify({ prompt: userInput}), // send user input as JSON payload
        }); // Call Flask API
        console.log(response)
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        setMessage(data.message); // Update state with the fetched message
        setUserInput('')
        setIsProcessing(false)
      } catch (error) {
          console.error('Error submitting the prompt:', error);
          setError('Error submitting and fetching the message. Please try again later.');  // Update error state
      }
    };

    return (
        <div className="app-container">
          <div
            className="markdown-output"
            dangerouslySetInnerHTML={{
              __html: DOMPurify.sanitize(error ? error : marked(message))
            }}
          />
          <h2>{userInput ? userInput : "Enter your message"}</h2>

          <form onSubmit={handleSubmit} style={{ marginTop: '20px' }}>
            <input
              type="text"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              placeholder='Enter your prompt'
              className="prompt-input"
              disabled={isProcessing} // in future the user should be allowed serial prompts
            />
            <button 
              type="submit"
              className="submit-button"
            >
              {isProcessing ? 'Processing...' : 'Enter'}
            </button>
          </form>

          {/* Link to the Settings page */}
          <nav>
            <Link to="/settings" className="link">Go to Settings</Link>
          </nav>
            
        </div>
    );
};

export default App;