import React, { useState, useContext, useEffect } from 'react';

import { handleLogout } from '../../utils/loginUtils';
import { formatPrice } from '../../utils/numberUtils';
import AutoExpandingTextarea from '../../utils/AutoExpandingTextarea';
import TextSizeSlider from '../../utils/textSizeSlider';
import Navigation from '../../components/Navigation';
import ExpandableElement from '../../utils/expandableElement';
import { apiFetch } from '../../utils/authUtils';
import TooltipConstants from '../../constants/tooltips';

import './Settings.css';

import { SettingsContext } from './SettingsContext';

import ModelSelector from '../../components/Selectors/ModelSelector';
import { Tooltip } from 'react-tooltip';
import { userInfoEndpoint } from '../../constants/endpoints';


const FUNCTIONALITY_STATES = {
  OFF: 'off',
  ON: 'on',
  AUTO: 'auto',
};

/* Sections 
 * ToDo: Add config checks to leave sections open if they user left them
 */

/**
 * UserInterfaceSettings Component
 *
 * Renders User Interface related settings.
 */
const UserInterfaceSettings = ({ settings, toggleDarkMode, toggleAiColourisation }) => {
  const sectionHeading = (<h2 className="settings-heading">User Interface</h2>)

  const maxContent = (
  <div>
    {sectionHeading}
    <label className="settings-label">
      <input
        type="checkbox"
        checked={settings.darkMode}
        onChange={toggleDarkMode}
        className="settings-checkbox"
      />
      Dark Mode
    </label>
    <label 
      className="settings-label"
      data-tooltip-id="tooltip"
      data-tooltip-content={TooltipConstants.categoryColoursisationToggle}
      data-tooltip-place="bottom"
    >
      <input
        type="checkbox"
        checked={settings.aiColour}
        onChange={toggleAiColourisation}
        className="settings-checkbox"
      />
      New Category Colourisation via LLM Prompt
    </label>

    <TextSizeSlider />
  </div>)

  return (<ExpandableElement
    minContent={sectionHeading}
    maxContent={maxContent}
    initiallyExpanded={false}
    toggleButtonLabel=""
  />);
};


/**
 * AI Model Component
 *
 * Renders settings related to AI model utilisation.
 */
const AiModelSettings = ({ settings, handleForegroundModelChange, handleBackgroundModelChange }) => {
  const sectionHeading = (<h2 className="settings-heading">AI Models</h2>)

  const maxContent = (
  <div>
    {sectionHeading}
    <h3>Foreground Model Default</h3>
    <p>This will specifiy the foreground model to be selected by default, each step in each workflow will run on the selected model</p>
    <ModelSelector
      selectedModel={settings?.defaultForegroundModel || ''}
      setTags={handleForegroundModelChange}
    />

    <h3>Background Model</h3>
    <p>
      In the thinker many programs actually run in the background to try and improve the main 'foreground' prompt and the user experience overall, for this 
      purpose you want a functional econonmical, to the point LLM.
    </p>
    <ModelSelector
      selectedModel={settings?.defaultBackgroundModel || ''}
      setTags={handleBackgroundModelChange}
      economicalMode={true}
    />
  </div>)

  return (<ExpandableElement
    minContent={sectionHeading}
    maxContent={maxContent}
    initiallyExpanded={true}
    toggleButtonLabel=""
  />);
}

/**
 * FunctionalitySettings Component
 *
 * Renders Functionality related settings.
 */
const FunctionalitySettings = ({
  settings,
  changeSetting,
  handleMessageChange,
  userInfo
}) => {
  const sectionHeading = (<h2 className="settings-heading">Functionality</h2>)

  const maxContent = (<div>
    {sectionHeading}

    <h3>Auto select persona</h3>
    <p>Total costs {formatPrice(parseFloat(userInfo?.select_persona_cost))}</p>

    <h3>Auto select worfklows</h3>
    <p>Total costs {formatPrice(parseFloat(userInfo?.select_workflow_cost))}</p>

    <AutoPromptEngineeringSection
      currentValue={settings.augmentedPromptsEnabled}
      onChange={changeSetting}
      promptMessage={settings.promptAugmentationMessage}
      handleMessageChange={handleMessageChange}
      cost={userInfo?.augmentation_cost}
    />

    <PromptQuestioningSection
      currentValue={settings.questionUserPromptsEnabled}
      onChange={changeSetting}
      promptMessage={settings.promptQuestioningMessage}
      handleMessageChange={handleMessageChange}
      cost={userInfo?.questioning_cost}
    />

    <InternetSearchSection 
      currentValue={settings.internetSearchEnabled}
      onChange={changeSetting}
      cost={userInfo?.internet_search_cost}
    />

    <BestOfSection 
      currentValue={settings.bestOfEnabled}
      promptMessage={settings.bestOfMessage}
      onChange={changeSetting}
      handleMessageChange={handleMessageChange}
      cost={userInfo?.best_of_cost}
    />
  </div>)

  return (<ExpandableElement
    minContent={sectionHeading}
    maxContent={maxContent}
    initiallyExpanded={false}
    toggleButtonLabel=""
  />);
}

/**
 * WorkflowsSettings Component
 *
 * Renders Workflows related settings.
 */
const WorkflowsSettings = ({
   settings,
   toggleWritePagesInParallel,
}) => {
  const sectionHeading = (<h2 className="settings-heading">Workflows</h2>);
  
  const maxContent = (
  <div>
    {sectionHeading}

    <p>Write each page at once rather than in sequence - faster but means pages can't refer to prior content</p>
    <label className="settings-label">
      <input
        type="checkbox"
        className="settings-checkbox"
        checked={settings.writePagesInParallel}
        onChange={toggleWritePagesInParallel}  // ToDo: This approach might be a lot more efficient
      />
      Write Pages in Parallel
    </label>
  </div>)

  return (<ExpandableElement
    minContent={sectionHeading}
    maxContent={maxContent}
    initiallyExpanded={false}
    toggleButtonLabel=""
  />);
}


/**
 * SummariesSettings Component
 *
 * Renders Summaries related settings.
 */
const SummariesSettings = ({
  settings,
  toggleSummarisation,
  toggleFileSummarisation,
  handleMessageChange,
  summarise_workflows_cost,
  summarise_files_cost,
}) => {
  const sectionHeading = (<h2 className="settings-heading">Summaries</h2>)

  const maxContent = (
  <div>
    {sectionHeading}
    <label className="settings-label">
      <input
        type="checkbox"
        className="settings-checkbox"
        id="summarise-checkbox"
        checked={settings.summarisationEnabled}
        onChange={toggleSummarisation}
      />
      Enables summaries on compatible workflows
    </label>
    <h4>Total cost: {formatPrice(parseFloat(summarise_workflows_cost))}</h4>
    <div
      data-tooltip-id="tooltip"
      data-tooltip-content={TooltipConstants.summarisationSystemMessage}
      data-tooltip-place="bottom"
    >
      <AutoExpandingTextarea
        value={settings.summarisationMessage}
        className="textarea"
        onChange={(e) =>
          handleMessageChange('summarisationMessage', e.target.value)
        }
        style={{ opacity: 0.9 }}
      />
    </div>

    <label className="settings-label">
      <input
        type="checkbox"
        className="settings-checkbox"
        id="summarise-checkbox"
        checked={settings.fileSummarisationEnabled}
        onChange={toggleFileSummarisation}
      />
      Add a summary to new files after they've been created
    </label>
    <h4>Total cost: {formatPrice(parseFloat(summarise_files_cost))}</h4>
    <div
      data-tooltip-id="tooltip"
      data-tooltip-content={TooltipConstants.summarisationSystemMessage}
      data-tooltip-place="bottom"
    >
      <AutoExpandingTextarea
        value={settings.fileSummarisationMessage}
        className="textarea"
        onChange={(e) =>
          handleMessageChange('fileSummarisationMessage', e.target.value)
        }
        style={{ opacity: 0.9 }}
      />
    </div>
  </div>)

  return (<ExpandableElement
    minContent={sectionHeading}
    maxContent={maxContent}
    initiallyExpanded={false}
    toggleButtonLabel=""
  />);
}

/**
 * SystemMessagesSettings Component
 *
 * Renders System Messages related settings without using the MessageSettings component.
 */
const SystemMessagesSettings = ({ settings, handleMessageChange }) => {
  const sectionHeading = (<h2 className="settings-heading">System Messages</h2>);

  const maxContent = (
  <div>
    {sectionHeading}
    
    <div className="message-settings">
      {/* Coder Persona Message */}
      <label className="message-label">
        Coder Persona Message
        <AutoExpandingTextarea
          value={settings.coderPersonaMessage}
          className="textarea"
          onChange={(e) =>
            handleMessageChange('coderPersonaMessage', e.target.value)
          }
          style={{ opacity: 0.9 }}
        />
      </label>

      {/* Writer Persona Message */}
      <label className="message-label">
        Writer Persona Message
        <AutoExpandingTextarea
          value={settings.writerPersonaMessage}
          className="textarea"
          onChange={(e) =>
            handleMessageChange('writerPersonaMessage', e.target.value)
          }
          style={{ opacity: 0.9 }}
        />
      </label>

      {/* Categorisation Message */}
      <label className="message-label">
        Categorisation Message
        <div
          data-tooltip-id="tooltip"
          data-tooltip-content={TooltipConstants.categorisationSystemMessage}
          data-tooltip-place="bottom"
        >
          <AutoExpandingTextarea
            value={settings.categorisationMessage}
            className="textarea"
            onChange={(e) =>
              handleMessageChange('categorisationMessage', e.target.value)
            }
            style={{ opacity: 0.9 }}
          />
        </div>
        
      </label>
    </div>
  </div>)


  return (<ExpandableElement
    minContent={sectionHeading}
    maxContent={maxContent}
    initiallyExpanded={false}
    toggleButtonLabel=""
  />);
}

/**
 * BetaFeaturesSettings Component
 *
 * Renders Beta Features related settings.
 */
const BetaFeaturesSettings = ({
  settings,
  toggleDebug,
  toggleUserEncyclopedia,
  toggleEncyclopedia,
  toggleMultiFileProcessing,
}) => {
  const sectionHeading = (<h2 className="settings-heading">🚧 Beta Features</h2>);

  const maxContent = (
  <div>
    <h2 className="settings-heading">🚧 Beta Features</h2>
    <label className="settings-label" style={{ paddingBottom: '30px' }}>
      <input
        type="checkbox"
        className="settings-checkbox"
        id="debug-checkbox"
        checked={settings.debug}
        onChange={toggleDebug}
      />
      Enable debug view (Directly view prompt tags)
    </label>

    <label className="settings-label">
      <input
        type="checkbox"
        checked={settings.userEncyclopediaEnabled}
        onChange={toggleUserEncyclopedia}
        className="settings-checkbox"
      />
      User knowledge - The thinker will remember details about the user and their preferences
    </label>

    <label className="settings-label">
      <input
        type="checkbox"
        checked={settings.encyclopediaEnabled}
        onChange={toggleEncyclopedia}
        className="settings-checkbox"
      />
      Reference knowledge - The thinker will look up details online (Wikipedia currently) and use
      them in reference to your prompt where appropriate
    </label>

    <label className="settings-label">
      <input
        type="checkbox"
        checked={settings.multiFileProcessingEnabled}
        onChange={toggleMultiFileProcessing}
        className="settings-checkbox"
      />
      Multi file processing - personas can operate on multiple files at once (unstable)
    </label>
  </div>)

  return (<ExpandableElement
    minContent={sectionHeading}
    maxContent={maxContent}
    initiallyExpanded={false}
    toggleButtonLabel=""
  />);
}

/* Individual settings blocks */

/**
 * PromptQuestioningSection Component
 *
 * Renders settings for Prompt Questioning.
 */
const PromptQuestioningSection = ({
  currentValue,
  onChange,
  promptMessage,
  handleMessageChange,
  cost,
}) => (
  <div>
    <h3>Prompt Questioning</h3>
    <h4>Total cost: {formatPrice(parseFloat(cost))}</h4>
    <label className="settings-label">
      <select
        className="settings-select"
        value={currentValue}
        onChange={(e) =>
          onChange(
            'beta_features.question_user_prompts_enabled',
            e.target.value,
            'questionUserPromptsEnabled'
          )
        }
      >
        <option value={FUNCTIONALITY_STATES.OFF}>Off</option>
        <option value={FUNCTIONALITY_STATES.ON}>On</option>
        <option value={FUNCTIONALITY_STATES.AUTO}>Auto</option>
      </select>
      Generates questions against the user's prompt and reference material.
    </label>
    <p>👍 Difficult, 'knotty' technical questions, where extra context can help clarify the problem - for the machine and potentially for <i>you</i></p>
    <p>👎 When you <i>just</i> want an answer quickly</p>
    <div
      data-tooltip-id="tooltip"
      data-tooltip-content={TooltipConstants.questioningSystemMessage}
      data-tooltip-place="bottom"
    >
      <AutoExpandingTextarea
      value={promptMessage}
      className="textarea"
      onChange={(e) =>
        handleMessageChange('promptQuestioningMessage', e.target.value)
      }
      style={{ opacity: 0.9 }}
    />
    </div>
    
  </div>
);

/**
 * AutoPromptEngineeringSection Component
 *
 * Renders settings for Auto Prompt Engineering.
 */
const AutoPromptEngineeringSection = ({
  currentValue,
  onChange,
  promptMessage,
  handleMessageChange,
  cost
}) => (
  <div>
    <h3>Prompt Improvement</h3>
    <h4>Total cost: {formatPrice(parseFloat(cost))}</h4>
    <label className="settings-label">
      <select
        className="settings-select"
        value={currentValue}
        onChange={(e) =>
          onChange(
            'beta_features.augmented_prompts_enabled',
            e.target.value,
            'augmentedPromptsEnabled'
          )
        }
      >
        <option value={FUNCTIONALITY_STATES.OFF}>Off</option>
        <option value={FUNCTIONALITY_STATES.ON}>On</option>
        <option value={FUNCTIONALITY_STATES.AUTO}>Auto</option>
      </select>
      Generates a copy of your prompt that meets 'prompt engineering' standards.
    </label>
    <p>👍 Simple prompts</p>
    <p>👎 Complex, specific and precisely worded prompts with exacting long references</p>
    <div
      data-tooltip-id="tooltip"
      data-tooltip-content={TooltipConstants.autoPromptEngigneeringSystemMessage}
      data-tooltip-place="bottom"
    >
      <AutoExpandingTextarea
        value={promptMessage}
        className="textarea"
        onChange={(e) =>
          handleMessageChange('promptAugmentationMessage', e.target.value)
        }
        style={{ opacity: 0.9 }}
      />
    </div>
    <small>And the shills told you it would be a career skill...</small>
    
  </div>
);

/**
 * BestOfSection Component
 *
 * Renders settings for 'Best of' multiple reruns functionality.
 */
const BestOfSection = ({
  currentValue,
  onChange,
  promptMessage,
  handleMessageChange,
  cost
}) => (
  <div>
    <h3>Best of multiple runs</h3>
    <h4>Total cost: {formatPrice(parseFloat(cost))}</h4>
    <label className="settings-label">
      <select
        className="settings-select"
        value={currentValue}
        onChange={(e) =>
          onChange(
            'features.multiple_reruns_enabled',
            e.target.value,
            'bestOfEnabled'
          )
        }
      >
        <option value={FUNCTIONALITY_STATES.OFF}>Off</option>
        <option value={FUNCTIONALITY_STATES.ON}>On</option>
      </select>
      For a given step runs multiple prompts in parrallel, running an additional call to select for the best response.
    </label>

    <p>👍 Improving response coherency or any other selected metric</p>
    <p>👍 Helping inexpensive models compete against more expensive ones</p>
    <p>👎 Keeping costs low while running expensive models.</p>
    <div
      data-tooltip-id="tooltip"
      data-tooltip-content={TooltipConstants.bestOfSystemMessage}
      data-tooltip-place="bottom"
    >
      <AutoExpandingTextarea
        value={promptMessage}
        className="textarea"
        onChange={(e) =>
          handleMessageChange('bestOfMessage', e.target.value)
        }
        style={{ opacity: 0.9 }}
      />
    </div>
    
  </div>
);

/**
 * InternetSearch Component
 * 
 * ToDo: system message for search after full implementation
 *
 * Contains the settings and rules for internet search functionality
 */
const InternetSearchSection = ({
  currentValue,
  onChange,
  cost
}) => (
  <div>
    <h3>Internet Search</h3>
    <h4
      data-tooltip-id="tooltip"
      data-tooltip-content={TooltipConstants.internetSearchCosting}
      data-tooltip-place="bottom"
    >
      Total cost: {formatPrice(parseFloat(cost))}
    </h4>
    <label className="settings-label">
      <select
        className="settings-select"
        value={currentValue}
        onChange={(e) =>
          onChange(
            'features.internet_search_enabled',
            e.target.value,
            'internetSearchEnabled'
          )
        }
      >
        <option value={FUNCTIONALITY_STATES.OFF}>Off</option>
        <option value={FUNCTIONALITY_STATES.ON}>On</option>
      </select>
      If enabled each step will search the internet, if applicable, for additional context
    </label>

    <p>👍 Additional context can improve the response, access information the AI doesn't know and mitigate hallucinations</p>
    <p>👎 Increases costs and time per request (though input is cheaper than output)</p> 
  </div>
);

/* Settings Page */

/**
 * Settings Component
 *
 * Main component that aggregates all settings sections.
 */
export function Settings() {
  const [parameters, setParameters] = useState(['email', 'augmentation_cost', 'select_persona_cost', 'select_workflow_cost', 'questioning_cost', 'best_of_cost', 'internet_search_cost', 'summarise_workflows_cost', 'summarise_files_cost']);
  const [userInfo, setUserInfo] = useState(null);
  const [error, setError] = useState(null);

  const {
    settings,
    changeSetting,
    toggleSetting,
    handleMessageChange,
  } = useContext(SettingsContext);

  // Toggle Handlers
  const toggleDebug = () => toggleSetting('interface.debug', 'debug');
  const toggleDarkMode = () =>
    toggleSetting('interface.dark_mode', 'darkMode');
  const toggleAiColourisation = () =>
    toggleSetting('interface.ai_colour', 'aiColour');
  const toggleUserEncyclopedia = () =>
    toggleSetting(
      'beta_features.user_context_enabled',
      'userEncyclopediaEnabled'
    );
  const toggleEncyclopedia = () =>
    toggleSetting('beta_features.encyclopedia_enabled', 'encyclopediaEnabled');
  const toggleMultiFileProcessing = () =>
    toggleSetting(
      'beta_features.multi_file_processing_enabled',
      'multiFileProcessingEnabled'
    );
  const toggleSummarisation = () =>
    toggleSetting('optimization.summarise', 'summarisationEnabled');
  const toggleFileSummarisation = () =>
    toggleSetting('optimization.summariseFiles', 'fileSummarisationEnabled');
  const toggleWritePagesInParallel = () =>
    toggleSetting('optimization.writePagesInParallel', 'writePagesInParallel');

  const fetchUserInformation = async () => {
    setError(null);
    setUserInfo(null);
    try {
      // Filter out empty parameters
      const filteredParameters = parameters.filter(param => param.trim() !== '');

      if (filteredParameters.length === 0) {
        throw new Error('Please specify at least one parameter.');
      }

      const response = await apiFetch(userInfoEndpoint, {
        method: 'POST',
        body: JSON.stringify({ parameters: filteredParameters }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch user information.');
      }

      const data = await response.json();
      setUserInfo(data.user_data);
    } catch (err) {
      console.error('Error fetching user information:', err);
      setError(err.message || 'Unable to load user information. Please try again.');
    }
  };

  const handleForegroundModelChange = (selectedModelValue) => {
    changeSetting(
      'models.default_foreground_model',
      selectedModelValue,
      'defaultForegroundModel');
  };

  const handleBackgroundModelChange = (selectedModelValue) => {
    changeSetting(
      'models.default_background_model',
      selectedModelValue,
      'defaultBackgroundModel');
  };

  useEffect(() => {
    fetchUserInformation();
  }, [])

  return (
    <div className="scrollable settings-container">
      <Navigation />

      {error && <p>{error}</p>}

      <small>
        {userInfo?.email}
      </small>

      <UserInterfaceSettings
        settings={settings}
        toggleDarkMode={toggleDarkMode}
        toggleAiColourisation={toggleAiColourisation}
      />

      <AiModelSettings
        settings={settings}
        handleForegroundModelChange={handleForegroundModelChange}
        handleBackgroundModelChange={handleBackgroundModelChange}
      />

      <FunctionalitySettings
        settings={settings}
        changeSetting={changeSetting}
        handleMessageChange={handleMessageChange}
        userInfo={userInfo}
      />

      <WorkflowsSettings
        settings={settings}
        toggleWritePagesInParallel={toggleWritePagesInParallel}
      />

      <SummariesSettings
        settings={settings}
        toggleSummarisation={toggleSummarisation}
        toggleFileSummarisation={toggleFileSummarisation}
        handleMessageChange={handleMessageChange}
        summarise_workflows_cost={userInfo?.summarise_workflows_cost}
        summarise_files_cost={userInfo?.summarise_files_cost}
      />

      <SystemMessagesSettings
        settings={settings}
        handleMessageChange={handleMessageChange}
      />

      <BetaFeaturesSettings
        settings={settings}
        toggleDebug={toggleDebug}
        toggleUserEncyclopedia={toggleUserEncyclopedia}
        toggleEncyclopedia={toggleEncyclopedia}
        toggleMultiFileProcessing={toggleMultiFileProcessing}
      />

      <div className="center-contents">
        <button onClick={handleLogout} className="centered logout-button">
          Logout
        </button>
      </div>
      <Tooltip id="tooltip" />
    </div>
  );
}

export default Settings;
