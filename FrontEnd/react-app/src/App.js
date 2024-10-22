import React, { useState, useEffect, useRef, useContext } from 'react';
import debounce from 'lodash.debounce';

import { SettingsContext } from './pages/Settings/Settings';

import FilePane from './components/FilePane'
import MessageHistory from './components/MessageHistory';
import OutputSection from './components/OutputSection';
import PromptAugmentation from './components/PromptAugmentation';
import PersonaSelector from './components/PersonaSelector';
import UserInputForm from './components/UserInputForm';
import SuggestedQuestions from './components/SuggestedQuestions';
import Navigation from './components/Navigation';

import useSubmitMessage from './hooks/useSubmitMessage';
import useAugmentedPrompt from './hooks/useAugmentedPrompt';
import useSuggestedQuestions from './hooks/useSuggestedQuestions';

import './App.css';
/**
 * App component
 * 
 * Main application component that handles user input, displays messages,
 * and manages state related to prompts and API interactions.
 */
const flask_port= "http://localhost:5000"

function App () {

    // User Input States
    const [userInput, setUserInput] = useState('')
    const [selectedPersona, setSelectedPersona] = useState('auto');
    const autoDetectedPersona = 'Coder' // Temporary hardcoded value

    // Debounce timer reference to optimize input handling
    const idleTime = 1500; // milliseconds
    const typingTimer = useRef(null);

    // Context Settings
    const { settings } = useContext(SettingsContext);
    const { augmentedPromptsEnabled, questionUserPromptsEnabled } = settings;

    // QA Management
    const [concatenatedQA, setConcatenatedQA] = useState('');
    const [resetResponsesTrigger, setResetResponsesTrigger] = useState(0);

    // File Management
    const [selectedFile, setSelectedFile] = useState(null);
 
    // Custom hooks
    const { message, setMessage, error: messageError, isProcessing, handleSubmit } = useSubmitMessage(flask_port, concatenatedQA);
    const { augmentedPrompt, setAugmentedPrompt, isAugmenting, error: augmentedError, generateAugmentedPrompt } = useAugmentedPrompt(flask_port);
    const { questionsForPrompt, setQuestionsForPrompt, isQuestioning, error: questionsError, generateQuestionsForPrompt } = useSuggestedQuestions(flask_port);

    // Form State
    const [formsFilled, setFormsFilled] = useState(false);

    const handleInputChange = (event) => {
      // ToDo: don't think it respects shift enters, issue for inputting code
      setUserInput(event.target.value);
      if (typingTimer.current) {
        clearTimeout(typingTimer.current);
      }
      
      // Adjust height to fit content, up to a max height
      event.target.style.height = "auto"; // Reset height to calculate scroll height properly
      event.target.style.height = `${Math.min(event.target.scrollHeight, 8 * 24)}px`;

      debouncedHandleTyping(event.target.value);
    };

    const handleTyping = (value) => {
      if (augmentedPromptsEnabled) {
        generateAugmentedPrompt(value);
      }
      if (questionUserPromptsEnabled && !formsFilled) {
        generateQuestionsForPrompt(value);
      }
    };

    const debouncedHandleTyping = useRef(
      debounce((value) => handleTyping(value), idleTime)
    ).current;
    
    // Clean up the debounce on unmount
    useEffect(() => {
      return () => {
        debouncedHandleTyping.cancel();
      };
    }, [debouncedHandleTyping]);

    const handleFormSubmit = async (event) => {
      event.preventDefault(); // Always prevent default if event exists
      try {
        await handleSubmit(userInput, selectedPersona);
        setUserInput(''); 
        setAugmentedPrompt('');
        setQuestionsForPrompt('');
        setFormsFilled(false);
        setResetResponsesTrigger(prev => prev + 1);
      } catch (error) {
        // Handle submission errors here
        console.error("Form submission error:", error);
      }
    };


    const copyAugmentedPrompt = () => {
      setUserInput(augmentedPrompt); // Copy augmentedPrompt into userInput
    };

    // Clean up the typing timer when the component unmounts
    useEffect(() => {
      return () => clearTimeout(typingTimer.current);
    }, []);

    const handleFileSelect = (file) => {
      setSelectedFile(file);
      // Implement functionality to write a prompt related to the selected file
      // This could involve opening a modal, displaying a form, etc.
      console.log("Selected File:", file);
    };

    return (
        <div className="app-container">
          <aside className="left-pane">
            <FilePane onFileSelect={handleFileSelect}/>
            <MessageHistory />
          </aside>

          <main className="right-pane">
            <OutputSection 
              message={message} 
              error={messageError} 
              isProcessing={isProcessing} 
            />

            <PromptAugmentation 
              augmentedPromptsEnabled={augmentedPromptsEnabled}
              augmentedPrompt={augmentedPrompt}
              error={augmentedError}
              isAugmenting={isAugmenting}
              copyAugmentedPrompt={copyAugmentedPrompt}
            />

            <PersonaSelector 
              selectedPersona={selectedPersona} 
              setSelectedPersona={setSelectedPersona} 
              autoDetectedPersona={autoDetectedPersona}
            />

            {/* ToDo: Should expand out on hover */}
            <UserInputForm 
              handleSubmit={handleFormSubmit}
              handleInputChange={handleInputChange}
              userInput={userInput}
              isProcessing={isProcessing}
              selectedFile={selectedFile}
            />
            
            <SuggestedQuestions 
              questionUserPromptsEnabled={questionUserPromptsEnabled}
              questionsForPrompt={questionsForPrompt}
              error={questionsError}
              isQuestioning={isQuestioning}
              onFormsFilled={setFormsFilled} // Pass the state updater as callback
              setConcatenatedQA={setConcatenatedQA}
              resetResponsesTrigger={resetResponsesTrigger}
            />

            <Navigation />
          </main>
        </div>
    );
};

export default App;