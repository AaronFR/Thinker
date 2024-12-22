import React, { createContext, useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';

import { handleLogout } from '../../utils/loginUtils';
import AutoExpandingTextarea from '../../components/AutoExpandingTextarea';

import './Settings.css';   

const FLASK_PORT = process.env.REACT_APP_THE_THINKER_BACKEND_URL || "http://localhost:5000";

export const SettingsContext = createContext();

/**
 * Fetches configuration settings from the server.
 *
 * @returns {Object|null} Loaded configuration or null if fetch fails.
 */
const fetchConfig = async () => {
  try {
    const response = await fetch(`${FLASK_PORT}/data/config`, {
      method: 'GET',
      headers: { "Content-Type": 'application/json' },
      credentials: "include"
    });
    if (response.ok) {
      const loadedConfig = await response.json();
      return loadedConfig.interface && loadedConfig.beta_features  && loadedConfig.systemMessages
       ? loadedConfig : null;
    } else {
      console.error('Failed to load config');
      return null;
    }
  } catch (error) {
    console.error('Error loading config:', error);
    return null;
  }
};

/**
 * Saves a setting to the server.
 *
 * @param {string} field - The config field to update.
 * @param {object} value - The new value for the config field.
 */
const saveConfig = async (field, value) => {
  try {
    const response = await fetch(`${FLASK_PORT}/data/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ field, value }),
      credentials: "include"
    });

    if (!response.ok) {
      throw new Error(`Server responded with status ${response.status}`);
    }

  } catch (error) {
    console.error('Error saving config:', error);
  }
};

// ToDo - cache in local memory for quicker loading
export function SettingsProvider({ children }) {
  const [settings, setSettings] = useState({
    darkMode: false,
    language: 'en',
    augmentedPromptsEnabled: true,
    questionUserPromptsEnabled: true,
    userEncyclopediaEnabled: false,
    encyclopediaEnabled: false,
    multiFileProcessingEnabled: false
  });

  const typingTimer = useRef(null);
  const idleTime = 2000;

  // Load config from server
  useEffect(() => {
    const loadConfig = async () => {
      const loadedConfig = await fetchConfig();
      if (loadedConfig) {
        setSettings(prevSettings => ({
          ...prevSettings,
          darkMode: loadedConfig.interface.dark_mode ?? false,
          augmentedPromptsEnabled: loadedConfig.beta_features.augmented_prompts_enabled ?? false,
          questionUserPromptsEnabled: loadedConfig.beta_features.question_user_prompts_enabled ?? false,
          userEncyclopediaEnabled: loadedConfig.beta_features.user_context_enabled ?? false,
          encyclopediaEnabled: loadedConfig.beta_features.encyclopedia_enabled ?? false,
          multiFileProcessingEnabled: loadedConfig.beta_features.multi_file_processing_enabled ?? false,
          // ToDo: You should decide what setting the contents to null does, the current default message for '' values is misleading and unhelpful
          promptAugmentationMessage: loadedConfig.systemMessages.promptAugmentationMessage || 'Default prompt augmentation message...',
          promptQuestioningMessage: loadedConfig.systemMessages.promptQuestioningMessage || 'Default prompt questioning message...',
          coderPersonaMessage: loadedConfig.systemMessages.coderPersonaMessage || 'Default coder persona message...',
          categorisationMessage: loadedConfig.systemMessages.categorisationMessage || 'Default categorisation message...'
        }));
      }
    };
    loadConfig();
  }, []);

  const toggleSetting = (field, key) => {
    const newValue = !settings[key];
    setSettings(prev => ({ ...prev, [key]: newValue }));
    saveConfig(field, newValue);
  };

  const handleMessageChange = (key, value) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
    if (typingTimer.current) {
        clearTimeout(typingTimer.current);
    }

    const configField = `systemMessages.${key}`
    typingTimer.current = setTimeout(() => {
        saveConfig(configField, value);
    }, idleTime);
  };

  // Apply Dark Mode to Document Body
  useEffect(() => {
    document.body.classList.toggle('dark-mode', settings.darkMode);
  }, [settings.darkMode]);

  return (
    <SettingsContext.Provider value={{
      settings,
      toggleDarkMode: () => toggleSetting('interface.dark_mode', 'darkMode'),
      toggleAugmentedPrompts: () => toggleSetting('beta_features.augmented_prompts_enabled', 'augmentedPromptsEnabled'),
      toggleQuestionUserPrompts: () => toggleSetting('beta_features.question_user_prompts_enabled', 'questionUserPromptsEnabled'),
      toggleUserEncyclopedia: () => toggleSetting('beta_features.user_context_enabled', 'userEncyclopediaEnabled'),
      toggleEncyclopedia: () => toggleSetting('beta_features.encyclopedia_enabled', 'encyclopediaEnabled'),
      toggleMultiFileProcessing: () => toggleSetting('beta_features.multi_file_processing_enabled', 'multiFileProcessingEnabled'),
      handleMessageChange
    }}>
      {children}
    </SettingsContext.Provider>
  );
}

export function Settings() {
  const { 
    settings,
    toggleDarkMode,
    toggleAugmentedPrompts,
    toggleQuestionUserPrompts,
    toggleUserEncyclopedia,
    toggleEncyclopedia,
    toggleMultiFileProcessing,
    handleMessageChange
  } = React.useContext(SettingsContext);

  const uiOptions = [
    { label: "Dark Mode", value: settings.darkMode, onChange: toggleDarkMode },
  ];

  const betaOptions = [
    { label: "User knowledge - The thinker will remember details about the user and their preferences (user preferences and facts are accumulated when enabled but not currently used when prompting)",
     value: settings.userEncyclopediaEnabled, onChange: toggleUserEncyclopedia },
    { label: "Reference knowledge - The thinker will look up details online (Wikipedia currently) and use them in reference to your prompt where appropriate",
     value: settings.encyclopediaEnabled, onChange: toggleEncyclopedia },
    { label: "Multi file processing - personas can operate on multiple files at once (unstable)",
     value: settings.multiFileProcessingEnabled, onChange: toggleMultiFileProcessing },
  ];

  return (
    <div className="settings-container">
      <nav className="settings-nav">
        <Link to="/" className="link">Home</Link>
        <Link to="/pricing" className="link">Pricing</Link>
      </nav>

      <h2 className="settings-heading">User Interface</h2>
      {uiOptions.map(({ label, value, onChange }, index) => (
        <label key={index} className="settings-label">
          <input type="checkbox" checked={value} onChange={onChange} className="settings-checkbox" />
          {label}
        </label>
      ))}

      <h2 className="settings-heading">Functionality</h2>
      <h2>Prompt Questioning</h2>
          <label className="settings-label">
            <input 
              type="checkbox"
              className="settings-checkbox"
              id="prompt-questioning-checkbox"
              checked={settings.questionUserPromptsEnabled}
              onChange={toggleQuestionUserPrompts}
            />
            Generates questions against the users prompt and reference material, giving suggestions for the user to think about their prompt in detail
          </label>
          <p>Use case: Difficult, 'knotty' technical questions where the extra details can help fomulate solutions. Not so useful when you *just* want any answer from the AI</p>
          <div className="message-settings">
            <AutoExpandingTextarea
              value={settings.promptQuestioningMessage}
              className='textarea'
              onChange={(e) => handleMessageChange('promptQuestioningMessage', e.target.value)}
              style={{ opacity: 0.9 }}  // ToDo: Opacity needs to change based on if its a default value or not
            />
        </div>

      <h2>Auto Prompt Engineering</h2>
        <label className="settings-label">
          <input
            type="checkbox"
            className="settings-checkbox"
            id="auto-prompt-engineering-checkbox"
            checked={settings.augmentedPromptsEnabled}
            onChange={toggleAugmentedPrompts}
          />
          Generates a copy of your prompt, re-written in line with 'prompt engineering' to produce better responses.
        </label>
        <p>And the shills told you it would be a career skill...</p>
        <p>Use case: simple, plain prompts that can none the less benefit from a *good* well thought out response</p>
        <div className='message-settings'>
          <AutoExpandingTextarea
            value={settings.promptAugmentationMessage}
            className='textarea'
            onChange={(e) => handleMessageChange('promptAugmentationMessage', e.target.value)}
            style={{ opacity: 0.9 }}
          />
        </div>

      <h2 className="settings-heading">🚧 Beta features</h2>
      {betaOptions.map(({ label, value, onChange }, index) => (
        <label key={index} className="settings-label">
          <input type="checkbox" checked={value} onChange={onChange} className="settings-checkbox" />
          {label}
        </label>
      ))}

      <h2 className="settings-heading">System Messages</h2>
        <div className="message-settings">
          <label className="message-label">
            Coder Persona:
            <AutoExpandingTextarea
              value={settings.coderPersonaMessage}
              className='textarea'
              onChange={(e) => handleMessageChange('coderPersonaMessage', e.target.value)}
              style={{ opacity: 0.9 }}
            />
          </label>
          <label className="message-label">
            Categorisation:
            <AutoExpandingTextarea
              value={settings.categorisationMessage}
              className='textarea'
              onChange={(e) => handleMessageChange('categorisationMessage', e.target.value)}
              style={{ opacity: 0.9 }}
            />
          </label>
        </div>

      <button onClick={handleLogout} className="logout-button">Logout</button>
    </div>
  );
}

export default Settings;