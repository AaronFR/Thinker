import React, { useState, useEffect, useRef, useContext } from 'react';

import debounce from 'lodash.debounce';

import { SettingsContext } from './pages/Settings/SettingsContext';
import { SelectionContext } from './pages/Messages/SelectionContext';

import ResizablePane from './utils/resizeablePane';
import FilePane from './pages/Messages/FilePane'
import MessagePane from './pages/Messages/MessagePane';
import OutputSection from './components/OutputSection';
import PromptAugmentation from './components/PromptAugmentation';
import UserInputForm from './components/UserInputForm';
import SuggestedQuestions from './components/SuggestedQuestions';
import Workflow from './components/Workflow';
import Navigation from './components/Navigation';

import useSubmitMessage from './hooks/useSubmitMessage';
import useAugmentedPrompt from './hooks/useAugmentedPrompt';
import useSuggestedQuestions from './hooks/useSuggestedQuestions';
import useSelectedWorkflow from './hooks/useSelectedWorkflow';
import LowBalanceWarning from './utils/BalanceWarning';

import { apiFetch } from './utils/authUtils';

import './App.css';
import useSelectedPersona from './hooks/useSelectedPersona';
import { userBalanceEndpoint } from './constants/endpoints';


/**
 * App component
 * 
 * Main application component that handles user input, displays messages,
 * and manages state related to prompts and API interactions.
 */

function App () {

    // User Input States
    const [userInput, setUserInput] = useState('')
    const [selectedPersona, setSelectedPersona] = useState('auto');

    // Debounce timer reference to optimize input handling
    const idleTime = 1500; // milliseconds
    const typingTimer = useRef(null);

    // Context Settings
    const { settings } = useContext(SettingsContext);
    const settingsRef = useRef(settings);

    useEffect(() => {
      settingsRef.current = settings;
    }, [settings]);

    const { augmentedPromptsEnabled, questionUserPromptsEnabled } = settings;

    // QA management
    const [concatenatedQA, setConcatenatedQA] = useState('');
    const [resetResponsesTrigger, setResetResponsesTrigger] = useState(0);

    // Tags management
    const [tags, setTags] = useState(
      { model: "gpt-4o-mini" }  // e.g. write: "example.txt" category: "example"
    );

    // Context Selected Items
    const { 
      selectedMessages,
      setSelectedMessages,
      toggleMessageSelection,
      selectedFiles,
      setSelectedFiles,
      toggleFileSelection,
    } = useContext(SelectionContext);

    // Workflow display
    const [workflow, setWorkflow] = useState()
 
    // Custom hooks
    const { message, files, error: messageError, isProcessing, handleSubmit } = useSubmitMessage(concatenatedQA, selectedFiles, selectedMessages, tags, workflow, setWorkflow);
    const { augmentedPrompt, setAugmentedPrompt, isAugmenting, error: augmentedError, generateAugmentedPrompt } = useAugmentedPrompt();
    const { questionsForPrompt, setQuestionsForPrompt, isQuestioning, error: questionsError, generateQuestionsForPrompt } = useSuggestedQuestions();
    const { selectedWorkflow, workflowIsLoading, selectMessageError, selectWorkflow } = useSelectedWorkflow();
    const { automaticallySelectedPersona, personaIsLoading, selectPersonaError, selectPersona } = useSelectedPersona();

    // Form State
    const [formsFilled, setFormsFilled] = useState(false);

    // Balance management
    const [balance, setBalance] = useState();

    const loadBalance = async () => {
      try {
          const response = await apiFetch(userBalanceEndpoint, {
              method: 'GET',
          });

          if (response.ok) {
              const balanceData = await response.json();
              if (balanceData && typeof balanceData.balance === 'number') {
                  setBalance(balanceData.balance);
              }
          } else {
              console.error('Failed to load user balance', response);
          }
      } catch (error) {
          console.error('Error retrieving user balance:', error);
      }
    }

    useEffect(() => {
      loadBalance()
    }, [formsFilled])

    useEffect(() => {
      setTags(prevTags => ({ ...prevTags, workflow: selectedWorkflow }));
    }, [selectedWorkflow]);

    useEffect(() => {
      setSelectedPersona(automaticallySelectedPersona);
    }, [automaticallySelectedPersona]);

    const handleInputChange = (event, selectedMessages, selectedFiles, tags) => {      
      setUserInput(event.target.value);
      if (typingTimer.current) {
        clearTimeout(typingTimer.current);
      }

      // Adjust height to fit content, up to a max height
      event.target.style.height = "auto"; // Reset height to calculate scroll height properly
      event.target.style.height = `${Math.min(event.target.scrollHeight, 8 * 24)}px`;

      debouncedHandleTyping(event.target.value, selectedMessages, selectedFiles, tags);
    };

    const handleTyping = (value, selectedMessages, selectedFiles, tags) => {
      const currentSettings = settingsRef.current;
      
      selectPersona(value)
      selectWorkflow(value, tags)
      if (currentSettings.augmentedPromptsEnabled  === "auto") {
        generateAugmentedPrompt(value);
      }
      if (currentSettings.questionUserPromptsEnabled  === "auto" && !formsFilled) {
        generateQuestionsForPrompt(value, selectedMessages, selectedFiles);
      }
    };

    const debouncedHandleTyping = useRef(
      debounce((value, selectedMessages, selectedFiles, tags) => handleTyping(value, selectedMessages, selectedFiles, tags), idleTime)
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
        await handleSubmit(userInput, selectedPersona, selectedMessages, selectedFiles, tags);
        setSelectedFiles([])
        setSelectedMessages([])

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
      if (questionUserPromptsEnabled && !formsFilled && settings.questionUserPromptsEnabled == 'auto') {
        generateQuestionsForPrompt(augmentedPrompt, selectedMessages, selectedFiles); // Retrigger questions for prompt
        setResetResponsesTrigger(prev => prev + 1);
      }
    };

    // Clean up the typing timer when the component unmounts
    useEffect(() => {
      return () => clearTimeout(typingTimer.current);
    }, []);

    return (
      <div className="app-container">
        <ResizablePane>
          <div className="scrollable left-pane">
            <FilePane 
              isProcessing={isProcessing}
              onFileSelect={toggleFileSelection}
              selectedFiles={selectedFiles}
            />
            <MessagePane 
              isProcessing={isProcessing}
              onMessageSelect={toggleMessageSelection}
              selectedMessages={selectedMessages}
            />
          </div>
        
          <div className="scrollable right-pane">

            <LowBalanceWarning balance={balance} />
    
            {/* ToDo: Should expand out on hover */}
            <UserInputForm 
              handleSubmit={handleFormSubmit}
              handleInputChange={handleInputChange}
              userInput={userInput}
              isProcessing={isProcessing}
              selectedPersona={selectedPersona}
              setSelectedPersona={setSelectedPersona}
              generateAugmentedPrompt={generateAugmentedPrompt}
              generateQuestionsForPrompt={generateQuestionsForPrompt}
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
              files={files}
              error={messageError} 
              isProcessing={isProcessing}
            />
    
            <Navigation />
          </div>
        </ResizablePane>
      </div>
    );
};

export default App;