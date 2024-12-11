import React, { createContext, useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

import { handleLogout } from '../../utils/loginUtils';

import './Settings.css';   

const FLASK_PORT = process.env.REACT_APP_THE_THINKER_BACKEND_URL || "http://localhost:5000";

export const SettingsContext = createContext();

const fetchConfig = async () => {
  try {
    const response = await fetch(`${FLASK_PORT}/data/config`, {
      method: 'GET',
      headers: { "Content-Type": 'application/json' },
      credentials: "include"
    });
    if (response.ok) {
      const loadedConfig = await response.json();
      return loadedConfig.interface && loadedConfig.beta_features ? loadedConfig : null;
    } else {
      console.error('Failed to load config');
      return null;
    }
  } catch (error) {
    console.error('Error loading config:', error);
    return null;
  }
};

const saveConfig = async (field, value) => {
  try {
    await fetch(`${FLASK_PORT}/data/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ field, value }),
      credentials: "include"
    });
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
    toggleMultiFileProcessing
  } = React.useContext(SettingsContext);

  const uiOptions = [
    { label: "Dark Mode", value: settings.darkMode, onChange: toggleDarkMode },
  ];

  const betaOptions = [
    { label: "Augmented prompt suggestions - A copy of the prompt will be generated, optimised with prompt engineering in mind to produce better responses. For reference or copying all",
     value: settings.augmentedPromptsEnabled, onChange: toggleAugmentedPrompts },
    { label: "Question user prompt - Questions will be generated against the users prompt as suggestions for the user to think about their prompt in detail",
     value: settings.questionUserPromptsEnabled, onChange: toggleQuestionUserPrompts },
    { label: "User knowledge - The thinker will remember details about the user and their preferences",
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

      <h2 className="settings-heading">🚧 Beta features</h2>
      {betaOptions.map(({ label, value, onChange }, index) => (
        <label key={index} className="settings-label">
          <input type="checkbox" checked={value} onChange={onChange} className="settings-checkbox" />
          {label}
        </label>
      ))}

      <button onClick={handleLogout} className="logout-button">Logout</button>
    </div>
  );
}

export default Settings;