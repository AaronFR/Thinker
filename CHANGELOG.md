# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Model descriptions and price per token comparisons are displayed in Pricing
- New users are sent email verification emails
  - New user *can* receive the free dollar promotion after verification
- Newly created messages will be automatically selected by default
- Workflow duration in seconds
- Auto categorisation before prompt is sent
  - Allows user to pick category, display which category will be selected in advance
    and reduce request durations.
  - User can enter in new category in selector
- Edit internet search instructions in settings.
- File size displayed
- LICENSE: AGPL v3
- Option (on by default) to use the category in tags for file uploads.
- Option to only automatically select a category, persona or workflow once.

### Changed

- New messages will trigger a category refresh if that category is already open
- Settings sections can be minimised to make settings less overwhelming
  - Most sections start minimised
- Full internet search: Relevant pages are used as reference for the user's prompt
  - Pages are sourced and displayed to the user per step
- Added o3-mini, the cutting edge open-ai model
  - o1-mini prices update (now lower)
- More intuitive file upload, files are uploaded ..after file upload, not after sending a prompt with the uploaded files
 attached.
- Ongoing requests won't be affected by a change in configuration mid-run.
- A step's output is properly formatted when displayed
- 'User context' is no longer in 'beta'
  - (Usually) Remembers user facts and preferences, but increases prompt durations significantly
- Improved formatting, especially for mobile
  - User input page formatted to clearly separate different categories and selectors by topic
  - Message/File pane more compact, cleaner, making it easier to browse many categories
  - Messages and Files more streamlined and less 'Chunky' easier to browse multiple files/messages
  - Reduced 'over-scrolling'
- loops (parallel runs) available for all workflows instead of having it's own specific workflow.
- Max data storage per user of 1 GB (Only text is supported currently so this should be *impossible* to breach)
- New category description and description created simultaneously, decreasing time take to create new categories
- Uploaded code files are formatted correctly as code not text
- Category, Persona and Workflow selectors visually display when a value is being generated automatically.

### Removed

- o1-preview (o1 is released but not as good as o3-mini, while being *much* more expensive)
- staging-directory: was used at the end of a request, saving files (typically in threads) is faster.
- EncyclopediaManagement - made redundant by internet search
- Loops workflow

## [0.9.5] - 2025-02-18 - Pre public beta

### Added

- Gemini models are available (gemini-2.0-flash and gemini-2.0-flash-lite-preview)
- Generated files are displayed under the underneath the response
- Costs for individual functionalities are displayed
- Option to run write pages workflow in parallel
- Select default model
- Use 'new' after submitting a prompt to immediately start entering a new prompt while the current request
 runs in the background
- Options for giving files summaries on creation

### Changed

- Summaries properly displayed under files (disabled by default)

### Removed

- Best of: 'Differentiated' option, openAi doesn't like multiple simultaneous similar prompts, but primarily it was bugged and is 
  exceptionally difficult to debug, its simply not a priority before open beta

## [0.9.4] - 2025-01-29 - Self-Expository

### Added

- Loop workflow - will run through the same prompt multiple times with a separate quality factor considered on each loop
- Internet search, each step will now search the internet for any relevant context, 
   currently just a rough overview of the top 3 results
- The tags that can selected are now made explicitly clear for the user in the 'palette' directly under the prompt window
  - Tag selectors will appear as applicable to the users prompt
  - Tooltip comments to help the user understand how the website works
- Best of: 'Differentiated' option, this means when running multiple prompts at once each run prioritises a different 
   quality e.g. coherency, creativity, etc

### Changed

- Left Pane (message and file reference) is only enabled on desktop
- Dark mode set to default
- Auto workflow is much faster by processing all files in parallel 
- Tags redesign: User is prompted to enter values for tags as the context of a prompt is defined. More intuitive and self-explanatory
  - Tags values hidden behind 'debug view' mode

## [0.9.3] - 2025-01-20 - It certainly is

### Added

- Messages pages - for displaying prior messages and files to the user and for selection as reference
- Files and messages are highlighted visually when selected as reference
- Files and messages can be de-selected from the display area over the prompt textarea
- Categories are automatically assigned a random colour with an option for an LLM assigned colour
- Messages display incurred cost at the bottom
- Workflow is automatically selected based on user prompt (While small this now means if you tell the application to write a file it will use a supplied file name
   or come up with one on its own and do so)
- Persona is automatically selected based on user prompt
- Selecting messages or files in one tab will instantly affect other tabs

### Changed

- Categories are listed according to their latest component
- Workflow is selected from the 'workflow' tag, not interpolated from the 'write' or 'auto' tag if they exist.
- Selected messages and files are persisted on a device, meaning you can leave the site and come back to the same selected items
- More accurate search of user knowledge

### Removed

- Receipt nodes have been removed, instead costs are saved against messages themselves (*I'm* billed by the node)

## [0.9.2] - 2025-01-11 - Quantity is a Quality of its own

### Added

- Auto workflow: In coder, select 'auto' in the tags -> 1 prompt is applied to all file references individually
- Writer Persona ✍ : When writing to a file, specify 'pages' to a number in the tags and the llm will respond that many
   times (capped at 10 for now)
- Update base text size in settings
- More coherent visuals
- 'Best of' Feature: Run a prompt multiple times in parallel then compare the results to improve performance.
- Can toggle summarisation of workflows off and change the summarisation system message

### Changed

- The current state of the workflow is more accurately presented, including response updates
- When run locally user data is stored inside the /UserData directory (not /Backend). Cleaner and also prevents 
   unnecessary restarts when running flask in debug
- Various bug fixes
- General misc refactor of code (via Auto workflow)
- Optimise and auto engineering of prompts can be toggled off - not present at all, on - can be triggered manually and auto - automatically triggers if the prompt updates.

## [0.9.1] - 2024-12-22 - Getting ready for β

### Added

- User can manually specify llm system message instructions
- File size limit of 10 MB implemented to avoid incorrect use (Only text files are accepted for now)
- Any route that uses LLM calls checks the user has sufficient balance (sorry 🤗)
- User is warned if their balance is too low.

### Changed

- Question prompt will also reference files and/or messages added to the prompt (no more: "Can you tell me what language
  (lorem.py) is written in...)
- Resizing file/prompt panes works on mobile with touch
- Minor tweaks to scale better on mobile


## [0.9.0] - 2024-12-14 - Auth, Login and Online Deployment AKA 'I now use this app instead of ChatGPT.com'

### Added

- Staged files remain staged persistently
- User registration and login. User authentication
- Users can manually select one or more messages as context for a prompt
- Users can select which model they want to use (any model they want, as long as it's an OpenAi model)
- Workflow progress is shown visually to the user
- Left pane (files and message select) and Right pane (prompts) can be resized dynamically against one another
   .e.g. for reading a file or message properly.
- User balance displayed to user
- FrontEnd and Backend can communicate when deployed on Heroku
- https://theThinkerAi.com domain permitted through CORS

### Changed

- Responses now highlight code appropriately
  - Can copy code sections
- user config files unique for each user
- File storage locally or in AWS s3 based on configuration

## [0.8.1] - 2024-11-08 - File Selection and Streaming

### Added

- User can upload files for reference in their prompts
- Users can (actually) select, unselect and view previously uploaded text files for reference in a new prompt
- User context is saved and referenced allowing the application to remember details from prompt to prompt
- Responses are now streamed as soon as they start generating, reducing wait times before *a* response
- Users can tag prompts e.g. "write": "example.txt" will trigger a write workflow, "category" can be user defined

### Changed

- Renamed `/thoughts` -> `/FileData`
- Files are now stored in uuid designated folders uniquely related to the user
- Improved auto-categorisation

### Removed

- UserEncylopedia.yaml and UserEncyclopedia References are no longer created, user *topics* now being saved to the graph database

## [0.8.0] - 2024-10-18 - Front End and Database

### Added

- A front end to interactive with 🎉
  - A main page where the user can send prompts with options for prompt augmentation
  - Settings page where users can toggle beta features
    - Dark mode 😎
  - Pricing page placeholder that gives current session costs
- A database to save user messages, allowing the system to finally display and retain message history
- Configuration: Beta features can be enabled or disabled from settings
- Micro thoughts - processes that run in the background to improve prompts and responses
  - Augmented prompt is suggested to the user
  - Automatically generated questions, that are presented to the user, giving the opertunity to supply additional context to a given prompt

### Changed

- Coder: write_workflow streamlined, now quicker while more consistent and versatile
- Message Processing: The most important message for chatGpt is the last AKA 'latest' message, Ai Orchestration has been
 corrected to use this design properly leading to less confused and erroneous operations by the system
- Resolved an issue where the application says it doesn't have access to a file, because the file name wasn't supplied with
 the associated content.

## [0.7.0] - 2024-09-17 - Knowledge


### Added

- Coder
  - Write tests workflow
  - Can write to multiple files at once
- UserConfig.yaml for configuration specific to the individual user
- EncyclopediaManagement.py with search_encyclopedia functionality, Persona's can now evaluate prompts and ask for reference material
 in advance of evaluating a given prompt
  - UserEncyclopedia.yaml: Facts about the user are stored in their own encyclopedia, for reference as required
- WikipediaApi For accessing content if required by a request and caching it in a Encyclopedia.yaml for future reference
- chat_workflow: for conversing with the user without saving files

## [0.6.0] - 2024-08-30 - Scalability

### Added

- ChatGptModel enum added for representing OpenAi models
- Thinker persona: thinks through problems and interacts closely with the user. It illustrates the general path of solving a given problem in detail which will be followed by ""subconscious"" executors.
- Coder persona: for creating new software files
- Configuration: Persona's will load configuration dependent on their role that instructs how they operate, e.g. tone,
 style, length of replies, etc
- Coding, Organising and Writing functionality classes to be used by Persona roles as per their function.

### Changed

- workflow system replacing the 'executive plan' system. Instead of giving the AI model free rein to devise how to approach a given problem, a matching workflow is selected and run.
 This makes outputs more predictable and reliable while allowing us to tailor the workflow over the course of development.
  - Personas are now only responsible for defining their own workflows and configuration, execution logic is stored in the interface BasePersona.py 
- Refactored: AiWrapper -> AiOrchestrator, Prompter -> ChatGptWrapper, added to new AiOrchestration directory.
- Docstrings: all refactored in the reStructuredText format

## [0.5.0] - 2024-08-15 - Quality

### Added

- Global 'solved' variable, Analyst persona can now indicate that the task is finished and the process can stop iterating through work on the initial user prompt
- ExecutionLogs.py for handling writing up the exact movements of the persona system as it works on the given task
- 'regex refactor' task: regex replacing large sections of text repeatedly fails, so the application was refactored (🙃) to replace a word or words for all files.
- 'rewrite' task: instead of trying to replace lines of text with regex which is very error-prone, instead the replacement is done by swapping out the content based on line number
- multiple prompts functionality: AiWrapper can now be instructed to output multiple answers, selecting one according to judgement criteria

### Changed

- calculate_prompt_cost method added for *all* usages of the LLM API, letting the program give out an *accurate* value for the cost for a given run
- thought_id is determined via global, while this may need to be updated if the application is every to be used in bulk this prevents the program from accessing other task folders it's not supposed to

### Removed

- CorpusCallosum.py, PromptManagement.py and config.json as these files are deprecated and no relevant to the main application

## [0.4.0] - 2024-08-08 - Quantity

### Added

- Analyst role: reviews the current output files against the initially supplied user prompt, making comments and finally 
 suggesting a list of workers to work on the task to improve it in line with their suggestions
- Writer role: Writes reports, iterating multiple times to overcome ChatGPT's output limit
- Editor role: reviews reports and rewrites the entire file 1000 tokens at a time in line with an instruction from the Analyst and its own observations

### Changed

- Editor suitable tasks split out from Writer, reducing 'confusion' in executing functions
- User, System and Function constant messages refactored with prompt engineering techniques + examples
- thought_id directory and individual request costs passed as globals rather than through the class hierarchy

### Removed

- Analyser.py and ExecutiveThought.py now long since integrated into Analyser.py and the executive planning process in Writer and Editor

## [0.3.0] - 2024-08-03

### Added

- TaskRunner for running individual tasks in order to improve solution: APPEND, REWRITE, REWRITE_FILE

### Changed

- Total Refactor of ThoughtProcessing. 'Thought' Metaphor abandoned to more practical terminology.
- Editor suitable tasks split out from Writer, reducing 'confusion' in executing functions

## [0.2.1] - 2024-08-01

### Added

- FileManagement.py for /Thoughts splitting out methods from ThoughtProcess.py
- Docstrings to each major method

### Changed

- Files are now automatically loaded if added to the appropriate 'Thought space'
- Executive thoughts can now dictate where output is to be saved and if it should overwrite existing content
- Executive thoughts can split out multiple new executor thought instances to be run
- ThoughtProcessing now works where each iteration is a 2-step process. Llm looks at the state of the solution and produces a plan of action -> Acted on by the next llm with output saved to the directed file

## [0.2.0] - 2024-07-27

### Added

- Thought.py, ThoughtProcess.py created as a way of iteratively trying to solve a solution one step at a time, instead of the previous approach where a solution plan would be designed and followed from the first step

## [0.1.1] - 2024-07-24

### Added

- Affordable alternative to using Chat-Gpt 4o base for creating initial plans of actions for initial prompts, enabled by default
  - Current method performs better than a single base omni model prompt but takes longer. Still has a bad habit of writing tasks that are not used and dead-ends in the task chain.
- A method 'aggregate_files' in FileManagement.py

### Changed

- HtmlProcessing.py -> FileProcessing.py

## [0.1.0] - 2024-07-23

### Added

- PromptManagement.py handling and aggregating uses of the Prompter.py api methods
- logging and error checking

### Fixed

- Regex checks, square bracket clues, file replacement and management of prompts occurs without error
- Cleaned up internal files and reduced duplicate methods/less than sensible placements

### Changed

- Upgrade dependencies: Ruby 3.2.1, Middleman, etc.

### Removed

- SubPrompter.py is now made outdated by the PromptManagement.py class

## [0.0.1] - 2024-07-21

### Added

- Analyser.py method for analysing a target output against initial prompt and recommending if the process needs to be re-triggered
- HtmlProcessing.py methods for outputting html and text files (to be split out later)

## [0.0.0] - 2024-07-19

### Added

- Prompter.py acting as the primary interface to the ChatGpt api
