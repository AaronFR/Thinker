import React, { createContext, useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Settings.css';


const flaskPort= "http://localhost:5000"

export const SettingsContext = createContext();

const fetchConfig = async () => {
  try {
    const response = await fetch(`${flaskPort}/data/config`, {
      method: 'GET',
      headers: { "Content-Type": 'application/json' },
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
    await fetch(`${flaskPort}/data/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ field, value }),
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
    userEncyclopediaEnabled: false,
  });

  // Load config from server
  useEffect(() => {
    const loadConfig = async () => {
      const loadedConfig = await fetchConfig();
      if (loadedConfig) {
        setSettings(prevSettings => ({
          ...prevSettings,
          darkMode: loadedConfig.interface.dark_mode ?? false,
          userEncyclopediaEnabled: loadedConfig.beta_features.user_encyclopedia_enabled ?? false,
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
      toggleUserEncyclopedia: () => toggleSetting('beta_features.user_encyclopedia_enabled', 'userEncyclopediaEnabled'),
    }}>
      {children}
    </SettingsContext.Provider>
  );
}

export function Settings() {
  const { 
    settings,
    toggleDarkMode,
    toggleUserEncyclopedia,
  } = React.useContext(SettingsContext);

  const uiOptions = [
    { label: "Dark Mode", value: settings.darkMode, onChange: toggleDarkMode },
  ];

  const betaOptions = [
    { label: "User knowledge - The thinker will remember details about the user and their preferences",
     value: settings.userEncyclopediaEnabled, onChange: toggleUserEncyclopedia },
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
    </div>
  );
}

export default Settings;