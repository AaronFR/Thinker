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
import useSelectedCategory from './hooks/useSelectedCategory';


/**
 * App component
 * 
 * Main application component that handles user input, displays messages,
 * and manages state related to prompts and API interactions.
 */

function App () {

    // User Input States
    const [userInput, setUserInput] = useState('')

    // Debounce timer reference to optimize input handling
    const idleTime = 1500; // milliseconds
    const typingTimer = useRef(null);

    // Context Settings
    const { settings } = useContext(SettingsContext);
    const settingsRef = useRef(settings);

    useEffect(() => {
      settingsRef.current = settings;
    }, [settings]);

    // QA management
    const [concatenatedQA, setConcatenatedQA] = useState('');
    const [resetResponsesTrigger, setResetResponsesTrigger] = useState(0);

    // Tags management
    const [tags, setTags] = useState(
      { model: settingsRef.current.defaultForegroundModel }
    );

    // Context Selected Items
    const { 
      selectedMessages,
      setSelectedMessages,
      removeMessage,
      toggleMessageSelection,
      selectedFiles,
      setSelectedFiles,
      removeFile,
      toggleFileSelection,
    } = useContext(SelectionContext);

    const [refreshFiles, setRefreshFiles] = useState(false)

    // Workflow display
    const [workflow, setWorkflow] = useState()
 
    // Custom hooks
    const { message, messageId, files, error: messageError, isProcessing, handleSubmit, disconnectFromRequest, refreshCategory } = useSubmitMessage(concatenatedQA, selectedFiles, selectedMessages, tags, workflow, setWorkflow);
    const { augmentedPrompt, setAugmentedPrompt, isAugmenting, error: augmentedError, generateAugmentedPrompt } = useAugmentedPrompt();
    const { questionsForPrompt, setQuestionsForPrompt, isQuestioning, error: questionsError, generateQuestionsForPrompt } = useSuggestedQuestions();
    const { automaticallySelectedWorkflow, workflowIsLoading, selectMessageError, selectWorkflow } = useSelectedWorkflow();
    const { automaticallySelectedPersona, personaIsLoading, selectPersonaError, selectPersona } = useSelectedPersona();
    const { automaticallySelectedCategory, categoryIsLoading, selectCategoryError, selectCategory } = useSelectedCategory();

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
      setTags(prevTags => ({ ...prevTags, workflow: automaticallySelectedWorkflow }));
    }, [automaticallySelectedWorkflow]);

    useEffect(() => {
      setTags(prevTags => ({ ...prevTags, persona: automaticallySelectedPersona }))
    }, [automaticallySelectedPersona]);

    useEffect(() => {
      setTags(prevTags => ({ ...prevTags, category: automaticallySelectedCategory }))
    }, [automaticallySelectedCategory])

    useEffect(() => {
      // ToDo: doesn't refresh when settings changes on another tab
      setTags(prevTags => ({ ...prevTags, model: settingsRef.current.models.default_foreground_model }));
    }, [settingsRef.current.models?.default_foreground_model])

    useEffect(() => {
      if (messageId == null || messageId == '') {
        return
      }

      setSelectedMessages(prevMessages => ([
        ...prevMessages,
        messageId,
      ]));
    }, [messageId])

    const handleInputChange = (event, selectedMessages, selectedFiles, tags) => {
      const newValue = event.target.value;
      setUserInput(newValue);

      if (typingTimer.current) {
        clearTimeout(typingTimer.current);
      }

      // Adjust height to fit content, up to a max height
      event.target.style.height = "auto"; // Reset height to calculate scroll height properly
      event.target.style.height = `${Math.min(event.target.scrollHeight, 8 * 24)}px`;

      debouncedHandleTyping(newValue, selectedMessages, selectedFiles, tags);
    };

    const handleTyping = (value, selectedMessages, selectedFiles, tags) => {
      const currentSettings = settingsRef.current;
      
      if (currentSettings?.features?.automatically_select_persona !== "once") {
        selectPersona(value)
      }
      if (currentSettings?.features?.automatically_select_persona === "once" && !tags.persona) {
        selectPersona(value)
      }
      
      if (currentSettings?.features?.automatically_select_workflow !== "once") {
        selectWorkflow(value, tags)
      }
      if (currentSettings?.features?.automatically_select_workflow === "once" && !tags.workflow) {
        selectWorkflow(value, tags)
      }

      if (currentSettings?.features?.automatically_select_category !== "once") {
        selectCategory(value)
      }
      if (currentSettings?.features?.automatically_select_category === "once" && !tags.category) {
        selectCategory(value)
      }


      if (currentSettings?.prompt_improvement?.augmented_prompts_enabled  === "auto") {
        generateAugmentedPrompt(value);
      }
      if (currentSettings?.prompt_improvement?.question_user_prompts_enabled  === "auto" && !formsFilled) {
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
        await handleSubmit(userInput, selectedMessages, selectedFiles, tags);
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
      if (settingsRef.current?.prompt_improvement?.augmented_prompts_enabled != "off" && !formsFilled && settings.questionUserPromptsEnabled == 'auto') {
        generateQuestionsForPrompt(augmentedPrompt, selectedMessages, selectedFiles); // Retrigger questions for prompt
        setResetResponsesTrigger(prev => prev + 1);
      }
    };

    // Clean up the typing timer when the component unmounts
    useEffect(() => {
      return () => clearTimeout(typingTimer.current);
    }, []);

    return (
      <ResizablePane className="app-container">
        <div className="scrollable left-pane">
          <FilePane
            isProcessing={isProcessing}
            onFileSelect={toggleFileSelection}
            selectedFiles={selectedFiles}
            removeFile={removeFile}
            refreshFiles={refreshFiles}
          />
          <MessagePane
            isProcessing={isProcessing}
            onMessageSelect={toggleMessageSelection}
            selectedMessages={selectedMessages}
            removeMessage={removeMessage}
            refreshCategory={refreshCategory}
          />
        </div>
      
        <div className="scrollable right-pane">
          <Navigation />
          <LowBalanceWarning balance={balance} />
  
          <UserInputForm
            handleSubmit={handleFormSubmit}
            disconnectFromRequest={disconnectFromRequest}
            handleInputChange={handleInputChange}
            userInput={userInput}
            isProcessing={isProcessing}
            generateAugmentedPrompt={generateAugmentedPrompt}
            generateQuestionsForPrompt={generateQuestionsForPrompt}
            categoryIsLoading={categoryIsLoading}
            workflowIsLoading={workflowIsLoading}
            personaIsLoading={personaIsLoading}
            tags={tags}
            setTags={setTags}
            setRefreshFiles={setRefreshFiles}
          />
          
          {settingsRef.current?.prompt_improvement?.question_user_prompts_enabled != "off" && 
          <SuggestedQuestions
            questionsForPrompt={questionsForPrompt}
            error={questionsError}
            isQuestioning={isQuestioning}
            onFormsFilled={setFormsFilled}
            setConcatenatedQA={setConcatenatedQA}
            resetResponsesTrigger={resetResponsesTrigger}
          />}
  
          {settingsRef.current?.prompt_improvement?.augmented_prompts_enabled != "off" && 
          <PromptAugmentation 
            augmentedPrompt={augmentedPrompt}
            error={augmentedError}
            isAugmenting={isAugmenting}
            copyAugmentedPrompt={copyAugmentedPrompt}
          />}
  
          <Workflow
            workflowData={workflow}
          />
  
          <OutputSection 
            message={message}
            files={files}
            error={messageError} 
            isProcessing={isProcessing}
          />
  

        </div>
      </ResizablePane>
    );
};

export default App;