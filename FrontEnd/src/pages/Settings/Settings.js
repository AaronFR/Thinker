import React, { useState, useContext, useEffect, useCallback, useMemo } from 'react';

import { handleLogout } from '../../utils/loginUtils';
import { formatPrice } from '../../utils/numberUtils';
import AutoExpandingTextarea from '../../utils/AutoExpandingTextarea';
import TextSizeSlider from '../../utils/textSizeSlider';
import Navigation from '../../components/Navigation';
import ExpandableElement from '../../utils/expandableElement';
import { apiFetch } from '../../utils/authUtils';
import TooltipConstants from '../../constants/tooltips';

import './Settings.css';

import { SettingsContext } from './SettingsContext';

import ModelSelector from '../../components/Selectors/ModelSelector';
import { Tooltip } from 'react-tooltip';
import { userInfoEndpoint } from '../../constants/endpoints';


const FUNCTIONALITY_STATES = {
  OFF: 'off',
  ON: 'on',
  AUTO: 'auto',
};

/* Sections 
 * ToDo: Add config checks to leave sections open if they user left them open
 */

/**
 *
 * Renders User Interface related settings.
 */
const UserInterfaceSettings = React.memo(({ settings, toggleDarkMode, toggleAiColourisation, changeSetting }) => {
  const sectionHeading = useMemo(() => (<h2 className="settings-heading">User Interface</h2>), []);

  const maxContent = (
    <div>
      {sectionHeading}
      <label className="settings-label">
        <input
          type="checkbox"
          checked={settings?.interface?.dark_mode}
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
          checked={settings?.interface?.ai_colour}
          onChange={toggleAiColourisation}
          className="settings-checkbox"
        />
        New Category Colourisation via LLM Prompt
      </label>
      <label className="settings-label">
      <select
        className="settings-select"
        value={settings?.interface?.display_category_description}
        onChange={(e) =>
          changeSetting(
            'interface',
            'display_category_description',
             e.target.value,
          )
        }
      >
        <option value={"always"}>Always</option>
        <option value={"when selected"}>When selected</option>
        <option value={"never"}>never</option>
      </select>
      Display category description
    </label>


      <TextSizeSlider />
    </div>
  );

  return (
    <ExpandableElement
      minContent={sectionHeading}
      maxContent={maxContent}
      initiallyExpanded={false}
      toggleButtonLabel=""
    />
  );
});

/**
 * Renders settings related to AI model utilisation.
 */
const AiModelSettings = React.memo(({ settings, handleForegroundModelChange, handleBackgroundModelChange }) => {
  const sectionHeading = useMemo(() => (<h2 className="settings-heading">AI Models</h2>), []);
  
  const maxContent = (
    <div>
      {sectionHeading}
      <h3>Foreground Model Default</h3>
      <p>This will specify the foreground model to be selected by default, each step in each workflow will run on the selected model</p>
      <ModelSelector
        selectedModel={settings?.models?.default_foreground_model || ''}
        setTags={handleForegroundModelChange}
      />
      <h3>Background Model</h3>
      <p>
        In The Thinker many programs actually run in the background to try and improve the main 'foreground' prompt and the user experience overall, for this
        purpose you want a functional, economical and to the point LLM.
      </p>
      <ModelSelector
        selectedModel={settings?.models.default_background_model || ''}
        setTags={handleBackgroundModelChange}
        economicalMode={true}
      />
    </div>
  );

  return (
    <ExpandableElement
      minContent={sectionHeading}
      maxContent={maxContent}
      initiallyExpanded={true}
      toggleButtonLabel=""
    />
  );
});

/**
 * Renders Functionality related settings.
 */
const FunctionalitySettings = React.memo(({
  settings,
  changeSetting,
  handleMessageChange,
  userInfo,
  toggleUserEncyclopedia
}) => {
  const sectionHeading = useMemo(() => (<h2 className="settings-heading">Functionality</h2>), []);
  
  const maxContent = (
    <div>
      {sectionHeading}
      <div className='settings-subsection'>
        <div className='side-by-side'>
          <h3>Auto select persona</h3>
          <p>{formatPrice(parseFloat(userInfo?.select_persona_cost))}</p>
        </div>
        <div className='side-by-side'>
          <h3>Auto select worfklows</h3>
          <p>{formatPrice(parseFloat(userInfo?.select_workflow_cost))}</p>
        </div>
        
      </div>
     
      <AutoPromptEngineeringSection
        currentValue={settings?.beta_features?.augmented_prompts_enabled}
        changeSetting={changeSetting}
        promptMessage={settings?.system_messages?.prompt_augmentation_message}
        handleMessageChange={handleMessageChange}
        cost={userInfo?.augmentation_cost}
      />
      <PromptQuestioningSection
        currentValue={settings?.beta_features?.question_user_prompts_enabled}
        changeSetting={changeSetting}
        promptMessage={settings?.system_messages?.prompt_questioning_message}
        handleMessageChange={handleMessageChange}
        cost={userInfo?.questioning_cost}
      />
      <InternetSearchSection 
        currentValue={settings?.features?.internet_search_enabled}
        changeSetting={changeSetting}
        cost={userInfo?.internet_search_cost}
      />
      <UserContextSection
        userContextEnabled={settings?.beta_features?.user_context_enabled}
        toggleUserEncyclopedia={toggleUserEncyclopedia}
        cost={userInfo?.user_context_cost}
      />
      <BestOfSection 
        currentValue={settings?.features?.multiple_reruns_enabled}
        promptMessage={settings?.system_messages?.best_of_message}
        changeSetting={changeSetting}
        handleMessageChange={handleMessageChange}
        cost={userInfo?.best_of_cost}
      />
    </div>
  );

  return (
    <ExpandableElement
      minContent={sectionHeading}
      maxContent={maxContent}
      initiallyExpanded={false}
      toggleButtonLabel=""
    />
  );
});

/**
 * Renders Workflows related settings.
 */
const WorkflowsSettings = React.memo(({
  settings,
  toggleWritePagesInParallel,
  toggleSummarisation,
  summarise_workflows_cost,
  handleMessageChange,
}) => {
  const sectionHeading = useMemo(() => (<h2 className="settings-heading">Workflows</h2>), []);
  
  const maxContent = (
    <div>
      {sectionHeading}
      <div className='settings-subsection'>
        <label className="settings-label">
          <input
            type="checkbox"
            className="settings-checkbox"
            checked={settings?.workflows?.write_pages_in_parallel}
            onChange={toggleWritePagesInParallel}
          />
          Write Pages in Parallel
        </label>
        
        <p>Write each page at once rather than in sequence - faster but means pages can't refer to prior content</p>
        <p>If enabled it can't reference what it did in 'prior' pages - this will make it cheaper to run however</p>
      </div>

      <div className='settings-subsection'>
        <div className='side-by-side'>
          <label className="settings-label">
          <input
            type="checkbox"
            className="settings-checkbox"
            id="summarise-checkbox"
            checked={settings?.workflows?.summarise}
            onChange={toggleSummarisation}
          />
          Enables summaries on compatible workflows
        </label>
        <h4>{formatPrice(parseFloat(summarise_workflows_cost))}</h4>
        </div>
        
        <div
          data-tooltip-id="tooltip"
          data-tooltip-content={TooltipConstants.summarisationSystemMessage}
          data-tooltip-place="bottom"
        >
          <AutoExpandingTextarea
            value={settings?.system_messages?.summarisation_message}
            className="textarea"
            onChange={(e) =>
              handleMessageChange('system_messages', 'summarisation_message', e.target.value)
            }
            style={{ opacity: 0.9 }}
          />
        </div>
      </div>
      
    </div>
  );

  return (
    <ExpandableElement
      minContent={sectionHeading}
      maxContent={maxContent}
      initiallyExpanded={false}
      toggleButtonLabel=""
    />
  );
});

/**
 * Renders Messages and Files related settings.
 */
const FilesSettings = React.memo(({
  settings,
  toggleFileSummarisation,
  toggleBulkUploadCategorisation,
  handleMessageChange,
  summarise_files_cost,
}) => {
  const sectionHeading = useMemo(() => (<h2 className="settings-heading">Messages & Files</h2>), []);
  
  const maxContent = (
    <div>
      {sectionHeading}

      <div className='settings-subsection'>
        <div className='side-by-side'>
          <label className="settings-label">
            <input
              type="checkbox"
              className="settings-checkbox"
              id="summarise-checkbox"
              checked={settings?.files?.summarise_files}
              onChange={toggleFileSummarisation}
            />
            Add a summary to new files after they've been created
          </label>
          <h4>{formatPrice(parseFloat(summarise_files_cost))}</h4>
        </div>
        
        <div
          data-tooltip-id="tooltip"
          data-tooltip-content={TooltipConstants.summarisationSystemMessage}
          data-tooltip-place="bottom"
        >
          <AutoExpandingTextarea
            value={settings?.system_messages?.file_summarisation_message}
            className="textarea"
            onChange={(e) =>
              handleMessageChange('system_messages', 'file_summarisation_message', e.target.value)
            }
            style={{ opacity: 0.9 }}
          />
        </div>
      </div>

      <div className='settings-subsection'>
        <label className="settings-label">
          <input
            type="checkbox"
            className="settings-checkbox"
            id="summarise-checkbox"
            checked={settings?.files?.bulk_upload_categorisation}
            onChange={toggleBulkUploadCategorisation}
          />
          Bulk file upload categorisation
        </label>
        <p>If you upload multiple files they will be categorised together</p>
      </div>
    </div>
  );

  return (
    <ExpandableElement
      minContent={sectionHeading}
      maxContent={maxContent}
      initiallyExpanded={false}
      toggleButtonLabel=""
    />
  );
});

/**
 * Renders System Messages related settings without using the MessageSettings component.
 */
const SystemMessagesSettings = React.memo(({ settings, handleMessageChange }) => {
  const sectionHeading = useMemo(() => (<h2 className="settings-heading">System Messages</h2>), []);

  const maxContent = (
    <div>
      {sectionHeading}

      <p>Bear in mind, LLMs pay particular attention to the first or last instructions</p>
      
      <div className="message-settings">
        <label className="message-label">
          Coder Persona Message
          <AutoExpandingTextarea
            value={settings?.system_messages?.coder_persona_message}
            className="textarea"
            onChange={(e) =>
              handleMessageChange('system_messages', 'coder_persona_message', e.target.value)
            }
            style={{ opacity: 0.9 }}
          />
        </label>
        <label className="message-label">
          Writer Persona Message
          <AutoExpandingTextarea
            value={settings?.system_messages?.writer_persona_message}
            className="textarea"
            onChange={(e) =>
              handleMessageChange('system_messages', 'writer_persona_message', e.target.value)
            }
            style={{ opacity: 0.9 }}
          />
        </label>
        <label className="message-label">
          Categorisation Message
          <div
            data-tooltip-id="tooltip"
            data-tooltip-content={TooltipConstants.categorisationSystemMessage}
            data-tooltip-place="bottom"
          >
            <AutoExpandingTextarea
              value={settings?.system_messages?.categorisation_message}
              className="textarea"
              onChange={(e) =>
                handleMessageChange('system_messages', 'categorisation_message', e.target.value)
              }
              style={{ opacity: 0.9 }}
            />
          </div>
        </label>
      </div>
    </div>
  );

  return (
    <ExpandableElement
      minContent={sectionHeading}
      maxContent={maxContent}
      initiallyExpanded={false}
      toggleButtonLabel=""
    />
  );
});

/**
 * Renders Beta Features related settings.
 */
const BetaFeaturesSettings = React.memo(({
  settings,
  toggleDebug,
  toggleMultiFileProcessing,
}) => {
  const sectionHeading = useMemo(() => (<h2 className="settings-heading">🚧 Beta Features</h2>), []);

  const maxContent = (
    <div>
      <h2 className="settings-heading">🚧 Beta Features</h2>
      <label className="settings-label" style={{ paddingBottom: '30px' }}>
        <input
          type="checkbox"
          className="settings-checkbox"
          id="debug-checkbox"
          checked={settings?.interface?.debug}
          onChange={toggleDebug}
        />
        Enable debug view (Directly view prompt tags)
      </label>
      <label className="settings-label">
        <input
          type="checkbox"
          checked={settings?.beta_features?.multi_file_processing_enabled}
          onChange={toggleMultiFileProcessing}
          className="settings-checkbox"
        />
        Multi file processing - personas can operate on multiple files at once (unstable)
      </label>
    </div>
  );

  return (
    <ExpandableElement
      minContent={sectionHeading}
      maxContent={maxContent}
      initiallyExpanded={false}
      toggleButtonLabel=""
    />
  );
});

/**
 * PromptQuestioningSection Component
 *
 * Renders settings for Prompt Questioning.
 */
const PromptQuestioningSection = React.memo(({
  currentValue,
  changeSetting,
  promptMessage,
  handleMessageChange,
  cost,
}) => (
  <div className='settings-subsection'>
    <div className='side-by-side'>
      <h3>Prompt Questioning</h3>
      <h4>{formatPrice(parseFloat(cost))}</h4>
    </div>

    <label className="settings-label">
      <select
        className="settings-select"
        value={currentValue}
        onChange={(e) =>
          changeSetting(
            'beta_features', 'question_user_prompts_enabled',
            e.target.value,
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
          handleMessageChange('system_messages', 'prompt_questioning_message', e.target.value)
        }
        style={{ opacity: 0.9 }}
      />
    </div>
  </div>
));

/**
 * Renders settings for Auto Prompt Engineering.
 */
const AutoPromptEngineeringSection = React.memo(({
  currentValue,
  changeSetting,
  promptMessage,
  handleMessageChange,
  cost
}) => (
  <div className='settings-subsection'>
    <div className='side-by-side'>
      <h3>Prompt Improvement</h3>
      <h4>{formatPrice(parseFloat(cost))}</h4>
    </div>
    
    <label className="settings-label">
      <select
        className="settings-select"
        value={currentValue}
        onChange={(e) =>
          changeSetting(
            'beta_features',
            'augmented_prompts_enabled',
            e.target.value,
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
          handleMessageChange('system_messages', 'prompt_augmentation_message', e.target.value)
        }
        style={{ opacity: 0.9 }}
      />
    </div>
    <small>And the shills told you it would be a career skill...</small>
  </div>
));

/**
 * Renders settings for 'Best of' multiple reruns functionality.
 */
const BestOfSection = React.memo(({
  currentValue,
  changeSetting,
  promptMessage,
  handleMessageChange,
  cost
}) => (
  <div className='settings-subsection'>
    <div className='side-by-side'>
      <h3>Best of multiple runs</h3>
      <h4>{formatPrice(parseFloat(cost))}</h4>
    </div>
    <label className="settings-label">
      <select
        className="settings-select"
        value={currentValue}
        onChange={(e) =>
          changeSetting(
            'features',
            'multiple_reruns_enabled',
            e.target.value,
          )
        }
      >
        <option value={FUNCTIONALITY_STATES.OFF}>Off</option>
        <option value={FUNCTIONALITY_STATES.ON}>On</option>
      </select>
      For a given step runs multiple prompts in parallel, running an additional call to select for the best response.
    </label>
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
          handleMessageChange('system_messages', 'best_of_message', e.target.value)
        }
        style={{ opacity: 0.9 }}
      />
    </div>
  </div>
));

/**
 * Contains the settings and rules for internet search functionality
 * 
 * ToDo: system message for search after full implementation
 */
const InternetSearchSection = React.memo(({
  currentValue,
  changeSetting,
  cost
}) => (
  <div className='settings-subsection'>
    <div className='side-by-side'>
      <h3>Internet Search</h3>
      <h4
        data-tooltip-id="tooltip"
        data-tooltip-content={TooltipConstants.internetSearchCosting}
        data-tooltip-place="bottom"
      >
        {formatPrice(parseFloat(cost))}
      </h4>
    </div>
    
    <label className="settings-label">
      <select
        className="settings-select"
        value={currentValue}
        onChange={(e) =>
          changeSetting(
            'features',
            'internet_search_enabled',
            e.target.value,
          )
        }
      >
        <option value={FUNCTIONALITY_STATES.OFF}>Off</option>
        <option value={FUNCTIONALITY_STATES.ON}>On</option>
      </select>
      Searches the internet for related information
    </label>
    <p>📰 Allows the AI to access information it didn't know. E.g. read the news</p>
    <p>👍 Additional context can improve the response and mitigate hallucinations</p>
    <p>⏰ Increases duration of requests (2x)</p>
  </div>
));

/**
 * Contains the settings and rules for User Context functionality
 */
const UserContextSection = React.memo(({
  userContextEnabled,
  toggleUserEncyclopedia,
  cost
}) => (
  <div className='settings-subsection'>
    <div className='side-by-side'>
      <h3>User Context</h3>
      <h4
        data-tooltip-id="tooltip"
        data-tooltip-content={TooltipConstants.userContextCosting}
        data-tooltip-place="bottom"
      >
        {formatPrice(parseFloat(cost))}
      </h4>
    </div>
    
    <label className="settings-label">
      <input
        type="checkbox"
        checked={userContextEnabled}
        onChange={toggleUserEncyclopedia}
        className="settings-checkbox"
      />
      Store and retrieve details about the user and their preferences
    </label>
    <p>📝 Remembers user facts and preferences</p>
    <p>🤔 Not always reliable</p>
    <p>⏰ Increases duration of requests (2.1x)</p>
  </div>
));

/* Settings Page */

/**
 * Main component that aggregates all settings sections.
 */
export function Settings() {
  const [parameters, setParameters] = useState(['email', 'augmentation_cost', 'select_persona_cost', 'select_workflow_cost', 'questioning_cost', 'best_of_cost', 'internet_search_cost', 'summarise_workflows_cost', 'summarise_files_cost', 'user_context_cost']);
  const [userInfo, setUserInfo] = useState(null);
  const [error, setError] = useState(null);

  const {
    settings,
    changeSetting,
    toggleSetting,
    handleMessageChange,
  } = useContext(SettingsContext);

  // Memoize toggle functions to prevent re-creation on every render.
  const toggleDebug = useCallback(() => toggleSetting('interface', 'debug'), [toggleSetting]);
  const toggleDarkMode = useCallback(() => toggleSetting('interface', 'dark_mode'), [toggleSetting]);
  const toggleAiColourisation = useCallback(() => toggleSetting('interface', 'ai_colour'), [toggleSetting]);
  const toggleWritePagesInParallel = useCallback(() => toggleSetting('workflows', 'write_pages_in_parallel'), [toggleSetting]);
  const toggleSummarisation = useCallback(() => toggleSetting('workflows', 'summarise'), [toggleSetting]);
  const toggleFileSummarisation = useCallback(() => toggleSetting('files', 'summarise_files'), [toggleSetting]);
  const toggleBulkUploadCategorisation = useCallback(() => toggleSetting('files', 'bulk_upload_categorisation'), [toggleSetting]);
  const toggleUserEncyclopedia = useCallback(() => toggleSetting('beta_features', 'user_context_enabled'), [toggleSetting]);
  const toggleMultiFileProcessing = useCallback(() => toggleSetting('beta_features', 'multi_file_processing_enabled'), [toggleSetting]);

  // Use AbortController to cancel unfinished fetch if component unmounts.
  const fetchUserInformation = useCallback(() => {
    setError(null);
    setUserInfo(null);
    const controller = new AbortController();
    const signal = controller.signal;

    // Filter out empty parameters
    const filteredParameters = parameters.filter(param => param.trim() !== '');
    if (filteredParameters.length === 0) {
      throw new Error('Please specify at least one parameter.');
    }

    apiFetch(userInfoEndpoint, {
      method: 'POST',
      body: JSON.stringify({ parameters: filteredParameters }),
      signal,
    })
      .then(response => {
        if (!response.ok) {
          return response.json().then(errorData => {
            throw new Error(errorData.error || 'Failed to fetch user information.');
          });
        }
        return response.json();
      })
      .then(data => {
        setUserInfo(data.user_data);
      })
      .catch(err => {
        if (err.name !== 'AbortError') {
          console.error('Error fetching user information:', err);
          setError(err.message || 'Unable to load user information. Please try again.');
        }
      });

    return () => {
      controller.abort();
    };
  }, [parameters]);

  useEffect(() => {
    // Call fetchUserInformation and perform cleanup on unmount
    const abortFetch = fetchUserInformation();
    return abortFetch;
  }, [fetchUserInformation]);

  const handleForegroundModelChange = useCallback((selectedModelValue) => {
    changeSetting('models', 'default_foreground_model', selectedModelValue);
  }, [changeSetting]);

  const handleBackgroundModelChange = useCallback((selectedModelValue) => {
    changeSetting('models', 'default_background_model', selectedModelValue);
  }, [changeSetting]);

  return (
    <div className="scrollable settings-container">
      <Navigation />
      {error && <p>{error}</p>}
      <small>{userInfo?.email}</small>
      
      <UserInterfaceSettings
        settings={settings}
        toggleDarkMode={toggleDarkMode}
        toggleAiColourisation={toggleAiColourisation}
        changeSetting={changeSetting}
      />

      <AiModelSettings
        settings={settings}
        handleForegroundModelChange={handleForegroundModelChange}
        handleBackgroundModelChange={handleBackgroundModelChange}
      />

      <FunctionalitySettings
        settings={settings}
        changeSetting={changeSetting}
        handleMessageChange={handleMessageChange}
        userInfo={userInfo}
        toggleUserEncyclopedia={toggleUserEncyclopedia}
      />

      <WorkflowsSettings
        settings={settings}
        toggleWritePagesInParallel={toggleWritePagesInParallel}
        toggleSummarisation={toggleSummarisation}
        summarise_workflows_cost={userInfo?.summarise_workflows_cost}
        handleMessageChange={handleMessageChange}
      />

      <FilesSettings
        settings={settings}
        toggleFileSummarisation={toggleFileSummarisation}
        toggleBulkUploadCategorisation={toggleBulkUploadCategorisation}
        handleMessageChange={handleMessageChange}
        summarise_files_cost={userInfo?.summarise_files_cost}
      />

      <SystemMessagesSettings
        settings={settings}
        handleMessageChange={handleMessageChange}
      />

      <BetaFeaturesSettings
        settings={settings}
        toggleDebug={toggleDebug}
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
