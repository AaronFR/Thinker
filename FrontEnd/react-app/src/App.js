import React, { useState, useEffect, useRef, useContext } from 'react';
import './App.css';

import { SettingsContext } from './pages/Settings/Settings';

import OutputSection from './components/OutputSection';
import PromptAugmentation from './components/PromptAugmentation';
import PersonaSelector from './components/PersonaSelector';
import UserInputForm from './components/UserInputForm';
import SuggestedQuestions from './components/SuggestedQuestions';
import Navigation from './components/Navigation';

import useSubmitMessage from './hooks/useSubmitMessage';
import useAugmentedPrompt from './hooks/useAugmentedPrompt';
import useSuggestedQuestions from './hooks/useSuggestedQuestions';

/**
 * App component
 * 
 * Main application component that handles user input, displays messages,
 * and manages state related to prompts and API interactions.
 */
const flask_port= "http://localhost:5000"

function App () {

    const [userInput, setUserInput] = useState('')

    const [selectedPersona, setSelectedPersona] = useState('auto');
    const autoDetectedPersona = 'Coder' // Temporary hardcoded value

    const idleTime = 1500; // Time in milliseconds before triggering input handlers
    const typingTimer = useRef(null);

    const { settings } = useContext(SettingsContext);
    const { augmentedPromptsEnabled, questionUserPromptsEnabled } = settings;

    const [concatenatedQA, setConcatenatedQA] = useState('');
    const [resetResponsesTrigger, setResetResponsesTrigger] = useState(0);
 
    // Custom hooks
    const { message, setMessage, error: messageError, isProcessing, handleSubmit } = useSubmitMessage(flask_port, concatenatedQA);
    const { augmentedPrompt, setAugmentedPrompt, isAugmenting, error: augmentedError, generateAugmentedPrompt } = useAugmentedPrompt(flask_port);
    const { questionsForPrompt, setQuestionsForPrompt, isQuestioning, error: questionsError, generateQuestionsForPrompt } = useSuggestedQuestions(flask_port);

    const [formsFilled, setFormsFilled] = useState(false);

    const handleFormSubmit = async (event) => {
      if (event) event.preventDefault();
      await handleSubmit(userInput, selectedPersona);
      setUserInput(''); 
      setAugmentedPrompt('');

      setQuestionsForPrompt('');
      setFormsFilled(false)
      setResetResponsesTrigger(prev => prev + 1);
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
        if (questionUserPromptsEnabled && !formsFilled) {
          generateQuestionsForPrompt(event.target.value);
        }
      }, idleTime);
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
        </div>
    );
};

export default App;