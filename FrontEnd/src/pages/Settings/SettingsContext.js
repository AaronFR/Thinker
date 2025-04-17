import React, { createContext, useState, useEffect, useRef, useCallback } from 'react';
import { apiFetch } from '../../utils/authUtils';
import { userConfigEndpoint } from '../../constants/endpoints';

/**
 * Provides context for managing and accessing application settings globally,
 * including font size, dark mode, and various feature toggles.
 */
export const SettingsContext = createContext();

/**
 * Fetches configuration settings from the server.
 *
 * :returns {Promise<Object|null>} Loaded configuration or null if fetch fails.
 */
export const fetchConfig = async () => {
    try {
        console.log("Fetching user config")
        const response = await apiFetch(userConfigEndpoint, {
            method: 'GET',
        });

        if (response.ok) {
            const loadedConfig = await response.json();
            const hasRequiredFields =
                loadedConfig.interface &&
                loadedConfig.system_messages;
                
            return hasRequiredFields ? loadedConfig : null;
        }

        console.error('Failed to load config');
        return null;
    } catch (error) {
        console.error('Error loading config:', error);
        return null;
    }
};

/**
 * Wraps the application components and provides settings-related state and functions.
 *
 * @param {object} props - The component props.
 * @param {React.ReactNode} props.children - React components that consume this context.
 */
export const SettingsProvider = ({ children, initialSettings }) => {
    const [settings, setSettings] = useState(initialSettings);

    const [fontSize, setFontSize] = useState(() => {
        const savedFontSize = localStorage.getItem('fontSize');
        return savedFontSize ? parseInt(savedFontSize, 10) : 16;
    });

    const typingTimer = useRef(null);
    const idleTime = 2000; // Time before processing user message changes

    /**
     * Saves a setting to the server.
     *
     * @param {string} field - The config field to update.
     * @param {any} value - The new value for the config field.
     */
    const saveConfig = async (field, value) => {
        try {
            const response = await apiFetch(userConfigEndpoint, {
                method: 'POST',
                body: JSON.stringify({ field, value }),
            });

            if (!response.ok) {
                throw new Error(`Server responded with status ${response.status}`);
            }
        } catch (error) {
            console.error('Error saving config:', error);
        }
    };

    // Load config from server on component mount
    useEffect(() => {
        const loadConfig = async () => {
            if (!initialSettings) {
                const loadedConfig = await fetchConfig();
                if (loadedConfig) {
                    setSettings((prevSettings) => ({
                        ...prevSettings,
                        loadedConfig
                    }));
                };
                loadConfig();
            } else {
                // If initialSettings is provided, we assume settings are already loaded.
                setSettings(initialSettings);
            }
        }
    }, []);

    /**
     * Toggles a boolean setting and saves the updated config to the server.
     *
     * @param {string} section - The section in the settings to update
     * @param {string} field - The field in this settings subsection to update.
     */
    const toggleSetting = useCallback((section, field) => {
        setSettings((prev) => {
          const newValue = !prev[section][field];
          saveConfig(section + '.' + field, newValue);
          return {
            ...prev,
            [section]: {
              ...prev[section],
              [field]: newValue,
            },
          };
        });
      }, [saveConfig]);
    const changeSetting = useCallback((section, field, value, settingKey) => {
        setSettings((prev) => {
            saveConfig(section + '.' + field, value);
            return {
            ...prev,
            [section]: {
                ...prev[section],
                [field]: value,
            },
            };
        });
    }, []);

    /**
     * Handles changes to message settings with debounce.
     *
     * @param {string} key - The key of the message to update.
     * @param {string} value - The new message value.
     */
    const handleMessageChange = useCallback((section, field, value) => {
        setSettings((prev) => ({
            ...prev,
            [section]: {
                ...prev[section],
                [field]: value,
            },
        }));
        if (typingTimer.current) {
            clearTimeout(typingTimer.current);
        }

        const configField = section + '.' + field;
        typingTimer.current = setTimeout(() => {
            saveConfig(configField, value);
        }, idleTime);
    }, []);

    // Apply Dark Mode to Document Body
    useEffect(() => {
        document.body.classList.toggle('dark-mode', settings?.interface?.dark_mode);
        return () => {
            document.body.classList.remove('dark-mode');
        };
    }, [settings?.interface?.dark_mode]);
    

    // Apply Font Size to Document
    useEffect(() => {
        document.documentElement.style.fontSize = `${fontSize}px`;
    }, [fontSize]);

    return (
        <SettingsContext.Provider
            value={{
                settings,
                changeSetting,
                toggleSetting,
                handleMessageChange,
                fontSize,
                setFontSize,
            }}
        >
            {children}
        </SettingsContext.Provider>
    );
};
