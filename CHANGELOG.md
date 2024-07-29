# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- FileManagment.py for /Thoughts splitting out methods from ThoughtProcess.py
- Docstrings
- 

### Changed

- Files are now automatically loaded if added to the appropriate 'Thought space'
- Executive thoughts can now dictate where output is to be saved and if it should overwrite existing content
- Executive thoughts can split out multiple new executor thought instances to be run
- ThoughtProcessing now works where each iteration is a 2-step process. Llm looks at the state of the solution and produces a plan of action -> Acted on by the next llm with output saved to the directed file

### Removed

-


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
