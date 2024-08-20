# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- ChatGptModel enum added for representing OpenAi models
- Thinker persona, thinks through problems and interacts closely with the user. It illustrates the general path of solving a given problem in detail which will be followed by ""subconscious"" executors.

### Changed

- Refactored: AiWrapper -> AiOrchestrator, Prompter -> ChatGptWrapper and to new AiOrchestration directory.
 To make their purpose in the project clearer

### Removed

- 

## 0.5.0 - 2024-08-15 - Quality

### Added

- Global 'solved' variable, Analyst persona can now indicate that the task is finished and the process can stop iterating through work on the initial user prompt
- ExecutionLogs.py for handling writing up the exact movements of the persona system as it works on the given task
- 'regex refactor' task: regex replacing large sections of text repeatedly fails, so the application was refactored (🙃) to replace a word or words for all files.
- 'rewrite' task: instead of trying to replace lines of text with regex which is very error prone, instead the replacement is done by swapping out the content based on line number
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
- Writer role: Writes reports, iterating multiple times to overcome ChatGpt's output limit
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

- FileManagment.py for /Thoughts splitting out methods from ThoughtProcess.py
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
  - Current method performs better than a single base omni model prompt but takes longer. Still has a bad habit of writing tasks that are not used and deadends in the task chain.
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

- Analyser.py method for analysing a target output against initial prompt and recommending if the process needs to be retriggered
- HtmlProcessing.py methods for outputing html and text files (to be split out later)

## [0.0.0] - 2024-07-19

### Added

- Prompter.py acting as the primary interface to the ChatGpt api
