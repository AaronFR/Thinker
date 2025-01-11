import React, { useContext } from 'react';

import { handleLogout } from '../../utils/loginUtils';
import AutoExpandingTextarea from '../../utils/AutoExpandingTextarea';
import TextSizeSlider from '../../utils/textSizeSlider';
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
        toggleDarkMode,
        togglesummarisation,
        toggleUserEncyclopedia,
        toggleEncyclopedia,
        toggleMultiFileProcessing,
        handleMessageChange
    } = useContext(SettingsContext);

    const uiOptions = [
        { label: "Dark Mode", value: settings.darkMode, onChange: toggleDarkMode },
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

    return (
      <div className="scrollable settings-container">
        <Navigation />

        <h2 className="settings-heading">User Interface</h2>
        {uiOptions.map(({ label, value, onChange }, index) => (
          <label key={index} className="settings-label">
            <input type="checkbox" checked={value} onChange={onChange} className="settings-checkbox" />
            {label}
          </label>
        ))}

        <TextSizeSlider />

        <h2 className="settings-heading">Functionality</h2>
        
        <h2>Prompt Questioning</h2>
        <label className="settings-label">
          <select
            className="settings-select"
            id="prompt-questioning-select"
            value={settings.questionUserPromptsEnabled} // current setting value
            onChange={(e) => changeSetting(
              'beta_features.question_user_prompts_enabled',
              e.target.value,
              'questionUserPromptsEnabled')} // update setting
          >
            <option value={FUNCTIONALITY_STATES.OFF}>Off</option>
            <option value={FUNCTIONALITY_STATES.ON}>On</option>
            <option value={FUNCTIONALITY_STATES.AUTO}>Auto</option>
          </select>
          Generates questions against the users prompt and reference material, giving suggestions for the user to think about their prompt in detail
        </label>
        <p>Use case: Difficult, 'knotty' technical questions where the extra details can help formulate solutions. Not so useful when you <em>just</em> want any answer from the AI</p>
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
          <select
            className="settings-select"
            id="prompt-augmenting-select"
            value={settings.augmentedPromptsEnabled} // current setting value
            onChange={(e) => changeSetting(
              'beta_features.augmented_prompts_enabled',
              e.target.value,
              'augmentedPromptsEnabled')} // update setting
          >
            <option value={FUNCTIONALITY_STATES.OFF}>Off</option>
            <option value={FUNCTIONALITY_STATES.ON}>On</option>
            <option value={FUNCTIONALITY_STATES.AUTO}>Auto</option>
          </select>
          Generates a copy of your prompt, re-written in line with 'prompt engineering' standards to produce better responses.
        </label>
        <small>And the shills told you it would be a career skill...</small>
        <p>Use case: simple, plain prompts that can nonetheless benefit from a <em>good</em> well-thought-out response</p>
        <div className='message-settings'>
          <AutoExpandingTextarea
            value={settings.promptAugmentationMessage}
            className='textarea'
            onChange={(e) => 
              handleMessageChange('promptAugmentationMessage', e.target.value
            )}
            style={{ opacity: 0.9 }}
          />
        </div>

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
            Coder Persona
            <AutoExpandingTextarea
              value={settings.coderPersonaMessage}
              className='textarea'
              onChange={(e) => handleMessageChange('coderPersonaMessage', e.target.value)}
              style={{ opacity: 0.9 }}
            />
          </label>
          <label className="message-label">
            Writer Persona
            <AutoExpandingTextarea
              value={settings.writerPersonaMessage}
              className='textarea'
              onChange={(e) => handleMessageChange('writerPersonaMessage', e.target.value)}
              style={{ opacity: 0.9 }}
            />
          </label>
          <label className="message-label">
            Categorisation
            <AutoExpandingTextarea
              value={settings.categorisationMessage}
              className='textarea'
              onChange={(e) => handleMessageChange('categorisationMessage', e.target.value)}
              style={{ opacity: 0.9 }}
            />
          </label>
          <label className="message-label">
            Best Of - Judgement Criteria
            <AutoExpandingTextarea
              value={settings.bestOfMessage}
              className='textarea'
              onChange={(e) => handleMessageChange('bestOfMessage', e.target.value)}
              style={{ opacity: 0.9 }}
            />
          </label>
        </div>

        <div className='center-contents'>
          <button onClick={handleLogout} className="centered logout-button">Logout</button>
        </div>
      </div>
    );
}

export default Settings;
