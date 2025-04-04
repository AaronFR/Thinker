

const TooltipConstants = {
  /* Login page */
  limitDetails: `Well okay, there <i>litterally</i> are limits, but those are for avoiding malicous abuse.
    If your hitting those something is going very wrong or <i>right</i>.. please get in contact if so!
  `,
  bountyDetails: `Website would probably have to see *some* use first, I plan to pay myself at the same rate eventually: 
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
  categorySelector: "Select a Category folder for convenient future reference",
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
  loopsSelector: `Enable to run the LLM calls inside each step multiple times in sequence, improving on the answer with each loop.
    Increases in time and cost are roughly proprotional to the number of loops`,
  writeSelector: "Specify a filename for the output. If left blank, a name will be generated automatically",
  pagesSelector: `Indicate the desired length of the document in 'pages' (individual responses). The AI will plan instructions for each individual response.`,

  /* Toggles */
  categoryColoursisationToggle: "Enable automatic color assignment for new categories. The AI will choose a color that represents the category as opposed to a random colour.",
  
  /* System Messages */
  categorySystemMessage: "These instructions are applied to any prompt that fits this category. Click to edit.",
  categorisationSystemMessage: "Categorization helps organize your files and messages by assigning them to existing or new 'folders'.",
  questioningSystemMessage: `When generating questions, the AI references your prompt, uploaded files, and previous messages. (As of yet it does not reference user knowledge)
  
  Note: 'Provide only the questions.' instructs the LLM to only output the questions themselves without preface: faster and less expensive to run.`,
  autoPromptEngigneeringSystemMessage: `Prompt Augmentation uses only your initial prompt. It does not reference selected files or messages.

  Trade-off: keeping especially long reference text reduces the 'space' the AI has to plan out a better answer, condensing the actual prompt. It may be preferable to organise the prompt first and (re)include any references afterwards`,
  summarisationSystemMessage: "The summarisation step will be provided with every single file and message reference supplied originally, this means a For All workflow can see each re-written file",
  fileSummarisationSystemMessage: "File summaries only access the content of the file. TIP: be creative: it doesn't <i>have</i> to be a generic summary, prioritise what you want.",
  bestOfSystemMessage: "The AI compares all generated responses with your original prompt request to select the best response",
  internetSearchInstructions: "Has access to your prompt, the search term(s) it creates will then be run in a browser (DuckDuckGo).",

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
