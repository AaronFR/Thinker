

const TooltipConstants = {
  /* Buttons */
  copyButton: "Copy to clipboard",
  fileUploadButton: "Upload file(s) as reference for your prompt",
  augmentButton: "Generates a copy of your prompt, omptimised to be more machine readable/provide a better response",
  questionButton: "The app will ask questions it has about your prompt.<br>Provide answers for additional context or just use it for rubber ducking 🦆",
  submitButton_whileProcessing: "Processing prompt... if its stuck that means something went wrong and we haven't implemented a terminate button yet.. so you'll just have to refresh your page 😅",

  /* Selectors */
  personaSelector: "Choose a speciality. This affects how the AI responds, also different 'personas' run some workflows in their own specific way",
  workflowSelector: "Select workflow, workflows determine how your prompt is answered, each workflow consists of steps where each step typically contains *at least* one call to an LLM",
  modelSelector: `
    Select the AI model to use, listed from the most affordable to the most powerful.<br>
    Note: Only "key" operations within workflow steps use the selected model, 
    Most tasks use the economical gpt-4o-mini model.
  `,
  bestOfSelector: "Enable to run each step multiple times and run an additional time for the AI to select the best output (e.g. best of two means x3 more prompts).<br>Adjust selection criteria in settings",
  loopsSelector: "Set the number of times the workflow will iterate over your prompt, refining it each time",
  writeSelector: "Specify a filename for the output. If left blank, filenames are generated based on your prompt automatically",

  /* Toggles */
  categoryColoursisationToggle: "This means that when a new category is created a LLM call on the inexpensive model (gpt-4o-mini) will be run to generate an *appropriate* colour for the category.",
  
  /* System Messages */
  categorisationSystemMessage: "Categorisation occurs at the end of a workflow, referencing initial prompt and response. A new category should be created only if none of the existing ones fit",
  questioningSystemMessage: "When generating questions, the AI references your prompt, uploaded files, and previous messages. (As of yet it does not reference user knowledge)",
  autoPromptEngigneeringSystemMessage: "When generating a 'prompt engineering' copy the application only reads the users prompt. It does not reference selected files or messages.",
  summarisationSystemMessage: "The summarisation step will be provided with every single file and message reference supplied originally, this means a For All workflow can see each re-written file",
  bestOfSystemMessage: "The AI compares all generated responses with your original prompt request to select the best response",
};

export default TooltipConstants;
  