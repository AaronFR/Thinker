import React, { useState, useContext, useEffect } from 'react';

import { handleLogout } from '../../utils/loginUtils';
import { formatPrice } from '../../utils/numberUtils';
import AutoExpandingTextarea from '../../utils/AutoExpandingTextarea';
import TextSizeSlider from '../../utils/textSizeSlider';
import Navigation from '../../components/Navigation';
import { apiFetch } from '../../utils/authUtils';
import TooltipConstants from '../../constants/tooltips';

import './Settings.css';

import { SettingsContext } from './SettingsContext';

import { Tooltip } from 'react-tooltip';


const FLASK_PORT = process.env.REACT_APP_THE_THINKER_BACKEND_URL || "http://localhost:5000";

const FUNCTIONALITY_STATES = {
  OFF: 'off',
  ON: 'on',
  AUTO: 'auto',
};

/**
 * UserInterfaceSettings Component
 *
 * Renders User Interface related settings.
 */
const UserInterfaceSettings = ({ settings, toggleDarkMode, toggleAiColourisation }) => (
  <div>
    <h2 className="settings-heading">User Interface</h2>
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
  </div>
);

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
}) => (
  <div>
    <h2 className="settings-heading">Functionality</h2>

    <h3>Auto select persona</h3>
    <p>Total costs {formatPrice(parseFloat(userInfo?.select_persona_cost))}</p>

    <h3>Auto select worfklows</h3>
    <p>Total costs {formatPrice(parseFloat(userInfo?.select_workflow_cost))}</p>

    {/* Auto Prompt Engineering Subsection */}
    <AutoPromptEngineeringSection
      currentValue={settings.augmentedPromptsEnabled}
      onChange={changeSetting}
      promptMessage={settings.promptAugmentationMessage}
      handleMessageChange={handleMessageChange}
      cost={userInfo?.augmentation_cost}
    />

    {/* Prompt Questioning Subsection */}
    <PromptQuestioningSection
      currentValue={settings.questionUserPromptsEnabled}
      onChange={changeSetting}
      promptMessage={settings.promptQuestioningMessage}
      handleMessageChange={handleMessageChange}
      cost={userInfo?.questioning_cost}
    />

    <BestOfSection 
      currentValue={settings.bestOfEnabled}
      promptMessage={settings.bestOfMessage}
      onChange={changeSetting}
      handleMessageChange={handleMessageChange}
    />

    
  </div>
);

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
    <h3>Auto Prompt Engineering</h3>
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
}) => (
  <div>
    <h3>Best of multiple runs</h3>
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
        <option value="differentiated">Differentiated</option>
      </select>
      For a given step runs multiple prompts in parrallel, running an additional call to select for the best response.
    </label>
    <p>
      If you select 'differentiated' each response will be instructed to focus on different factors: quality, creativity, etc<br/>
      Otherwise each run is supplied the same information but will vary randomly.
    </p>

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
 * SummariesSettings Component
 *
 * Renders Summaries related settings.
 */
const SummariesSettings = ({
  settings,
  toggleSummarisation,
  handleMessageChange,
}) => (
  <div>
    <h2 className="settings-heading">Summaries</h2>
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
    
  </div>
);

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
}) => (
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
  </div>
);

/**
 * SystemMessagesSettings Component
 *
 * Renders System Messages related settings without using the MessageSettings component.
 */
const SystemMessagesSettings = ({ settings, handleMessageChange }) => (
  <div>
    <h2 className="settings-heading">System Messages</h2>
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
  </div>
);

/**
 * Settings Component
 *
 * Main component that aggregates all settings sections.
 */
export function Settings() {
  const [parameters, setParameters] = useState(['email', 'augmentation_cost', 'select_persona_cost', 'select_workflow_cost', 'questioning_cost']);
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

  const fetchUserInformation = async () => {
    setError(null);
    setUserInfo(null);
    try {
      // Filter out empty parameters
      const filteredParameters = parameters.filter(param => param.trim() !== '');

      if (filteredParameters.length === 0) {
        throw new Error('Please specify at least one parameter.');
      }

      const response = await apiFetch(`${FLASK_PORT}/info/user`, {
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

      <FunctionalitySettings
        settings={settings}
        changeSetting={changeSetting}
        handleMessageChange={handleMessageChange}
        userInfo={userInfo}
      />

      <SummariesSettings
        settings={settings}
        toggleSummarisation={toggleSummarisation}
        handleMessageChange={handleMessageChange}
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
