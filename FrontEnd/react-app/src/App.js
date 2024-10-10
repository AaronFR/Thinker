import React, { useState } from 'react';
import './App.css';


export function Settings() {
  return (
    <div>Insert configuration here</div>
  )
}

export function Pricing() {
  return (
    <div>Insert pricing information here</div>
  )
}

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
      } catch (error) {
          console.error('Error submitting the prompt:', error);
          setError('Error submitting and fetching the message. Please try again later.');  // Update error state
      }
    };

    return (
        <div className="app-container">
            <p className="app-heading">{error ? error : message}</p> {/* Display error message or the fetched message */}
            <h2>{userInput ? userInput : "Enter your message"}</h2>

            <form onSubmit={handleSubmit} style={{ marginTop: '20px' }}>
              <input
                type="text"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                placeholder='Enter your prompt'
                style={{ padding: '1opx', fontSize: '16px'}}
              />
              <button 
                type="submit"
                className="submit-button"
              >
                {isProcessing ? 'Processing...' : 'Enter'}
              </button>
            </form>
            
        </div>
    );
};

export default App;