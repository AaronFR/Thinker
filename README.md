# The Thinker

## Objectives
The primary objective of this project is to create an intelligent system that's more than the sum of its parts, 
utilising multiple LLM calls to be able to iterate and evaluate prompts with quality and if requested quantity.

- Automate Problem-Solving: To provide a system that can evaluate and generate solutions for various tasks without
 extensive manual intervention.
- Modular-Architecture: That can explore and evaluate a wide range of tasks using AI-based thought processing, with flexibility and adaptability.

## Current Limitations

- **Quality**: The ideal goal for this project would be for a ChatGpt4o-mini driven workflow to consistently deliver 
  better quality answers than a single chatGpt prompt on ChatGpt4o, this is not a standard it actually meets.
- **Limited workflows**: Currently the Thinker can create code classes, test classes and write general reports for a given topic.

## Features
- **Workflows**: A user prompt is fed into a persona and evaluated for one of its workflows, a workflow representing a
 series of prompts to be run to achieve an ideal outcome for the given task type.
- **Pre-Prompt-Processing**: 'sub-conscious' processes, referencing information as required by context in advance of an
 actual LLM call

## Architecture
The project's architecture is designed with modularity in mind, allowing for the easy addition of new features and components:

- **Personas**: (because ChatGpt uses 'roles' already) a class that structurally represents the idea of a worker specialised for a
  particular task, the idea is that in concert a series of Persona's could work together in a sensible way, while leveraging individual specialisations
  - **PersonaSpecification**: Handles the defining of lengthy system messages and instructions
- **AiOrchestration**: Handles the actual to calls to a given llm, working with executors that handle user messages (prompts), contextual system messages, history and attached files
- **Functionality**: While Personas' have workflows, many workflows and many workers can share the same code, do the same thing
- **Data**: Handles the processing, creation and editing of data, including written files and accessed configuration files

## Features to implement
To refine the system's architecture and enhance its capabilities and efficiency, several key features are intended for implementation:
- **Expand Workflows**: More workflows for more use-cases, improving on the quality of existing workflows.
  - **Modular Workflows**: In write_workflow for coder there's always a step for improving code quality/
    writing documentation this should actually be a switch depending on the context.
    Many workflows should consist of switch logic that allows for intelligent processing of a given request without needless details.
  - **Workflow Feedback**: The coder module can and should actually check that its code works and try and improve upon itself if it doesn't.
   even if it can only try a fixed number of times and worst case scenario explains to the user that its solution is invalid 
   and this is the best it can do, this is a huge improvement in value.
  - **Blueprint**: Certain workflows should follow outlined blueprints created on the spot, guiding the construction of 
   documents, ensuring internal consistency and coherence.
- **Expand data stores**: Encyclopedias need to be filled out with relevant information (Currently in prototyping stage)
- **n-shot prompting**: Give the AI models examples of how it should answer roughly similar tasks.
- **Parallel Processing**: Implement parallel processing to handle multiple tasks simultaneously, improving performance and reducing task completion time.
- **DAG Structure for Task Management**: Introduce a Directed Acyclic Graph (DAG) framework to streamline decision-making efficiency, enabling better organization and oversight of tasks.
- **API Integrations**: Integrate additional AI models for improved capability and accuracy, along with the ability to search resources like Wikipedia and the web.


