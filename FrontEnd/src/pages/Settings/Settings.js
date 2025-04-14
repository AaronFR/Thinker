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
          checked={settings?.category?.ai_colour}
          onChange={toggleAiColourisation}
          className="settings-checkbox"
        />
        New Category Colourisation via LLM Prompt
      </label>
      
      
      <label className="settings-label">
        <select
          className="settings-select"
          value={settings?.category?.display}
          onChange={(e) =>
            changeSetting(
              'category',
              'display',
              e.target.value,
            )
          }
        >
          <option value={'latest'}>Latest</option>
          <option value={'alphabetically'}>Alphabetically</option>
        </select>
        Choose how Categories are displayed
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
    <div className='message-settings'>
      {sectionHeading}

      <div className='settings-subsection'>
        <div className='side-by-side'>
          <h3>Auto categorisation</h3>
          <p>{formatPrice(parseFloat(userInfo?.select_category_cost))}</p>
        </div>
        <label className="settings-label">
          <select
            className="settings-select"
            value={settings?.features?.automatically_select_category}
            onChange={(e) =>
              changeSetting(
                'features',
                'automatically_select_category',
                e.target.value,
              )
            }
          >
            <option value={'always'}>Always</option>
            <option value={'once'}>Once</option>
          </select>
          Automatically select a Category (folder) to store the promp/files in
        </label>
        <label className="message-label">
          Categorisation Instructions
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


        <div className='side-by-side'>
          <h3>Auto select persona</h3>
          <p>{formatPrice(parseFloat(userInfo?.select_persona_cost))}</p>
        </div>
        <label className="settings-label">
          <select
            className="settings-select"
            value={settings?.features?.automatically_select_persona}
            onChange={(e) =>
              changeSetting(
                'features',
                'automatically_select_persona',
                e.target.value,
              )
            }
          >
            <option value={'always'}>Always</option>
            <option value={'once'}>Once</option>
          </select>
          Automatically select a Persona (speciality) based on your prompt
        </label>
        <label className="message-label">
          Persona Selection Instructions
          <div
            data-tooltip-id="tooltip"
            data-tooltip-content={TooltipConstants.personaSelectionSystemMessage}
            data-tooltip-place="bottom"
          >
            <AutoExpandingTextarea
              value={settings?.system_messages?.persona_selection_message}
              className="textarea"
              onChange={(e) =>
                handleMessageChange('system_messages', 'persona_selection_message', e.target.value)
              }
              style={{ opacity: 0.9 }}
            />
          </div>
        </label>
        

        <div className='side-by-side'>
          <h3>Auto select worfklows</h3>
          <p>{formatPrice(parseFloat(userInfo?.select_workflow_cost))}</p>
        </div>
        <label className="settings-label">
          <select
            className="settings-select"
            value={settings?.features?.automatically_select_workflow}
            onChange={(e) =>
              changeSetting(
                'features',
                'automatically_select_workflow',
                e.target.value,
              )
            }
          >
            <option value={'always'}>Always</option>
            <option value={'once'}>Once</option>
          </select>
          Automatically select a Workflow for deciding how to process this prompt
        </label>
        <label className="message-label">
          Workflow Selection Instructions
          <div
            data-tooltip-id="tooltip"
            data-tooltip-content={TooltipConstants.workflowSelectionSystemMessaeg}
            data-tooltip-place="bottom"
          >
            <AutoExpandingTextarea
              value={settings?.system_messages?.workflow_selection_message}
              className="textarea"
              onChange={(e) =>
                handleMessageChange('system_messages', 'workflow_selection_message', e.target.value)
              }
              style={{ opacity: 0.9 }}
            />
          </div>
        </label>
        
      </div>
     
      <AutoPromptEngineeringSection
        currentValue={settings?.prompt_improvement?.augmented_prompts_enabled}
        changeSetting={changeSetting}
        promptMessage={settings?.system_messages?.prompt_augmentation_message}
        handleMessageChange={handleMessageChange}
        cost={userInfo?.augmentation_cost}
      />
      <PromptQuestioningSection
        currentValue={settings?.prompt_improvement?.question_user_prompts_enabled}
        changeSetting={changeSetting}
        promptMessage={settings?.system_messages?.prompt_questioning_message}
        handleMessageChange={handleMessageChange}
        cost={userInfo?.questioning_cost}
      />
      <InternetSearchSection 
        currentValue={settings?.response_improvement?.internet_search_enabled}
        changeSetting={changeSetting}
        promptMessage={settings?.system_messages?.internet_search_instructions}
        handleMessageChange={handleMessageChange}
        cost={userInfo?.internet_search_cost}
      />
      <UserContextSection
        userContextEnabled={settings?.response_improvement?.user_context_enabled}
        toggleUserEncyclopedia={toggleUserEncyclopedia}
        cost={userInfo?.user_context_cost}
      />
      <BestOfSection 
        currentValue={settings?.response_improvement?.multiple_reruns_enabled}
        promptMessage={settings?.system_messages?.best_of_message}
        changeSetting={changeSetting}
        handleMessageChange={handleMessageChange}
        cost={userInfo?.best_of_cost}
      />
      <LoopsSection
        currentValue={settings?.response_improvement?.loops_enabled}
        promptMessage={settings?.system_messages?.best_of_message}
        changeSetting={changeSetting}
        handleMessageChange={handleMessageChange}
        cost={userInfo?.loops_cost}
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
    <div className='message-settings'>
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
        
        <p>⏰ Faster, pages can be written in batches, almost simutaneously</p>
        <p>⛔ Can't reference prior pages, not good when <i>coherency</i> is important</p>
        <p>💲 This reduction in input does however reduce costs, roughly halving cost when creating a document with many pages</p>
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
  toggleUseTagsCategory,
  toggleCategorySystemMessages,
  toggleGenerateCategorySystemMessages,
  changeSetting,
  handleMessageChange,
  summarise_files_cost,
}) => {
  const sectionHeading = useMemo(() => (<h2 className="settings-heading">Messages & Files</h2>), []);
  
  const maxContent = (
    <div>
      {sectionHeading}

      <div className='settings-subsection message-settings'>
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
            id="useTags-checkbox"
            checked={settings?.files?.use_tags_category}
            onChange={toggleUseTagsCategory}
          />
          Use Tags category for File Upload
        </label>
        <p>Uses the category specified in the tags, if there is any. Removing the need for an AI call to categorise uploads. Faster.</p>
      </div>

      <div className='settings-subsection'>
        <label className="settings-label">
          <input
            type="checkbox"
            className="settings-checkbox"
            id="bulkFileUpload-checkbox"
            checked={settings?.files?.bulk_upload_categorisation}
            onChange={toggleBulkUploadCategorisation}
          />
          Bulk file upload categorisation
        </label>
        <p>If you upload multiple files they will be categorised together</p>
      </div>

      <div className='settings-subsection'>
        <label className="settings-label">
          <input
            type="checkbox"
            className="settings-checkbox"
            id="categorySystemMessages-checkbox"
            checked={settings?.category?.category_system_message}
            onChange={toggleCategorySystemMessages}
          />
          Use Category Instructions
        </label>

        <p>Responses created for this category will follow specific instructions for that category</p>

        <label className="settings-label">
          <div
            data-tooltip-id="tooltip"
            data-tooltip-content={TooltipConstants.generateCategorySystemMessagesToggle}
            data-tooltip-place="bottom"
          >
            <input
              type="checkbox"
              className="settings-checkbox"
              id="generateCategorySystemMessages-checkbox"
              checked={settings?.category?.generate_category_system_message}
              onChange={toggleGenerateCategorySystemMessages}
            />
            Automatically Generate Category Instructions - For new Categories
          </div>
          
        </label>
        <label className="settings-label">
          <select
            className="settings-select"
            value={settings?.interface?.display_category_instructions}
            onChange={(e) =>
              changeSetting(
                'interface',
                'display_category_instructions',
                e.target.value,
              )
            }
          >
            <option value={"always"}>Always</option>
            <option value={"when selected"}>When selected</option>
            <option value={"never"}>Never</option>
          </select>
          Display category instructions
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
 * Renders Persona System Messages related settings without using the MessageSettings component.
 */
const SystemMessagesSettings = React.memo(({ settings, handleMessageChange }) => {
  const sectionHeading = useMemo(() => (<h2 className="settings-heading">Personas</h2>), []);

  const maxContent = (
    <div>
      {sectionHeading}

      <p>Bear in mind, LLMs pay particular attention to the first or last instructions</p>
      
      <div className="message-settings">
        <label className="message-label">
          Coder Instructions
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
          Writer Instructions
          <AutoExpandingTextarea
            value={settings?.system_messages?.writer_persona_message}
            className="textarea"
            onChange={(e) =>
              handleMessageChange('system_messages', 'writer_persona_message', e.target.value)
            }
            style={{ opacity: 0.9 }}
          />
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
          checked={settings?.files?.multi_file_processing_enabled}
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
            'prompt_improvement',
            'question_user_prompts_enabled',
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
    <p>👍 Difficult, technical problems, where extra context can help clarify the issues - for the machine and potentially for <i>you</i>.</p>
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
            'prompt_improvement',
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
    <p>⚙ Creating more comprehensive, considered and detailed responses</p>
    <p>🦥 Expanding on simple, quick prompts</p>
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
            'response_improvement',
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
    <p>💲 Expensive. 5 runs would cost roughly 6x a regular prompt</p>
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
 * Renders settings for 'Looping' responses sequentially.
 */
const LoopsSection = React.memo(({
  currentValue,
  changeSetting,
  promptMessage,
  handleMessageChange,
  cost
}) => (
  <div className='settings-subsection'>
    <div className='side-by-side'>
      <h3>Looping over responses</h3>
      <h4
        data-tooltip-id="tooltip"
        data-tooltip-content={TooltipConstants.loopsCosting}
        data-tooltip-place="bottom-start"
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
            'response_improvement',
            'loops_enabled',
            e.target.value,
          )
        }
      >
        <option value={FUNCTIONALITY_STATES.OFF}>Off</option>
        <option value={FUNCTIONALITY_STATES.ON}>On</option>
      </select>
      For a given step runs multiple prompts in sequence, reviewing and improving the response against the user's initial prompt.
    </label>
    <p>👍 Optimising responses</p>
    <p>💲⏰ Increases time and cost proportional to number of re-runs</p>
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
  promptMessage,
  handleMessageChange,
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
            'response_improvement',
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
    <div
      data-tooltip-id="tooltip"
      data-tooltip-content={TooltipConstants.internetSearchInstructions}
      data-tooltip-place="bottom"
    >
      <AutoExpandingTextarea
        value={promptMessage}
        className="textarea"
        onChange={(e) =>
          handleMessageChange('system_messages', 'internet_search_instructions', e.target.value)
        }
        style={{ opacity: 0.9 }}
      />
    </div>
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
  const [parameters, setParameters] = useState(['email', 'augmentation_cost', 'select_category_cost', 'select_persona_cost', 'select_workflow_cost', 'questioning_cost', 'best_of_cost', 'loops_cost', 'internet_search_cost', 'summarise_workflows_cost', 'summarise_files_cost', 'user_context_cost']);
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
  const toggleAiColourisation = useCallback(() => toggleSetting('category', 'ai_colour'), [toggleSetting]);
  const toggleWritePagesInParallel = useCallback(() => toggleSetting('workflows', 'write_pages_in_parallel'), [toggleSetting]);
  const toggleSummarisation = useCallback(() => toggleSetting('workflows', 'summarise'), [toggleSetting]);
  const toggleFileSummarisation = useCallback(() => toggleSetting('files', 'summarise_files'), [toggleSetting]);
  const toggleBulkUploadCategorisation = useCallback(() => toggleSetting('files', 'bulk_upload_categorisation'), [toggleSetting]);
  const toggleUseTagsCategory = useCallback(() => toggleSetting('files', 'use_tags_category'), [toggleSetting])
  const toggleCategorySystemMessages = useCallback(() => toggleSetting('category', 'category_system_message'), [toggleSetting])
  const toggleGenerateCategorySystemMessages = useCallback(() => toggleSetting('category', 'generate_category_system_message'), [toggleSetting])
  const toggleUserEncyclopedia = useCallback(() => toggleSetting('response_improvement', 'user_context_enabled'), [toggleSetting]);
  const toggleMultiFileProcessing = useCallback(() => toggleSetting('files', 'multi_file_processing_enabled'), [toggleSetting]);

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
      body: JSON.stringify({ }),
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
    <div className="scrollable settings-container container">
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
        toggleUseTagsCategory={toggleUseTagsCategory}
        toggleCategorySystemMessages={toggleCategorySystemMessages}
        toggleGenerateCategorySystemMessages={toggleGenerateCategorySystemMessages}
        changeSetting={changeSetting}
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
