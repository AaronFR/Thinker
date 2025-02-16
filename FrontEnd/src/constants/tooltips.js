

const TooltipConstants = {
  /* Login page */
  bountyDetails: `
    Website would probably have to see *some* use first, I plan to pay myself at the same rate eventually: 
    <br>393 hrs and counting at time of writing...
    <br>But I would definetely plan to <b>thank</b> contributers first.
  `,

  /* Buttons */
  copyButton: "Copy to clipboard",
  fileUploadButton: "Upload file(s) as reference for your prompt",
  augmentButton: "Generates a more detailed copy of your prompt. <br>Optimised to be more machine readable/provide a better response",
  questionButton: "The app will ask questions it has about your prompt.<br>Provide answers for additional context or just use it for rubber ducking 🦆",
  submitButton: `Send your message to The Thinker for a response.
    <br>If you click here again you can enter another prompt while this one continues in the background
  `,
  submitButton_whileProcessing: `Processing prompt... <br>
    click here if you want to go to enter a new prompt, the current request will continue in the background
  `,

  /* Selectors */
  personaSelector: "Choose a speciality. This affects how the AI responds, also different 'personas' run some workflows in their own specific way",
  workflowSelector: "Select workflow, workflows determine how your prompt is answered, each workflow consists of steps where each step typically contains *at least* one call to an LLM",
  modelSelector: `Select the AI model to use, listed from the most affordable to the most powerful.<br>
    Note: Only "key" operations within workflow steps use the selected model, 
    Most tasks use the economical gpt-4o-mini model.
  `,
  bestOfSelector: "Enable to run each step multiple times and run an additional time for the AI to select the best output (e.g. best of two means x3 more prompts).<br>Adjust selection criteria in settings",
  loopsSelector: "Set the number of times the workflow will iterate over your prompt, refining it each time",
  writeSelector: "Specify a filename for the output. If left blank, filenames are generated based on your prompt automatically",
  pagesSelector: "Please select the number of pages long this document will be.<br>Each page will be planned out and an LLM given the instructions for that page, page by page",

  /* Toggles */
  categoryColoursisationToggle: "This means that when a new category is created a LLM call on the inexpensive model (gpt-4o-mini) will be run to generate an *appropriate* colour for the category.",
  
  /* System Messages */
  categorisationSystemMessage: "Categorisation occurs at the end of a workflow, referencing initial prompt and response. A new category should be created only if none of the existing ones fit",
  questioningSystemMessage: "When generating questions, the AI references your prompt, uploaded files, and previous messages. (As of yet it does not reference user knowledge)",
  autoPromptEngigneeringSystemMessage: "When generating a 'prompt engineering' copy the application only reads the users prompt. It does not reference selected files or messages.",
  summarisationSystemMessage: "The summarisation step will be provided with every single file and message reference supplied originally, this means a For All workflow can see each re-written file",
  bestOfSystemMessage: "The AI compares all generated responses with your original prompt request to select the best response",

  /* Explanations */
  llmDetails: `Large Language Model, sometimes for advanced models you'll see LRM (Large <i>Reasoning</i> Model)
    <br>LLMs are the foundation of "Artificial Intelligence"
    <br>Simply, a LLM is a statistical function that predicts which character should be ouput next in responding to a set of inputs.
    <br>Letter by letter, until a full response is generated.
    <br>
    <br>We may be called 'The Thinker AI' but you'll be better off using AI/LLMs if you understand that they do NOT think
    <br>It guesses at correct answers statistically, and sometimes these guesses can be far removed from anything resembling actual thought
  `,
  minFeeDetails: `Which we have to pay and will pass on directly rather than indirectly by increasing prices
    <br><i class="sarcasm">Ahhh the joy of cash-free transactions am I right</i>?
  `,
};

export default TooltipConstants;
