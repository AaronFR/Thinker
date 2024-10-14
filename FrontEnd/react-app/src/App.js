import React, { useState, useEffect, useRef, useContext } from 'react';
import { marked } from 'marked';
import { Link } from 'react-router-dom';
import DOMPurify from 'dompurify';
import './App.css';

import { SettingsContext } from './Settings';

/**
 * App component
 * 
 * Main application component that handles user input, displays messages,
 * and manages state related to prompts and API interactions.
 */
const flask_port= "http://localhost:5000"

function App () {
    const [message, setMessage] = useState('');
    const [error, setError] = useState(null);

    const [userInput, setUserInput] = useState('')
    const [isProcessing, setIsProcessing] = useState(false);

    const [augmentedPrompt, setAugmentedPrompt] = useState('');
    const [isAugmenting, setIsAugmenting] = useState(false);

    const [questionsForPrompt, setQuestionsForPrompt] = useState('');
    const [isQuestioning, setIsQuestioning] = useState(false);

    const [selectedPersona, setSelectedPersona] = useState('auto');
    const autoDetectedPersona = 'Coder' // Temporary hardcoded value

    const idleTime = 1500; // Time in milliseconds before triggering input handlers
    const typingTimer = useRef(null);

    const { settings } = useContext(SettingsContext);
    const { augmentedPromptsEnabled } = settings;
 
    // Handle user input submission
    const handleSubmit = async (event) => {
      // ToDo: When submitting the micro thoughts (augmented and questions) should be minimised
      if (event) event.preventDefault();
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
        setQuestionsForPrompt('')
    };

    const handleInputChange = (event) => {
      // ToDo: don't think it respects shift enters, issue for inputting code
      setUserInput(event.target.value);
      if (typingTimer.current) {
        clearTimeout(typingTimer.current);
      }
      
      // Adjust height to fit content, up to a max height
      event.target.style.height = "auto"; // Reset height to calculate scroll height properly
      event.target.style.height = `${Math.min(event.target.scrollHeight, 8 * 24)}px`; // 24px per row, max 8 rows

      typingTimer.current = setTimeout(() => {
        if (augmentedPromptsEnabled) {
          generateAugmentedPrompt(event.target.value);
        }
        generateQuestionsForPrompt(event.target.value);
      }, idleTime);
    };

    // Generates an augmented prompt based on user input.
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

    const generateQuestionsForPrompt = async (input) => {
      console.log("Generating questions for:", input);
      setIsQuestioning(true)
      try {
        const response = await fetch("http://localhost:5000/api/question_prompt", {
          method: 'POST',
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ user_prompt: input })
        });
    
        if (!response.ok) {
          throw new Error('Failed to generate questions for prompt');
        }
    
        const data = await response.json();
        console.log("questions against user prompt:", data.message);
    
        setQuestionsForPrompt(data.message);
    
      } catch (error) {
        console.error("Error in questioning user prompt:", error);
      } finally {
        setIsQuestioning(false)
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
          {augmentedPromptsEnabled && (
            <>
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
                <button className="augment-button" onClick={copyAugmentedPrompt}>
                  {isAugmenting ? 'Augmenting...' : 'Copy Augmented Prompt'}
                </button>
              )}
            </>
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
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
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
            </div>
          </form>

          {/* Suggested questions Section */}
          <div style={{ opacity: isQuestioning ? 0.5 : 1 }}>
            {questionsForPrompt ? 
              <div
                
                className="markdown-augmented"
                dangerouslySetInnerHTML={{
                  __html: DOMPurify.sanitize(error ? error : marked(questionsForPrompt))
                }}
              /> : ""
            }
          </div>

          {/* Link to Settings page */}
          <nav>
            <Link to="/settings" className="link">Go to Settings</Link>
          </nav>
            
        </div>
    );
};

export default App;