The project's architecture is designed with modularity in mind:

- **Personas**: (because ChatGpt uses 'roles' already) a class that structurally represents the idea of a worker specialised for a
  particular task, the (original) idea is that in concert a series of Persona's could work together in a sensible way, while leveraging individual specialisations
  - **PersonaSpecification**: Handles the defining of lengthy system messages and instructions
- **Workflows**: A workflow to be run against the users prompt, called by the relevant persona.
- **AiOrchestration**: Handles the actual to calls to a given llm, working with executors that handle user messages (prompts), contextual system messages, history and attached files
- **Functionality**: While Personas' have workflows, many workflows and many workers can share the same code, do the same thing
- **Data**: Handles the processing, creation and editing of data, including written files and accessed configuration files
