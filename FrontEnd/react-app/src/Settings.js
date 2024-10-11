import React, { createContext, useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Settings.css';

const flask_port= "http://localhost:5000"


export const SettingsContext = createContext();

// ToDo - cache in local memory for quicker loading
export function SettingsProvider({ children }) {
  const [settings, setSettings] = useState({
    darkMode: false,
    language: 'en',
  });

  useEffect(() => {
    // Load config from server using Flask API
    const loadConfig = async () => {
      try {
        console.log("trying to load config");
        const response = await fetch(flask_port + '/data/config', {
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
              // You can load other settings here as well
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

  // Function to handle toggling dark mode
  const toggleDarkMode = async () => {
    const newMode = !settings.darkMode;
    setSettings(prevSettings => ({
      ...prevSettings,
      darkMode: newMode,
    }));

    try {
      await fetch(flask_port + '/data/config', {
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

  // Apply dark mode to the document body
  useEffect(() => {
    if (settings.darkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  }, [settings.darkMode]);

  return (
    <SettingsContext.Provider value={{ settings, setSettings }}>
      {children}
    </SettingsContext.Provider>
  );
}

export function Settings() {
  const { settings, toggleDarkMode } = React.useContext(SettingsContext);

  return (
    <div>
      <nav>
        <Link to="/" className="link">Home</Link>
        <Link to="/pricing" className="link">Pricing</Link>
      </nav>

      <h2>Insert configuration here</h2>
      <label>
        <input
          type="checkbox"
          checked={settings.darkMode}
          onChange={toggleDarkMode}
        />
        Dark Mode
      </label>
    </div>
  );
}

export default Settings;