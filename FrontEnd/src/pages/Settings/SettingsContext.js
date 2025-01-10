import React, { createContext, useState, useEffect, useRef, useCallback } from 'react';
import { apiFetch } from '../../utils/authUtils';

/**
 * SettingsContext
 *
 * Provides context for managing and accessing application settings globally,
 * including font size, dark mode, and various feature toggles.
 */
export const SettingsContext = createContext();

/**
 * SettingsProvider Component
 *
 * Wraps the application components and provides settings-related state and functions.
 *
 * @param {object} props - The component props.
 * @param {React.ReactNode} props.children - React components that consume this context.
 */
export const SettingsProvider = ({ children }) => {
    const initialSettings = {
        darkMode: false,
        language: 'en',
        augmentedPromptsEnabled: "off",
        questionUserPromptsEnabled: "off",
        userEncyclopediaEnabled: false,
        summarisationEnabled: false,
        encyclopediaEnabled: false,
        multiFileProcessingEnabled: false,
        promptAugmentationMessage: 'Default prompt augmentation message...',
        promptQuestioningMessage: 'Default prompt questioning message...',
        coderPersonaMessage: 'Default coder persona message...',
        categorisationMessage: 'Default categorisation message...',
        summarisationMessage: 'Default summarisation message...'
    };

    const [settings, setSettings] = useState(initialSettings);

    const [fontSize, setFontSize] = useState(() => {
        const savedFontSize = localStorage.getItem('fontSize');
        return savedFontSize ? parseInt(savedFontSize, 10) : 16;
    });

    const typingTimer = useRef(null);
    const idleTime = 2000; // Time before processing user message changes

    const FLASK_PORT = process.env.REACT_APP_THE_THINKER_BACKEND_URL || 'http://localhost:5000';

    /**
     * Fetches configuration settings from the server.
     *
     * :returns {Promise<Object|null>} Loaded configuration or null if fetch fails.
     */
    const fetchConfig = async () => {
        try {
            const response = await apiFetch(`${FLASK_PORT}/data/config`, {
                method: 'GET',
            });
            if (response.ok) {
                const loadedConfig = await response.json();
                const hasRequiredFields =
                    loadedConfig.interface &&
                    loadedConfig.beta_features &&
                    loadedConfig.systemMessages;
                    
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
     * Saves a setting to the server.
     *
     * @param {string} field - The config field to update.
     * @param {any} value - The new value for the config field.
     */
    const saveConfig = async (field, value) => {
        try {
            const response = await apiFetch(`${FLASK_PORT}/data/config`, {
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
            const loadedConfig = await fetchConfig();
            if (loadedConfig) {
                setSettings((prevSettings) => ({
                    ...prevSettings,
                    darkMode: loadedConfig.interface.dark_mode ?? initialSettings.darkMode,
                    augmentedPromptsEnabled:
                        loadedConfig.beta_features.augmented_prompts_enabled ?? initialSettings.augmentedPromptsEnabled,
                    questionUserPromptsEnabled:
                        loadedConfig.beta_features.question_user_prompts_enabled ?? initialSettings.questionUserPromptsEnabled,
                    summarisationEnabled:
                        loadedConfig.optimization.summarise ?? initialSettings.summarisationEnabled,
                    userEncyclopediaEnabled:
                        loadedConfig.beta_features.user_context_enabled ?? initialSettings.userEncyclopediaEnabled,
                    encyclopediaEnabled:
                        loadedConfig.beta_features.encyclopedia_enabled ?? initialSettings.encyclopediaEnabled,
                    multiFileProcessingEnabled:
                        loadedConfig.beta_features.multi_file_processing_enabled ?? initialSettings.multiFileProcessingEnabled,
                    promptAugmentationMessage:
                        loadedConfig.systemMessages.promptAugmentationMessage || initialSettings.promptAugmentationMessage,
                    promptQuestioningMessage:
                        loadedConfig.systemMessages.promptQuestioningMessage || initialSettings.promptQuestioningMessage,
                    coderPersonaMessage:
                        loadedConfig.systemMessages.coderPersonaMessage || initialSettings.coderPersonaMessage,
                    categorisationMessage:
                        loadedConfig.systemMessages.categorisationMessage || initialSettings.categorisationMessage,
                    summarisationMessage:
                        loadedConfig.systemMessages.summarisationMessage || initialSettings.summarisationMessage,
                }));
            }
        };
        loadConfig();
    }, [FLASK_PORT]);

    /**
     * Toggles a boolean setting and saves the updated config to the server.
     *
     * @param {string} field - The config field to update.
     * @param {string} key - The key in the settings state to toggle.
     */
    const toggleSetting = useCallback((field, key) => {
        setSettings((prev) => {
            const newValue = !prev[key];
            saveConfig(field, newValue);
            return { ...prev, [key]: newValue };
        });
    }, []);
    const changeSetting = useCallback((field, value, settingKey) => {
        setSettings((prev) => {
            saveConfig(field, value);
            return { ...prev, [settingKey]: value };
        });
    }, []);

    /**
     * Handles changes to message settings with debounce.
     *
     * @param {string} key - The key of the message to update.
     * @param {string} value - The new message value.
     */
    const handleMessageChange = useCallback((key, value) => {
        setSettings((prev) => ({ ...prev, [key]: value }));
        if (typingTimer.current) {
            clearTimeout(typingTimer.current);
        }

        const configField = `systemMessages.${key}`;
        typingTimer.current = setTimeout(() => {
            saveConfig(configField, value);
        }, idleTime);
    }, []);

    // Apply Dark Mode to Document Body
    useEffect(() => {
        document.body.classList.toggle('dark-mode', settings.darkMode);
    }, [settings.darkMode]);

    // Apply Font Size to Document
    useEffect(() => {
        document.documentElement.style.fontSize = `${fontSize}px`;
    }, [fontSize]);

    return (
        <SettingsContext.Provider
            value={{
                settings,
                changeSetting,
                toggleDarkMode: () =>
                    toggleSetting('interface.dark_mode', 'darkMode'),
                togglesummarisation: () =>
                    toggleSetting(
                        'optimization.summarise',
                        'summarisationEnabled'
                    ),
                toggleUserEncyclopedia: () =>
                    toggleSetting(
                        'beta_features.user_context_enabled',
                        'userEncyclopediaEnabled'
                    ),
                toggleEncyclopedia: () =>
                    toggleSetting(
                        'beta_features.encyclopedia_enabled',
                        'encyclopediaEnabled'
                    ),
                toggleMultiFileProcessing: () =>
                    toggleSetting(
                        'beta_features.multi_file_processing_enabled',
                        'multiFileProcessingEnabled'
                    ),
                handleMessageChange,
                fontSize,
                setFontSize,
            }}
        >
            {children}
        </SettingsContext.Provider>
    );
};
