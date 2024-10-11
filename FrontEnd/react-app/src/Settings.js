import React, { createContext, useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Settings.css';


const flaskPort= "http://localhost:5000"

export const SettingsContext = createContext();

// ToDo - cache in local memory for quicker loading
export function SettingsProvider({ children }) {
  const [settings, setSettings] = useState({
    darkMode: false,
    language: 'en',
  });

  // Load config from server
  useEffect(() => {
    const loadConfig = async () => {
      try {
        console.log("trying to load config");
        const response = await fetch(flaskPort + '/data/config', {
          method: 'GET',
          headers: {
            "Content-Type": 'application/json',
          },
        });
        
        if (response.ok) {
          const loadedConfig = await response.json();
          console.log(loadedConfig);
          if (loadedConfig && loadedConfig.interface) {
            setSettings(prevSettings => ({
              ...prevSettings,
              darkMode: loadedConfig.interface.dark_mode ?? false,
            }));
          }
        } else {
          console.error('Failed to load config');
        }
      } catch (error) {
        console.error('Error loading config:', error);
      }
    };
    loadConfig();
  }, []);

  // Toggle Dark Mode
  const toggleDarkMode = async () => {
    const newMode = !settings.darkMode;

    setSettings(prevSettings => ({
      ...prevSettings,
      darkMode: newMode,
    }));

    try {
      await fetch(flaskPort + '/data/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ field: 'interface.dark_mode', value: newMode }),
      });
    } catch (error) {
      console.error('Error saving config:', error);
    }
  };

  // Apply Dark Mode to Document Body
  useEffect(() => {
    document.body.classList.toggle('dark-mode', settings.darkMode);
  }, [settings.darkMode]);

  return (
    <SettingsContext.Provider value={{ settings, setSettings, toggleDarkMode }}>
      {children}
    </SettingsContext.Provider>
  );
}

export function Settings() {
  const { settings, toggleDarkMode } = React.useContext(SettingsContext);

  return (
    <div className="settings-container">
      <nav className="settings-nav">
        <Link to="/" className="link">Home</Link>
        <Link to="/pricing" className="link">Pricing</Link>
      </nav>

      <h2 className="settings-heading">Insert configuration here</h2>
      <label className="settings-label">
        <input
          type="checkbox"
          checked={settings.darkMode}
          onChange={toggleDarkMode}
          className="settings-checkbox"
        />
        Dark Mode
      </label>
    </div>
  );
}

export default Settings;