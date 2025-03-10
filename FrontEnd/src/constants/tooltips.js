

const TooltipConstants = {
  /* Login page */
  bountyDetails: `
    Website would probably have to see *some* use first, I plan to pay myself at the same rate eventually: 
    <br>557 hrs and counting at time of writing...
    <br>But I would definetely plan to <b>thank</b> contributers first.
  `,

  /* Buttons */
  copyButton: "Copy to clipboard",
  fileUploadButton: "Upload file(s) as reference for your prompt",
  augmentButton: "Generate a more detailed copy of your prompt. <br>Optimised to be more machine readable/provide a better response.",
  questionButton: `The app will ask you questions it has about your prompt.
    Provide answers for additional context or just use it for rubber ducking 🦆`,
  submitButton: `Send your message to The Thinker for a response.
    <br>If you click here again you can enter another prompt while this one continues in the background
  `,
  submitButton_whileProcessing: `Processing prompt... <br>
    click here if you want to go to enter a new prompt, the current request will continue in the background
  `,

  /* Selectors */
  personaSelector: "Select an AI 'persona' with it's own response style and workflows.",
  workflowSelector: "Select a workflow to determine how your request is responded to. Workflows are sequences of individual steps, each using AI to achieve a set task",
  modelSelector: `Select the primary AI model to use, listed from the most affordable first.<br>
    Note: Only "key" operations within workflow steps use the selected model, 
    Most background LLM calls use a seperate, economical model.sele
  `,
  backgroundModelSelector: `Select a secondary, background model, this should be a fast and economical model.<br>
    Used throughout the application for everything that *isn't* a primary workflow task.
    categorising, summarising, basic decision making.
  `,
  bestOfSelector: `Enable to run each step multiple times and then select for the best response.
  e.g. best of two means roughly x3 more prompts
  Adjust selection criteria in settings`,
  loopsSelector: "Set the number of times the workflow will iterate over your prompt, refining it each time",
  writeSelector: "Specify a filename for the output. If left blank, a name will be generated automatically",
  pagesSelector: `Indicate the desired length of the document in 'pages' (individual responses). The AI will plan and generate content page by page.`,

  /* Toggles */
  categoryColoursisationToggle: "Enable automatic color assignment for new categories. The AI will choose a color that represents the category as opposed to a random colour.",
  
  /* System Messages */
  categorisationSystemMessage: "Categorization helps organize your files and messages by assigning them to existing or new 'folders'.",
  questioningSystemMessage: "When generating questions, the AI references your prompt, uploaded files, and previous messages. (As of yet it does not reference user knowledge)",
  autoPromptEngigneeringSystemMessage: "Prompt Augmentation uses only your initial promptt. It does not reference selected files or messages.",
  summarisationSystemMessage: "The summarisation step will be provided with every single file and message reference supplied originally, this means a For All workflow can see each re-written file",
  fileSummarisationSystemMessage: "File summaries only access the content of the file. TIP: be creative: it doesn't <i>have</i> to be a generic summary, prioritise what you want.",
  bestOfSystemMessage: "The AI compares all generated responses with your original prompt request to select the best response",

  /* Explanations */
  llmDetails: `Large Language Model, sometimes for advanced models you'll see LRM (Large <i>Reasoning</i> Model)
    LLMs are the foundation of "Artificial Intelligence"
    <br>Simply, a LLM is a statistical function that takes in inputs and predicts what letter should come next in response.
    Letter by letter, until a full response is generated.


    We may be called 'The Thinker AI' but you'll be better off using AI/LLMs if you understand that they do NOT think.

    It guesses at correct answers statistically, and sometimes these guesses can be far removed from anything resembling actual thought
  `,
  minFeeDetails: `Which we have to pay and will pass on directly rather than indirectly by increasing prices
    
    <i class="sarcasm">Ahhh the joy of cash-free transactions am I right</i>?
  `,
  perToken: `Tokens are what LLMs actually 'read', they roughly correspond to one word.
  
  Precise measurements differ from model to model. 
  This explanation is 40 tokens long to GPT-4o.
  `,
  perMillionToken: `1 million tokens more accurately correpsonds to ~750,000 words
  The average novel is about 100,000 words long.
  `,
  byCheapest: `Gemini-2.0- Flash lite - preview
  At time of writing`,
  internetSearchCosting: `This is the minimum cost, page content will also increase the input costs of a prompt`,
  userContextCosting: `This is just the minimum cost for deciding what user info to store and retrieve. 
  The referenced context will also increase the input costs of a prompt.`,
};

export default TooltipConstants;
