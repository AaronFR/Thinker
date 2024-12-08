# The Thinker

🚧🚧🚧 ***WORK IN PROGRESS PROTOTYPE*** 🚧🚧🚧

## Table of Contents

1. [Objectives](#objectives)
2. [Current Limitations](#current-limitations)
3. [Features](#features)
4. [Architecture](#architecture)
5. [Planned](#planned)

## About

'The Thinker' is orientated towards bringing more complex, continuous and iterative agentic workflows to the average everyday
user, filling the middle ground between simple LLM wrapper applications and advanced Enterprise-orientated AI products.

A powerful, general purpose AI application

## Objectives

The primary objective of this project is to create an intelligent system that improves upon the quality of responses given
by the base model,
utilising multiple LLM calls to be able to iterate and evaluate prompts with quality and scaling to any arbitrary size of 
request.

- Automate Problem-Solving: To provide a system that can evaluate and generate solutions for various tasks without
 extensive manual intervention.
- Role driven: Users can utilise roles that specialise in a specific domain -or themselves can delegate and instruct other
 roles as required to complete its given
- Flexible and useful memory and configuration system: The system learns the users preferences *once* and can
 continually refer to them or any appropriate internal or external reference material as required.
- Hallucination avoidance/minimisation through pre- and post-process analysis, feeding the system the appropriate reference
 material to keep it grounded in reality.
- Scheduling: Enabling the scheduling and running of workflows/generated code at specific user defined intervals

## Current Limitations

- **Limited workflows**: Currently the Thinker can create code classes, test classes and write general reports for a given topic.
- **Inability to bring things together**: The thinker uses multiple files to determine different types of context for the prompt
 changing this to a more unified (graph) database, could improve program coherency and contextual awareness while reducing
 costs and simplifying outputs.
- **Polish**: As of yet there is still a lot of work to do to make every interaction with the UI tolerable and pleasant, 
 in particular showing messages and *especially* folders takes far to long/manual refreshes

## Features

- **Prompt optimisation**: User prompts will automatically be enhanced side by side with the Prompt Enginering standards,giving the user ideas for how to improve their prompt or just to run the augmented prompt instead for better results. Questions are automatically generated and presented to the user, that help the AI provide a more relevant answer.
- **Workflows**: A user prompt is fed into a persona and evaluated for one of its workflows, a workflow representing a
 series of prompts to be run to achieve an ideal outcome for the given task type.
- **Pre-Prompt-Processing**: 'sub-conscious' processes, referencing contextual information as required by context in advance of an
 actual LLM call

## Architecture

The project's architecture is designed with modularity in mind, allowing for the easy addition of new features and components:

- **Personas**: (because ChatGpt uses 'roles' already) a class that structurally represents the idea of a worker specialised for a
  particular task, the idea is that in concert a series of Persona's could work together in a sensible way, while leveraging individual specialisations
  - **PersonaSpecification**: Handles the defining of lengthy system messages and instructions
- **AiOrchestration**: Handles the actual to calls to a given llm, working with executors that handle user messages (prompts), contextual system messages, history and attached files
- **Functionality**: While Personas' have workflows, many workflows and many workers can share the same code, do the same thing
- **Data**: Handles the processing, creation and editing of data, including written files and accessed configuration files

## Planned

To refine the system's architecture and enhance its capabilities and efficiency, several key features are intended for implementation:

- **Auto-select messages**: After a message the option exists to automatically select that one for the next prompt.
  - **prompt-chains**: instead of storing individual prompts store chains, first prompt to final in one set, simplifies organisation and reduces visual
   clutter

- **Expand Workflows**: More workflows for more use-cases, improving on the quality of existing workflows.
  - **Flexible workflows**: Workflows shouldn't really be 'hardcoded', they should be defined from a common format likely
    JSON, this would allow workflow to be flexible and easily modified, copied and extended by the user.

  - **Modular Workflows**: In write_workflow for coder there's always a step for improving code quality/
    writing documentation this should actually be a switch depending on the context.
    Many workflows should consist of switch logic that allows for intelligent processing of a given request without needless details.

  - **'Boss' Personas**: Large tasks should be enabled by 'boss' personas, e.g. a 'Coder' persona can write and update a file,
     but a 'Team Lead' persona could manage several coder's to improve or write an entire application. 
     (These types of arbitrarily large tasks are the **central** point of this whole project)
  
  - **Workflow Feedback**: The coder module can and should actually check that its code works and try and improve upon itself if it doesn't.
   even if it can only try a fixed number of times and worst case scenario explains to the user that its solution is invalid
   and this is the best it can do, this is a huge improvement in value.

  - **Blueprint**: Certain workflows should follow outlined blueprints created on the spot, guiding the construction of
   documents, ensuring internal consistency and coherence.

  - **Mathematician/Engineer/Physicist**: LLMs are bad at math the same way Humans are bad at math, neurons are just not well
   suited to counting and arithmetic operations compared to binary functions. However, unlike humans their *terrible* at **spatial reasoning**
   But why does that need to be a limitation? If we let it connect to tools that help it simulate the world while it ""thinks"" in words
   we can have the best of both worlds. Unlocking a lot of capability/accuracy.


- **Payment System**: Top up system for updating balance(awaiting stripe integration), ~~log files for each individual cost incurred~~.

- **Best of X**: Let users run multiple prompts in parallel and have the system automatically select/pick and choice to create a superior answer
  - Can be customised on preference: Should the other attempts be identical or optimise for different qualities entirely, returning a balanced approach.

- **Programmes**: schedules and programs written on the fly for use by the user, customisable code base.

- **Micro thoughts**: Generated even while the prompt is being written. Question -> answer
  - ~~Generate list of questions in regard to prompt, if appropriate ask user~~, otherwise pull from memory.
  - Auto select persona to describe which persona will be selected for a given prompt, workflow to be suggested in advance

- **QOL**:
  - categories should be listed according to date of their latest massage
  - messages and files show when they are selected, categories holding selected files are also visually identified
  - Can deselect a message or file from the main view area rather than their item
  - (optional) automatic category colourisation
  - its hard to select a file vs expanding it for review (solved if that means the same thing though..)
  - ~~files and messages should display in the large main section not tucked into the corner~~

- **Automated test writing**: Tests are non-existent in the prototyping stage, hopefully when ready the application can
 actually write its own tests automatically to full standard.
  - Long due that specific "integration" user tests where created to test that the system can satisfactorily answer the user,
   avoid hallucinations, provide scores of high value, asses performance against tests and benchmarks etc.

- **Internet access**: Adding internet access for workflows based on context, including the ability to expand the
 encyclopedia with web-sourced data.

- **User Configuration Profile**: Profiles the user can easily select from the prompt screen and are clearly visible, e.g
 "expensive request", "private mode", "work", "humorous mode", etc so the user can quickly swap out configuration as they want
  - e.g. I would prefer if coder displayed all code changes as 'before and after' rather than the entire file, additionally I prefer if
   if it aims to implement the feature I'm asking for with the *minimum* amount of changes to the existing functionality.
- **Persona Configuration**: Left to the user as much as possible.

- **Undo Changes Files**: e.g. to files

- **Graph Database Implementation**: A lot of work was put into creating functionality which now needs to be done with a 
 graph based methodology
  - general knowledge (? Internet search will have to be implemented first to see the exact utility..)
  - ~~user knowledge~~
  - configuration (changes)
  - Connecting relevant messages to the current prompt -> chain of messages displayed on the main section
  - sub-categories (possibly)

- **Parallel Processing**: Implement parallel processing to handle multiple tasks simultaneously, improving performance and reducing task completion time.

- **API Integrations**: Integrate additional AI models to leverage the most appropriate based on context
