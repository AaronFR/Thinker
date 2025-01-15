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

- **Limited workflows**: The thinker can process an arbitrary number of files and generate a document of arbitrary length,
   but there's not a lot of specification, workflows could benefit from switches based on certain events occurring. And more detailed, 
   more tailored workflows.
- **Context**: The thinker uses multiple files to determine different types of context for the prompt
 changing this to a more unified (graph) database, could improve program coherency and contextual awareness while reducing
 costs and simplifying outputs.
- **Polish**: Yet there is still a lot of work to do to make every interaction with the UI tolerable and pleasant, 
 in particular showing messages and *especially* folders takes far to long/manual refreshes

## Features

- **Prompt optimisation**: User prompts will automatically be enhanced side by side with the Prompt Engineering standards,giving the user ideas for how to improve their prompt or just to run the augmented prompt instead for better results. Questions are automatically generated and presented to the user, that help the AI provide a more relevant answer.
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

### Functionality

- **Auto-select messages**: After a message the option exists to automatically select that one for the next prompt.
- **Payment System**: Top up system for updating balance(awaiting stripe integration)
  - Attach receipts to ~~prompts~~, workflows and features. So the user always knows how much they've spent and on what.
- **Category descriptions**: input is cheap and a small description would probably significantly increase selection 
   relevance
- **Memory System**: In beta, needs to be made reliable: That means 'remembering' less useless information, storing it better and reading it better
  - Descriptions for knowledge node concepts? Same idea for improving category specificity?
- **Modular Workflows**: The coder module can and should actually check that its code works and try and improve upon itself if it doesn't.
   even if it can only try a fixed number of times and worst case scenario explains to the user that its solution is invalid.
   Many workflows should consist of switch logic that allows for intelligent processing of a given request without needless details.
- **Best of X**: ~~Let users run multiple prompts in parallel and have the system automatically select/pick and choice to create a superior answer~~
  - Can be customised on preference: Should the other attempts be identical or optimise for different qualities entirely, returning a balanced approach.
- **Internet access**: Adding internet access for workflows based on context, including the ability to expand the
 encyclopedia with web-sourced data.
  - general knowledge shared nodes (e.g. information on a technology or recent event)
  - Coder github integration
- **API Integrations**: Integrate additional AI models to leverage the most appropriate based on context
- **Loop Workflows**: Say you want to 'Optimise a file', the thing is you can actually keep doing that. A setting should be added to run the prompt
  multiple times in a row, possibly based on various different qualities. [First general refactor, then readability, then performance for example]
- **Programmes**: schedules and programs written on the fly for use by the user, customisable code base.
- **'Boss' Personas**: Large tasks should be enabled by 'boss' personas, e.g. a 'Coder' persona can write and update a file,
     but a 'Team Lead' persona could manage several coder's to improve or write an entire application.
- **Micro thoughts**: Generated even while the prompt is being written. Question -> answer
  - Auto select persona to describe which persona will be selected for a given prompt, workflow to be suggested in advance
  - Auto select workflow
- **Mathematician/Engineer/Physicist**: LLMs are bad at math the same way Humans are bad at math, neurons are just not well
   suited to counting and arithmetic operations compared to binary functions. However, unlike humans their *terrible* at **spatial reasoning**
   But why does that need to be a limitation? If we let it connect to tools that help it simulate the world while it ""thinks"" in words
   we can have the best of both worlds. Unlocking a lot of capability/accuracy.
- **Parallel Processing**: Implement parallel processing to handle multiple tasks simultaneously, improving performance and reducing task completion time.

- **Automated test writing**: Tests are non-existent in the prototyping stage, hopefully when ready the application can
 actually write its own tests automatically to full standard.
  - Long due that specific "integration" user tests where created to test that the system can satisfactorily answer the user,
   avoid hallucinations, provide scores of high value, asses performance against tests and benchmarks etc.

### UI

- **Message Stacks**: Messages are displayed one at a time. Organising prompts that are referencing each other in a chain into
  a singular stack would make navigation easier
- **QOL**:
  - Q&A can be malformed at times
  - Ability to terminate a mid-process prompt
  - Prompts can fail and the user doesn't know why, it just stalls at 'Processing..'
  - It's hard to select a file vs expanding it for review (solved if that means the same thing though..)
  - Ability to undo changes to files
- **User Configuration Profile**: Profiles the user can easily select from the prompt screen and are clearly visible, e.g
 "expensive request", "private mode", "work", "humorous mode", etc so the user can quickly swap out configuration as they want
  - e.g. I would prefer if coder displayed all code changes as 'before and after' rather than the entire file, additionally I prefer if
   if it aims to implement the feature I'm asking for with the *minimum* amount of changes to the existing functionality.
- **Persona Configuration**: Left to the user as much as possible.



