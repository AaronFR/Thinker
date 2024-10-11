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
    const [selectedPersona, setSelectedPersona] = useState('auto'); // State to hold dropdown selection
    
    const autoDetectedPersona = 'Coder' // Temporary hardcoded value
 
    // Handle user input submission
    const handleSubmit = async (e) => {
      e.preventDefault();
      setError(null);
      setIsProcessing(true)

      try {
        const response = await fetch(flask_port + '/api/message', {
          method: 'POST',
          headers: {
            "Content-Type": 'application/json'
          },
          body: JSON.stringify({ prompt: userInput, persona: selectedPersona}), 
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        updateMessage(data.message);
      } catch (error) {
          setError('Error submitting and fetching the message. Please try again later.');
      } finally {
          setIsProcessing(false);
      }
    };

    const updateMessage = (newMessage) => {
        setMessage(newMessage);
        setUserInput(''); // Clear the input after successful submission
    };

    return (
        <div className="app-container">

          {/* Output Section */}
          <div
            className="markdown-output"
            dangerouslySetInnerHTML={{
              __html: DOMPurify.sanitize(error ? error : marked(message))
            }}
          />

          <h2>{userInput ? userInput : "Enter your message"}</h2>

          {/* Dropdown for Selecting Persona */}
          <div style={{ marginBottom: '20px' }}>
            <label>
              Select Persona:
              <select 
                value={selectedPersona} 
                onChange={(e) => setSelectedPersona(e.target.value)}
                className="dropdown"
              >
                <option value="auto">Auto - {autoDetectedPersona}</option>
                <option value="coder">Coder</option>
              </select>
            </label>
          </div>

          {/* Form for User Input */}
          <form onSubmit={handleSubmit} style={{ marginTop: '20px' }}>
            <input
              type="text"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              placeholder='Enter your prompt'
              className="prompt-input"
            />
            <button 
              type="submit"
              className="submit-button"
              disabled={isProcessing} // Prevent multiple submissions - for now
            >
              {isProcessing ? 'Processing...' : 'Enter'}
            </button>
          </form>

          {/* Link to Settings page */}
          <nav>
            <Link to="/settings" className="link">Go to Settings</Link>
          </nav>
            
        </div>
    );
};

export default App;