import React, { useContext } from 'react';

import { handleLogout } from '../../utils/loginUtils';
import AutoExpandingTextarea from '../../utils/AutoExpandingTextarea';
import TextSizeSlider from '../../utils/textSizeSlider';
import { toTitleCase } from '../../utils/textUtils'
import Navigation from '../../components/Navigation';


import './Settings.css';

import { SettingsContext } from './SettingsContext';

const FUNCTIONALITY_STATES = {
  OFF: 'off',
  ON: 'on',
  AUTO: 'auto',
};


/**
 * Settings Component
 *
 * Renders the settings interface, allowing users to modify various application preferences.
 */
export function Settings() {
  const { 
      settings,
      changeSetting,
      toggleSetting,
      handleMessageChange
  } = useContext(SettingsContext);

  const toggleDebug = () => toggleSetting('interface.debug', 'debug');
  const toggleDarkMode = () => toggleSetting('interface.dark_mode', 'darkMode');
  const toggleAiColourisation = () => toggleSetting('interface.ai_colour', 'aiColour')
  const toggleUserEncyclopedia = () => toggleSetting('beta_features.user_context_enabled', 'userEncyclopediaEnabled')
  const toggleEncyclopedia = () => toggleSetting('beta_features.encyclopedia_enabled', 'encyclopediaEnabled') 
  const toggleMultiFileProcessing = () => toggleSetting('beta_features.multi_file_processing_enabled', 'multiFileProcessingEnabled')
  const togglesummarisation = () => toggleSetting('optimization.summarise', 'summarisationEnabled')

  const uiOptions = [
      { label: "Dark Mode", value: settings.darkMode, onChange: toggleDarkMode },
      { label: "New Category Colourisation via LLM Prompt", value: settings.aiColour, onChange: toggleAiColourisation }
  ];

  const betaOptions = [
      { 
          label: "User knowledge - The thinker will remember details about the user and their preferences (user preferences and facts are accumulated when enabled but not currently used when prompting)",
          value: settings.userEncyclopediaEnabled, 
          onChange: toggleUserEncyclopedia
      },
      { 
          label: "Reference knowledge - The thinker will look up details online (Wikipedia currently) and use them in reference to your prompt where appropriate",
          value: settings.encyclopediaEnabled, 
          onChange: toggleEncyclopedia 
      },
      { 
          label: "Multi file processing - personas can operate on multiple files at once (unstable)",
          value: settings.multiFileProcessingEnabled, 
          onChange: toggleMultiFileProcessing
      },
  ];

  const PromptQuestioningSection = ({ currentValue, onChange, promptMessage, handleMessageChange }) => (
    <>
      <h2>Prompt Questioning</h2>
      <label className="settings-label">
        <select
          className="settings-select"
          value={currentValue}
          onChange={(e) => onChange('beta_features.question_user_prompts_enabled', e.target.value, 'questionUserPromptsEnabled')}
        >
          <option value={FUNCTIONALITY_STATES.OFF}>Off</option>
          <option value={FUNCTIONALITY_STATES.ON}>On</option>
          <option value={FUNCTIONALITY_STATES.AUTO}>Auto</option>
        </select>
        Generates questions against the user's prompt and reference material.
      </label>
      <p>Use case: Difficult, 'knotty' technical questions.</p>
      <AutoExpandingTextarea
        value={promptMessage}
        className='textarea'
        onChange={(e) => handleMessageChange('promptQuestioningMessage', e.target.value)}
        style={{ opacity: 0.9 }}
      />
    </>
  );

  const AutoPromptEngineeringSection = ({ currentValue, onChange, promptMessage, handleMessageChange }) => (
    <>
      <h2>Auto Prompt Engineering</h2>
      <label className="settings-label">
        <select
          className="settings-select"
          value={currentValue}
          onChange={(e) => onChange('beta_features.augmented_prompts_enabled', e.target.value, 'augmentedPromptsEnabled')}
        >
          <option value={FUNCTIONALITY_STATES.OFF}>Off</option>
          <option value={FUNCTIONALITY_STATES.ON}>On</option>
          <option value={FUNCTIONALITY_STATES.AUTO}>Auto</option>
        </select>
        Generates a copy of your prompt that meets 'prompt engineering' standards.
      </label>
      <p>Use case: simple prompts that can-benefit from refinement.</p>
      <AutoExpandingTextarea
        value={promptMessage}
        className='textarea'
        onChange={(e) => handleMessageChange('promptAugmentationMessage', e.target.value)}
        style={{ opacity: 0.9 }}
      />
    </>
  );

  /**
   * Renders a System Message setting with a text area.
   */
  const MessageSettings = ({ label, value, onChange }) => (
    <label className="message-label">
      {label}
      <AutoExpandingTextarea
        value={value}
        className='textarea'
        onChange={onChange}
        style={{ opacity: 0.9 }}
      />
    </label>
  );

  return (
    <div className="scrollable settings-container">
      <Navigation />

      {/* User Interface Section */}
      <h2 className="settings-heading">User Interface</h2>
      {uiOptions.map(({ label, value, onChange }, index) => (
        <label key={index} className="settings-label">
          <input type="checkbox" checked={value} onChange={onChange} className="settings-checkbox" />
          {label}
        </label>
      ))}

      <TextSizeSlider />

      {/* Functionality Section */}
      <h2 className="settings-heading">Functionality</h2>
      
      <PromptQuestioningSection 
          currentValue={settings.questionUserPromptsEnabled}
          onChange={changeSetting}
          promptMessage={settings.promptQuestioningMessage}
          handleMessageChange={handleMessageChange}
      />

      <AutoPromptEngineeringSection 
          currentValue={settings.augmentedPromptsEnabled}
          onChange={changeSetting}
          promptMessage={settings.promptAugmentationMessage}
          handleMessageChange={handleMessageChange}
      />

      <h2>Summaries</h2>
      <label className="settings-label">
        <input
          type="checkbox"
          className="settings-checkbox"
          id="summarise-checkbox"
          checked={settings.summarisationEnabled}
          onChange={togglesummarisation}
        />
        Enables summaries on compatible workflows
      </label>
      <AutoExpandingTextarea
        value={settings.summarisationMessage}
        className='textarea'
        onChange={(e) => handleMessageChange('summarisationMessage', e.target.value)}
        style={{ opacity: 0.9 }}
      />

      {/* Beta Features Section */}
      <h2 className="settings-heading">🚧 Beta features</h2>
      <label className="settings-label" style={{"paddingBottom": "30px"}}>
        <input
          type="checkbox"
          className="settings-checkbox"
          id="debug-checkbox"
          checked={settings.debug}
          onChange={toggleDebug}
        />
        Enable debug view (Directly view prompt tags)
      </label>
      {betaOptions.map(({ label, value, onChange }, index) => (
        <label key={index} className="settings-label">
          <input type="checkbox" checked={value} onChange={onChange} className="settings-checkbox" />
          {label}
        </label>
      ))}

      {/* System Messages Section */}
      <h2 className="settings-heading">System Messages</h2>
      <div className="message-settings">
        {['coderPersonaMessage', 'writerPersonaMessage', 'categorisationMessage', 'bestOfMessage'].map((msgType, index) => (
          <MessageSettings
            key={index}
            label={toTitleCase(msgType.replace(/([A-Z])/g, ' $1'))}
            value={settings[msgType]}
            onChange={(e) => handleMessageChange(msgType, e.target.value)}
          />
        ))}
      </div>

      <div className='center-contents'>
        <button onClick={handleLogout} className="centered logout-button">Logout</button>
      </div>
    </div>
  );
}

export default Settings;
