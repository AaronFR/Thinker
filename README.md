# The Thinker

### Table of Contents

1. [Objectives](#objectives)
2. [Current Limitations](#current-limitations)
3. [Features](#features)
4. [Architecture](#architecture)
5. [Planned](#planned)

## About

'The Thinker' is designed to be a llm wrapper application that is more than the sum of its parts, where most wrapper
applications are focused on single prompt to a few llm calls, The Thinker is intended to be automated as much as possible
and capable of initiating and completing lengthy tasks longer than a single response.

All the while streamling using a llm as much as possible, with pre-prompt processing, 
defined workflows to be used automatically based on use case and automatic file management and user preference configuration.

## Objectives
The primary objective of this project is to create an intelligent system that improves upon the quality of responses given 
by the base model, 
utilising multiple LLM calls to be able to iterate and evaluate prompts with quality and if requested quantity.

- Automate Problem-Solving: To provide a system that can evaluate and generate solutions for various tasks without
 extensive manual intervention.
- Modular-Architecture: That can explore and evaluate a wide range of tasks using AI-based thought processing, with flexibility and adaptability.

## Current Limitations

- **Limited workflows**: Currently the Thinker can create code classes, test classes and write general reports for a given topic.
- **Inability to bring things together**: The thinker uses multiple files to determines different types of context for the prompt
 changing this to a more unified (graph) database, could improve program coherency and contextual awareness while reducing
 costs and simplifying outputs.

## Features
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
- **Graph Database**: utilise a singular graph database with nodes and edges to work as a better approximation of a mind, rather than desperate folders and files.
  - more efficient too, allowing a single call by context to determine knowledge, user knowledge, configuration and memory context.
- **Streamlining the Writer and Editor personas**: Streamlining persona workflows and increasing capability, re-adding the ability to write an arbitrary number of pages based on
 the user's request.
- **Automated test writing**: Tests are non-existent in the prototyping stage, hopefully when ready the application can 
 actually write its own tests automatically to full standard.
- **Internet access**: Adding internet access for workflows based on context, including the ability to expand the 
 encyclopedia with web-sourced data.#
- **Attributes**: Summaries and simple summaries to be stored as attributes against files
- **Message History**: Message's saved for future reference
- **Improved persona configurations**: Personas currently don't fully "understand" their roles or the tools available to them.
 Improving this configuration will enable personas to better leverage their resources.

- **Expand Workflows**: More workflows for more use-cases, improving on the quality of existing workflows.
  - **Modular Workflows**: In write_workflow for coder there's always a step for improving code quality/
    writing documentation this should actually be a switch depending on the context.
    Many workflows should consist of switch logic that allows for intelligent processing of a given request without needless details.
  - **Workflow Feedback**: The coder module can and should actually check that its code works and try and improve upon itself if it doesn't.
   even if it can only try a fixed number of times and worst case scenario explains to the user that its solution is invalid 
   and this is the best it can do, this is a huge improvement in value.
  - **Blueprint**: Certain workflows should follow outlined blueprints created on the spot, guiding the construction of 
   documents, ensuring internal consistency and coherence.
- **Programmes**: schedules and programs written on the fly for use by the user, customisable code base.
- **n-shot prompting**: Give the AI models examples of how it should answer roughly similar tasks.
- **Parallel Processing**: Implement parallel processing to handle multiple tasks simultaneously, improving performance and reducing task completion time.
- **API Integrations**: Integrate additional AI models to leverage the most appropriate based on context
