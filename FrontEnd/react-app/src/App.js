import React, { useState, useEffect, useRef, useContext } from 'react';
import debounce from 'lodash.debounce';

import { SettingsContext } from './pages/Settings/Settings';

import FilePane from './components/FilePane'
import MessagePane from './components/MessagePane';
import OutputSection from './components/OutputSection';
import PromptAugmentation from './components/PromptAugmentation';
import PersonaSelector from './components/PersonaSelector';
import UserInputForm from './components/UserInputForm';
import SuggestedQuestions from './components/SuggestedQuestions';
import Workflow from './components/Workflow';
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

    // Tags Management
    const [tags, setTags] = useState(
      { model: "gpt-4o-mini" }  // e.g. write: "example.txt" category: "example"
    );

    // File Management
    const [selectedFiles, setSelectedFiles] = useState([]);

    // Message management
    const [selectedMessages, setSelectedMessages] = useState([])

    // Workflow display
    const [workflow, setWorkflow] = useState()
 
    // Custom hooks
    const { message, error: messageError, isProcessing, handleSubmit } = useSubmitMessage(flask_port, concatenatedQA, selectedFiles, selectedMessages, tags, workflow, setWorkflow);
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
      setSelectedFiles((prevFiles) => {
        // ToDo: should filter by id not name, but uploaded files aren't setup for that yet
        if (prevFiles.some((f) => f.name === file.name)) {
          // If the file is already selected, filter it out
          return prevFiles.filter((f) => f.name !== file.name);
        } else {
          // Otherwise, add new the new file to the list of selectedFiles
          return [...prevFiles, file];
        }
      });
    };

    const handleMessageSelect = (message) => {
      setSelectedMessages((prevMessages) => {
        // ToDo: should filter by id not prompt, but uploaded files aren't setup for that yet
        if (prevMessages.some((f) => f.prompt === message.prompt)) {
          // If the message is already selected, filter it out
          return prevMessages.filter((f) => f.prompt !== message.prompt);
        } else {
          // Otherwise, add new the new message to the list of selectedMessages
          return [...prevMessages, message];
        }
        
      });
    };


    return (
        <div className="app-container">
          <aside className="left-pane">
            <FilePane 
              onFileSelect={handleFileSelect}
              isProcessing={isProcessing}
            />
            <MessagePane 
              isProcessing={isProcessing}
              onMessageSelect={handleMessageSelect}
            />
          </aside>

          <main className="right-pane">
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
              selectedFiles={selectedFiles}
              setSelectedFiles={setSelectedFiles}
              selectedMessages={selectedMessages}
              setSelectedMessages={setSelectedMessages}
              tags={tags}
              setTags={setTags}
            />
            
            <SuggestedQuestions 
              questionUserPromptsEnabled={questionUserPromptsEnabled}
              questionsForPrompt={questionsForPrompt}
              error={questionsError}
              isQuestioning={isQuestioning}
              onFormsFilled={setFormsFilled}
              setConcatenatedQA={setConcatenatedQA}
              resetResponsesTrigger={resetResponsesTrigger}
            />

            <PromptAugmentation 
              augmentedPromptsEnabled={augmentedPromptsEnabled}
              augmentedPrompt={augmentedPrompt}
              error={augmentedError}
              isAugmenting={isAugmenting}
              copyAugmentedPrompt={copyAugmentedPrompt}
            />

            <Workflow
              workflowData={workflow}
            />

            <OutputSection 
              message={message} 
              error={messageError} 
              isProcessing={isProcessing} 
            />

            <Navigation />
          </main>
        </div>
    );
};

export default App;