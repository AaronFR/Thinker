import React, { useState, useEffect, useRef } from 'react';
import { marked } from 'marked';
import { Link } from 'react-router-dom';
import DOMPurify from 'dompurify';
import './App.css';


const flask_port= "http://localhost:5000"

function App () {
    const [message, setMessage] = useState(''); // State to hold the message
    const [error, setError] = useState(null); // State to hold error messages
    const [userInput, setUserInput] = useState('') // State to hold user input
    const [augmentedPrompt, setAugmentedPrompt] = useState(''); // New state for augmented prompt
    const [isProcessing, setIsProcessing] = useState(false); // State tracking if processing prompt
    const [isAugmenting, setIsAugmenting] = useState(false); // State tracking if prompt is being augmented
    const [selectedPersona, setSelectedPersona] = useState('auto'); // State to hold dropdown selection
    
    const autoDetectedPersona = 'Coder' // Temporary hardcoded value

    const idleTime = 1000;
    const typingTimer = useRef(null);
 
    // Handle user input submission
    const handleSubmit = async (e) => {
      if (e) e.preventDefault();
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

    // Clear the messages after successful submission
    const updateMessage = (newMessage) => {
        setMessage(newMessage);
        setUserInput(''); 
        setAugmentedPrompt('')
    };

    const handleInputChange = (e) => {
      setUserInput(e.target.value);
      if (typingTimer.current) {
        clearTimeout(typingTimer.current);
      }
      
      // Adjust height to fit content, up to a max height
      e.target.style.height = "auto"; // Reset height to calculate scroll height properly
      e.target.style.height = `${Math.min(e.target.scrollHeight, 8 * 24)}px`; // 24px per row, max 8 rows

      typingTimer.current = setTimeout(() => {
        generateAugmentedPrompt(e.target.value);
      }, idleTime);
    };

    const generateAugmentedPrompt = async (input) => {
      console.log("Generating augmented prompt for:", input);
      setIsAugmenting(true)
      try {
        const response = await fetch("http://localhost:5000/api/augment_prompt", {
          method: 'POST',
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ user_prompt: input })
        });
    
        if (!response.ok) {
          throw new Error('Failed to fetch augmented prompt');
        }
    
        const data = await response.json();
        console.log("Augmented response:", data.message);
    
        // Assuming you have a setAugmentedPrompt function or similar to store/display the response
        setAugmentedPrompt(data.message);
    
      } catch (error) {
        console.error("Error in augmenting prompt:", error);
      } finally {
        setIsAugmenting(false)
      }
    };

    const copyAugmentedPrompt = () => {
      setUserInput(augmentedPrompt); // Copy augmentedPrompt into userInput
    };

    // Clean up the typing timer when the component unmounts
    useEffect(() => {
      return () => clearTimeout(typingTimer.current);
    }, []);

    return (
        <div className="app-container">

          {/* Output Section */}
          <div
            style={{ opacity: isProcessing ? 0.5 : 1 }}
            className="markdown-output"
            dangerouslySetInnerHTML={{
              __html: DOMPurify.sanitize(error ? error : marked(message))
            }}
          />

          {/* Prompt augmentation Section */}
          <div style={{ opacity: isAugmenting ? 0.5 : 1 }}>
            {augmentedPrompt ? 
              <div
                
                className="markdown-augmented"
                dangerouslySetInnerHTML={{
                  __html: DOMPurify.sanitize(error ? error : marked(augmentedPrompt))
                }}
              /> : "Waiting to augment prompt.."
            }
          </div>
          { augmentedPrompt && (
            <button
              className="augment-button"
              onClick={copyAugmentedPrompt}
            >
              {isAugmenting ? 'Augmenting...' : 'Copy Augmented Prompt'}
                
            </button>
          )}

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
            style={{ marginTop: '20px' }}>
            <textarea
              value={userInput}
              onChange={handleInputChange}
              placeholder='Enter your prompt'
              className="prompt-input"
              rows="2"
              style={{ resize: 'none', overflowY: 'auto'  }} // Prevent resizing
            ></textarea>
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