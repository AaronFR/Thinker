<h1 align="center">
    <a href="https://thethinkerai.com/">
        <img src="FrontEnd/public/ThinkerLogo.png" style="width:280px; height:auto;" alt="ThinkerAI Logo">
    </a>
</h1>

# The Thinker

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

🚧🚧🚧 ***WORK IN PROGRESS PROTOTYPE*** 🚧🚧🚧

## Table of Contents

1. [Objectives](#objectives)
2. [Current Limitations](#current-limitations)
3. [Features](#features)
4. [Architecture](#architecture)
5. [Planned](#planned)

## About

'The Thinker' is an open source toolkit for AI bringing powerful workflows through a highly customisable interface to the average everyday
user, filling the middle ground between simple LLM wrapper applications and advanced Enterprise-orientated AI products.

A powerful, general purpose AI application

## Objectives

The primary objective of this project is to create an intelligent system that improves upon the quality of responses given
by the base model,
utilising multiple LLM calls to be able to iterate and evaluate prompts with quality and scaling to any arbitrary size of 
request.

This project aims to create an intelligent system for using AI: using AI to automate using AI itself as much as possible and 
using as many AI calls and additional functionalities as the user wants to improve responses based on various metrics

- Automate Problem-Solving: To provide a system that can evaluate and generate solutions for various tasks without
 extensive manual intervention.
- Pre-defined workflows: Instead of trying to get current day LLMs to somehow manage the task of defining custom workflows for 
  each task as they are given them, pre-defined workflows are selected/can be selected based on their suitabilities for the 
  users task. Ensuring a coherent and consistent response.
- Role: Structured to think in terms of 'personas' affecting how the system responds to each step in a given workflow and how those 
  workflows are them selves structures.
- Flexible and useful memory and configuration system: The system learns the users preferences *once* and can
 continually refer to them or any appropriate internal or external reference material as required.
- Hallucination avoidance/minimisation through pre- and post-process analysis, feeding the system the appropriate reference
 material to keep it grounded in reality.
- Scheduling: Enabling the scheduling and running of workflows/generated code at specific user defined intervals

## Current Limitations

- **Limited workflows**: Currently there are only four workflows Chat, Write, For Each and Loop. These workflows are 
  *general* purpose rather than being targeted at specific use cases. Feedback/ideas wanted!
- **Polish**: Yet there is still a lot of work to do to make every interaction with the UI tolerable and pleasant
  - **Mobile friendly**: While the site has been made responsive the project has been primarily developed with desktop
    use in mind, mobile use is unnecessarily clunky.
- **More settings, more overview**: There are still features e.g automatic categorisation that cannot yet be disabled in 
  settings. At the same time, it is currently not possible to see external data like memory.

## Features

- **Prompt optimisation**: User prompts will automatically be enhanced side by side with the Prompt Engineering standards,giving the user ideas for how to improve their prompt or just to run the augmented prompt instead for better results. Questions are automatically generated and presented to the user, that help the AI provide a more relevant answer.
- **Workflows**: A user prompt is fed into a persona and evaluated for one of its workflows, a workflow representing a
 series of prompts to be run to achieve an ideal outcome for the given task type.
- **Pre-Prompt-Processing**: 'sub-conscious' processes, referencing contextual information as required by context in advance of an
 actual LLM call
- **Memory**: If enabled, the system will note details about the user, their prompts and preferences, and use them for 
   ~~selling them ads~~ providing a consistent context to their prompts. (though seriously we WONT sell data, eventually
   messages, files and memory need to be encrypted when the option to run private models is available)

## Architecture

The project's architecture is designed with modularity in mind, allowing for the easy addition of new features and components:

- **Personas**: (because ChatGpt uses 'roles' already) a class that structurally represents the idea of a worker specialised for a
  particular task, the idea is that in concert a series of Persona's could work together in a sensible way, while leveraging individual specialisations
  - **PersonaSpecification**: Handles the defining of lengthy system messages and instructions
- **AiOrchestration**: Handles the actual to calls to a given llm, working with executors that handle user messages (prompts), contextual system messages, history and attached files
- **Functionality**: While Personas' have workflows, many workflows and many workers can share the same code, do the same thing
- **Data**: Handles the processing, creation and editing of data, including written files and accessed configuration files

## Planned

v0.9.5 needs to iron out many of the existing bugs and introduce QOL features for making the site comfortable to use, as well as
adding a paywall before public beta (sorry 😅)

Some of the features planned for the next few releases..

### Functionality

- **Response options**: After a response is output the option exists to reference it immediately, with settings for automatic reference
   or to make saving a message a manual selection rather an automatic process.
- **Payment System**: Top up system for updating balance (via stripe)
  - Attach receipts to ~~prompts~~, workflows and ~~features~~. So the user always knows how much they've spent and on what.
- **Internet access**: Rather than just reading a related summary of a search actually read the content of the first few 
  pages of each internet search
  - Settings to disable automatic internet searches and specify pages to search through
  - Visual display in workflow of pages visited
- **Deepseek R1**:
  - Option for selecting the 'default' model (internally and for workflow steps)
- **O3-mini**:
  - Awaiting access..
- **Reference/File message optimisation**: Optimised with regards to the prompt referencing them, this could both minimise
  confusion when using a lot of reference material and also serve as basically a 2nd step in the 'though process' of responding
  to a given prompt

### UI

- **QOL**:
  - Visual redesign of pages and messages, make messages ~~and files~~ viewable at the end of a workflow response
    - Add option to manually specify if a file should be overwritten or a new version created
  - 'Delete selected items' button
  - 'Delete category' button
  - Prompts can fail and the user doesn't know why, it just stalls at 'Processing..'
  - It's hard to select a file vs expanding it for review (solved if that means the same thing though..)
  - Ability to undo changes to files



